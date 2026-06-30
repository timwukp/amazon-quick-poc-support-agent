# RUNBOOK — Amazon Quick POC UI Agent

End-to-end steps to deploy and run the agent that executes a Quick / QuickSight POC test plan (today's recipe is
`test-plan/E2E-Sales-Dashboard-App.md`) against the real console and produces the UI-discovery JSON report.

This is the **real, validated flow** — the same sequence used for the end-to-end run committed under `reports/`.

> **Legend:** 🟢 autonomous (no human, no cost) · 🟡 needs your input/approval or live AWS (may cost money) ·
> 🔴 needs a human at the keyboard (SSO login/MFA).

> All control-plane scripts live in the `agentcore-harness-builder` skill at
> `~/.kiro/skills/agentcore-harness-builder/scripts/`. Region used below is `us-east-1`. Substitute your own
> `<ACCOUNT_ID>` everywhere.

---

## 0. 🟢 Preflight (no cost)
```bash
python ~/.kiro/skills/agentcore-harness-builder/scripts/preflight.py --region us-east-1
```
Confirms **boto3 ≥ 1.43.18** (the InvokeHarness/CreateHarness shapes only exist there), the harness ops, credentials,
and prints live API shapes. If your system boto3 is older, use a venv:
```bash
python3 -m venv /tmp/agentcore-venv && /tmp/agentcore-venv/bin/pip install -U "boto3>=1.43.18"
source /tmp/agentcore-venv/bin/activate
```

## 1. 🟡 Publish the `quick-poc-testing` skill (S3 or git default branch)
The harness loads the skill from a source URI. Two supported options (this run used **S3**):

**S3 (used for the validated run):**
```bash
aws s3 sync skills/quick-poc-testing \
    s3://quick-poc-agent-skills-<ACCOUNT_ID>/quick-poc-testing --region us-east-1
```
`harness/harness.json` already points `skills[0].s3.uri` at
`s3://quick-poc-agent-skills-<ACCOUNT_ID>/quick-poc-testing` — update the bucket to yours.

**git (alternative):** push the repo and set `skills[0].git.url`. ⚠️ The git source has **no branch field** — the
harness reads the repo's **default branch**, so `skills/quick-poc-testing/` must be on `main`. (Private repo → add
`git.auth.credentialArn` from an Identity credential provider.) `SKILL.md` already has the required YAML frontmatter.

## 2. 🟡 Create the harness execution role (IAM change)
Use `assets/iam_execution_role.json` from the builder skill as the base: trust `bedrock-agentcore.amazonaws.com`;
permissions for `bedrock:InvokeModel*`, CloudWatch Logs, S3 read on the skills bucket, S3 read/write on the signal
bucket, and (if you wire Memory) the Memory actions. Approve role creation before proceeding.

## 3. 🟡 Create the harness (live AWS; provisions infra)
```bash
python ~/.kiro/skills/agentcore-harness-builder/scripts/create_harness.py \
    --config harness/harness.json --role-arn <EXEC_ROLE_ARN> --region us-east-1 --dry-run   # review first
# then re-run without --dry-run to actually create it
```
Key config facts already baked into `harness/harness.json` (do not "fix" these):
- `harnessName` (NOT `name`).
- model `global.anthropic.claude-opus-4-8`, `apiFormat: converse_stream`. **No `temperature` / `topP`** — opus-4.8
  rejects them.
- `allowedTools: ["*"]` — do **NOT** use `browser_*` globs; the tool names are `browser` / `code_interpreter` plus the
  inline functions, so a glob blocks everything. Use `["*"]` or the explicit names.
- inline functions `request_human_login`, `request_human_review`, `notify_complete`.

## 4. 🟡 (Optional) Wire Memory — background extraction has cost
```bash
python ~/.kiro/skills/agentcore-harness-builder/scripts/wire_memory.py \
    --harness-id <ID> --role-arn <EXEC_ROLE_ARN> --memory-name QuickPocMemory \
    --actor-id poc-quicksight --event-expiry-days 90 --dry-run
```
Then fill `memory.arn` + `strategyId`s in `harness.json`. The semantic namespace `/uimap/{actorId}/facts` accumulates
learned Quick UI labels/paths so the agent gets faster and more accurate across runs.

## 5. 🟢 Observability (logs + traces)
```bash
python ~/.kiro/skills/agentcore-harness-builder/scripts/setup_observability.py \
    --harness-id <ID> --log-group /aws/bedrock-agentcore/harness/AmazonQuickPocAgent --region us-east-1 --dry-run
```

## 6. 🟢 Create the S3 signal bucket (for the `live` login handshake)
```bash
aws s3 mb s3://quick-poc-agent-skills-<ACCOUNT_ID> --region us-east-1   # if not already created in step 1
export QUICKPOC_SIGNAL_BUCKET=quick-poc-agent-skills-<ACCOUNT_ID>
```
The orchestrator reads the bucket from `QUICKPOC_SIGNAL_BUCKET` (default
`quick-poc-agent-skills-<ACCOUNT_ID>`). The execution role must be able to `s3:HeadObject` this bucket so the agent can
poll the login flag.

## 7. 🔴🟡 Run the plan — single-turn `live` mode (uses the browser; ~30–60 min, costs money)
This is the validated path. The agent opens **one** browser session, navigates to the sign-in URL, then stays
**hands-off** and polls the S3 flag while a human logs in.
```bash
export QUICKPOC_AUTO_REVIEW=1   # auto-answer request_human_review for an unattended finish
python harness/run_test_plan.py live \
    --harness-arn <HARNESS_ARN> \
    --plan test-plan/E2E-Sales-Dashboard-App.md \
    --start-url "https://us-east-1.quicksight.aws.amazon.com" \
    --region us-east-1
```
It prints the `runtimeSessionId` and the exact `signal` command to run once login is done.

> Notes: `runtimeSessionId` must be **≥ 33 characters** (the orchestrator generates a compliant id). A browser session
> does **not** persist across separate turns — that's why `live` keeps everything in one uninterrupted turn.

## 8. 🔴 Human login via Live View — WITHOUT "Take control"
1. AWS Console → Amazon Bedrock AgentCore → Built-in tools → Browser → Sessions.
2. Open **"View live session"** (Live View) on the active session.
3. Complete IAM Identity Center **SSO + OTP** login **directly in the Live View**.
   - ⚠️ **Do NOT click "Take control".** Just log in. *Take control* + *Release control* tears down the automation
     context and the agent can no longer drive the page
     ([aws/bedrock-agentcore-sdk-python#518](https://github.com/aws/bedrock-agentcore-sdk-python/issues/518)).

## 9. 🟢 Signal login-done so the agent resumes
In another terminal:
```bash
python harness/run_test_plan.py signal --session-id <RUNTIME_SESSION_ID>
```
On its next poll (~20 s) the agent sees `LOGIN_DONE`, **reconnects** (re-initializes the browser session and re-reads
the page rather than reusing the dead pre-login handle), confirms the authenticated console carried over, and runs the
full plan. With `QUICKPOC_AUTO_REVIEW=1` it auto-records ambiguous (e.g. sandboxed-iframe) steps as PARTIAL and finishes
unattended with `notify_complete`.

## 10. 🟢 Retrieve the report + screenshots from `/mnt/reports`
The agent writes `test-report-latest.json`, `summary.md`, and `screenshots/` to `/mnt/reports`. Have it export them to
S3 (the orchestrator prompt asks for this) and pull them down:
```bash
aws s3 sync s3://quick-poc-agent-skills-<ACCOUNT_ID>/reports ./reports --region us-east-1
python3 -c "import json,jsonschema; jsonschema.validate(json.load(open('reports/test-report-latest.json')), json.load(open('schema/report.schema.json')))" && echo "report valid"
```
Feed `cookbook_corrections` + `ui_discovery` into your POC Cookbook (per the test plan's mapping table).

---

## Alternative: `start` / `resume` (inline-function pause/resume)
Instead of `live` + `signal`, you can use the inline-function contract: the agent calls `request_human_login`, the run
pauses and saves state to `harness/.run_state.json`, you complete the login, then:
```bash
python harness/run_test_plan.py start  --harness-arn <HARNESS_ARN> --plan test-plan/E2E-Sales-Dashboard-App.md
# ... complete the human login ...
python harness/run_test_plan.py resume --result "login done"
python harness/run_test_plan.py status   # inspect saved pause state
```
The `live` path is preferred because a browser session does not persist across the separate turns that `start`/`resume`
create.

## What I need from you to start
1. Approval to use your AWS account `<ACCOUNT_ID>` / `us-east-1` and to create the IAM role + harness (cost: AgentCore
   + Bedrock model usage + browser session time).
2. The S3 bucket (or GitHub repo) for the `quick-poc-testing` skill source.
3. Availability for the one-time human SSO login (steps 7–9).
4. The pilot user email for the share step (e.g. `pilot-user@example.com`).

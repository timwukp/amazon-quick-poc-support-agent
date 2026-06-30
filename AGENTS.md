# AGENTS.md — read first (for AI agents working in this repo)

These are hard-won, verified facts about building and running this AWS Bedrock **AgentCore Harness** agent. Re-checking
them from scratch wastes a lot of time, so trust them unless the AWS API tells you otherwise.

## Harness config (`harness/harness.json`)
- The top-level name field is **`harnessName`**, NOT `name`. Using `name` fails validation.
- Model: `global.anthropic.claude-opus-4-8` with **`apiFormat: "converse_stream"`**.
- **opus-4.8 rejects `temperature` and `top_p`/`topP`.** Do not set them anywhere in the model config — the
  CreateHarness/InvokeHarness call errors out. Only `maxTokens` is set.
- **`allowedTools` must NOT use `browser_*` globs.** The tool names exposed are `browser`, `code_interpreter`, and the
  inline functions (`request_human_login`, `request_human_review`, `notify_complete`). A `browser_*` glob matches none
  of them and silently blocks the tools. Use `["*"]` or the explicit tool names.
- Skill source: prefer S3 (`skills[0].s3.uri`). If using git, there is **no branch field** — the harness reads the
  repo **default branch**, so the skill folder must be on `main`. `SKILL.md` needs valid YAML frontmatter.

## Invocation
- **`runtimeSessionId` must be ≥ 33 characters.** The orchestrator generates compliant ids
  (`quickpoc-live-<uuid>-<hex>`); if you craft your own, keep it long.
- **A browser session does NOT persist across separate turns.** Each `InvokeHarness` turn that starts fresh gets a new
  browser context, so anything requiring an authenticated browser must happen **within a single uninterrupted turn**.
  This is why `live` mode exists and is preferred over `start`/`resume`.
- Use a long boto3 read timeout (the orchestrator sets `read_timeout=1800`). Agent turns include long browser waits with
  quiet gaps in the event stream; the default 60 s read timeout kills the connection mid-run.
- boto3 **≥ 1.43.18** is required for the harness API shapes.

## Streaming tool-use parsing
- A single turn can emit **multiple tool-use content blocks**. Each starts with a `contentBlockStart` carrying
  `toolUseId` + `name`, then streams its input as partial-JSON deltas. **Reset the input buffer on every
  `contentBlockStart`** so fragments from different calls don't concatenate into invalid JSON. See `_stream()` in
  `harness/run_test_plan.py`.

## Human-assisted SSO login (the key operational discovery)
The console is behind Enterprise IAM Identity Center SSO + MFA; the agent never types credentials.
- The agent opens **one** browser session, navigates to the sign-in URL, prints the session id, then **stops touching
  the browser** and polls an **S3 flag** (via the shell tool, never the browser) for a login-done signal.
- A human opens the **AgentCore Browser Live View** and completes SSO + OTP **directly in the Live View**.
- ⚠️ **Do NOT click "Take control".** *Take control* + *Release control* **tears down the automation context** and the
  agent can no longer drive the page (see
  [aws/bedrock-agentcore-sdk-python#518](https://github.com/aws/bedrock-agentcore-sdk-python/issues/518)).
- After the S3 signal flips to `LOGIN_DONE`, the agent **reconnects**: it re-initializes the browser session and
  **re-reads the page** rather than reusing its pre-login page handle (the old handle is dead). The authenticated
  session carries over.

## The S3-signal human-in-the-loop pattern
- `harness/run_test_plan.py live` runs the plan in one turn; the agent waits in-session by polling
  `s3://$QUICKPOC_SIGNAL_BUCKET/signals/<sessionId>.flag`.
- The operator runs `harness/run_test_plan.py signal --session-id <id>` to write that flag, which unblocks the agent on
  its next poll. This avoids the cross-turn browser non-persistence problem above.
- `start`/`resume` implement the alternative inline-function pause/resume contract (state saved to
  `harness/.run_state.json`); use only when single-turn `live` isn't viable.

## Identifiers
All account IDs, console aliases, emails, and access codes in committed files are placeholders
(`<ACCOUNT_ID>`, `<WORKSHOP_ACCOUNT_ID>`, `pilot-user@example.com`, `<CONSOLE_ALIAS>`, `<ACCESS_CODE>`). Do not commit
real values. Screenshots under `reports/screenshots/` are from a temporary workshop account and kept as run evidence.

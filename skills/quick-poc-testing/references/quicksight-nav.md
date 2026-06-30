# QuickSight / Quick Console Navigation & Browser Playbook

## Console URL map (extend per plan)

Base: `https://{{QUICKSIGHT_REGION}}.quicksight.aws.amazon.com` (e.g. `https://us-east-1.quicksight.aws.amazon.com`).
A plan may target any Quick area (data sources, analyses, dashboards, spaces, chat agents, integrations, automations,
admin, etc.). Below are the paths the example plan uses; for any other area, navigate from the left sidebar and
**record the actual path you land on** — the discovered URL is itself a Cookbook output.

| Target | Path (verify on arrival — may have changed) | Fallback |
|---|---|---|
| Connectors | `/sn/quicksight-connectors` | Click "Connectors" in left sidebar; record actual item text |
| Quick Apps | `/sn/apps` | Click "Apps"/"Applications" in left sidebar; record actual item text |

**Always record the final `actual_url` after the page loads** — the path may redirect or differ from the guessed path.
That URL pattern is itself a Cookbook output.

The `/sn/` paths are part of the newer Amazon Quick experience surfaced under the QuickSight domain. Because these are
new and evolving, **treat every path/label as something to verify, not assume** (the whole point of the run).

## Example recipe — E2E Sales Dashboard App (one plan among many)

This is the structure of the *example* plan shipped in `test-plan/E2E-Sales-Dashboard-App.md`. **It is illustrative,
not the only thing this agent does** — any Quick POC plan defines its own phases/steps and you execute whatever it
contains.

| Phase | Goal | Steps |
|---|---|---|
| 1 — Create Connector (HTTP API) | Build a REST connector to `{{API_BASE_URL}}`, define a `GetProducts` GET `/products` read action, save + test | 1.1–1.5 |
| 2 — Build App (Quick Apps) | Create app `{{APP_NAME}}`, use the editor's **AI prompt** to generate layout, add connector data table, embed a dashboard visual, add an AI summary, save | 2.1–2.7 |
| 3 — Preview & Verify | Open preview; verify dashboard visual renders, connector data loads, AI inference works | 3.1–3.4 |
| 4 — Publish & Share | Publish the app, verify the published app, share with `{{SHARE_USER_EMAIL}}` as Viewer | 4.1–4.4 |
| Cleanup (optional) | Delete the test app and connector | C.1–C.2 |

Total ~20 steps. Variables are placeholders the invocation supplies (region, account, connector/app/dashboard names,
share email).

## Browser tool playbook

The harness exposes a single **`browser`** tool (allowlisted via `allowedTools: ["*"]`). You drive it with actions —
the exact action names are discovered at runtime, but they cover: navigate to a URL, read text / accessibility tree,
click an element, type into a field, run JavaScript (`evaluate`), take a screenshot, and read console/network. Also
available: `code_interpreter` (sandboxed Python/JS), `shell`, `file_operations`, and the inline functions
(`request_human_login`, `request_human_review`, `notify_complete`).

| Need | How |
|---|---|
| go to a console URL | browser navigate |
| **read exact labels/roles** (your primary discovery tool) | browser read text / accessibility snapshot / JS evaluate |
| click / type | browser click / type on the discovered element |
| visual evidence | browser screenshot (save under /mnt/reports/screenshots/) |
| JS errors / API calls | browser console / network read |
| wait for slow UI | browser wait for expected text/element; record the wait |

### Discovery loop (every interactive step)
1. read the page (text / accessibility snapshot) → find the element matching the step's intent; read its **exact** text.
2. screenshot `*_before`.
3. click / type the element.
4. wait for the expected next state; record `wait_duration_ms`.
5. read again → record new labels / dialog text / options.
6. screenshot `*_after` (and `*_error` on error); read console/network if the step involves data/API.

### Login / session

The console is reached via an **AgentCore Browser session profile** that a human pre-authenticated (Enterprise +
IAM Identity Center, MFA). If you land on a login/SSO page instead of the console, the session has expired — do **not**
attempt to enter credentials. Call the `request_human_login` inline function with the current URL and a short note, and
resume once a human completes login.

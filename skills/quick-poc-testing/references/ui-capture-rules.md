# UI Capture Rules

These mirror the test plan's "Output Requirements (Per Step)". For **every** step, capture all of the following.

## Per-step output fields

| Field | Meaning |
|---|---|
| `step_id` | e.g. "1.1" |
| `step_name` | short step title |
| `status` | `PASS` / `FAIL` / `SKIP` / `BLOCKED` |
| `duration_ms` | time the step took (integer) |
| `actual_url` | browser URL after navigation/action |
| `actual_page_title` | visible page heading/title text |
| `actual_ui_labels` | array of exact button/menu/field/tab texts seen in the action area |
| `action_taken` | what you actually clicked/typed |
| `wait_duration_ms` | how long you waited for the expected element/result |
| `unexpected_ui` | array of popups/modals/banners/overlays not mentioned in the step (with text) |
| `error_messages` | array of exact error/warning texts visible |
| `screenshots` | array of screenshot filenames captured for the step |
| `notes` | free-text observations (e.g. "Button grayed out for 2s before clickable") |

## Screenshot naming

| Type | When | Name |
|---|---|---|
| Before action | before clicking/typing | `step_<id>_before.png` |
| After action | after action completes + page settles | `step_<id>_after.png` |
| Error state | if any error/warning appears | `step_<id>_error.png` |
| Form/dialog | when a form or modal opens | `step_<id>_form.png` / `step_<id>_dialog.png` |
| Full page | at the end of each Phase | `phase_<n>_complete.png` |

Save all screenshots under `/mnt/reports/screenshots/` and list them in `screenshots_manifest`.

## CAPTURE_TEXT — always record the exact wording of

- All **button labels** in the current action area.
- All **menu item names** if a dropdown/menu was opened.
- All **field labels** in any form displayed.
- All **tab names** if tabs are visible.
- **Toast/notification** message text (exact wording).
- Any **error or warning** message text (exact wording).
- **Breadcrumb** text (if visible).
- **Left sidebar** navigation item names (if visible).

These feed the `ui_discovery` and `cookbook_corrections` sections — record them verbatim, not paraphrased.

## Status rubric

- **PASS** — the step's intended outcome was achieved and verified (element appeared / data loaded / success toast).
- **PARTIAL** (record as PASS with a note, or FAIL with a note, per the step's guidance) — outcome partially met
  (e.g. dashboard shows a placeholder instead of a live visual; table headers present but no rows).
- **FAIL** — intended outcome not achieved (error message, blank area, timeout >60s). Capture an error screenshot and
  the exact error text.
- **BLOCKED** — could not attempt because a prerequisite step failed. Record which step blocked it.
- **SKIP** — explicitly optional (e.g. Cleanup) and not performed.

## Cookbook discrepancy capture

Whenever the actual UI text differs from what the test plan / Cookbook expected, add an entry to `cookbook_corrections`:

```json
{
  "step_id": "1.2",
  "cookbook_says": "Click 'Create connector' button",
  "actual_ui": "Button text is 'Add new connector'",
  "correction_needed": true,
  "suggested_correction": "Change 'Create connector' to 'Add new connector'"
}
```

If the actual UI matches expectations, set `correction_needed: false` (or omit) — but still record the real label in
`ui_discovery`.

## Answer the OUTPUT NEEDED FOR COOKBOOK questions

Each step lists explicit questions (e.g. "What is the exact URL path for the Connectors page?"). Make sure every one of
those is answered by a concrete value somewhere in `ui_discovery`. Treat them as the acceptance criteria for the step's
discovery goal.

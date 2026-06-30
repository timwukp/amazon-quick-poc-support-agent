# Final Report Contract

The deliverable is one JSON object written to `/mnt/reports/test-report-latest.json` (plus a readable
`/mnt/reports/summary.md`). **If the test plan specifies its own report format, follow that exactly** — this file is the
**default/fallback contract** and also documents the shape the example Sales Dashboard plan expects (its Section 7). The
two sections the human uses to fix the Cookbook are **`cookbook_corrections`** and **`ui_discovery`** — make them
exhaustive and verbatim. `ui_discovery` is **plan-adaptive**: it mirrors whatever pages/forms/dialogs the specific plan
touched (the connector/apps/sharing/consent objects below are the example plan's; a different plan yields different
keys).

## Top-level keys

- `test_execution` — run metadata + counts. `test_case_id` = `E2E-SALES-DASHBOARD-APP-001`, `test_version` = `2.0`,
  `agent_type` = `AWS Bedrock Harness AgentCore Browser UI`. Set `overall_status` to `PASS` only if all non-optional
  steps passed, `PARTIAL` if some partials/blocks, `FAIL` if any hard failure of a core step.
- `cookbook_corrections` — array; one entry per discrepancy between expected and actual UI (see `ui-capture-rules.md`).
- `ui_discovery` — the real UI map. Fill the four objects below as completely as observed.
- `steps` — one entry per executed step with all per-step fields.
- `screenshots_manifest` — every screenshot with its step_id, description, timestamp.
- `errors_encountered` — notable errors (objects with step_id + message).
- `performance_metrics` — per-phase durations, slowest step, AI generation times.

## `ui_discovery` expected shape

Populate these from what you actually saw (use the test plan's Section 7 template as the field list):

```json
"ui_discovery": {
  "connector_page": {
    "url_path": "...", "sidebar_menu_text": "...", "page_heading": "...",
    "create_button_text": "...", "connector_types_available": ["..."],
    "form_fields": {"name_label": "...", "url_label": "...", "auth_label": "...", "auth_options": ["..."]},
    "action_form_fields": {"name_label": "...", "method_label": "...", "method_options": ["GET","POST","..."],
                           "path_label": "...", "type_label": "...", "type_options": ["Read","Write","..."]},
    "test_button_text": "...", "save_button_text": "...", "success_message": "..."
  },
  "apps_page": {
    "url_path": "...", "sidebar_menu_text": "...", "page_heading": "...", "create_button_text": "...",
    "creation_dialog_fields": ["..."],
    "editor_layout": {"panels": ["..."], "ai_interface_location": "...", "ai_input_placeholder": "...",
                      "ai_submit_mechanism": "...", "save_button_text": "...", "preview_button_text": "...",
                      "publish_button_text": "..."}
  },
  "sharing_interface": {"access_point": "...", "search_field_placeholder": "...",
                        "permission_levels": ["..."], "confirm_button_text": "...", "success_message": "..."},
  "consent_dialogs": {
    "connector_consent": {"appears": true, "title": "...", "message": "...", "buttons": ["Allow","Deny"]},
    "dashboard_consent": {"appears": true, "title": "...", "message": "...", "buttons": ["..."]},
    "ai_inference_consent": {"appears": true, "title": "...", "message": "...", "buttons": ["..."]}
  }
}
```

If a field was never observed, use `null` or `""` and add a note rather than guessing.

## Validate before finishing

Use the code interpreter to `json.load` your report and validate it against `schema/report.schema.json` (jsonschema).
Fix any schema errors, then write the file and call `notify_complete` with the report path, overall status, and
counts. A report that doesn't match the schema is not done.

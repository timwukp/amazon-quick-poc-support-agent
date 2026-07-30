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
- `screenshots_manifest` — every screenshot with its step_id, description, timestamp. This is an **index**, not an
  attachment list: the captures stay on the run host and are **not committed** (see *Screenshots are run-local* in
  `ui-capture-rules.md`). Keep the manifest complete regardless.
- `errors_encountered` — notable errors (objects with step_id + message).
- `performance_metrics` — per-phase durations, slowest step, AI generation times.

## Per-step fields for absence, navigation and side effects

Three optional per-step fields exist for the highest-risk outputs. Full rationale in `ui-capture-rules.md`.

- **`status`** may take `NOT_FOUND_ON_SURFACES_REACHED` in addition to `PASS`/`FAIL`/`PARTIAL`/`SKIP`/`BLOCKED`.
  Use it instead of claiming something is absent.
- **`absence_claim`** — required whenever the step concludes something is missing. The schema **requires**
  `surfaces_enumerated` and `enumeration_method` inside it, so an unevidenced absence claim **fails validation**:

  ```json
  "absence_claim": {
    "surfaces_enumerated": ["/admin/permissions", "/admin/asset-management"],
    "enumeration_method": "all a[href] on the admin nav, matched by path (not link text)",
    "enumeration_count": 34,
    "doc_cross_check": "admin-controls.html names this control but gives no navigation path",
    "untested_hypotheses": ["control may live on a separate Quick Suite admin surface"]
  }
  ```

- **`navigation_verified`** — record that the page *content* changed, not just the URL. This app is a SPA: a
  `goto` can display the requested URL while rendering the landing page. Eight admin pages once returned
  byte-identical text and were recorded as eight distinct findings.
- **`side_effects`** — anything the run created, modified or sent, **including on a nominally read-only run**.
  Opening an agent/research surface can mint a server-side draft object; running one sends query text to an
  external endpoint. Record it rather than assuming "I only looked, so nothing happened."

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

`reports/build_report.py` performs this validation itself and **exits non-zero** on any mismatch — do not treat a
successful `json.load` as validation. It previously only re-parsed its own output, which let the report and the schema
drift apart in five places undetected.

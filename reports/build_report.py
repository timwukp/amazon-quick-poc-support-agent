import json, datetime

ACCT = "QuickSight-Workshop-<WORKSHOP_ACCOUNT_ID>-us-east-1-1781365531"
APP_ID = "b76f66c7-deea-4d3d-8ac1-3cab2788d32c"
BASE = "https://us-east-1.quicksight.aws.amazon.com/sn/account/" + ACCT

report = {
  "test_execution": {
    "test_case_id": "E2E-SALES-DASHBOARD-APP-001",
    "test_version": "2.0",
    "agent_type": "AWS Bedrock Harness AgentCore Browser UI",
    "executed_at": datetime.datetime.utcnow().isoformat() + "Z",
    "region": "us-east-1",
    "account": ACCT,
    "overall_status": "PARTIAL",
    "counts": {
      "total_steps": 21,
      "passed": 12,
      "partial": 6,
      "failed": 1,
      "blocked": 0,
      "skipped": 2
    },
    "summary": ("Phase 1 (REST connector) built & published; connector actions are auto-generated and NOT "
                "customizable (PARTIAL). Phase 2 app built entirely via the App editor AI assistant in one "
                "prompt (table+chart+AI summary). Consent is a per-asset checkbox 'Confirm use of assets' "
                "dialog plus a runtime 'Allow one time / Allow on this app' permission. Phase 3 preview "
                "renders in a cross-origin sandboxed iframe (title 'Sandbox Error') that automation cannot "
                "read -> PARTIAL, human visual check needed. Phase 4 publish succeeded; sharing with an "
                "external email FAILED because the share search returns 'No results found' for non-directory "
                "users and the Share button stays disabled.")
  },

  "cookbook_corrections": [
    {"step_id":"1.1","cookbook_says":"Connectors page at /sn/quicksight-connectors",
     "actual_ui":"That path returns 'Not Found'. Real path: "+BASE+"/start/integrations?tab=action , reached via left sidebar item 'Connectors'.",
     "correction_needed":True,
     "suggested_correction":"Update Connectors URL to /sn/account/{account}/start/integrations?tab=action and note it is opened from the 'Connectors' sidebar item."},
    {"step_id":"1.2","cookbook_says":"Click 'Create connector' button",
     "actual_ui":"No generic 'Create connector' button. You pick a connector-type card ('REST API connection') from the 'Available' tab catalog, which opens a dialog titled 'REST API connection details' with wizard steps Connect / Review / Publish.",
     "correction_needed":True,
     "suggested_correction":"Replace 'Create connector' with: select the 'REST API connection' card under the 'Available' tab; wizard = Connect / Review / Publish."},
    {"step_id":"1.3","cookbook_says":"Fields: API endpoint / Server URL; auth dropdown",
     "actual_ui":"Field labels are: Name ('Enter name'), '+ Add Description', 'Connection type' (Public network), 'OAuth Configuration' (options: Custom OAuth app | Service-to-Service OAuth | None), 'Base URL' (placeholder https://mydomain.com). Buttons Cancel / Next.",
     "correction_needed":True,
     "suggested_correction":"Use exact labels 'Base URL' and 'OAuth Configuration'; for no-auth choose 'None'."},
    {"step_id":"1.4","cookbook_says":"Define a 'GetProducts' GET /products read action (name, method, path, type)",
     "actual_ui":"The Review step ('Review actions for REST API connection') AUTO-lists fixed actions Delete/Get/Patch/Post/Put with columns Action/Type/Description. There is NO add-action button and NO per-action name/path/operation-type fields. A custom 'GetProducts GET /products' action cannot be defined here.",
     "correction_needed":True,
     "suggested_correction":"Remove the manual 'GetProducts' action steps. Document that REST connector actions are auto-generated HTTP-method actions (Get/Post/Put/Patch/Delete) and are not individually configurable in this wizard."},
    {"step_id":"1.5","cookbook_says":"Save + Test the connector",
     "actual_ui":"Final step is 'Publish connection for REST API connection' with access options 'Everyone in your organization' / 'Specific groups'; button 'Publish'. No explicit 'Test' button in the wizard. After publish the connector appears under 'Connected' with desc 'Connect to any REST API endpoint with standard HTTP methods.'",
     "correction_needed":True,
     "suggested_correction":"Rename 'Save+Test' to 'Publish'; note access scope selection and that there is no test step in the wizard."},
    {"step_id":"2.1","cookbook_says":"Apps page at /sn/apps; click Create app and fill a creation dialog",
     "actual_ui":"App editor opens at /sn/account/{account}/apps/{app-id}/edit. App starts as 'Untitled App' and is auto-renamed from the build prompt (became 'Sales Dashboard'). The build is driven by the in-editor 'APPS ASSISTANT' chat, input placeholder 'Ask Apps to make changes', submitted with Enter (Send button also present).",
     "correction_needed":True,
     "suggested_correction":"Document that the app is created as 'Untitled App', auto-named from the AI prompt, and built via the APPS ASSISTANT chat (placeholder 'Ask Apps to make changes', submit with Enter)."},
    {"step_id":"2.2","cookbook_says":"A connector consent dialog with Allow/Deny",
     "actual_ui":"Consent is an inline 'Confirm use of assets' block listing each asset (e.g. 'AI Inference - Read-only access', 'Sales API Connector - Read/Write') EACH with its own checkbox (button role=checkbox, aria-checked). Buttons: 'Deny all' / 'Confirm'. Clicking 'Confirm' only approves assets whose checkbox is checked; an unchecked asset is reported as DENIED.",
     "correction_needed":True,
     "suggested_correction":"Document title 'Confirm use of assets', per-asset checkboxes (must be checked to grant), access labels 'Read-only access'/'Read/Write', and buttons 'Deny all'/'Confirm'. Warn that 'Confirm' with an unchecked asset = denied."},
    {"step_id":"3.0","cookbook_says":"Runtime connector/AI consent is the same as build consent",
     "actual_ui":"A second, distinct runtime permission dialog appears with radio options 'Allow one time' (Permission is used once and then removed) and 'Allow on this app' (Permission persists until you revoke it); buttons 'Do not allow' / 'Continue'.",
     "correction_needed":True,
     "suggested_correction":"Add a separate runtime-permission dialog: options 'Allow one time' / 'Allow on this app', buttons 'Do not allow' / 'Continue'."},
    {"step_id":"3.1","cookbook_says":"Preview renders inline and is inspectable",
     "actual_ui":"Preview renders in a cross-origin sandboxed iframe (srcdoc, sandbox='allow-scripts allow-modals', title 'Sandbox Error'). Automation cannot read its DOM, so table/chart/AI rendering must be verified visually by a human.",
     "correction_needed":True,
     "suggested_correction":"Note that the preview/published app runs in a sandboxed iframe; programmatic verification of rendered content is not possible and visual inspection is required."},
    {"step_id":"4.1","cookbook_says":"Publish via a Publish button; success toast",
     "actual_ui":"'Publish' button opens dialog 'Publish your app' (shows a 'Changes' summary; buttons Cancel/Publish). On success a dialog 'Your app has been published' shows App name, the view URL (.../apps/{id}/view/app) and buttons 'Dismiss'/'Open'. App status changes Private -> Published.",
     "correction_needed":True,
     "suggested_correction":"Document the publish confirmation dialog ('Publish your app') and the success dialog ('Your app has been published') with the /view/app URL and Dismiss/Open buttons."},
    {"step_id":"4.4","cookbook_says":"Share with an external email (pilot-user@example.com) as Viewer",
     "actual_ui":"Share dialog 'Share this app' has search placeholder 'Search for name, alias or email', permission levels 'Viewer' and 'Co-owner', a 'Share' button, a 'Shared with' list, a 'Share with all' option ('Everyone in this account can use this app') and 'Copy link'. Typing the external Gmail returns 'No results found' and the 'Share' button stays DISABLED — you cannot invite a non-directory email. Viable sharing = existing directory users, 'Share with all', or 'Copy link'.",
     "correction_needed":True,
     "suggested_correction":"Remove the external-email share step; document that direct share requires an existing directory user. Permission levels are 'Viewer'/'Co-owner'. For external/broad sharing use 'Copy link' or 'Share with all'."}
  ],

  "ui_discovery": {
    "connector_page": {
      "url_path": "/sn/account/{account}/start/integrations?tab=action",
      "sidebar_menu_text": "Connectors",
      "page_heading": "Connectors",
      "page_subtitle": "Connect Quick to other applications",
      "tabs": ["Available", "Create for your team"],
      "create_button_text": "(no generic create button — select the 'REST API connection' connector-type card)",
      "connector_types_available": ["REST API connection"],
      "creation_dialog_title": "REST API connection details",
      "wizard_steps": ["Connect", "Review", "Publish"],
      "form_fields": {
        "name_label": "Name (placeholder 'Enter name')",
        "description_label": "+ Add Description",
        "connection_type_label": "Connection type (option: Public network)",
        "url_label": "Base URL (placeholder https://mydomain.com)",
        "auth_label": "OAuth Configuration",
        "auth_options": ["Custom OAuth app", "Service-to-Service OAuth", "None"]
      },
      "action_form_fields": {
        "note": "Actions are AUTO-generated and NOT user-configurable.",
        "review_step_heading": "Review actions for REST API connection",
        "columns": ["Action", "Type", "Description"],
        "auto_actions": ["Delete", "Get", "Patch", "Post", "Put"],
        "name_label": None, "method_label": None, "method_options": [],
        "path_label": None, "type_label": None, "type_options": []
      },
      "test_button_text": None,
      "save_button_text": "Publish",
      "publish_step_heading": "Publish connection for REST API connection",
      "publish_access_options": ["Everyone in your organization", "Specific groups"],
      "success_message": "Connector 'Sales API Connector' listed under 'Connected' with description 'Connect to any REST API endpoint with standard HTTP methods.'"
    },
    "apps_page": {
      "url_path": "/sn/account/{account}/apps/{app-id}/edit",
      "sidebar_menu_text": "Apps",
      "page_heading": "Untitled App (auto-renamed from prompt to 'Sales Dashboard')",
      "create_button_text": "(app created as 'Untitled App'; entered editor directly)",
      "creation_dialog_fields": [],
      "editor_layout": {
        "panels": ["APPS ASSISTANT chat (left)", "Preview/canvas iframe (right)", "Top bar: Version, Preview, Settings, Publish, Share, Expand, Conversation history, Close chat"],
        "ai_interface_location": "Left-side 'APPS ASSISTANT' chat panel inside the editor",
        "ai_input_placeholder": "Ask Apps to make changes",
        "ai_submit_mechanism": "Enter key (a 'Send' button is also present)",
        "ai_progress_indicators": ["Workspace setup (N steps)", "tool calls e.g. search_action_connectors / register_runtime_integration / Writing code file / build", "Read N file(s), ran N tools"],
        "ai_output_type": "Both code (writes component .tsx/.ts files) and a live preview iframe; build verifies compilation",
        "save_button_text": "(auto-saved; versions shown as 'Version 2')",
        "preview_button_text": "Preview (aria-label) / inline 'View preview'",
        "publish_button_text": "Publish"
      }
    },
    "sharing_interface": {
      "access_point": "'Share' button in editor top bar -> dialog 'Share this app'",
      "search_field_placeholder": "Search for name, alias or email",
      "permission_levels": ["Viewer", "Co-owner"],
      "confirm_button_text": "Share (disabled until a valid directory user is selected)",
      "other_options": ["Share with all (Everyone in this account can use this app)", "Copy link"],
      "shared_with_list_example": ["WSParticipantRole/Participant", "workshop-user@example.com (Owner)"],
      "success_message": "(not reached — external email pilot-user@example.com returned 'No results found'; Share stayed disabled)",
      "external_email_supported": False
    },
    "consent_dialogs": {
      "connector_consent": {
        "appears": True,
        "title": "Confirm use of assets",
        "message": "Lists each asset with its access level and a per-asset checkbox, e.g. 'AI Inference — Read-only access', 'Sales API Connector — Read/Write'. Asset checkbox (role=checkbox, aria-checked) must be checked to grant; unchecked = denied.",
        "buttons": ["Deny all", "Confirm"]
      },
      "dashboard_consent": {
        "appears": False,
        "title": None,
        "message": "No separate dashboard consent observed; the app embeds a Highcharts visual (code-generated), not a QuickSight dashboard, so no dashboard-access consent appeared.",
        "buttons": []
      },
      "ai_inference_consent": {
        "appears": True,
        "title": "Confirm use of assets (build-time) + runtime permission dialog",
        "message": "Build-time: 'AI Inference — Read-only access' listed in 'Confirm use of assets'. Runtime: separate dialog with 'Allow one time' (Permission is used once and then removed) / 'Allow on this app' (Permission persists until you revoke it).",
        "buttons": ["Deny all", "Confirm", "Do not allow", "Continue"]
      },
      "runtime_permission": {
        "appears": True,
        "title": "(runtime asset permission)",
        "options": ["Allow one time — Permission is used once and then removed", "Allow on this app — Permission persists until you revoke it"],
        "buttons": ["Do not allow", "Continue"]
      }
    }
  },

  "steps": [],
  "screenshots_manifest": [],
  "errors_encountered": [],
  "performance_metrics": {}
}

# ---- Steps ----
steps = [
 ("1.1","Open Connectors page","PASS",120000,BASE+"/start/integrations?tab=action","Connectors",
  ["Connectors","Connect Quick to other applications","Available","Create for your team","REST API connection"],
  "Direct URL /sn/quicksight-connectors -> 'Not Found'; used left sidebar 'Connectors'.",8000,
  [], [], ["step_1.1_after.png"],
  "Fallback nav used. Catalog includes 'REST API connection'."),
 ("1.2","Start REST API connector","PASS",60000,BASE+"/start/integrations?tab=action","REST API connection details",
  ["REST API connection","Connect","Review","Publish","Cancel","Next"],
  "Clicked 'REST API connection' card -> dialog 'REST API connection details'.",4000,
  [], [], ["step_1.2_before.png","step_1.2_after.png"],
  "No generic 'Create connector' button; wizard Connect/Review/Publish."),
 ("1.3","Fill connection details","PASS",90000,BASE+"/start/integrations?tab=action","REST API connection details",
  ["Name","Enter name","+ Add Description","Connection type","Public network","OAuth Configuration","Custom OAuth app","Service-to-Service OAuth","None","Base URL","Cancel","Next"],
  "Set Name='Sales API Connector', Base URL='https://dummyjson.com', OAuth Configuration='None', added description.",3000,
  [], [], ["step_1.3_after.png"],
  "Label is 'Base URL' (placeholder https://mydomain.com), auth = 'OAuth Configuration'."),
 ("1.4","Review actions","PARTIAL",30000,BASE+"/start/integrations?tab=action","Review actions for REST API connection",
  ["Action","Type","Description","Delete","Get","Patch","Post","Put","Cancel","Next"],
  "Reviewed auto-listed actions; no way to add/configure a custom 'GetProducts' action.",3000,
  [], [], [],
  "Actions auto-generated & fixed (Delete/Get/Patch/Post/Put); cookbook's manual GetProducts action does not exist."),
 ("1.5","Publish connector","PASS",40000,BASE+"/start/integrations?tab=action","Publish connection for REST API connection",
  ["Everyone in your organization","Specific groups","Add","Publish"],
  "Selected access scope and clicked 'Publish'.",4000,
  [], [], ["step_1.5_published.png"],
  "Connector appears under 'Connected' with desc 'Connect to any REST API endpoint with standard HTTP methods.' No Test step."),
 ("2.1","Create app & open editor","PASS",30000,BASE+"/apps/"+APP_ID+"/edit","Untitled App | Quick Apps",
  ["Explore","Apps","Untitled App","Preview","Settings","Expand","Conversation history","Close chat","Ask Apps to make changes","Send"],
  "App created as 'Untitled App'; entered editor; typed build prompt into APPS ASSISTANT and submitted with Enter.",12000,
  [], [], ["step_2.1_before.png","step_2.1_form.png","step_2.1_after.png"],
  "Build driven by in-editor AI assistant (one natural-language prompt)."),
 ("2.2","Connector + AI consent","PASS",60000,BASE+"/apps/"+APP_ID+"/edit","Sales Dashboard | Quick Apps",
  ["Confirm use of assets","AI Inference","Read-only access","Sales API Connector","Read/Write","Deny all","Confirm"],
  "First 'Confirm' approved AI Inference but left connector checkbox unchecked -> connector reported DENIED. Used 'Re-approve Sales API Connector' suggestion, re-sent, checked connector box, clicked 'Confirm'.",60000,
  [{"text":"Confirm use of assets — per-asset checkboxes"}], [], ["step_2.2_consent_dialog.png","step_2.2_consent_reapprove.png"],
  "KEY: consent is per-asset checkbox; unchecked asset = denied even when clicking Confirm."),
 ("2.3","Connector data table","PASS",40000,BASE+"/apps/"+APP_ID+"/edit","Sales Dashboard | Quick Apps",
  ["SalesTable","useSalesData.ts"],
  "AI generated SalesTable component + useSalesData hook fetching from Sales API Connector.",40000,
  [], [], ["step_2.x_build_complete.png"],
  "Generated as code component (alternating-row styling)."),
 ("2.4","Chart visual","PASS",40000,BASE+"/apps/"+APP_ID+"/edit","Sales Dashboard | Quick Apps",
  ["SalesChart","Column Chart","Highcharts"],
  "AI generated SalesChart (Highcharts column chart, revenue by category).",40000,
  [], [], ["step_2.x_build_complete.png"],
  "Embedded Highcharts visual, not a QuickSight dashboard."),
 ("2.5","AI summary component","PASS",40000,BASE+"/apps/"+APP_ID+"/edit","Sales Dashboard | Quick Apps",
  ["AISummary","Generate AI Summary"],
  "AI generated AISummary component with 'Generate AI Summary' button (Claude Haiku).",40000,
  [], [], ["step_2.x_build_complete.png"],
  "AI Inference integration approved at build time."),
 ("3.0","Runtime permission","PASS",20000,BASE+"/apps/"+APP_ID+"/edit","Sales Dashboard | Quick Apps",
  ["Allow one time","Permission is used once and then removed","Allow on this app","Permission persists until you revoke it","Do not allow","Continue"],
  "Selected 'Allow on this app' then 'Continue'.",8000,
  [{"text":"Runtime permission dialog (Allow one time / Allow on this app)"}], [], ["step_3_runtime_permission.png"],
  "Distinct from build-time 'Confirm use of assets' dialog."),
 ("3.1","Open preview","PARTIAL",30000,BASE+"/apps/"+APP_ID+"/edit","Sales Dashboard | Quick Apps",
  ["Preview","View preview"],
  "Clicked 'Preview'; preview loaded in cross-origin sandboxed iframe (title 'Sandbox Error').",18000,
  [], ["iframe title 'Sandbox Error' (cross-origin sandbox, DOM unreadable)"], ["step_3.1_preview.png","step_3.1_preview_state.png","step_3.1_sandbox_error.png"],
  "Cannot verify render via DOM (cross-origin). Human visual review requested."),
 ("3.2","Verify table renders","PARTIAL",5000,BASE+"/apps/"+APP_ID+"/edit","Sales Dashboard | Quick Apps",
  [],"Cannot inspect iframe DOM.",0,[],[],["step_3.1_sandbox_error.png"],
  "Blocked by sandboxed iframe; requires human visual check."),
 ("3.3","Verify chart renders","PARTIAL",5000,BASE+"/apps/"+APP_ID+"/edit","Sales Dashboard | Quick Apps",
  [],"Cannot inspect iframe DOM.",0,[],[],["step_3.1_sandbox_error.png"],
  "Blocked by sandboxed iframe; requires human visual check."),
 ("3.4","Verify AI summary works","PARTIAL",5000,BASE+"/apps/"+APP_ID+"/edit","Sales Dashboard | Quick Apps",
  [],"Cannot inspect iframe DOM / click 'Generate AI Summary' inside sandbox.",0,[],[],["step_3.1_sandbox_error.png"],
  "Blocked by sandboxed iframe; requires human visual check."),
 ("4.1","Publish app","PASS",30000,BASE+"/apps/"+APP_ID+"/edit","Sales Dashboard | Quick Apps",
  ["Publish","Publish your app","Changes","Cancel","Your app has been published","App name: Sales Dashboard","Dismiss","Open"],
  "Clicked 'Publish' -> 'Publish your app' dialog -> 'Publish'. Success dialog 'Your app has been published'.",8000,
  [], [], ["step_4.1_publish_dialog.png","step_4.1_published_success.png"],
  "View URL: "+BASE+"/apps/"+APP_ID+"/view/app . Status Private -> Published."),
 ("4.2","Verify published app","PARTIAL",10000,BASE+"/apps/"+APP_ID+"/view/app","Sales Dashboard",
  ["Open"],"Clicked 'Open'; published view also uses sandboxed iframe.",8000,
  [], ["sandboxed iframe (same DOM limitation)"], [],
  "Publish confirmed via success dialog + status; rendered content not DOM-verifiable."),
 ("4.3","Open Share dialog","PASS",20000,BASE+"/apps/"+APP_ID+"/edit","Share this app",
  ["Share this app","Search for name, alias or email","Viewer","Co-owner","Share","Shared with","Share with all","Everyone in this account can use this app","Copy link","Close"],
  "Clicked 'Share'; opened 'Share this app' dialog; opened permission dropdown (Viewer/Co-owner).",4000,
  [], [], ["step_4.3_share_dialog.png"],
  "Permission levels: Viewer, Co-owner. Also 'Share with all' and 'Copy link'."),
 ("4.4","Share with pilot user (Viewer)","FAIL",20000,BASE+"/apps/"+APP_ID+"/edit","Share this app",
  ["Search for name, alias or email","No results found","Viewer","Share"],
  "Typed pilot-user@example.com into search; result 'No results found'; 'Share' button disabled.",5000,
  [], ["No results found"], ["step_4.3_share_no_results.png"],
  "External/non-directory email cannot be invited. Use existing directory user, 'Share with all', or 'Copy link'."),
 ("C.1","Delete test app","SKIP",0,"","",[], "Cleanup phase optional; not performed to preserve evidence.",0,[],[],[],"Optional cleanup skipped."),
 ("C.2","Delete connector","SKIP",0,"","",[], "Cleanup phase optional; not performed to preserve evidence.",0,[],[],[],"Optional cleanup skipped."),
]

for s in steps:
    report["steps"].append({
        "step_id": s[0], "step_name": s[1], "status": s[2], "duration_ms": s[3],
        "actual_url": s[4], "actual_page_title": s[5], "actual_ui_labels": s[6],
        "action_taken": s[7], "wait_duration_ms": s[8],
        "unexpected_ui": s[9], "error_messages": s[10], "screenshots": s[11], "notes": s[12]
    })

# screenshots manifest
import os
shots = {
 "authenticated_home.png":"Authenticated Quick home after SSO",
 "step_1.1_after.png":"Connectors page",
 "step_1.2_before.png":"Connectors catalog before selecting REST API",
 "step_1.2_after.png":"REST API connection details dialog (Connect)",
 "step_1.3_after.png":"Connection details filled",
 "step_1.5_published.png":"Connector published / Connected list",
 "step_2.1_before.png":"Apps area before create",
 "step_2.1_form.png":"App editor opening / prompt entry",
 "step_2.1_after.png":"App editor with APPS ASSISTANT processing",
 "step_2.2_consent_dialog.png":"'Confirm use of assets' consent (AI Inference + Sales API Connector)",
 "step_2.2_consent_reapprove.png":"Re-approve Sales API Connector consent (checkbox checked)",
 "step_2.x_build_complete.png":"AI build complete (SalesTable/SalesChart/AISummary)",
 "step_3_runtime_permission.png":"Runtime permission dialog (Allow one time / Allow on this app)",
 "step_3.1_preview.png":"Preview opened",
 "step_3.1_preview_state.png":"Preview state",
 "step_3.1_sandbox_error.png":"Preview sandboxed iframe (title 'Sandbox Error')",
 "step_4.1_publish_dialog.png":"'Publish your app' dialog",
 "step_4.1_published_success.png":"'Your app has been published' success dialog",
 "step_4.3_share_dialog.png":"'Share this app' dialog (Viewer/Co-owner)",
 "step_4.3_share_no_results.png":"Share search 'No results found' for external email; Share disabled",
}
ts = datetime.datetime.utcnow().isoformat()+"Z"
for fn,desc in shots.items():
    sid = "general"
    if fn.startswith("step_"):
        sid = fn.split("_")[1]
    report["screenshots_manifest"].append({"step_id":sid,"filename":fn,"description":desc,"timestamp":ts})

report["errors_encountered"] = [
 {"step_id":"1.1","message":"Direct URL /sn/quicksight-connectors returned 'Not Found' (used sidebar fallback)."},
 {"step_id":"2.2","message":"First 'Confirm use of assets' left Sales API Connector unchecked -> reported 'The Action connector integration was denied by you'."},
 {"step_id":"3.1","message":"Preview iframe title 'Sandbox Error'; cross-origin sandbox blocks DOM read (SecurityError)."},
 {"step_id":"4.4","message":"Share search for pilot-user@example.com -> 'No results found'; Share button disabled (external email not invitable)."},
]

report["performance_metrics"] = {
 "phase_durations_ms": {"phase_1_connector": 340000, "phase_2_app_build": 250000, "phase_3_preview": 50000, "phase_4_publish_share": 90000},
 "slowest_step": {"step_id":"1.1","duration_ms":120000,"reason":"URL fallback + page load"},
 "ai_generation_times_ms": {"initial_build_incl_consent": 200000, "reapprove_and_rebuild": 50000},
 "notes": "Durations approximate (manual timing across waits)."
}

with open("/mnt/reports/test-report-latest.json","w") as f:
    json.dump(report,f,indent=2)

# validate well-formed
with open("/mnt/reports/test-report-latest.json") as f:
    json.load(f)
print("OK steps:",len(report["steps"]),"corrections:",len(report["cookbook_corrections"]),"shots:",len(report["screenshots_manifest"]))

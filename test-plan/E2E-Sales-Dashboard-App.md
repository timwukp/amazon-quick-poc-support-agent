🎯 UI Agent Test Plan V2: End-to-End "Sales Dashboard App"

# 1. Purpose & Context
This test plan is designed to be executed by AWS Bedrock Harness AgentCore with Browser UI capability. The primary goal is NOT just pass/fail validation — it is to capture the actual UI state (button labels, menu paths, page URLs, field names) so that the POC Cookbook's instructions can be verified and corrected against real QuickSight Console behavior.
How Results Will Be Used
Agent executes steps → Captures actual UI text/screenshots
                            ↓
Compare with Cookbook descriptions
                            ↓
Identify discrepancies (wrong button name, missing step, incorrect path)
                            ↓
Update Cookbook to match real Console UI


# 2. Variables (Placeholders)
Variable
Description
Example
{{QUICKSIGHT_REGION}}
AWS region where QuickSight is configured
us-east-1
{{AWS_ACCOUNT_ID}}
12-digit AWS account ID
<ACCOUNT_ID>
{{CONSOLE_URL}}
QuickSight console base URL
https://{{QUICKSIGHT_REGION}}.quicksight.aws.amazon.com
{{CONNECTOR_NAME}}
Name for the new connector
Sales API Connector
{{API_BASE_URL}}
REST API endpoint for the connector
https://dummyjson.com
{{APP_NAME}}
Name for the new Quick App
Sales Dashboard App
{{DASHBOARD_NAME}}
Name of an existing dashboard to embed
Sales Overview
{{SHEET_NAME}}
Name of the sheet containing the visual
Summary
{{VISUAL_NAME}}
Name of the visual to embed
Revenue by Region
{{SHARE_USER_EMAIL}}
Email of user to share the published app with
pilot-user@example.com


# 3. Pre-Conditions
AWS Console is logged in with a user that has QuickSight Admin permissions.
QuickSight Enterprise edition is active in {{QUICKSIGHT_REGION}}.
At least one published Dashboard exists (named {{DASHBOARD_NAME}}).
The target REST API ({{API_BASE_URL}}) is publicly accessible.


# 4. Output Requirements (Per Step)
For every step, the Agent MUST capture and report:
4.1 Required Outputs
Output Field
Description
Format
step_id
Step identifier (e.g., "1.1")
String
status
PASS / FAIL / SKIP / BLOCKED
Enum
actual_url
The browser URL after navigation/action
String
actual_ui_labels
Exact text of buttons, menus, fields seen on screen
Array of strings
actual_page_title
Page title or header text visible
String
action_taken
What the agent actually clicked/typed
String
wait_duration_ms
How long the agent waited for the expected element
Integer
unexpected_ui
Any popups, modals, banners not mentioned in the step
Array of strings
error_messages
Any error text visible on screen
Array of strings
screenshot_filename
Filename of captured screenshot
String
notes
Free-text observations (e.g., "Button was grayed out for 2s before becoming clickable")
String
4.2 Screenshot Requirements
Type
When to Capture
Naming Convention
Before Action
Before clicking/typing (shows initial state)
step_{id}_before.png
After Action
After action completes + page settles
step_{id}_after.png
Error State
If any error/warning appears
step_{id}_error.png
Full Page
At the end of each Phase
phase_{n}_complete.png
4.3 Text Capture Requirements
For Cookbook correction purposes, the Agent MUST record:
- **CAPTURE_TEXT:**  All button labels visible in the current action area
- **CAPTURE_TEXT:**  All menu item names if a dropdown/menu was opened
- **CAPTURE_TEXT:**  All field labels in any form displayed
- **CAPTURE_TEXT:**  All tab names if tabs are visible
- **CAPTURE_TEXT:**  Toast/notification message text (exact wording)
- **CAPTURE_TEXT:**  Any error or warning message text (exact wording)
- **CAPTURE_TEXT:**  Page breadcrumb text (if visible)
- **CAPTURE_TEXT:**  Left sidebar navigation item names (if visible)


# 5. Test Steps


## Phase 1: Create Connector (HTTP API)


### STEP 1.1: Navigate to QuickSight Connectors
- **NAVIGATE:**  {{CONSOLE_URL}}/sn/quicksight-connectors
- **WAIT FOR:**  Page contains a section related to "Connectors"

- **CAPTURE:** 
  - actual_url: Record the final URL after page loads
  - actual_page_title: Record the page heading text
  - actual_ui_labels: Record all navigation menu items in the left sidebar
  - actual_ui_labels: Record all buttons visible on the page (e.g., "Create", "+", "Add")
  - screenshot: step_1.1_after.png (full page)

- **FALLBACK:**  If URL does not load the connectors page:
  - Look for "Connectors" in the left navigation sidebar and click it
  - Record the actual menu item text used (may be different from "Connectors")

- **OUTPUT NEEDED FOR COOKBOOK:** 
  - What is the exact URL path for the Connectors page?
  - What is the exact menu item name in the sidebar?
  - What is the page heading text?


### STEP 1.2: Initiate Connector Creation
- **ACTION:**  Click the button that initiates creating a new connector
- **LOOK FOR:**  "Create connector" / "Add connector" / "New" / "+" button

- **CAPTURE (BEFORE):** 
  - screenshot: step_1.2_before.png
  - actual_ui_labels: Record the EXACT text on the create button

- **ACTION:**  Click the create button
- **WAIT FOR:**  A new page, modal, or form appears

- **CAPTURE (AFTER):** 
  - screenshot: step_1.2_after.png
  - actual_url: Record URL if page changed
  - actual_page_title: Record heading of the new page/modal
  - actual_ui_labels: Record all connector type options visible
    (e.g., "HTTP API", "REST API", "OAuth 2.0", "Custom", etc.)

- **ACTION:**  Select the connector type for HTTP/REST API
- **LOOK FOR:**  "HTTP" / "REST API" / "Custom API" / "HTTP API"
- **RECORD:**  The exact text of the option selected

- **WAIT FOR:**  Configuration form is displayed

- **CAPTURE:** 
  - screenshot: step_1.2_form.png
  - actual_ui_labels: Record ALL field labels visible in the form

- **OUTPUT NEEDED FOR COOKBOOK:** 
  - What is the exact button text to create a connector?
  - What are the available connector types listed?
  - What is the exact name of the HTTP connector type option?
  - What fields appear in the initial form?


### STEP 1.3: Configure Connector Basic Settings
- **CAPTURE (BEFORE):** 
  - screenshot: step_1.3_before.png
  - actual_ui_labels: Record all form field labels exactly as shown
  - actual_ui_labels: Record all dropdown options for Authentication type

- **ACTION:**  In the field labeled for connector name, type: {{CONNECTOR_NAME}}
- **RECORD:**  The actual field label (e.g., "Name", "Connector name", "Display name")

- **ACTION:**  In the description field, type: POC test connector for Sales API
- **RECORD:**  The actual field label (e.g., "Description", "Details")

- **ACTION:**  In the URL/endpoint field, type: {{API_BASE_URL}}
- **RECORD:**  The actual field label (e.g., "Base URL", "API endpoint", "Server URL", "Host")

- **ACTION:**  For Authentication, select no-auth option
- **RECORD:**  The actual dropdown label (e.g., "Authentication", "Auth type", "Security")
- **RECORD:**  The actual option text selected (e.g., "None", "No authentication", "No auth")

- **CAPTURE (AFTER):** 
  - screenshot: step_1.3_after.png

- **VERIFY:** 
  - All fields are populated (no red validation errors)
  - Record any validation messages shown

- **OUTPUT NEEDED FOR COOKBOOK:** 
  - What is the exact field label for the API URL?
  - What is the exact label for the auth dropdown?
  - What is the exact text of the "no auth" option?
  - Are there any other required fields not covered above?


### STEP 1.4: Define a Read Action
- **CAPTURE (BEFORE):** 
  - screenshot: step_1.4_before.png
  - actual_ui_labels: Record section headers visible (look for "Actions", "Operations", "Endpoints")

- **ACTION:**  Look for a way to add an action/operation/endpoint
- **LOOK FOR:**  "Add action" / "Create action" / "New action" / "+" / "Add operation"
- **RECORD:**  The exact button/link text

- **ACTION:**  Click the add action button
- **WAIT FOR:**  Action configuration form appears

- **CAPTURE:** 
  - screenshot: step_1.4_form.png
  - actual_ui_labels: Record ALL field labels in the action form

- **ACTION:**  In the action name field, type: GetProducts
- **RECORD:**  Exact field label (e.g., "Action name", "Name", "Operation name")

- **ACTION:**  In the description field, type: Retrieve list of products
- **RECORD:**  Exact field label

- **ACTION:**  For HTTP method, select: GET
- **RECORD:**  Exact dropdown label (e.g., "Method", "HTTP Method", "Request method")
- **RECORD:**  All available method options (GET, POST, PUT, DELETE, PATCH, etc.)

- **ACTION:**  In the path field, type: /products
- **RECORD:**  Exact field label (e.g., "Path", "Endpoint path", "Resource path", "URL path")

- **ACTION:**  For operation type, select: Read
- **RECORD:**  Exact dropdown label (e.g., "Operation type", "Action type", "Type")
- **RECORD:**  All available type options (e.g., "Read", "Write", "Read/Write")

- **CAPTURE (AFTER):** 
  - screenshot: step_1.4_after.png

- **VERIFY:** 
  - Action appears in a list or is confirmed added
  - Record exact confirmation text or UI state

- **OUTPUT NEEDED FOR COOKBOOK:** 
  - What is the section name where actions are defined?
  - What are all the fields required to define an action?
  - What are the operation type options?
  - Is there a separate "Save action" button or does it auto-save?


### STEP 1.5: Save and Test Connector
- **CAPTURE (BEFORE):** 
  - screenshot: step_1.5_before.png
  - actual_ui_labels: Record all buttons in the toolbar/footer (Save, Cancel, Test, etc.)

- **ACTION:**  Click the save/create button for the connector
- **LOOK FOR:**  "Save" / "Create" / "Create connector" / "Done"
- **RECORD:**  Exact button text

- **WAIT FOR:**  Success confirmation
- **RECORD:**  Exact toast/notification/banner message text
- **RECORD:**  Time waited for confirmation (ms)

- **CAPTURE:** 
  - screenshot: step_1.5_saved.png
  - actual_url: Record URL of connector detail page
  - actual_ui_labels: Record connector status text (e.g., "Active", "Connected", "Ready")

- **ACTION:**  Look for test functionality
- **LOOK FOR:**  "Test" / "Test connection" / "Try it" / "Run" / "Execute"
- **RECORD:**  Exact button text and its location on page

- **ACTION:**  Click test button
- **WAIT FOR:**  Test result appears (may take several seconds)
- **RECORD:**  Wait duration

- **CAPTURE (AFTER):** 
  - screenshot: step_1.5_test_result.png
  - actual_ui_labels: Record test result status text
  - actual_ui_labels: Record HTTP status code if shown
  - actual_ui_labels: Record response preview format (JSON tree, raw text, table, etc.)

- **VERIFY:** 
  - Test shows success (HTTP 200 or equivalent indicator)
  - Response contains valid data
  - Record any response metadata shown (response time, size, etc.)

- **OUTPUT NEEDED FOR COOKBOOK:** 
  - What is the exact save button text?
  - What is the exact success notification wording?
  - What is the connector status label after creation?
  - What is the test button text?
  - How is the test result displayed (format, location)?
  - What does a successful test look like vs. a failed test?


## Phase 2: Build App (Quick Apps)


### STEP 2.1: Navigate to Quick Apps
- **NAVIGATE:**  {{CONSOLE_URL}}/sn/apps
- **WAIT FOR:**  Page related to Apps/Applications loads

- **CAPTURE:** 
  - actual_url: Record the final URL
  - actual_page_title: Record page heading
  - actual_ui_labels: Record left sidebar menu items
  - actual_ui_labels: Record all buttons on the page
  - actual_ui_labels: Record any tabs or filters visible
  - screenshot: step_2.1_after.png

- **FALLBACK:**  If URL does not work:
  - Click "Apps" or "Applications" in left sidebar
  - Record actual menu item text

- **OUTPUT NEEDED FOR COOKBOOK:** 
  - What is the exact URL path for the Apps page?
  - What is the sidebar menu item text?
  - What is the page heading?
  - What does the empty state look like (if no apps exist)?


### STEP 2.2: Create New App
- **ACTION:**  Click the button to create a new app
- **LOOK FOR:**  "Create app" / "New app" / "Create" / "+" / "Build app"
- **RECORD:**  Exact button text

- **WAIT FOR:**  Creation dialog or new page

- **CAPTURE:** 
  - screenshot: step_2.2_dialog.png
  - actual_ui_labels: Record all fields in the creation dialog

- **ACTION:**  In the app name field, type: {{APP_NAME}}
- **RECORD:**  Exact field label

- **ACTION:**  If description field exists, type: End-to-end POC test - Sales Dashboard with connector integration
- **RECORD:**  Whether description field exists, and its label

- **ACTION:**  Click create/continue button
- **LOOK FOR:**  "Create" / "Continue" / "Next" / "Build" / "Start building"
- **RECORD:**  Exact button text

- **WAIT FOR:**  App editor loads
- **RECORD:**  Wait duration (this may be slow, 5-15 seconds)

- **CAPTURE:** 
  - screenshot: step_2.2_editor.png
  - actual_url: Record editor URL (important — contains app ID?)
  - actual_page_title: Record editor heading
  - actual_ui_labels: Record all panels/sections visible in the editor
  - actual_ui_labels: Record toolbar buttons
  - actual_ui_labels: Record any welcome/onboarding overlay text

- **VERIFY:** 
  - Editor is functional (not loading/error state)
  - Record whether a blank canvas, template picker, or AI prompt is shown first

- **OUTPUT NEEDED FOR COOKBOOK:** 
  - What is the create button text?
  - What fields are in the creation dialog?
  - What is the initial editor state (blank? template? AI prompt?)?
  - What panels are visible in the editor (code, preview, properties, AI chat)?
  - What is the editor URL pattern?


### STEP 2.3: Use AI Prompt to Generate Base Layout
- **ACTION:**  Locate the AI assistant interface
- **LOOK FOR:**  Chat panel / input field / "AI" button / "Generate" button / floating icon
- **SEARCH LOCATIONS:**  Bottom of screen, right sidebar, top toolbar, floating button
- **RECORD:**  Exact location and appearance of the AI interface
- **RECORD:**  Any label/placeholder text in the AI input field

- **CAPTURE (BEFORE):** 
  - screenshot: step_2.3_ai_interface.png

- **ACTION:**  Click on the AI input field
- **ACTION:**  Type the following prompt:

  Create a sales dashboard app with the following layout:
  - A header with the title "Sales Dashboard"
  - A section showing product data from an API
  - A section for an embedded dashboard visual
  - A summary section that uses AI to analyze the data

- **ACTION:**  Submit the prompt
- **LOOK FOR:**  Enter key / "Send" button / "Generate" button / arrow icon
- **RECORD:**  Exact submit mechanism (key press or button, and button text if applicable)

- **WAIT FOR:**  AI generates response (may take 10-60 seconds)
- **RECORD:**  Wait duration
- **RECORD:**  Any progress indicator shown (spinner, progress bar, streaming text)

- **CAPTURE (AFTER):** 
  - screenshot: step_2.3_ai_response.png
  - actual_ui_labels: Record what the AI response looks like (code block? visual preview? both?)

- **VERIFY:** 
  - AI produced some output (code or visual)
  - App preview area shows layout changes
  - Record whether AI shows code, visual preview, or both simultaneously

- **OUTPUT NEEDED FOR COOKBOOK:** 
  - Where exactly is the AI interface located in the editor?
  - What is the placeholder text in the AI input?
  - How do you submit a prompt (Enter? Button?)?
  - How long does generation take?
  - What does the response look like (inline code? separate panel?)?
  - Does the preview auto-update or need manual refresh?


### STEP 2.4: Add Connector Integration (Display API Data)
- **ACTION:**  In the AI input, type:

  Add a component that calls the "{{CONNECTOR_NAME}}" connector's "GetProducts" action
  and displays the results in a table with columns: title, price, category, rating.

- **ACTION:**  Submit the prompt
- **WAIT FOR:**  AI generates connector integration code/component
- **RECORD:**  Wait duration

- **CAPTURE:** 
  - screenshot: step_2.4_after.png
  - actual_ui_labels: Record any consent/permission dialogs that appear
    (e.g., "Allow this app to access Sales API Connector?")
  - RECORD: If a permission/consent dialog appeared, record:
    - Dialog title
    - Dialog message text
    - Button options (e.g., "Allow" / "Deny" / "Approve")
    - What you clicked

- **VERIFY:** 
  - Code or component was generated referencing the connector
  - Record whether the app preview shows the table or an error
  - If error, record exact error message text

- **ALTERNATIVE PATH (if AI cannot integrate connector):** 
- **ACTION:**  Look for manual component insertion
- **RECORD:**  Menu path to add connector component manually
- **RECORD:**  All steps and selections required

- **OUTPUT NEEDED FOR COOKBOOK:** 
  - Does the AI know about existing connectors by name?
  - Is there a consent/permission step when adding connector integration?
  - What does the consent dialog say exactly?
  - What happens in the preview after adding connector code?


### STEP 2.5: Add Dashboard Visual Embedding
- **ACTION:**  In the AI input, type:

  Add an embedded dashboard visual from the "{{DASHBOARD_NAME}}" dashboard,
  sheet "{{SHEET_NAME}}", visual "{{VISUAL_NAME}}".
  Set the width to 800 pixels and height to 500 pixels.

- **ACTION:**  Submit the prompt
- **WAIT FOR:**  AI generates dashboard embedding code/component
- **RECORD:**  Wait duration

- **CAPTURE:** 
  - screenshot: step_2.5_after.png
  - actual_ui_labels: Record any consent/permission dialogs that appear
    (e.g., "Allow this app to access dashboard 'Sales Overview'?")
  - RECORD: If a permission dialog appeared, record full text and buttons

- **VERIFY:** 
  - Code references the dashboard/sheet/visual
  - Preview shows a placeholder or rendered visual
  - Record what the dashboard placeholder looks like in preview

- **OUTPUT NEEDED FOR COOKBOOK:** 
  - Does the AI know about existing dashboards by name?
  - Is there a consent/permission step for dashboard access?
  - What does the embedded visual look like in the editor preview?
  - Does it render live or show a placeholder?


### STEP 2.6: Add AI Inference (Data Summary)
- **ACTION:**  In the AI input, type:

  Add an AI-powered summary section that takes the product data from the connector
  and generates a brief business insight summary using Claude.
  Include a "Generate Summary" button that triggers the AI analysis.

- **ACTION:**  Submit the prompt
- **WAIT FOR:**  AI generates AI inference component
- **RECORD:**  Wait duration

- **CAPTURE:** 
  - screenshot: step_2.6_after.png
  - actual_ui_labels: Record any consent/permission dialogs for AI inference
  - RECORD: If a permission dialog appeared, record full text and buttons

- **VERIFY:** 
  - Code includes AI inference logic
  - Preview shows a button or AI interaction area

- **OUTPUT NEEDED FOR COOKBOOK:** 
  - Is there a consent/permission step for AI inference?
  - What model options are available (if shown)?


### STEP 2.7: Save App
- **ACTION:**  Save the app
- **LOOK FOR:**  "Save" button / Ctrl+S / Cmd+S / auto-save indicator
- **RECORD:**  Exact save mechanism available

- **CAPTURE (BEFORE):** 
  - RECORD: Is there an "unsaved changes" indicator? What does it look like?

- **ACTION:**  Click Save (or press keyboard shortcut)
- **WAIT FOR:**  Save confirmation
- **RECORD:**  Wait duration
- **RECORD:**  Exact confirmation text/toast message

- **CAPTURE (AFTER):** 
  - screenshot: step_2.7_after.png
  - RECORD: How do you know the save was successful? (toast? icon change? text change?)

- **OUTPUT NEEDED FOR COOKBOOK:** 
  - What is the save button location and text?
  - Does auto-save exist?
  - What is the save confirmation indicator?


## Phase 3: Preview & Verify


### STEP 3.1: Open Preview
- **ACTION:**  Open app preview
- **LOOK FOR:**  "Preview" button / "Run" / "Test" / eye icon / play icon
- **RECORD:**  Exact button text/icon and location

- **WAIT FOR:**  Preview loads
- **RECORD:**  Wait duration
- **RECORD:**  Does preview open in same tab, split view, or new tab?

- **CAPTURE:** 
  - screenshot: step_3.1_preview_full.png (full preview page)
  - actual_url: Record preview URL (if new tab)
  - RECORD: Preview layout — what sections are visible?

- **OUTPUT NEEDED FOR COOKBOOK:** 
  - What is the preview button text/icon?
  - How does preview open (split, new tab, overlay)?
  - What is the preview URL pattern?


### STEP 3.2: Verify Dashboard Visual Renders
- **VERIFY:**  In the preview, locate the dashboard visual area
- **RECORD:**  Does it show:
    a) A fully rendered chart/visual from QuickSight? → PASS
    b) A loading spinner? → WAIT and re-check after 10 seconds
    c) A placeholder box with dashboard name? → PARTIAL PASS
    d) An error message? → FAIL, record exact error text
    e) A blank/empty area? → FAIL

- **CAPTURE:** 
  - screenshot: step_3.2_dashboard_visual.png (focused on the visual area)
  - RECORD: Visual dimensions as rendered
  - RECORD: Any interactive elements on the visual (filters, tooltips, etc.)

- **OUTPUT NEEDED FOR COOKBOOK:** 
  - How long does the dashboard visual take to render?
  - What does the loading state look like?
  - Is the visual interactive in the app preview?


### STEP 3.3: Verify Connector Data Loads
- **VERIFY:**  In the preview, locate the data table area
- **RECORD:**  Does it show:
    a) A table with column headers and data rows? → PASS
    b) A loading state? → WAIT and re-check
    c) An error message? → FAIL, record exact error text
    d) Empty table with headers but no rows? → PARTIAL FAIL

- **IF PASS:** 
- **RECORD:**  Number of rows displayed
- **RECORD:**  Column headers exactly as shown
- **RECORD:**  First row of data values
- **RECORD:**  Any pagination controls visible

- **CAPTURE:** 
  - screenshot: step_3.3_data_table.png (focused on the table)

- **OUTPUT NEEDED FOR COOKBOOK:** 
  - Does the connector call happen automatically on page load?
  - Is there a loading state while data fetches?
  - What does an API error look like in the rendered app?


### STEP 3.4: Verify AI Inference Works
- **ACTION:**  Locate the AI summary section in the preview
- **ACTION:**  Click the "Generate Summary" button (or equivalent)
- **RECORD:**  Exact button text

- **WAIT FOR:**  AI response appears
- **RECORD:**  Wait duration
- **RECORD:**  Is there a loading indicator? What does it look like?

- **VERIFY:**  AI response is displayed
- **RECORD:**  Does it show:
    a) A text summary referencing the data? → PASS
    b) A loading spinner that never resolves (>60s)? → FAIL (timeout)
    c) An error message? → FAIL, record exact error text
    d) Generic/irrelevant text? → PARTIAL PASS

- **CAPTURE:** 
  - screenshot: step_3.4_ai_summary.png (focused on AI output area)
  - RECORD: First 200 characters of the AI response text

- **OUTPUT NEEDED FOR COOKBOOK:** 
  - How long does AI inference take?
  - What does the loading state look like?
  - What does an AI error look like?


## Phase 4: Publish & Share


### STEP 4.1: Navigate Back to Editor
- **ACTION:**  Close or exit preview mode
- **LOOK FOR:**  "Back to editor" / "Close preview" / "Edit" / X button / browser back
- **RECORD:**  Exact mechanism to exit preview

- **CAPTURE:** 
  - screenshot: step_4.1_editor.png
  - RECORD: Confirm editor is back in editable state

- **OUTPUT NEEDED FOR COOKBOOK:** 
  - How do you exit preview mode?


### STEP 4.2: Publish the App
- **ACTION:**  Look for publish button
- **LOOK FOR:**  "Publish" / "Deploy" / "Go live" / "Release"
- **RECORD:**  Exact button text and location (toolbar? menu? dropdown?)

- **CAPTURE (BEFORE):** 
  - screenshot: step_4.2_before.png

- **ACTION:**  Click Publish
- **WAIT FOR:**  Confirmation dialog or page

- **CAPTURE:** 
  - screenshot: step_4.2_dialog.png
  - actual_ui_labels: Record ALL text in the publish dialog
  - RECORD: Dialog title
  - RECORD: Any input fields (version notes? description?)
  - RECORD: All button options

- **ACTION:**  If version notes field exists, type: Initial release - Sales Dashboard App POC
- **ACTION:**  Click confirm button
- **LOOK FOR:**  "Publish" / "Confirm" / "Yes" / "Deploy"
- **RECORD:**  Exact button text

- **WAIT FOR:**  Publish success confirmation
- **RECORD:**  Wait duration
- **RECORD:**  Exact success message text

- **CAPTURE (AFTER):** 
  - screenshot: step_4.2_published.png
  - RECORD: App status indicator after publishing
  - RECORD: Any links shown (e.g., "View published app", "Copy link")

- **OUTPUT NEEDED FOR COOKBOOK:** 
  - What is the publish button text?
  - What does the publish confirmation dialog contain?
  - What fields are in the dialog (version notes? etc.)?
  - What is the exact success message?
  - What links/options appear after successful publish?


### STEP 4.3: Verify Published App
- **ACTION:**  Open the published app
- **LOOK FOR:**  "View published app" / "Open" / app URL link
- **RECORD:**  How to access the published app (link in success message? navigate to app list?)

- **WAIT FOR:**  Published app loads fully
- **RECORD:**  Wait duration

- **CAPTURE:** 
  - screenshot: step_4.3_published_app.png (full page)
  - actual_url: Record the published app URL pattern

- **VERIFY:** 
  ☐ App header/title is visible → RECORD exact header text
  ☐ Data table loads with data → RECORD row count
  ☐ Dashboard visual renders → RECORD visual state
  ☐ AI section is present → RECORD whether button is visible

- **OUTPUT NEEDED FOR COOKBOOK:** 
  - What is the published app URL pattern?
  - Does the published app look identical to preview?
  - Any differences between preview and published version?


### STEP 4.4: Share with Pilot User
- **ACTION:**  Navigate to sharing/permissions
- **LOOK FOR:**  "Share" / "Manage access" / "Permissions" / "Users" / people icon
- **SEARCH LOCATIONS:**  App detail page, editor toolbar, app list actions menu
- **RECORD:**  Exact button/menu text and location

- **WAIT FOR:**  Sharing interface appears

- **CAPTURE:** 
  - screenshot: step_4.4_share_dialog.png
  - actual_ui_labels: Record all elements in the sharing interface
  - RECORD: Interface type (dialog? page? panel?)

- **ACTION:**  In the user search field, type: {{SHARE_USER_EMAIL}}
- **RECORD:**  Exact field label/placeholder text
- **RECORD:**  Does it search as you type (autocomplete) or require submit?

- **WAIT FOR:**  User appears in results
- **RECORD:**  How users are displayed (email, name, both?)

- **ACTION:**  Select the user
- **ACTION:**  Set permission to Viewer
- **RECORD:**  Available permission levels (e.g., "Viewer", "Editor", "Admin", "Can view", "Can edit")
- **RECORD:**  Exact text of the selected permission

- **ACTION:**  Confirm sharing
- **LOOK FOR:**  "Share" / "Save" / "Add" / "Confirm" / "Done"
- **RECORD:**  Exact button text

- **WAIT FOR:**  Share confirmation
- **RECORD:**  Exact confirmation message text

- **CAPTURE (AFTER):** 
  - screenshot: step_4.4_shared.png
  - RECORD: How shared users are displayed in the access list

- **OUTPUT NEEDED FOR COOKBOOK:** 
  - Where is the share button located?
  - What does the sharing interface look like (dialog, page, panel)?
  - What are the available permission levels?
  - How is the user search performed?
  - What is the confirmation message?


# 6. Post-Test Cleanup (Optional)

### STEP C.1: Delete the test app
- **ACTION:**  Navigate to app list → find {{APP_NAME}} → Delete
- **RECORD:**  How to delete an app (menu path, confirmation dialog)


### STEP C.2: Delete the test connector
- **ACTION:**  Navigate to connector list → find {{CONNECTOR_NAME}} → Delete
- **RECORD:**  How to delete a connector (menu path, confirmation dialog)


# 7. Final Report Format
After completing all steps, produce the following structured report:
{
  "test_execution": {
    "test_case_id": "E2E-SALES-DASHBOARD-APP-001",
    "test_version": "2.0",
    "execution_timestamp": "{{ISO 8601 timestamp}}",
    "agent_type": "AWS Bedrock Harness AgentCore Browser UI",
    "region": "{{QUICKSIGHT_REGION}}",
    "account_id": "{{AWS_ACCOUNT_ID}}",
    "overall_status": "PASS | FAIL | PARTIAL",
    "total_duration_seconds": 0,
    "total_steps": 20,
    "passed_steps": 0,
    "failed_steps": 0,
    "skipped_steps": 0
  },

  "cookbook_corrections": [
    {
      "step_id": "1.2",
      "cookbook_says": "Click 'Create connector' button",
      "actual_ui": "Button text is 'Add new connector'",
      "correction_needed": true,
      "suggested_correction": "Change 'Create connector' to 'Add new connector'"
    }
  ],

  "ui_discovery": {
    "connector_page": {
      "url_path": "/sn/quicksight-connectors",
      "sidebar_menu_text": "Connectors",
      "page_heading": "...",
      "create_button_text": "...",
      "connector_types_available": ["HTTP API", "..."],
      "form_fields": {
        "name_label": "...",
        "url_label": "...",
        "auth_label": "...",
        "auth_options": ["None", "..."]
      },
      "action_form_fields": {
        "name_label": "...",
        "method_label": "...",
        "method_options": ["GET", "POST", "..."],
        "path_label": "...",
        "type_label": "...",
        "type_options": ["Read", "Write", "..."]
      },
      "test_button_text": "...",
      "save_button_text": "...",
      "success_message": "..."
    },
    "apps_page": {
      "url_path": "/sn/apps",
      "sidebar_menu_text": "...",
      "page_heading": "...",
      "create_button_text": "...",
      "creation_dialog_fields": ["..."],
      "editor_layout": {
        "panels": ["..."],
        "ai_interface_location": "...",
        "ai_input_placeholder": "...",
        "ai_submit_mechanism": "...",
        "save_button_text": "...",
        "preview_button_text": "...",
        "publish_button_text": "..."
      }
    },
    "sharing_interface": {
      "access_point": "...",
      "search_field_placeholder": "...",
      "permission_levels": ["..."],
      "confirm_button_text": "...",
      "success_message": "..."
    },
    "consent_dialogs": {
      "connector_consent": {
        "appears": true,
        "title": "...",
        "message": "...",
        "buttons": ["Allow", "Deny"]
      },
      "dashboard_consent": {
        "appears": true,
        "title": "...",
        "message": "...",
        "buttons": ["..."]
      },
      "ai_inference_consent": {
        "appears": true,
        "title": "...",
        "message": "...",
        "buttons": ["..."]
      }
    }
  },

  "steps": [
    {
      "step_id": "1.1",
      "step_name": "Navigate to QuickSight Connectors",
      "status": "PASS",
      "duration_ms": 3200,
      "actual_url": "https://us-east-1.quicksight.aws.amazon.com/sn/quicksight-connectors",
      "actual_page_title": "Connectors",
      "actual_ui_labels": ["Create connector", "Filter", "Search"],
      "action_taken": "Navigated directly via URL",
      "unexpected_ui": [],
      "error_messages": [],
      "screenshots": ["step_1.1_after.png"],
      "notes": ""
    }
  ],

  "screenshots_manifest": [
    {
      "filename": "step_1.1_after.png",
      "step_id": "1.1",
      "description": "Connectors page after navigation",
      "timestamp": "..."
    }
  ],

  "errors_encountered": [],

  "performance_metrics": {
    "phase_1_duration_seconds": 0,
    "phase_2_duration_seconds": 0,
    "phase_3_duration_seconds": 0,
    "phase_4_duration_seconds": 0,
    "slowest_step": { "step_id": "...", "duration_ms": 0 },
    "ai_generation_times_ms": [0, 0, 0]
  }
}


# 8. How to Use Results to Update Cookbook
After receiving the Agent's report:
Step 1: Review cookbook_corrections array
Each entry tells you exactly what the Cookbook currently says vs. what the actual UI shows.
Step 2: Review ui_discovery object
This is a complete map of the real QuickSight Console UI — button labels, field names, menu items, URL paths.
Step 3: Update these Cookbook sections:
Report Section
Updates Which Cookbook Component
connector_page
ConnectorsSection.tsx
apps_page.editor_layout
AppsSection.tsx
apps_page.ai_interface_location
AppsSection.tsx (AI prompt guidance)
sharing_interface
SuccessSection.tsx (publish & share steps)
consent_dialogs
All sections mentioning permissions
performance_metrics
TestingSection.tsx (expected duration estimates)
Step 4: Re-run test after corrections
After updating the Cookbook, generate a new test plan and re-run to confirm corrections are accurate.

Generated for AWS Bedrock Harness AgentCore Browser UI Agent Test Case ID: E2E-SALES-DASHBOARD-APP-001 Version: 2.0 Purpose: UI Discovery + Cookbook Verification

以上就是完整的 V2 版本。您可以直接全選複製。
關鍵改進點：
✅ 每步都有 OUTPUT NEEDED FOR COOKBOOK — 明確告訴 Agent 要抓什麼回來給我們
✅ CAPTURE_TEXT 要求 — Agent 必須記錄實際 UI 文字
✅ 結構化 JSON 報告 — 包含 cookbook_corrections 和 ui_discovery
✅ 最後有「如何用結果更新 Cookbook」的對應表
測試完後把 JSON 報告貼回來給我，我就能直接修正 Cookbook！🚀




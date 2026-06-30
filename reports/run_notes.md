# Run Notes - E2E Sales Dashboard App
- Session: quickpoc-e2e-run
- Auth carried over after human SSO. Home title: "Quick - Home"
- Sidebar: Home, Favorites, Chat agents, Spaces, Flows, Apps, Preview, Research, Automations | CONNECT APPS AND DATA: Knowledge, Connectors, Extensions | QUICK SIGHT: Analyses, Dashboards, Scenarios, Stories, Topics, Datasets, My folders, Shared folders

## Phase 1 - REST API Connector
- 1.1 Connectors: direct URL /sn/quicksight-connectors => "Not Found". Real path: /sn/account/{acct}/start/integrations?tab=action via sidebar "Connectors". PASS(fallback)
- Connectors page: heading "Connectors", subtitle "Connect Quick to other applications". Tabs: "Available", "Create for your team". Catalog includes "REST API connection".
- 1.2 No generic "Create connector" button; pick connector type card "REST API connection" -> opens dialog "REST API connection details". Wizard steps: Connect / Review / Publish. PASS
- 1.3 Fields: Name(Enter name), +Add Description, Connection type(Public network), OAuth Configuration(Custom OAuth app|Service-to-Service OAuth|None), Base URL(https://mydomain.com). Selected None for no-auth. Filled Name="Sales API Connector", Base URL=https://dummyjson.com, desc. Btns Cancel/Next. PASS
- 1.4 Next -> "Review actions for REST API connection". Auto-listed fixed actions: Delete/Get/Patch/Post/Put (cols Action/Type/Description). NOT customizable; no add-action, no name/path/operation-type per action. Cookbook's manual "GetProducts GET /products read action" does NOT exist. PARTIAL.
- 1.5 Next -> "Publish connection for REST API connection". Access: "Everyone in your organization"/"Specific groups"/Add field. Btn Publish. Published OK. Connector "Sales API Connector" shows under "Connected" with desc "Connect to any REST API endpoint with standard HTTP methods." PASS.

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

---

## AgentCore Browser pitfalls (learned from real runs — each one cost debugging time)

These are failure modes observed while driving the real Quick console over CDP/Playwright against an AgentCore
built-in browser session. Every one of them produced a **silently wrong result**, not an error, which is what
makes them dangerous: the run appears to succeed and the report records a finding that isn't true.

### 1. Direct `goto` does not navigate this SPA — click the nav element

Amazon Quick is a single-page app. Navigating directly to an admin path (`/admin/custom-permissions`) or a
hash URL (`/sn/admin?#/security`) frequently loads the **settings landing page** while the address bar shows
the URL you asked for. In one run this produced **eight admin pages with byte-identical text** — the landing
page read eight times, each recorded as a separate PASS.

**Rule: never trust the URL as proof of navigation.** After any navigation, assert the page *content* changed:

```python
before = "|".join(lines_of(page)[:30])
click_nav(page, "Custom permissions")
after = "|".join(lines_of(page)[:30])
if after == before:
    record(step, "PARTIAL", "clicked but content did not change — cannot attest")
```

Record `PARTIAL`, not `PASS`, when the signature is unchanged. A landing page read N times is not N findings.

### 2. `element.click()` / `element.hover()` time out on this UI — use raw mouse events

Playwright waits indefinitely for an element to be judged "stable". Several Quick controls (notably the region
submenu, which opens on hover) never satisfy that check. Dispatch raw mouse events at JS-computed coordinates
instead, which bypasses the stability wait:

```python
def click_text(pg, t, timeout=8000):
    box = pg.evaluate("""(t) => {
        const els=[...document.querySelectorAll('*')].filter(e =>
            e.children.length===0 && e.textContent.trim()===t);
        if(!els.length) return null;
        const r=els[0].getBoundingClientRect();
        if(r.width===0||r.height===0) return null;   // guard invisible matches
        return {x:r.x+r.width/2, y:r.y+r.height/2};
    }""", t)
    if not box: return False
    pg.mouse.click(box["x"], box["y"]); pg.wait_for_timeout(timeout)
    return True
```

### 3. Compute coordinates only *after* `scrollIntoView`

`getBoundingClientRect()` is viewport-relative. For an element below the fold it returns a y beyond the viewport
and the click lands on nothing — **silently**. One `Cancel` click was computed at `y=3035` and simply did not
fire; the form stayed open and the run continued as if it had closed. Always scroll first, then measure:

```python
box = pg.evaluate("""() => {const a=[...document.querySelectorAll('a')]
    .find(e=>e.textContent.trim()==='Custom permissions');
    if(!a) return null; a.scrollIntoView({block:'center'});
    const r=a.getBoundingClientRect();
    return {x:r.x+r.width/2, y:r.y+r.height/2};}""")
```

Better still, verify the click's effect (did the form close?) rather than assuming the click landed.

### 4. Enumerate by `href`, not by link text — and absence by text is not absence

Searching the admin nav by visible text misses items whose label differs from what you expect, and gives you no
way to distinguish "not present" from "not found". Enumerate every anchor's `href` and match on the path:

```python
navs = pg.evaluate("""() => [...document.querySelectorAll('a[href]')]
    .map(a=>({t:a.textContent.trim(), h:a.getAttribute('href')})).filter(x=>x.t)""")
```

This turned "the feature is disabled in this account" into the correct finding: the console exposed **34
anchors, none matching the feature** — because those controls live on a *different admin surface entirely*.

### 5. One CDP connection per AgentCore session

A second `connect_over_cdp` to the same session returns **HTTP 429 — "Concurrent connections to the same
session are not supported."** If a driver process holds the connection, stop it with `SIGKILL`, not `SIGTERM`:
a graceful shutdown runs `finally: client.stop()` and destroys the authenticated session you need to keep.

```bash
kill -9 <driver_pid>    # NOT kill/SIGTERM — that would stop the browser session
```

Then confirm the session is still `READY` before attaching.

### 6. Never `close()` or re-initialise after the human login

The most expensive failure mode: the agent sees a stale pre-login page handle, calls `close()` + re-init, and
destroys the human's authenticated session — the run cannot recover without another human login. Hold **one**
CDP connection open across the login and re-read the page from the context:

```python
try:
    u = page.url
except Exception:
    page = ctx.pages[-1]   # handle went stale across the login redirect
    u = page.url
```

### 7. Grids may have no `<tr>` — check `role=` attributes

Quick's list views render as ARIA grids, not HTML tables. `document.querySelectorAll('tr')` returns empty and
"no rows" looks like "no data". Read `[role=row]` / `[role=gridcell]`, and read the pagination text
(`0-0 of 0`) as the authoritative empty-state signal.

### 8. Read-only runs still mint server-side objects

Opening a creation flow purely to *read* its form can cause the service to create a draft object — e.g. opening
`New research` returns `/research/view/<uuid>/prompt`. That is a server-side write, however empty. If the run
claims to be read-only, say so precisely: state what was minted, confirm nothing was entered, and **verify
afterwards** whether it persisted (the list showed `No rows` / `0-0 of 0`). Do not claim "read-only" without
that check.

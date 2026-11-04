# LLM MemoryGrid — Dashboard Design Specification

**Status:** Task A deliverable; implementation is intentionally out of scope.

## 1. Product intent

LLM MemoryGrid is a developer research workspace for submitting a prompt and inspecting the result of the current MemoryGrid API. The visual tone is quiet, technical, and deliberate: a graphite workspace with one restrained purple interaction color and muted green for confirmed success. It must never imply that telemetry or model streaming exists when the API does not provide it.

The dashboard has one primary job: make the prompt-to-result path legible. Secondary information must support that job, not compete with it.

## 2. Audited architecture

### Active render path

```
main.jsx
  ├─ index.css (global reset)
  └─ App.jsx
       └─ App.css
       ├─ Topology (local function)
       ├─ Journey (local function)
       └─ Response (local function)
```

`main.jsx` mounts only `App`; it does not mount `ThemeProvider`, the exported MUI theme, or any file in `src/components/`. `App.jsx` is therefore the live dashboard. It owns prompt editing, API calls, local response/history state, status checking, the topology presentation, and request-state presentation.

### Available integration

`vite.config.js` proxies `/api` to `http://localhost:8000`; `VITE_API_URL` may override the base URL. The active app additionally requests `/health`, which is direct to the configured base URL and works in local development because the empty base URL is same-origin.

The verified API contract is:

| Endpoint | Verified frontend-relevant response | Design use |
| --- | --- | --- |
| `GET /health` | `{ status: "ok" }` | Backend reachable indicator only. |
| `POST /api/prompt` | `request_id`, `status`, `prompt`, `response`, `cache`, optional `error` | Result panel, request history, cache outcome. |
| `GET /api/grid/stats` | `nodes[]` with `node_id`, `entries`, `capacity`, `alive`; `cache_hits`, `cache_misses`, `hit_rate` | Node capacity/detail and, if fetched/stored, cache summary. |
| `GET /api/grid/config` | node count, cache size per node, default TTL | Optional static configuration summary. |
| `POST /api/grid/clear` | clear result | Not required in Task B unless product scope explicitly adds a destructive cache-control flow. |

### Present but unused/legacy components

`Header.jsx`, `PromptInputArea.jsx`, `ResponsePanel.jsx`, `StatusAndLoading.jsx`, and `RequestHistory.jsx` are not imported by the active render path. They describe a separate, dark MUI concept and must not be assumed functional in production. `theme.js` is also unused because no `ThemeProvider` is mounted. These components are useful reference material only until Task B deliberately adopts, rewires, or removes them under a separate implementation decision.

## 3. Existing behavior to preserve

- Trim prompt text and prevent blank or duplicate in-flight submissions.
- Submit `POST /api/prompt` with `{ prompt }` and retain the backend request ID and returned prompt.
- Support Ctrl/Cmd+Enter submission.
- Keep client-measured round-trip latency visibly labeled as client-measured latency.
- Retain resilient non-JSON/HTTP/network error handling and a dismissible error state.
- Show the backend response text, status, and request ID; retain copy-request-ID functionality.
- Refresh the backend health/grid statistics after a successful submission.
- Preserve accessible labels, keyboard-operable controls, focus indication, responsive behavior, and the existing `prefers-reduced-motion` treatment.

## 4. Metric and visualization source audit

Definitions: **LIVE** is delivered by the backend and displayed from it. **STATIC** is a fixed UI value/copy. **SIMULATED** is demonstrative data rather than backend state. **UNKNOWN** has no verified source.

| Visible item in active dashboard | Classification | Verified source / concern | Task B direction |
| --- | --- | --- | --- |
| “Backend connected” / “Backend unavailable” | LIVE | `GET /health`; only means request health succeeded/failed. | Keep, label as API connection. Do not imply worker health. |
| `localhost:8000` caption | STATIC | Hard-coded display text, not derived from `VITE_API_URL`. | Replace with neutral “API connection” or derive safely. |
| Session request count in header tooltip | LIVE (client session) | `requestHistory.length`, populated after successful requests only. | Keep only if labeled “this session”. |
| Prompt character count | LIVE (client input) | `prompt.length`. | Keep. |
| Prompt word count | LIVE (client input) | Trimmed whitespace split. | Keep. |
| “tokens” / token estimate | STATIC-derived estimate | `ceil(characters / 4)`; not model tokenization or API data. | Label “estimated tokens” with explanatory tooltip, or omit. |
| Examples / quick prompts | STATIC | Fixed strings. | Keep as examples, never as recent queries or recommendations from backend. |
| Request journey steps | LIVE (client request state), except wording | Derived from `idle/loading/error/accepted/completed`; no server progress events. | Reduce to “Validating”, “Sending”, “Response received/error”. Do not show server-side processing progress. |
| Response timestamp | LIVE (client local) | Browser `toLocaleTimeString()` after response. | Label “received at” or remove. It is not backend time. |
| Latency | LIVE (client-measured) | `performance.now()` around the fetch. | Keep as “round-trip time”; it is not TTFT, inference time, or server latency. |
| Response content | LIVE | `response` from successful API response. Current backend uses a stub inference response. | Display under “Response”; only call it generated output when backend contract guarantees generation. |
| Request ID | LIVE | `request_id` from API. | Keep and make copyable. |
| Response status | LIVE | `status` from API. | Keep. |
| Cache hit/miss | **UNKNOWN in current UI** | API returns `cache`, but active UI does not display it. | May be added only from this field, labelled “cache result”. |
| Cache hits/misses and hit rate | **UNKNOWN in current UI** | API exposes them but active app discards them when it stores only `nodes`. | Do not display until Task B stores and renders the returned values. |
| Node entries/capacity/alive in selected popover | LIVE when a matching stat exists | `GET /api/grid/stats` node data. | Keep as a data table/list, with clear API origin. |
| Node count and positions | SIMULATED | Six hard-coded `TOPOLOGY_NODES`; may disagree with configured grid. | Remove the spatial diagram or label it “Illustrative topology”. Prefer a live node list. |
| Node state: active/idle/unavailable | SIMULATED | Hard-coded states; API only offers `alive`. | Do not show. At most show backend `alive` as “available”. |
| Node type: memory/storage | SIMULATED | Hard-coded types; API provides no node role. | Do not show. |
| “Memory worker” role and “Route: Not exposed” | STATIC | Fixed labels, not API capabilities. | Remove. |
| Animated connection lines | SIMULATED | Decorative only. | Remove with the simulated topology; never suggest traffic. |
| Feature copy: multiple nodes, TTL/LRU | STATIC | Product description; implementation supports these concepts but the UI does not expose values. | Retain only in help/about context, not as dashboard telemetry. |
| Throughput / tokens per second | UNKNOWN | No API field or client calculation supports it. | Do not add. |
| TTFT | UNKNOWN | No streaming/timestamp contract. | Do not add. |
| Memory utilization percentage | UNKNOWN | Entries/capacity permit a client-side per-node ratio, but it is not currently shown and does not measure bytes/RAM. | If added, call it “cache entry capacity”, calculate from live fields, and disclose the formula. |
| Worker activity/processing state | UNKNOWN | No worker status/progress endpoint or streaming. | Do not add. |

## 5. Risks and decisions for Task B

1. The live app and legacy MUI files have conflicting design systems (light editorial vs. dark MUI). Choose one implementation path in Task B; this specification chooses the dark workspace direction and does not prescribe reuse of inactive files.
2. The active navigation contains `#system`, which has no matching section. Topology/history labels are also not backed by a durable section/history component. Correct only during the dashboard redesign.
3. Current topology maps `node_id + 1` to display IDs. That mapping is a frontend convention, not an API guarantee.
4. Current history is populated only after successful requests; it omits failures and disappears on reload. Decide whether session-only history is enough before implementing persistence.
5. Current response wording can call any `response` “Response received.” The verified backend currently returns stub inference output; the product team must specify whether “generated text” is truthful in each deployment.
6. `/api/grid/stats` has the needed cache aggregate fields, but the active state intentionally drops them. Task B may store them; no backend change is needed.

## 6. Design system

### Foundations

| Token | Value | Use |
| --- | --- | --- |
| `canvas` | `#0B0D12` | Page background. |
| `surface-1` | `#12151D` | Primary panels. |
| `surface-2` | `#181C26` | Inputs, nested regions, row hover. |
| `surface-raised` | `#1D2230` | Menus, popovers. |
| `border-subtle` | `rgba(226,232,240,.10)` | Resting boundaries. |
| `text-primary` | `#F3F5F8` | Key content. |
| `text-secondary` | `#A8B0C0` | Supporting labels. |
| `text-muted` | `#737D90` | De-emphasized metadata. |
| `purple` | `#9B8CFF` | Primary action/focus/selection. |
| `purple-muted` | `#24213C` | Selected/active surface. |
| `green` | `#77C89A` | Confirmed completed/cache-hit states only. |
| `amber` | `#E6B36A` | Sending/attention—not “processing” telemetry. |
| `red` | `#ED7E87` | Error/destructive states. |

Use a very low-contrast graphite gradient and a 1px noise/grid texture only if it remains invisible at normal viewing distance. No neon gradients, glass-heavy stacking, floating metric tiles, or decorative gauges.

### Typography and spacing

- UI sans: `Inter` or system sans. Technical identifiers/measurements: `ui-monospace, SFMono-Regular, Consolas, monospace`.
- Display: 28/34px, 650 weight, -0.02em; section title: 16/22px, 650; body: 14/22px; labels: 12/16px, 600, 0.04em uppercase where helpful.
- Use a 4px baseline grid: 4, 8, 12, 16, 24, 32, 40, 56. Panel padding is 24px desktop / 16px mobile. Global content width is 1240px.
- Radius: 12px panels, 8px controls, 999px compact status pills. One ambient shadow maximum per raised surface: `0 12px 32px rgba(0,0,0,.22)`.

### Controls and accessibility

- Visible keyboard focus: 2px `purple` ring with 2px offset, never color-only state.
- Touch targets: 44px minimum for icon-only actions; 36px minimum for compact text controls.
- Meet WCAG AA contrast; body content must not use `text-muted` below 14px on `surface-1`.
- Use buttons for actions and links for navigation. Status text uses `aria-live="polite"`; errors use an assertive alert only after submission fails.

## 7. Component hierarchy and desktop wireframe

```
App shell
├─ Header: brand | API connection indicator | session request count
├─ Workspace (max 1240px)
│  ├─ Context row: “Inference workspace” + concise API scope/help
│  ├─ PromptComposer (primary, full width)
│  │  ├─ label + Ctrl/Cmd+Enter hint
│  │  ├─ textarea
│  │  ├─ input counts (characters, words, estimated tokens)
│  │  └─ example prompt chips + submit action
│  ├─ RequestStatus (shown only while relevant)
│  └─ Results grid (8 / 4 columns)
│     ├─ ResultPanel (8): result/acknowledgment, request ID, round-trip time,
│     │  cache result, copy actions
│     └─ GridSummary (4): API-backed node list and cache summary when available
└─ SessionHistory (full width, below results; session-only label)
```

At >= 1024px, ResultPanel occupies two-thirds and GridSummary one-third. Do not use an abstract network map as the information-bearing layout. If an illustrative topology is retained for education, put it in an explicitly marked collapsed “How the grid is modeled” explainer, not on the live dashboard surface.

## 8. Mobile wireframe and responsive rules

```
Header: brand + compact API state
Workspace
├─ PromptComposer
├─ RequestStatus (conditional)
├─ ResultPanel
├─ GridSummary
└─ SessionHistory
```

- Under 768px, use one column, 16px gutters, 16px panel padding, and remove nonessential header navigation.
- Input metadata wraps into two lines; submit becomes a full-width labeled button rather than an icon-only circle.
- Result metadata becomes a vertical definition list; request IDs truncate visually but remain copyable and expose the complete value through accessible name/tooltip.
- Node rows remain lists, never a pinch/zoom topology. History is a capped list with an explicit “show more” control if needed.
- At 768–1023px, use one column or a 7/5 split only when both panels remain at least 320px wide.

## 9. Required state designs

| State | Presentation | Allowed claims / behavior |
| --- | --- | --- |
| Empty dashboard | Composer is prominent; ResultPanel explains that no response has been received; grid summary says whether stats are available. | No fake result, metric, or activity. |
| Prompt editing | Focused textarea, live client counts, enabled submit only for nonblank text. | “Estimated tokens” is explicitly estimated. |
| Loading / submitting | Disable duplicate submit; compact amber status: “Sending request to API…” with indeterminate progress. | Do not say a worker is processing or show a percent complete. |
| Request accepted | Only use if API returns a non-final accepted status in a future verified contract. Display request ID and “accepted by API”. | Current verified endpoint returns completed on success, so this is not normally reached. |
| Request processing | Reserved state only for a future API/streaming contract with actual progress. | With current API, do not render a processing state after fetch resolves. |
| Completed response | Green completion badge, backend response text, request ID, cache result, client round-trip time, received-at local time. | Call text “response”; call it “generated text” only when contract/deployment guarantees that. |
| Error / retry | Red alert with plain-language error, “Retry last prompt” and dismiss controls; preserve the prompt. | Error text can identify unreachable API, HTTP failure, or invalid response. |
| Request history | “This session” label; newest first; prompt excerpt, actual request ID, actual status, round-trip time, and cache result when stored. | No cross-session implication and no fabricated rows. |

## 10. Motion and interaction

- Use 140–180ms opacity/color/transform transitions for focus, hover, copied confirmation, and panel entry. Movement must be 2px or less.
- The submit button may transition to a small inline spinner while the fetch is pending. Indeterminate progress must be visually and textually identified as waiting for the API.
- Copy confirms with a concise “Copied” label/toast. Example prompts fill the editor and place focus in it without submission.
- In `prefers-reduced-motion: reduce`, eliminate spinners/animated gradients/route-line movement; retain immediate state changes and non-motion feedback.

## 11. Task B acceptance checklist

- Build the design from the verified endpoint fields only.
- Keep the response/acknowledgment distinction truthful.
- Render API-backed cache data only after it is stored from the actual grid response or prompt response.
- Replace the simulated worker/node map with a live node list, or clearly segregate it as illustrative.
- Do not add throughput, TTFT, active-worker count, or memory-RAM claims without an approved API contract.
- Verify keyboard-only flow, small-screen layout, high-contrast text, and reduced motion.

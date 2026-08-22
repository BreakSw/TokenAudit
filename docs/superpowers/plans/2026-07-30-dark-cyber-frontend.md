# TokenAudit Dark Cyber Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current light Vue frontend with the approved dark cyber audit console, add restrained scroll-reveal motion, and add a standard API-platform documentation page without changing backend contracts.

**Architecture:** Keep the existing Vue 3, Vue Router, Axios, Element Plus, and page-level business logic. Centralize visual tokens and Element Plus overrides in `theme.css`, add one lightweight reveal directive, keep shared stage/document data in focused modules, and drive the dashboard from the existing Token and Audit APIs. Add Vitest and Vue Test Utils before behavior changes.

**Tech Stack:** Vue 3.4, Vue Router 4, Element Plus 2.7, Axios, Vite 5, Vitest, Vue Test Utils, jsdom, CSS custom properties.

---

## File map

### Create

- `front-end/src/test/setup.js` — jsdom/browser API defaults for component tests.
- `front-end/src/directives/reveal.js` — one-shot IntersectionObserver reveal directive.
- `front-end/src/directives/reveal.test.js` — reveal behavior and fallback tests.
- `front-end/src/constants/auditStages.js` — canonical six-stage UI model plus overall stage.
- `front-end/src/constants/auditStages.test.js` — stage completeness tests.
- `front-end/src/utils/dashboard.js` — pure dashboard summary mapping.
- `front-end/src/utils/dashboard.test.js` — dashboard summary tests.
- `front-end/src/content/guide.js` — documentation navigation, sections, and local search.
- `front-end/src/content/guide.test.js` — guide search tests.
- `front-end/src/views/GuideView.vue` — standard API-platform documentation interface.
- `front-end/src/views/GuideView.test.js` — guide rendering and search interaction tests.

### Modify

- `front-end/package.json` and `front-end/package-lock.json` — add test dependencies and scripts.
- `front-end/vite.config.js` — configure Vitest/jsdom.
- `front-end/src/main.js` — register the reveal directive.
- `front-end/src/styles/theme.css` — dark tokens, Element Plus overrides, shared layout and motion styles.
- `front-end/src/App.vue` — dark console shell, responsive navigation, guide link.
- `front-end/src/router/index.js` — add `/guide`.
- `front-end/src/views/HomeView.vue` — real-data audit dashboard.
- `front-end/src/components/AuditForm.vue` — six-stage console workflow and terminal event panel.
- `front-end/src/components/TokenManager.vue` — dark form/table workspace.
- `front-end/src/components/HistoryRecord.vue` — compact task history.
- `front-end/src/components/ReportView.vue` — report console hierarchy.
- `front-end/src/views/AuditPage.vue`, `TokenPage.vue`, `HistoryPage.vue`, `ReportPage.vue` — reveal/page wrappers if required.

## Task 1: Install and configure the frontend test harness

**Files:**

- Modify: `front-end/package.json`
- Modify: `front-end/package-lock.json`
- Modify: `front-end/vite.config.js`
- Create: `front-end/src/test/setup.js`

- [ ] **Step 1: Install test dependencies**

Run:

```powershell
npm install --save-dev vitest@^2.1.9 @vue/test-utils@^2.4.6 jsdom@^25.0.1
```

Expected: dependencies are added to `package.json` and the lockfile updates without audit/install errors.

- [ ] **Step 2: Add the test script**

Add to `package.json`:

```json
"scripts": {
  "dev": "vite",
  "build": "vite build",
  "preview": "vite preview",
  "test": "vitest run",
  "test:watch": "vitest"
}
```

- [ ] **Step 3: Configure Vitest**

Update `vite.config.js` to:

```js
import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"

export default defineConfig({
  plugins: [vue()],
  server: {
    host: "0.0.0.0",
    port: 5173
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/test/setup.js"
  }
})
```

- [ ] **Step 4: Add test setup**

Create `src/test/setup.js`:

```js
import { afterEach } from "vitest"
import { config } from "@vue/test-utils"

config.global.stubs = {
  transition: false,
  "router-link": { template: "<a><slot /></a>" },
  "router-view": { template: "<div />" }
}

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener() {},
    removeListener() {},
    addEventListener() {},
    removeEventListener() {},
    dispatchEvent() {
      return false
    }
  })
})

afterEach(() => {
  document.body.innerHTML = ""
  localStorage.clear()
})
```

- [ ] **Step 5: Run the empty suite**

Run:

```powershell
npm test -- --passWithNoTests
```

Expected: exit code 0 and Vitest reports no test files.

- [ ] **Step 6: Commit the harness**

```powershell
git add front-end/package.json front-end/package-lock.json front-end/vite.config.js front-end/src/test/setup.js
git commit -m "test: add frontend vitest harness"
```

## Task 2: Add the one-shot scroll reveal directive

**Files:**

- Create: `front-end/src/directives/reveal.test.js`
- Create: `front-end/src/directives/reveal.js`
- Modify: `front-end/src/main.js`
- Modify: `front-end/src/styles/theme.css`

- [ ] **Step 1: Write failing directive tests**

Create `src/directives/reveal.test.js`:

```js
import { beforeEach, describe, expect, it, vi } from "vitest"
import reveal from "./reveal"

describe("v-reveal", () => {
  beforeEach(() => {
    delete window.IntersectionObserver
  })

  it("shows content immediately when IntersectionObserver is unavailable", () => {
    const element = document.createElement("section")
    reveal.mounted(element)
    expect(element.classList.contains("is-revealed")).toBe(true)
  })

  it("reveals once and disconnects observation after entering the viewport", () => {
    const unobserve = vi.fn()
    let callback
    window.IntersectionObserver = vi.fn((fn) => {
      callback = fn
      return { observe: vi.fn(), unobserve, disconnect: vi.fn() }
    })

    const element = document.createElement("section")
    reveal.mounted(element)
    callback([{ target: element, isIntersecting: true }])

    expect(element.classList.contains("is-revealed")).toBe(true)
    expect(unobserve).toHaveBeenCalledWith(element)
  })
})
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```powershell
npm test -- src/directives/reveal.test.js
```

Expected: FAIL because `./reveal` does not exist.

- [ ] **Step 3: Implement the directive**

Create `src/directives/reveal.js`:

```js
const reveal = {
  mounted(element, binding) {
    element.classList.add("reveal-block")
    if (binding.value?.stagger) {
      element.style.setProperty("--reveal-stagger", `${binding.value.stagger}ms`)
    }

    if (!("IntersectionObserver" in window)) {
      element.classList.add("is-revealed")
      return
    }

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue
          entry.target.classList.add("is-revealed")
          observer.unobserve(entry.target)
        }
      },
      { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
    )

    element.__revealObserver = observer
    observer.observe(element)
  },
  unmounted(element) {
    element.__revealObserver?.disconnect()
    delete element.__revealObserver
  }
}

export default reveal
```

- [ ] **Step 4: Register the directive**

Change `main.js` to:

```js
import { createApp } from "vue"
import ElementPlus from "element-plus"
import "element-plus/dist/index.css"
import "./styles/theme.css"
import App from "./App.vue"
import router from "./router"
import reveal from "./directives/reveal"

createApp(App).use(router).use(ElementPlus).directive("reveal", reveal).mount("#app")
```

- [ ] **Step 5: Add shared reveal CSS**

Add to `theme.css`:

```css
.reveal-block {
  opacity: 0;
  filter: blur(4px);
  transform: translate3d(0, 24px, 0);
  transition:
    opacity 520ms cubic-bezier(0.22, 1, 0.36, 1),
    transform 620ms cubic-bezier(0.22, 1, 0.36, 1),
    filter 500ms ease;
  transition-delay: var(--reveal-stagger, 0ms);
}

.reveal-block.is-revealed {
  opacity: 1;
  filter: blur(0);
  transform: translate3d(0, 0, 0);
}

@media (prefers-reduced-motion: reduce) {
  .reveal-block {
    opacity: 1;
    filter: none;
    transform: none;
    transition: none;
  }
}
```

- [ ] **Step 6: Run tests and verify GREEN**

Run:

```powershell
npm test -- src/directives/reveal.test.js
```

Expected: 2 tests pass.

- [ ] **Step 7: Commit**

```powershell
git add front-end/src/directives front-end/src/main.js front-end/src/styles/theme.css
git commit -m "feat: add restrained scroll reveal motion"
```

## Task 3: Define the canonical audit stage model

**Files:**

- Create: `front-end/src/constants/auditStages.test.js`
- Create: `front-end/src/constants/auditStages.js`
- Modify: `front-end/src/components/AuditForm.vue`

- [ ] **Step 1: Write the failing stage test**

Create `src/constants/auditStages.test.js`:

```js
import { describe, expect, it } from "vitest"
import { AUDIT_STAGES, stageIndex, stageLabel } from "./auditStages"

describe("audit stages", () => {
  it("includes all six implemented audit dimensions before overall", () => {
    expect(AUDIT_STAGES.map((stage) => stage.key)).toEqual([
      "validity",
      "permission",
      "watering",
      "compliance",
      "stability",
      "security",
      "overall"
    ])
  })

  it("maps unknown phases safely", () => {
    expect(stageIndex("security")).toBe(5)
    expect(stageLabel("security")).toBe("安全性审计")
    expect(stageIndex("unknown")).toBe(0)
    expect(stageLabel("unknown")).toBe("-")
  })
})
```

- [ ] **Step 2: Run and verify RED**

Run:

```powershell
npm test -- src/constants/auditStages.test.js
```

Expected: FAIL because `auditStages.js` does not exist.

- [ ] **Step 3: Implement the stage model**

Create `src/constants/auditStages.js`:

```js
export const AUDIT_STAGES = [
  { key: "validity", label: "有效性", detail: "验证 Token 和宣称模型是否可用" },
  { key: "permission", label: "权限", detail: "比较宣称模型、非宣称模型和匿名调用" },
  { key: "watering", label: "模型真实性", detail: "分析能力特征与模型声明是否一致" },
  { key: "compliance", label: "合规", detail: "检查敏感信息和异常调用风险" },
  { key: "stability", label: "稳定性", detail: "比较多次调用的一致性与耗时" },
  { key: "security", label: "安全性", detail: "检查 Token 结构与匿名访问风险" },
  { key: "overall", label: "综合判定", detail: "汇总 Agent 证据和风险建议" }
]

export function stageIndex(key) {
  const index = AUDIT_STAGES.findIndex((stage) => stage.key === key)
  return index < 0 ? 0 : index
}

export function stageLabel(key) {
  return AUDIT_STAGES.find((stage) => stage.key === key)?.label
    ? `${AUDIT_STAGES.find((stage) => stage.key === key).label}审计`.replace("综合判定审计", "综合判定")
    : "-"
}
```

- [ ] **Step 4: Refactor AuditForm to use the shared model**

Import:

```js
import { AUDIT_STAGES, stageIndex, stageLabel } from "../constants/auditStages"
```

Replace hard-coded phase sets and label branches with:

```js
const currentStage = computed(() => {
  const validPhases = new Set(AUDIT_STAGES.map((stage) => stage.key))
  for (let i = events.value.length - 1; i >= 0; i -= 1) {
    const event = events.value[i]
    const phase = event?.payload?.phase
    if (event?.event === "phase_start" && validPhases.has(phase)) return phase
    if (event?.event === "deepseek_call_start" && phase === "overall") return "overall"
  }
  return ""
})

const activeStepIndex = computed(() => stageIndex(currentStage.value))
const currentStageLabel = computed(() => stageLabel(currentStage.value))
```

Render steps with:

```vue
<el-step v-for="stage in AUDIT_STAGES" :key="stage.key" :title="stage.label" />
```

- [ ] **Step 5: Run tests and build**

```powershell
npm test -- src/constants/auditStages.test.js
npm run build
```

Expected: 2 stage tests pass and Vite build exits 0.

- [ ] **Step 6: Commit**

```powershell
git add front-end/src/constants front-end/src/components/AuditForm.vue
git commit -m "fix: show all implemented audit stages"
```

## Task 4: Build the global dark console shell and theme

**Files:**

- Modify: `front-end/src/styles/theme.css`
- Modify: `front-end/src/App.vue`
- Modify: `front-end/src/router/index.js`

- [ ] **Step 1: Add `/guide` to a failing router test**

Create `src/router/index.test.js`:

```js
import { describe, expect, it } from "vitest"
import router from "./index"

describe("application routes", () => {
  it("exposes the in-app documentation route", () => {
    const paths = router.getRoutes().map((route) => route.path)
    expect(paths).toContain("/guide")
  })
})
```

- [ ] **Step 2: Run and verify RED**

```powershell
npm test -- src/router/index.test.js
```

Expected: FAIL because `/guide` is missing.

- [ ] **Step 3: Add the guide route**

Add:

```js
import GuideView from "../views/GuideView.vue"
```

and:

```js
{ path: "/guide", component: GuideView }
```

Create a temporary compile-safe `GuideView.vue`:

```vue
<template><main class="docs-page">使用文档</main></template>
```

- [ ] **Step 4: Replace global visual tokens**

Rewrite `theme.css` around these tokens:

```css
:root {
  color-scheme: dark;
  --ta-bg: #050907;
  --ta-sidebar: #07100b;
  --ta-panel: #0a120e;
  --ta-panel-raised: #0d1711;
  --ta-code: #030604;
  --ta-line: rgba(67, 224, 162, 0.11);
  --ta-line-strong: rgba(67, 224, 162, 0.22);
  --ta-text: #e4f0e8;
  --ta-muted: rgba(220, 238, 226, 0.48);
  --ta-faint: rgba(220, 238, 226, 0.26);
  --ta-green: #43e0a2;
  --ta-amber: #e9bb63;
  --ta-danger: #ff7d79;
  --ta-radius: 6px;
  --el-color-primary: #43e0a2;
  --el-bg-color: #0a120e;
  --el-bg-color-overlay: #0d1711;
  --el-fill-color-blank: #0a120e;
  --el-text-color-primary: #e4f0e8;
  --el-text-color-regular: rgba(220, 238, 226, 0.68);
  --el-border-color: rgba(67, 224, 162, 0.12);
  --el-border-color-light: rgba(67, 224, 162, 0.08);
  --el-mask-color: rgba(0, 0, 0, 0.72);
  --el-border-radius-base: 6px;
}
```

Add global dark overrides for `.el-card`, `.el-input__wrapper`, `.el-select__wrapper`, `.el-table`, `.el-drawer`, `.el-dialog`, `.el-collapse`, `.el-alert`, `.el-tag`, `.el-button`, focus rings, and scrollbars.

- [ ] **Step 5: Replace App.vue shell**

Implement:

- fixed desktop sidebar with five routes;
- compact header with route label, local state, and settings;
- responsive mobile navigation;
- existing settings drawer and `backendApiKey` storage;
- no marketing hero in the shell.

Use this route map:

```js
const navigation = [
  { path: "/", label: "审计控制台", code: "00" },
  { path: "/audit", label: "发起审计", code: "01" },
  { path: "/tokens", label: "Token 管理", code: "02" },
  { path: "/history", label: "历史记录", code: "03" },
  { path: "/guide", label: "使用文档", code: "04" }
]
```

- [ ] **Step 6: Run router test and build**

```powershell
npm test -- src/router/index.test.js
npm run build
```

Expected: route test passes and the dark shell compiles.

- [ ] **Step 7: Commit**

```powershell
git add front-end/src/App.vue front-end/src/router front-end/src/styles/theme.css front-end/src/views/GuideView.vue
git commit -m "feat: add dark audit console shell"
```

## Task 5: Replace the homepage with a real-data dashboard

**Files:**

- Create: `front-end/src/utils/dashboard.test.js`
- Create: `front-end/src/utils/dashboard.js`
- Modify: `front-end/src/views/HomeView.vue`

- [ ] **Step 1: Write failing summary tests**

Create `src/utils/dashboard.test.js`:

```js
import { describe, expect, it } from "vitest"
import { summarizeDashboard } from "./dashboard"

describe("summarizeDashboard", () => {
  it("builds counts and the latest audit from real API data", () => {
    const summary = summarizeDashboard(
      [{ id: 1 }, { id: 2 }],
      [
        { id: 8, status: "completed", auditTime: "2026-07-30 10:00:00" },
        { id: 7, status: "failed", auditTime: "2026-07-29 10:00:00" }
      ]
    )

    expect(summary.tokenCount).toBe(2)
    expect(summary.auditCount).toBe(2)
    expect(summary.latestAudit.id).toBe(8)
    expect(summary.failedCount).toBe(1)
  })

  it("returns an explicit empty summary without fabricated values", () => {
    expect(summarizeDashboard([], [])).toEqual({
      tokenCount: 0,
      auditCount: 0,
      failedCount: 0,
      runningCount: 0,
      latestAudit: null
    })
  })
})
```

- [ ] **Step 2: Run and verify RED**

```powershell
npm test -- src/utils/dashboard.test.js
```

Expected: FAIL because `dashboard.js` is missing.

- [ ] **Step 3: Implement the pure summary**

Create `src/utils/dashboard.js`:

```js
export function summarizeDashboard(tokens = [], audits = []) {
  const sorted = [...audits].sort((a, b) => {
    const left = Date.parse(String(a.auditTime || "").replace(" ", "T")) || 0
    const right = Date.parse(String(b.auditTime || "").replace(" ", "T")) || 0
    return right - left
  })

  return {
    tokenCount: tokens.length,
    auditCount: audits.length,
    failedCount: audits.filter((audit) => audit.status === "failed").length,
    runningCount: audits.filter((audit) => audit.status === "running").length,
    latestAudit: sorted[0] || null
  }
}
```

- [ ] **Step 4: Rebuild HomeView**

Use `Promise.all([listTokens(), listAudits()])`, `summarizeDashboard`, loading state, explicit error state, and a retry button.

The template must include:

- compact “审计控制台” heading;
- real metrics only;
- recent task panel with empty state;
- six audit dimension rows;
- `v-reveal` on each major section;
- buttons to `/audit` and `/tokens`.

Do not include a giant slogan or fake risk score.

- [ ] **Step 5: Run tests and build**

```powershell
npm test -- src/utils/dashboard.test.js
npm run build
```

Expected: dashboard tests pass and the dashboard compiles.

- [ ] **Step 6: Commit**

```powershell
git add front-end/src/utils/dashboard* front-end/src/views/HomeView.vue
git commit -m "feat: turn homepage into audit dashboard"
```

## Task 6: Implement the standard API documentation page

**Files:**

- Create: `front-end/src/content/guide.test.js`
- Create: `front-end/src/content/guide.js`
- Create: `front-end/src/views/GuideView.test.js`
- Modify: `front-end/src/views/GuideView.vue`

- [ ] **Step 1: Write failing local search tests**

Create `src/content/guide.test.js`:

```js
import { describe, expect, it } from "vitest"
import { GUIDE_SECTIONS, searchGuideSections } from "./guide"

describe("guide search", () => {
  it("matches Chinese titles and API keywords", () => {
    expect(searchGuideSections("环境变量").map((item) => item.id)).toContain("configure")
    expect(searchGuideSections("POST /api/audits").map((item) => item.id)).toContain("run-audit")
  })

  it("returns all sections for an empty query and no fake match otherwise", () => {
    expect(searchGuideSections("")).toEqual(GUIDE_SECTIONS)
    expect(searchGuideSections("不存在的章节")).toEqual([])
  })
})
```

- [ ] **Step 2: Run and verify RED**

```powershell
npm test -- src/content/guide.test.js
```

Expected: FAIL because `guide.js` is missing.

- [ ] **Step 3: Implement searchable guide metadata**

Create `src/content/guide.js`:

```js
export const GUIDE_SECTIONS = [
  { id: "requirements", title: "运行要求", keywords: "Node Java Maven Python 安装" },
  { id: "configure", title: "配置环境变量", keywords: ".env DeepSeek API Key" },
  { id: "start", title: "启动项目", keywords: "npm Vite Spring Boot Maven Python" },
  { id: "token", title: "录入 Token", keywords: "Base URL 宣称模型 非宣称模型" },
  { id: "run-audit", title: "发起审计", keywords: "POST /api/audits auditId 事件" },
  { id: "report", title: "查看报告", keywords: "Markdown JSON Excel PDF 风险" },
  { id: "errors", title: "常见错误", keywords: "401 503 Model Not Exist python" }
]

export function searchGuideSections(query) {
  const normalized = String(query || "").trim().toLowerCase()
  if (!normalized) return GUIDE_SECTIONS
  return GUIDE_SECTIONS.filter((section) =>
    `${section.title} ${section.keywords}`.toLowerCase().includes(normalized)
  )
}
```

- [ ] **Step 4: Write the GuideView interaction test**

Create `src/views/GuideView.test.js`:

```js
import { mount } from "@vue/test-utils"
import { describe, expect, it } from "vitest"
import GuideView from "./GuideView.vue"

describe("GuideView", () => {
  it("filters the documentation navigation without calling a backend", async () => {
    const wrapper = mount(GuideView)
    const search = wrapper.get('[data-testid="guide-search"]')

    await search.setValue("环境变量")

    expect(wrapper.text()).toContain("配置环境变量")
    expect(wrapper.text()).not.toContain("常见错误")
  })
})
```

- [ ] **Step 5: Run and verify RED**

```powershell
npm test -- src/views/GuideView.test.js
```

Expected: FAIL because the temporary GuideView has no search input.

- [ ] **Step 6: Implement GuideView**

Build the approved API-platform layout:

- top search input with `data-testid="guide-search"`;
- left grouped documentation navigation filtered by `searchGuideSections`;
- central quickstart article with environment, startup, Token, audit, events, and report content;
- API endpoint blocks for health, creating an audit, querying status, and events;
- right on-page table of contents;
- code blocks with copy actions using `navigator.clipboard.writeText`;
- `v-reveal` on article sections;
- mobile layout hiding side navigation and table of contents.

Use real values from the repository: backend port `8086`, `python -m audit_core`, and implemented API paths.

- [ ] **Step 7: Run focused and full tests**

```powershell
npm test -- src/content/guide.test.js src/views/GuideView.test.js
npm test
```

Expected: all guide tests and the full suite pass.

- [ ] **Step 8: Commit**

```powershell
git add front-end/src/content front-end/src/views/GuideView*
git commit -m "feat: add in-app API usage documentation"
```

## Task 7: Restyle the audit workflow

**Files:**

- Modify: `front-end/src/components/AuditForm.vue`
- Modify: `front-end/src/views/AuditPage.vue`

- [ ] **Step 1: Preserve behavior and replace only presentation**

Keep these functions unchanged unless a failing test proves otherwise:

```text
reloadTokens
loadLastAuditId
saveLastAuditId
clearLastAuditId
startPolling
stopPolling
refreshOnce
submit
clearView
eventTagType
eventText
```

- [ ] **Step 2: Replace the template hierarchy**

Implement four `v-reveal` sections:

1. compact page heading and actions;
2. Token/export configuration panel;
3. seven-stage pipeline and progress panel using `AUDIT_STAGES`;
4. terminal event stream using the existing `displayEvents`.

Each event row must display timestamp, event tag, explanation, and available latency/status details.

- [ ] **Step 3: Replace scoped styles**

Use global design variables, 4–8px radii, thin borders, and code font for events. Remove light cards, oversized tutorial blocks, and inline layout styles.

- [ ] **Step 4: Run stage tests and build**

```powershell
npm test -- src/constants/auditStages.test.js
npm run build
```

Expected: stage tests pass and Vue compilation succeeds.

- [ ] **Step 5: Commit**

```powershell
git add front-end/src/components/AuditForm.vue front-end/src/views/AuditPage.vue
git commit -m "feat: redesign live audit workflow"
```

## Task 8: Restyle Token management and history

**Files:**

- Modify: `front-end/src/components/TokenManager.vue`
- Modify: `front-end/src/components/HistoryRecord.vue`
- Modify: `front-end/src/views/TokenPage.vue`
- Modify: `front-end/src/views/HistoryPage.vue`

- [ ] **Step 1: Rebuild TokenManager presentation**

Keep the existing form model, validation, create, list, delete, and password input behavior.

Use:

- compact page heading;
- two-column desktop layout;
- inline field help;
- terminal-style masked Token column;
- low-saturation danger action;
- single-column mobile layout;
- `v-reveal` on form and list panels.

- [ ] **Step 2: Rebuild HistoryRecord presentation**

Keep existing loading and navigation behavior.

Display:

- audit ID;
- Token ID;
- time;
- status;
- progress;
- truncated conclusion;
- report action.

Add an empty state linking to `/audit`.

- [ ] **Step 3: Run full tests and build**

```powershell
npm test
npm run build
```

Expected: all tests pass and production build exits 0.

- [ ] **Step 4: Commit**

```powershell
git add front-end/src/components/TokenManager.vue front-end/src/components/HistoryRecord.vue front-end/src/views/TokenPage.vue front-end/src/views/HistoryPage.vue
git commit -m "feat: redesign token and audit history pages"
```

## Task 9: Restyle the report console

**Files:**

- Modify: `front-end/src/components/ReportView.vue`
- Modify: `front-end/src/views/ReportPage.vue`

- [ ] **Step 1: Preserve report behavior**

Keep:

- loading by `auditId`;
- polling while running;
- stopping when completed/failed;
- event loading;
- Markdown copy;
- raw JSON access.

- [ ] **Step 2: Replace the report hierarchy**

Render:

- report header with audit ID, status, time, progress, and back action;
- overall conclusion panel;
- risk warnings and suggestions;
- six dimension sections in canonical order;
- Markdown, JSON, and event panels;
- terminal typography for JSON/events;
- `v-reveal` for major sections.

Do not inject raw Markdown as HTML; preserve the existing safe text rendering behavior.

- [ ] **Step 3: Run tests and build**

```powershell
npm test
npm run build
```

Expected: all tests pass and the report compiles.

- [ ] **Step 4: Commit**

```powershell
git add front-end/src/components/ReportView.vue front-end/src/views/ReportPage.vue
git commit -m "feat: redesign audit report console"
```

## Task 10: Responsive, accessibility, and visual verification

**Files:**

- Modify as needed: `front-end/src/styles/theme.css`
- Modify as needed: changed Vue files
- Create: `docs/superpowers/verification/2026-07-30-dark-cyber-frontend.md`

- [ ] **Step 1: Run the complete automated suite**

```powershell
npm test
```

Expected: all tests pass with zero failures.

- [ ] **Step 2: Run the production build**

```powershell
npm run build
```

Expected: Vite exits 0 and writes `front-end/dist`.

- [ ] **Step 3: Start the frontend and backend if available**

Frontend:

```powershell
npm run dev -- --host 127.0.0.1
```

Backend, in a separate terminal:

```powershell
mvn spring-boot:run
```

If the backend cannot start because external configuration is missing, use the existing page error states for layout verification and record the limitation.

- [ ] **Step 4: Browser-check desktop pages**

At a desktop viewport, inspect:

```text
/
/audit
/tokens
/history
/guide
/report/<existing-id when available>
```

Verify:

- no light Element Plus surfaces remain;
- no giant marketing headline remains;
- content does not overflow;
- all major sections reveal once during scrolling;
- focus styles are visible;
- guide navigation and search work;
- browser console has no new errors.

- [ ] **Step 5: Browser-check mobile layout**

At approximately 390×844:

- sidebar becomes mobile navigation;
- forms become one column;
- tables remain horizontally usable;
- guide sidebars are hidden;
- code blocks scroll horizontally;
- no action becomes unreachable.

- [ ] **Step 6: Verify reduced motion**

Emulate `prefers-reduced-motion: reduce` and confirm all reveal content is immediately visible and no continuous decorative animation remains.

- [ ] **Step 7: Record evidence**

Create `docs/superpowers/verification/2026-07-30-dark-cyber-frontend.md` only after the checks above finish. Record the exact Vitest pass count and exit code, Vite build exit code and output directory, every desktop route opened, the mobile viewport used, the observed reduced-motion behavior, the browser-console error count, and any concrete limitation. If no limitation remains, write `Known limitations: None observed during the checks above.`

- [ ] **Step 8: Final verification commit**

```powershell
git add front-end docs/superpowers/verification
git commit -m "test: verify dark cyber frontend"
```

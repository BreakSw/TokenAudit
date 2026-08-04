import { flushPromises, mount } from "@vue/test-utils"
import ElementPlus from "element-plus"
import { createMemoryHistory, createRouter } from "vue-router"
import { afterEach, describe, expect, it, vi } from "vitest"

import App from "./App.vue"

const ViewStub = { template: "<div>route content</div>" }
const DrawerStub = {
  props: ["modelValue", "title"],
  template: `
    <section v-if="modelValue" class="settings-drawer" role="dialog" :aria-label="title">
      <slot />
    </section>
  `
}

function createTestRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/", component: ViewStub },
      { path: "/audit", component: ViewStub },
      { path: "/tokens", component: ViewStub },
      { path: "/history", component: ViewStub },
      { path: "/guide", component: ViewStub },
      { path: "/report/:id", component: ViewStub }
    ]
  })
}

async function mountApp(path = "/") {
  const router = createTestRouter()
  await router.push(path)
  await router.isReady()

  const wrapper = mount(App, {
    attachTo: document.body,
    global: {
      plugins: [router, ElementPlus],
      stubs: {
        ElDrawer: DrawerStub,
        "router-link": false,
        "router-view": true
      }
    }
  })

  await flushPromises()
  return wrapper
}

function findButton(wrapper, label) {
  const matches = wrapper.findAll("button").filter((button) => button.text().trim() === label)
  expect(matches).toHaveLength(1)
  return matches[0]
}

async function openSettings(wrapper) {
  await findButton(wrapper, "设置").trigger("click")
  await flushPromises()
}

afterEach(() => {
  document.body.innerHTML = ""
})

describe("console shell routing", () => {
  it("shows the regular route title and marks its navigation link current", async () => {
    const wrapper = await mountApp("/audit")

    expect(wrapper.get(".header-heading h1").text()).toBe("发起审计")
    expect(wrapper.get('.primary-nav a[href="/audit"]').attributes("aria-current")).toBe("page")
  })

  it("shows the report title and marks history current", async () => {
    const wrapper = await mountApp("/report/42")

    expect(wrapper.get(".header-heading h1").text()).toBe("审计报告")
    expect(wrapper.get('.primary-nav a[href="/history"]').classes()).toContain("is-active")
    expect(wrapper.get('.primary-nav a[href="/history"]').attributes("aria-current")).toBe("page")
  })
})

describe("console shell settings", () => {
  it("loads the persisted API key only when settings opens", async () => {
    localStorage.setItem("backendApiKey", "stored-key")
    const wrapper = await mountApp()

    await openSettings(wrapper)

    expect(wrapper.get("#backend-api-key").element.value).toBe("stored-key")
  })

  it("discards a draft when settings closes", async () => {
    localStorage.setItem("backendApiKey", "stored-key")
    const wrapper = await mountApp()
    await openSettings(wrapper)

    await wrapper.get("#backend-api-key").setValue("draft-key")
    await wrapper.get("#backend-api-key").trigger("change")
    await findButton(wrapper, "关闭").trigger("click")
    await flushPromises()

    expect(localStorage.getItem("backendApiKey")).toBe("stored-key")
  })

  it("saves a non-empty draft", async () => {
    const wrapper = await mountApp()
    await openSettings(wrapper)

    await wrapper.get("#backend-api-key").setValue("new-key")
    await findButton(wrapper, "保存").trigger("click")

    expect(localStorage.getItem("backendApiKey")).toBe("new-key")
  })

  it("clears only the draft until an empty draft is saved", async () => {
    localStorage.setItem("backendApiKey", "stored-key")
    const wrapper = await mountApp()
    await openSettings(wrapper)

    await findButton(wrapper, "清除").trigger("click")
    expect(wrapper.get("#backend-api-key").element.value).toBe("")
    expect(localStorage.getItem("backendApiKey")).toBe("stored-key")

    await findButton(wrapper, "保存").trigger("click")
    expect(localStorage.getItem("backendApiKey")).toBeNull()
  })

  it("still mounts and reports an accessible error when storage reads fail", async () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new DOMException("blocked", "SecurityError")
    })

    const wrapper = await mountApp()
    await openSettings(wrapper)

    expect(wrapper.get(".console-shell").exists()).toBe(true)
    expect(wrapper.get('[role="alert"]').text()).toContain("无法访问浏览器本地存储")
  })

  it.each(["setItem", "removeItem"])("reports an accessible error when storage %s fails", async (method) => {
    vi.spyOn(Storage.prototype, method).mockImplementation(() => {
      throw new DOMException("blocked", "SecurityError")
    })

    const wrapper = await mountApp()
    await openSettings(wrapper)

    if (method === "setItem") {
      await wrapper.get("#backend-api-key").setValue("new-key")
    } else {
      await findButton(wrapper, "清除").trigger("click")
    }
    await findButton(wrapper, "保存").trigger("click")

    expect(wrapper.get('[role="alert"]').text()).toContain("无法访问浏览器本地存储")
  })
})

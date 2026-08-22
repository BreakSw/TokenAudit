import { flushPromises, mount } from "@vue/test-utils"
import { createMemoryHistory, createRouter } from "vue-router"
import { describe, expect, it } from "vitest"

import ProductHomeView from "./ProductHomeView.vue"

const RouteStub = { template: "<div>route target</div>" }

async function mountProductHome() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/home", component: RouteStub },
      { path: "/", component: RouteStub },
      { path: "/audit", component: RouteStub },
      { path: "/tokens", component: RouteStub },
      { path: "/guide", component: RouteStub }
    ]
  })
  await router.push("/home")
  await router.isReady()

  const wrapper = mount(ProductHomeView, {
    global: {
      plugins: [router],
      directives: { reveal: { mounted() {} } }
    }
  })

  return { router, wrapper }
}

describe("ProductHomeView", () => {
  it("presents the product without an oversized marketing headline structure", async () => {
    const { wrapper } = await mountProductHome()

    expect(wrapper.get(".hero-copy h1").text()).toContain("都有证据可查")
    expect(wrapper.findAll(".evidence-card")).toHaveLength(3)
    expect(wrapper.findAll(".scope-item")).toHaveLength(6)
  })

  it("switches the interactive audit workflow", async () => {
    const { wrapper } = await mountProductHome()
    const tabs = wrapper.findAll('[role="tab"]')

    expect(tabs).toHaveLength(4)
    expect(wrapper.get(".workflow-panel h3").text()).toContain("中转地址")

    await tabs[2].trigger("click")

    expect(tabs[2].attributes("aria-selected")).toBe("true")
    expect(wrapper.get(".workflow-panel h3").text()).toContain("事实先于模型结论")
  })

  it("navigates to the audit workflow from the primary action", async () => {
    const { router, wrapper } = await mountProductHome()
    const start = wrapper.findAll("button").find((button) => button.text().includes("开始一次审计"))

    await start.trigger("click")
    await flushPromises()

    expect(router.currentRoute.value.fullPath).toBe("/audit")
  })
})

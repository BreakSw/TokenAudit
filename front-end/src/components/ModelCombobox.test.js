import { mount } from "@vue/test-utils"
import ElementPlus from "element-plus"
import { describe, expect, it } from "vitest"

import ModelCombobox from "./ModelCombobox.vue"

const groups = [
  { label: "硅基流动", options: ["Qwen/Qwen3-8B", "deepseek-ai/DeepSeek-V3"] },
  { label: "OpenRouter", options: ["openai/gpt-4o-mini"] }
]

function mountCombobox(modelValue = "") {
  return mount(ModelCombobox, {
    props: { modelValue, groups },
    global: { plugins: [ElementPlus] }
  })
}

describe("ModelCombobox", () => {
  it("keeps arbitrary typed model ids instead of limiting input to the catalog", async () => {
    const wrapper = mountCombobox()
    const autocomplete = wrapper.findComponent({ name: "ElAutocomplete" })

    autocomplete.vm.$emit("update:modelValue", "vendor/custom-model-v2")
    autocomplete.vm.$emit("change", "vendor/custom-model-v2")
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted("update:modelValue")?.at(-1)).toEqual(["vendor/custom-model-v2"])
    expect(wrapper.emitted("commit")?.at(-1)).toEqual(["vendor/custom-model-v2"])
  })

  it("filters suggestions by complete model id and provider label", () => {
    const wrapper = mountCombobox()
    const fetchSuggestions = wrapper.findComponent({ name: "ElAutocomplete" }).props("fetchSuggestions")
    let qwenResults = []
    let providerResults = []

    fetchSuggestions("qwen3-8", (items) => { qwenResults = items })
    fetchSuggestions("硅基", (items) => { providerResults = items })

    expect(qwenResults.map((item) => item.value)).toEqual(["Qwen/Qwen3-8B"])
    expect(providerResults.map((item) => item.value)).toEqual([
      "Qwen/Qwen3-8B",
      "deepseek-ai/DeepSeek-V3"
    ])
  })

  it("commits a selected suggestion using its exact case-sensitive id", () => {
    const wrapper = mountCombobox()

    wrapper.findComponent({ name: "ElAutocomplete" }).vm.$emit("select", {
      value: "Qwen/Qwen3-8B",
      group: "硅基流动"
    })

    expect(wrapper.emitted("update:modelValue")?.at(-1)).toEqual(["Qwen/Qwen3-8B"])
    expect(wrapper.emitted("commit")?.at(-1)).toEqual(["Qwen/Qwen3-8B"])
  })
})

import { describe, expect, it } from "vitest"

import { MODEL_GROUPS } from "./modelCatalog"

describe("model catalog", () => {
  it("covers mainstream international and domestic model families", () => {
    const labels = MODEL_GROUPS.map((group) => group.label).join(" ")
    const models = MODEL_GROUPS.flatMap((group) => group.options)

    for (const family of ["OpenAI", "Claude", "Gemini", "DeepSeek", "Grok", "Kimi", "Qwen", "GLM", "豆包", "混元", "MiniMax", "Mistral", "Llama"]) {
      expect(labels).toContain(family)
    }
    expect(models.length).toBeGreaterThan(100)
    expect(new Set(models).size).toBe(models.length)
  })

  it("includes current OpenAI models in direct and OpenRouter formats", () => {
    const models = MODEL_GROUPS.flatMap((group) => group.options)
    const currentModels = [
      "gpt-5.6-sol",
      "gpt-5.6-terra",
      "gpt-5.6-luna",
      "gpt-5.5",
      "gpt-5.4",
      "gpt-5.4-mini"
    ]

    for (const model of currentModels) {
      expect(models).toContain(model)
      expect(models).toContain(`openai/${model}`)
    }
  })

  it("includes provider-qualified SiliconFlow model ids with exact casing", () => {
    const models = MODEL_GROUPS.flatMap((group) => group.options)

    expect(models).toContain("Qwen/Qwen3-8B")
    expect(models).toContain("deepseek-ai/DeepSeek-V3")
    expect(models).toContain("Pro/deepseek-ai/DeepSeek-R1")
    expect(models).not.toContain("qwen/qwen3-8b")
  })
})

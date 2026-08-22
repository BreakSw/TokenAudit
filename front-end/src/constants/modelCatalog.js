export const MODEL_GROUPS = [
  {
    label: "硅基流动 SiliconFlow（完整模型 ID）",
    options: [
      "Qwen/Qwen3-8B", "Qwen/Qwen3-14B", "Qwen/Qwen3-32B", "Qwen/Qwen3-235B-A22B",
      "deepseek-ai/DeepSeek-V3", "deepseek-ai/DeepSeek-R1",
      "Pro/deepseek-ai/DeepSeek-V3", "Pro/deepseek-ai/DeepSeek-R1",
      "moonshotai/Kimi-K2-Instruct", "THUDM/GLM-4-9B-0414",
      "meta-llama/Meta-Llama-3.1-70B-Instruct", "mistralai/Mistral-Large-Instruct-2411"
    ]
  },
  {
    label: "聚合中转常见写法（provider/model）",
    options: [
      "openrouter/free", "openai/gpt-5.6-sol", "openai/gpt-5.6-terra", "openai/gpt-5.6-luna",
      "openai/gpt-5.5", "openai/gpt-5.4", "openai/gpt-5.4-mini", "openai/gpt-4o-mini",
      "anthropic/claude-opus-4.6",
      "anthropic/claude-sonnet-4.5", "google/gemini-2.5-pro", "google/gemini-2.5-flash",
      "deepseek/deepseek-chat", "deepseek/deepseek-r1", "x-ai/grok-3-mini",
      "moonshotai/kimi-k2", "qwen/qwen3-235b-a22b", "meta-llama/llama-3.3-70b-instruct",
      "mistralai/mistral-large", "cohere/command-r-plus"
    ]
  },
  {
    label: "OpenAI / GPT / o 系列",
    options: [
      "gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna", "gpt-5.5", "gpt-5.4",
      "gpt-5.4-mini", "gpt-5.3", "gpt-5.2", "gpt-5", "gpt-5-mini", "gpt-5-nano",
      "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-4o", "gpt-4o-mini",
      "o1", "o1-mini", "o1-pro", "o3", "o3-mini", "o4-mini"
    ]
  },
  {
    label: "Anthropic / Claude",
    options: [
      "claude-opus-4.6", "claude-opus-4-6", "claude-opus-4.5", "claude-opus-4-5",
      "claude-sonnet-4.5", "claude-sonnet-4-5", "claude-haiku-4.5", "claude-haiku-4-5",
      "claude-sonnet-4", "claude-opus-4", "claude-3-7-sonnet", "claude-3-5-sonnet",
      "claude-3-5-haiku", "claude-3-opus", "claude-3-sonnet", "claude-3-haiku"
    ]
  },
  {
    label: "Google / Gemini",
    options: [
      "gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite",
      "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-pro", "gemini-1.5-flash"
    ]
  },
  {
    label: "DeepSeek",
    options: [
      "deepseek-chat", "deepseek-reasoner", "deepseek-v3", "deepseek-v3.1",
      "deepseek-r1", "deepseek-r1-distill-qwen-32b", "deepseek-coder"
    ]
  },
  {
    label: "xAI / Grok",
    options: ["grok-4", "grok-3", "grok-3-mini", "grok-2", "grok-2-mini"]
  },
  {
    label: "Moonshot / Kimi",
    options: [
      "kimi-k2", "kimi-k2-thinking", "kimi-latest", "moonshot-v1-auto",
      "moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"
    ]
  },
  {
    label: "阿里云 / Qwen / 通义千问",
    options: [
      "qwen3-max", "qwen3-plus", "qwen3-turbo", "qwen3-235b-a22b", "qwen3-32b",
      "qwen-max", "qwen-plus", "qwen-turbo", "qwen-long", "qwq-plus",
      "qwen2.5-72b-instruct", "qwen-vl-max", "qwen-vl-plus", "qwen-coder-plus"
    ]
  },
  {
    label: "智谱 AI / GLM",
    options: [
      "glm-4.5", "glm-4-plus", "glm-4-air", "glm-4-airx", "glm-4-flash",
      "glm-4-long", "glm-4v-plus", "glm-z1-air", "glm-z1-flash"
    ]
  },
  {
    label: "火山方舟 / 豆包",
    options: [
      "doubao-1.5-pro-32k", "doubao-1.5-pro-256k", "doubao-1.5-lite-32k",
      "doubao-pro-32k", "doubao-pro-128k", "doubao-lite-32k", "doubao-seed-1.6"
    ]
  },
  {
    label: "腾讯混元",
    options: [
      "hunyuan-turbos-latest", "hunyuan-turbo", "hunyuan-large", "hunyuan-standard",
      "hunyuan-lite", "hunyuan-code"
    ]
  },
  {
    label: "MiniMax",
    options: [
      "MiniMax-M1", "MiniMax-Text-01", "abab6.5s-chat", "abab6.5g-chat", "abab6.5-chat"
    ]
  },
  {
    label: "Mistral AI",
    options: [
      "mistral-large-latest", "mistral-medium-latest", "mistral-small-latest",
      "codestral-latest", "ministral-8b-latest", "ministral-3b-latest", "open-mixtral-8x22b"
    ]
  },
  {
    label: "Meta / Llama",
    options: [
      "llama-4-maverick", "llama-4-scout", "llama-3.3-70b-instruct",
      "llama-3.2-90b-vision-instruct", "llama-3.1-405b-instruct",
      "llama-3.1-70b-instruct", "llama-3.1-8b-instruct"
    ]
  },
  {
    label: "Cohere",
    options: ["command-a", "command-r-plus", "command-r", "command-light"]
  },
  {
    label: "Perplexity",
    options: ["sonar", "sonar-pro", "sonar-reasoning", "sonar-reasoning-pro", "sonar-deep-research"]
  },
  {
    label: "其他国内常用模型",
    options: [
      "Baichuan4", "Baichuan3-Turbo", "yi-lightning", "yi-large", "yi-medium",
      "step-2-16k", "step-1-256k", "step-1-flash", "ernie-4.0-turbo-8k",
      "ernie-speed-128k", "ernie-lite-8k"
    ]
  },
  {
    label: "其他开源与云端模型",
    options: [
      "phi-4", "phi-3.5-mini-instruct", "amazon-nova-pro-v1:0", "amazon-nova-lite-v1:0",
      "jamba-1.5-large", "jamba-1.5-mini", "nemotron-4-340b-instruct"
    ]
  }
]

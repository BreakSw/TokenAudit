---
model: "Kimi K3"
priority: "P3"
source_id: "05-openlm"
title: "Kimi K3 | OpenLM.ai"
source_url: "https://openlm.ai/kimi-k3/"
final_url: "https://openlm.ai/kimi-k3/"
captured_at: "2026-08-23T10:53:16.582Z"
capture_provider: "firecrawl"
accepted_for_review: true
sha256: "94e39706df6e9146ff5b081262eae66f314854ae47f22fa7983a527cc6fc12f3"
---
We introduce Kimi K3 — our most capable model. Kimi K3 is a 2.8T-parameter model built on our Kimi Delta Attention and Attention Residuals, with native vision capabilities and a 1-million-token context window. It is the world’s first open 3T-class model, designed for frontier intelligence across long-horizon coding, knowledge work, and reasoning.

While its overall performance still trails the most powerful proprietary models, Claude Fable 5 and GPT 5.6 Sol, Kimi K3 demonstrated frontier-level performance across our evaluation suite, consistently outperforming other tested models.

[![Chat](https://img.shields.io/badge/%F0%9F%A4%96%20Chat-Kimi%20K3-ff6b6b?color=1783ff&logoColor=white)](https://www.kimi.com/)[![Homepage](https://img.shields.io/badge/Homepage-Moonshot%20AI-white?logo=Kimi&logoColor=white)](https://www.moonshot.ai/)[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Moonshot%20AI-ffc107?color=ffc107&logoColor=white)](https://huggingface.co/moonshotai)

**[Tech Blog](https://www.kimi.com/blog/kimi-k3)**

## An Open 3T-Class Model

Kimi K3 is the first open model to reach 2.8 trillion parameters. It marks the latest step in Kimi’s sustained push at the scaling frontier: for nine of the past twelve months, Kimi models have set the upper bound of open-model sizes.

![Kimi K3 benchmarks](https://openlm.ai/assets/blog/moonshot/benchmark_3.webp)

## Model Introduction

### Key Features

- **New Architecture**: Kimi K3 is built on Kimi Delta Attention (KDA) and Attention Residuals (AttnRes), and scales up MoE sparsity with a Stable LatentMoE framework that activates 16 out of 896 experts — yielding an approximate 2.5× improvement in overall scaling efficiency over Kimi K2.
- **Long-Horizon Coding**: Operating with minimal human oversight, Kimi K3 sustains long engineering sessions, navigates massive repositories, and orchestrates terminal tools — from GPU kernel optimization and compiler development to vision-in-the-loop game dev, CAD, and even chip design.
- **Agentic Knowledge Work**: Kimi K3 advances end-to-end knowledge work, producing deep research with interactive visualizations, widgets and dashboards, and motion design and video editing, powered by its native multimodal architecture.
- **Native Multimodality & Long Context**: Kimi K3 understands text, images, and video within the same model, and supports a 1-million-token context window.
- **Open Frontier Weights**: We release the full Kimi K3 model weights under the Kimi K3 License, making frontier intelligence openly available for research, deployment, and further innovation.

### Architecture

Kimi K3 architecture diagramKimi K3 architecture: the Stable LatentMoE and KDA modules (left), the AttnRes operation α (top right), and the Block Attention Residuals backbone (right).

KDA provides an efficient foundation for scaling attention, while AttnRes selectively retrieves representations across depth rather than accumulating them uniformly. Together, they form the architectural backbone of a model designed to scale well beyond the trillion-parameter regime.

Kimi K3 uses Stable LatentMoE, effectively activating 16 of 896 experts. At this level of sparsity, routing and optimization become first-order challenges. Quantile Balancing derives expert allocation directly from router-score quantiles, eliminating heuristic updates and a sensitive balancing hyperparameter, while Per-Head Muon extends Muon by optimizing attention heads independently for more adaptive learning at scale. Sigmoid Tanh Unit (SiTU) and Gated MLA improve activation control and attention selectivity respectively. Together, these advances enable stable and efficient training at the 2.8-trillion-parameter scale.

Kimi K3 applies quantization-aware training from the SFT stage onward, using MXFP4 weights with MXFP8 activations for broad hardware compatibility. To prevent expert imbalance from degrading throughput at large expert-parallel scales, we introduce a fully balanced expert-parallel training method with static shapes and no host synchronization on the critical path. Since inference efficiency likewise benefits from larger high-bandwidth communication domains, we recommend deploying Kimi K3 on supernode configurations with 64 or more accelerators. Finally, as KDA poses new challenges for conventional prefix caching, we have contributed a corresponding implementation to the vLLM community, to be released alongside the model. KDA with prefill cache allows us to serve Kimi K3 at a highly competitive token price despite its scale and long context.

## Model Summary

|     |     |
| --- | --- |
| **Architecture** | Mixture-of-Experts (MoE) |
| **Total Parameters** | 2.8T |
| **Activated Parameters** | 104B |
| **Number of Layers** | 93 |
| **Number of Dense Layers** | 1 |
| **Attention-Layer Composition** | 69 KDA + 24 Gated MLA |
| **Attention Hidden Dimension** | 7168 |
| **Number of Attention Heads** | 96 |
| **Latent MoE Dimension** | 3584 |
| **MoE Hidden Dimension** (per Expert) | 3072 |
| **Number of Experts** | 896 |
| **Selected Experts per Token** | 16 |
| **Number of Shared Experts** | 2 |
| **Vocabulary Size** | 160K |
| **Context Length** | 1048576 |
| **Attention Mechanism** | KDA & Gated MLA |
| **Activation Function** | SiTU-GLU |
| **Vision Encoder** | MoonViT-V2 |
| **Parameters of Vision Encoder** | 401M |
| **Quantization** | MXFP4 weights / MXFP8 activations<br>(quantization-aware training) |
| **Modality** | Text, Image |

## Benchmarks

| Benchmark | Kimi K3 (max) | Claude Fable 5 (max) | GPT 5.6 Sol (max) | Claude Opus 4.8 (max) | GPT 5.5 (xhigh) | GLM-5.2 (max) |
| --- | --- | --- | --- | --- | --- | --- |
| **Coding** |  |  |  |  |  |  |
| DeepSWE | 67.5 | 70.0 | **73.0** | 59.0 | 67.0 | 46.2 |
| Program Bench | **77.8** | 76.8 | 77.6 | 71.9 | 70.8 | 63.7 |
| Terminal Bench 2.1 | 88.3 | 84.6 | **88.8** | 84.6 | 83.4 | 82.7 |
| FrontierSWE | 81.2 | **86.6** | 71.3 | 66.7 | 64.9 | 67.3 |
| SWE Marathon | **42.0** | 35.0 | 39.0 | 40.0 | 14.0 | 13.0 |
| PostTrain Bench | 36.6 | **41.4** | 34.6 | 34.1 | 28.4 | 34.3 |
| MLS Bench | 48.3 | **49.9** | 46.2 | 42.8 | 35.5 | 40.4 |
| Kimi Code Bench 2.0 (Internal) | 72.9 | **76.9** | 64.8 | 71.7 | 69.0 | 64.2 |
| **Agentic** |  |  |  |  |  |  |
| GDPval-AA v2 (Elo-score) | 1668 | **1760** | 1748 | 1600 | 1494 | 1514 |
| BrowseComp | **91.2** | 88.0 | 90.4 | 84.3 | 84.4 | — |
| DeepSearchQA (f1-score) | **95.0** | 94.2 | — | 93.1 | — | — |
| Toolathlon-Verified | 73.2 | **77.9** | 74.9 | 76.2 | 73.5 | 59.9 |
| MCP Atlas | 84.2 | **84.7** | 83.6 | 83.6 | 82.8 | 82.6 |
| Automation Bench | **30.8** | 29.1 | 29.7 | 27.2 | 22.7 | 12.9 |
| Job Bench | 52.9 | **57.4** | 46.5 | 48.4 | 38.3 | 43.4 |
| AA-Briefcase (Elo-score) | 1548 | **1583** | 1495 | 1354 | 1158 | 1260 |
| APEX-Agents | 37.6 | **43.3** | 39.9 | 39.4 | 38.5 | 35.6 |
| Office QA Pro | 63.3 | **69.9** | 63.2 | 63.9 | 60.9 | 41.4 |
| SpreadsheetBench 2 | **34.8** | 34.7 | 32.4 | 31.6 | 29.1 | 28.1 |
| DECK-Bench (Internal) | 73.5 | 73.0 | **74.7** | 66.9 | 68.2 | 68.6 |
| **Reasoning & Knowledge** |  |  |  |  |  |  |
| GPQA-Diamond | 93.5 | 92.6 | **94.1** | 91.0 | 93.5 | 91.2 |
| HLE-Full | 43.5 | **53.3** | 44.5 | 49.8 | 41.4 | — |
| HLE-Full w/ tools | 56.0 | **63.0** | 58.0 | 57.9 | 52.2 | — |
| **Vision** |  |  |  |  |  |  |
| MMMU-Pro | 81.6 | 81.2 | **83.0** | 78.9 | 81.2 | — |
| MMMU-Pro w/ python | 83.4 | **86.5** | 84.6 | 82.7 | 83.2 | — |
| CharXiv (RQ) | 84.8 | **88.9** | 84.6 | 80.5 | 84.1 | — |
| CharXiv (RQ) w/ python | 91.3 | **93.5** | 89.1 | 89.9 | 89.0 | — |
| MathVision | 94.3 | 94.8 | **95.8** | 86.7 | 92.2 | — |
| MathVision w/ python | 97.8 | **98.6** | 97.8 | 97.1 | 96.8 | — |
| BabyVision w/ python | 85.7 | **90.5** | 88.9 | 81.2 | 83.6 | — |
| ZeroBench\_main (pass@5) | **23.0** | **23.0** | 17.0 | 17.0 | 22.0 | — |
| ZeroBench\_main w/ python (pass@5) | 41.0 | **46.0** | 35.0 | 34.0 | 41.0 | — |
| WorldVQA ForceAnswer | 51.0 | **56.7** | 41.8 | 39.1 | 38.5 | — |
| OmniDocBench | **91.1** | 89.8 | 85.8 | 87.9 | 89.4 | — |
| PerceptionBench | 58.5 | 57.2 | **59.7** | 47.2 | 55.8 | — |

### Footnotes

All Kimi K3 results are obtained with the reasoning effort set to ‘max’, setting temperature = 1.0 and top-p = 1.0. Depending on the benchmark, each model is evaluated under one of three agentic harnesses — KimiCode, Claude Code, or Codex — as specified in the notes below.

**Coding benchmarks**

1. **DeepSWE.** Kimi K3 is evaluated with the KimiCode harness. The GLM-5.2 score is taken from the GLM-5.2 release blog ( [https://z.ai/blog/glm-5.2](https://z.ai/blog/glm-5.2)); all remaining scores are from the official DeepSWE leaderboard ( [https://deepswe.datacurve.ai](https://deepswe.datacurve.ai/)), under which Kimi K3 attains 67.3 with the mini-SWE-agent harness.
2. **Terminal-Bench 2.1.** Kimi K3 is evaluated with the KimiCode harness. For all other models, we report the best score across harnesses: GLM-5.2 with Claude Code ( [https://z.ai/blog/glm-5.2](https://z.ai/blog/glm-5.2)); Claude Opus 4.8 and Claude Fable 5 with Terminus 2 ( [https://artificialanalysis.ai/evaluations/terminalbench-v2-1](https://artificialanalysis.ai/evaluations/terminalbench-v2-1)); GPT 5.5 and GPT 5.6 Sol with Codex ( [https://openai.com/index/previewing-gpt-5-6-sol](https://openai.com/index/previewing-gpt-5-6-sol)).
3. **Program Bench.** Kimi K3 is evaluated with the KimiCode harness. The GLM-5.2 score is from [https://z.ai/blog/glm-5.2](https://z.ai/blog/glm-5.2); all other scores are from [https://www.vals.ai/benchmarks/programbench](https://www.vals.ai/benchmarks/programbench).
4. **SWE Marathon.** Kimi K3, Claude Opus 4.8, and Claude Fable 5 are evaluated with the Claude Code harness; GPT 5.6 Sol is evaluated with the Codex harness. The GLM-5.2 score is from [https://z.ai/blog/glm-5.2](https://z.ai/blog/glm-5.2).
5. **FrontierSWE.** Kimi K3 is evaluated with the KimiCode harness and GPT 5.6 Sol with the Codex harness; all other results are from [https://www.frontierswe.com](https://www.frontierswe.com/). Dominance scores are recomputed from the raw scores using the official evaluation script and are current as of July 16, 2026.
6. **PostTrain Bench.** Scores for GLM-5.2, GPT 5.5, and Claude Opus 4.8 are adopted from the official PostTrainBench results. Kimi K3, Claude Fable 5, and GPT 5.6 Sol are evaluated with the official Harbor implementation at maximum reasoning effort, averaged over three runs — Kimi K3 and Claude Fable 5 with the Claude Code harness, and GPT 5.6 Sol with the Codex harness. Under the Claude Code harness, requests refused by Claude Fable 5 due to its usage policy automatically fall back to Claude Opus 4.8.
7. **MLS Bench Lite.** Kimi K3 is evaluated with the KimiCode harness; GLM-5.2 and the Claude models with the Claude Code harness; GPT 5.5 and GPT 5.6 Sol with the Codex harness.
8. **KCB 2.0.** Kimi K3 is evaluated with both the KimiCode and Claude Code harnesses; GLM-5.2, Claude Opus 4.8, and Claude Fable 5 with the Claude Code harness; GPT 5.5 and GPT 5.6 Sol with the Codex harness. All models are evaluated at maximum reasoning effort, except GPT 5.5, which uses the “xhigh” setting.

**Productivity and agentic benchmarks**

1. **OfficeQA Pro and SpreadsheetBench 2.** Kimi K3, GLM-5.2, Claude Opus 4.8, and Claude Fable 5 are evaluated with the Claude Code harness; GPT 5.5 and GPT 5.6 Sol are evaluated with the Codex harness.
2. **MCP Atlas.** All models are evaluated on the 500-task public subset with a 100-turn limit, using Gemini 3.1 Pro as the judge.
3. **AutomationBench.** All models are evaluated on the 600-task public subset, following the official GitHub setup in all other respects.
4. **BrowseComp.** We adopt the context-compaction strategy used in the Claude model cards, triggered at 300K tokens. When evaluated with a 1M-token context window and no context management, Kimi K3 achieves a score of 90.4. The results of Claude Fable 5, Claude Opus 4.8, GPT 5.6 Sol, and GPT 5.5 are cited from [https://www.anthropic.com/news/claude-fable-5-mythos-5](https://www.anthropic.com/news/claude-fable-5-mythos-5) and [https://openai.com/index/gpt-5-6](https://openai.com/index/gpt-5-6).
5. **GDPval-AA v2 and AA-Briefcase** scores are cited from [https://artificialanalysis.ai](https://artificialanalysis.ai/).

**Multimodal benchmarks**

1. Except for ZeroBench, which follows the official setting and is run five times, all multimodal scores are averaged over three runs. MMMU-Pro is evaluated following the official protocol, preserving the original input order and prepending images to the text input.
2. **PerceptionBench.** PerceptionBench is an in-house benchmark that focuses on atomic visual perception capabilities.

## Deployment

> **ℹ️**
> **Note**
>
> You can access Kimi K3’s API on [https://platform.kimi.ai](https://platform.kimi.ai/) by selecting `kimi-k3`, and we provide an OpenAI/Anthropic-compatible API for you. Currently, Kimi K3 is recommended to run on the following inference engines:

- [vLLM](https://github.com/vllm-project/vllm) — see [recipes](https://recipes.vllm.ai/moonshotai/Kimi-K3)
- [SGLang](https://github.com/sgl-project/sglang) — see [cookbook](https://docs.sglang.io/cookbook/autoregressive/Moonshotai/Kimi-K3)
- [TokenSpeed](https://lightseek.org/tokenspeed) — see [recipes](https://lightseek.org/tokenspeed/recipes/models#kimi-k3)

## Model Usage

Kimi K3 always has thinking enabled, and will return `reasoning_content`. Thinking effort is configured with the top-level `reasoning_effort` request field, which supports `"low"`, `"high"`, and `"max"` (default `"max"`).

Kimi K3 was trained in the preserved thinking history mode. For multi-turn conversations and tool calls, Kimi K3 requires the complete assistant message returned by the API to be passed back to `messages` as-is — including `reasoning_content` and `tool_calls`, not just `content`:

```python
import openai

def chat_with_preserved_thinking(client: openai.OpenAI, model_name: str):
    messages = [\
        {\
            "role": "user",\
            "content": "Tell me three random numbers."\
        },\
        {\
            "role": "assistant",\
            "reasoning_content": "I'll start by listing five numbers: 473, 921, 235, 215, 222, and I'll tell you the first three.",\
            "content": "473, 921, 235"\
        },\
        {\
            "role": "user",\
            "content": "What are the other two numbers you have in mind?"\
        }\
    ]

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        stream=False,
        max_tokens=4096,
        reasoning_effort="max",
    )
    # the assistant should mention 215 and 222 that appear in the prior reasoning content
    print(f"response: {response.choices[0].message.reasoning}")
    return response.choices[0].message.content
```

For full guides and examples (vision input, structured output, partial mode, tool choice, dynamic tool loading, context caching), see the [Kimi K3 Quickstart](https://platform.kimi.ai/docs/guide/kimi-k3-quickstart) and [Thinking Effort](https://platform.kimi.ai/docs/guide/use-thinking-effort).

Kimi K3 works best with [Kimi Code CLI](https://www.kimi.com/code) as its agent framework. We warmly invite you to give it a try — run Kimi Code in your terminal and select Kimi K3 using the `/model` command. We hope you enjoy building with Kimi K3, and we would love to hear your feedback!

---
model: "GPT-5.6 Luna"
priority: "P0"
source_id: "01-openai-model-page"
title: "GPT-5.6 Luna Model | OpenAI API"
source_url: "https://developers.openai.com/api/docs/models/gpt-5.6-luna"
final_url: "https://developers.openai.com/api/docs/models/gpt-5.6-luna"
captured_at: "2026-08-23T10:48:28.152Z"
capture_provider: "firecrawl"
accepted_for_review: true
sha256: "999c2fd07730876194917bb7b8720d4a174161e603de5118f919d7e112eb8d98"
---
For the complete documentation index, see [llms.txt](https://developers.openai.com/llms.txt). Markdown versions of documentation pages are available by appending
`.md` to the page URL.

## Search the API docs

Search docs

### Suggested

response\_formatreasoning\_effortstreamingtools

Primary navigation

Search docs

### Suggested

response\_formatreasoning\_effortstreamingtools

Overview  Models  Agents  Tools  Voice & Audio  Production  API reference

OverviewModelsAgentsToolsVoice & AudioProductionAPI referenceDocs sectionModels

- [Model catalog](https://developers.openai.com/api/docs/models)

### Choose a model

- [Pricing](https://developers.openai.com/api/docs/pricing)
- [Model selection](https://developers.openai.com/api/docs/guides/model-selection)

### Text and code

- [Text generation](https://developers.openai.com/api/docs/guides/text)
- [Code generation](https://developers.openai.com/api/docs/guides/code-generation)
- [Structured output](https://developers.openai.com/api/docs/guides/structured-outputs)

### Prompting

- [Overview](https://developers.openai.com/api/docs/guides/prompting)
- [Prompt engineering](https://developers.openai.com/api/docs/guides/prompt-engineering)
- [Citation formatting](https://developers.openai.com/api/docs/guides/citation-formatting)
- [Migration guide](https://developers.openai.com/api/docs/guides/prompting/migrate-from-prompt-object)
- [Prompt generation](https://developers.openai.com/api/docs/guides/prompt-generation)
- [Frontend prompting](https://developers.openai.com/api/docs/guides/frontend-prompt)

### Reasoning

- [Reasoning models](https://developers.openai.com/api/docs/guides/reasoning)
- [Reasoning best practices](https://developers.openai.com/api/docs/guides/reasoning-best-practices)

### Images and video

- [Images and vision](https://developers.openai.com/api/docs/guides/images-vision)
- [Image generation](https://developers.openai.com/api/docs/guides/image-generation)
- [Video generation](https://developers.openai.com/api/docs/guides/video-generation)

### Realtime and audio

- [Audio and speech](https://developers.openai.com/api/docs/guides/audio)
- [Overview](https://developers.openai.com/api/docs/guides/realtime)
- [Voice agents](https://developers.openai.com/api/docs/guides/voice-agents)

### Specialized models

- [Deep research](https://developers.openai.com/api/docs/guides/deep-research)
- [Embeddings](https://developers.openai.com/api/docs/guides/embeddings)
- [Moderation](https://developers.openai.com/api/docs/guides/moderation)

[API Dashboard](https://platform.openai.com/login)

[Try ChatGPT](https://chatgpt.com/)

[Models](https://developers.openai.com/api/docs/models)

![gpt-5.6-luna](https://developers.openai.com/images/api/models/icons/gpt-5.6-luna.png)

GPT-5.6 Luna

Default

GPT-5.6 model optimized for cost-sensitive workloads

GPT-5.6 model optimized for cost-sensitive workloads

CompareTry in Playground

Reasoning

High

Speed

Fast

Price

$0.2•$1.2

Input•Output

Input

Text, image

Output

Text

GPT-5.6 Luna is designed for cost-sensitive, high-volume workloads. It
roughly corresponds to the nano model tier used in earlier GPT-5 families.
Reasoning.effort supports: none, low, medium (default), high, xhigh, and max.

1,050,000 context window

128,000 max output tokens

Feb 16, 2026 knowledge cutoff

Reasoning token support

Pricing

Pricing is based on the number of tokens used, or other metrics based on the model type. For tool-specific models, like search and computer use, there’s a fee per tool call. See details in the [pricing page](https://developers.openai.com/api/docs/pricing).

Text tokens

Per 1M tokens

Input

$0.20

Cached input

$0.02

Output

$1.20

Quick comparison

Input

Cached input

Output

GPT-5.6 Terra

$2.00

GPT-5.6 Luna

$0.20

GPT-5.4 nano

$0.20

Prompts with >272K input tokens are priced at 2x input and 1.5x output for the full request.

Cache writes are billed at 1.25x the uncached input token rate.

Modalities

Text

Input and output

Image

Input only

Audio

Not supported

Video

Not supported

Endpoints

Chat Completions

v1/chat/completions

Responses

v1/responses

Realtime

v1/realtime

Realtime translation

v1/realtime/translations

Realtime transcription

v1/realtime/transcription\_sessions

Assistants

v1/assistants

Batch

v1/batch

Fine-tuning

v1/fine-tuning

Embeddings

v1/embeddings

Image generation

v1/images/generations

Videos

v1/videos

Image edit

v1/images/edits

Speech generation

v1/audio/speech

Transcription

v1/audio/transcriptions

Translation

v1/audio/translations

Moderation

v1/moderations

Completions (legacy)

v1/completions

Features

Streaming

Supported

Function calling

Supported

Structured outputs

Supported

Fine-tuning

Not supported

Tools

Tools supported by this model when using the Responses API.

Web search

Supported

File search

Supported

Image generation

Supported

Code interpreter

Supported

Hosted shell

Supported

Apply patch

Supported

Skills

Supported

Computer use

Supported

MCP

Supported

Tool search

Supported

Snapshots

Snapshots let you lock in a specific version of the model so that performance and behavior remain consistent. Below is a list of all available snapshots and aliases for GPT-5.6 Luna.

![gpt-5.6-luna](https://developers.openai.com/images/api/models/icons/gpt-5.6-luna.png)

gpt-5.6-luna

gpt-5.6-luna

gpt-5.6-luna

Rate limits

Rate limits ensure fair and reliable access to the API by placing specific caps on requests, tokens, audio duration, or other usage within a given time period. Your usage tier determines how high these limits are set and automatically increases as you send more requests and spend more on the API.

| Tier | RPM | TPM | Batch queue limit |
| --- | --- | --- | --- |
| Free | Not supported |
| Tier 1 | 500 | 500,000 | 5,000,000 |
| Tier 2 | 5,000 | 2,000,000 | 20,000,000 |
| Tier 3 | 5,000 | 4,000,000 | 40,000,000 |
| Tier 4 | 10,000 | 10,000,000 | 1,000,000,000 |
| Tier 5 | 30,000 | 180,000,000 | 15,000,000,000 |

Ask AI

Loading docs agent...

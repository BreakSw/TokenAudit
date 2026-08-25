---
model: "Claude Opus 4.6"
priority: "P0"
source_id: "02-anthropic-models-overview"
title: "Models overview - Claude Platform Docs"
source_url: "https://platform.claude.com/docs/en/about-claude/models/overview"
final_url: "https://platform.claude.com/docs/en/about-claude/models/overview"
captured_at: "2026-08-23T10:50:29.913Z"
capture_provider: "firecrawl"
accepted_for_review: true
sha256: "d0986cc18e2ff087ad55413f20bbc975b4899256f1a5e6360e71e7c7362f8dca"
---
Ask Docs
![Chat avatar](https://platform.claude.com/docs/images/book-icon-light.svg)

Copy page



##   Choosing a model

If you're unsure which model to use, start with **Claude Opus 5** for complex agentic coding and enterprise work. For workloads that need the highest available capability, use [Claude Fable 5](https://platform.claude.com/docs/en/about-claude/models/overview#claude-fable-5-and-claude-mythos-5).

All current Claude models support text and image input, text output, multilingual capabilities, and vision. Models are available through the Claude API, [Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock), [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), [Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai), and [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry).

Once you've picked a model, [learn how to make your first API call](https://platform.claude.com/docs/en/get-started).

###   Claude Fable 5 and Claude Mythos 5

Claude Fable 5 (`claude-fable-5`) is Anthropic's most capable widely released model. Claude Mythos 5 (`claude-mythos-5`) shares Claude Fable 5's specs and pricing and joins the invitation-only Claude Mythos Preview (`claude-mythos-preview`) within [Project Glasswing](https://anthropic.com/glasswing). See [Introducing Claude Fable 5 and Claude Mythos 5](https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5) for launch details and API changes.

Claude Fable 5 is available on the Claude API, Amazon Bedrock, Claude Platform on AWS, Google Cloud, and Microsoft Foundry beginning June 9, 2026. Claude Mythos 5 is offered only to approved customers in [Project Glasswing](https://anthropic.com/glasswing), beginning the same day. For access, contact your Anthropic, AWS, or Google Cloud account team.

###   Latest models comparison

| Feature | Claude Fable 5 | Claude Opus 5 | Claude Sonnet 5 | Claude Haiku 4.5 |
| --- | --- | --- | --- | --- |
| **Description** | Next-generation intelligence for long-running agents | For complex agentic coding and enterprise work | The best combination of speed and intelligence | The fastest model with near-frontier intelligence |
| **Claude API ID** | claude-fable-5 | claude-opus-5 | claude-sonnet-5 | claude-haiku-4-5-20251001 |
| **Claude API alias** | claude-fable-5 | claude-opus-5 | claude-sonnet-5 | claude-haiku-4-5 |
| **AWS Bedrock ID** | anthropic.claude-fable-53 | anthropic.claude-opus-53 | anthropic.claude-sonnet-53 | anthropic.claude-haiku-4-5-20251001-v1:0 |
| **Google Cloud ID** | claude-fable-5 | claude-opus-5 | claude-sonnet-5 | claude-haiku-4-5@20251001 |
| **Pricing** 1 | $10 / input MTok<br>$50 / output MTok | $5 / input MTok<br>$25 / output MTok | $2 / input MTok<br>$10 / output MTok | $1 / input MTok<br>$5 / output MTok |
| **[Extended thinking (`thinking.type: "enabled"`)](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)** | No | No | No | Yes |
| **[Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)** | Yes (always on) | Yes | Yes | No |
| **Comparative latency** | Slower | Moderate | Fast | Fastest |
| **Context window** | 1M tokens | 1M tokens | 1M tokens | 200k tokens |
| **Max output** | 128k tokens | 128k tokens | 128k tokens | 64k tokens |
| **Reliable knowledge cutoff** | Jan 20262 | May 20262 | Jan 20262 | Feb 2025 |
| **Training data cutoff** | Jan 2026 | May 2026 | Jan 2026 | Jul 2025 |

_1 See [Pricing](https://platform.claude.com/docs/en/about-claude/pricing) for complete pricing information including Batch API discounts and prompt caching rates._

_2 **Reliable knowledge cutoff** indicates the date through which a model's knowledge is most extensive and reliable. **Training data cutoff** is the broader date range of training data used. For more information, see [Anthropic's Transparency Hub](https://www.anthropic.com/transparency)._

_3 Claude Fable 5, Claude Opus 5, and Claude Sonnet 5 are available on Bedrock through [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock) (the Messages-API Bedrock endpoint)._

### Legacy models

##   Prompt and output performance

Current Claude models excel in:

- **Performance:** Top-tier results in reasoning, coding, multilingual tasks, long-context handling, honesty, and image processing. See [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) for general and model-specific prompting guidance.

- **Engaging responses:** Claude models are ideal for applications that require rich, human-like interactions.
  - If you prefer more concise responses, you can adjust your prompts to guide the model toward the desired output length. Refer to the [prompt engineering guides](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering) for details.
  - For prompting best practices, see [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices).
- **Output quality:** When migrating from a previous model generation, you may notice larger improvements in overall performance.


##   Migrating to Claude Opus 5

If you're currently using Claude Opus 4.8 or earlier Claude models, see [Migrating to Claude Opus 5](https://platform.claude.com/docs/en/about-claude/models/migration-guide#migrating-from-claude-opus-4-8-to-claude-opus-5).

##   Get started with Claude

If you're ready to start exploring what Claude can do for you, dive in! Whether you're a developer looking to integrate Claude into your applications or a user wanting to experience the power of AI firsthand, the following resources can help.



[Intro to Claude](https://platform.claude.com/docs/en/intro)

Explore Claude's capabilities and development flow.



[Quickstart](https://platform.claude.com/docs/en/get-started)

Learn how to make your first API call in minutes.



[Claude Console](https://platform.claude.com/)

Craft and test powerful prompts directly in your browser.

If you have any questions or need assistance, don't hesitate to reach out to the [support team](https://support.claude.com/) or consult the [Discord community](https://www.anthropic.com/discord).

Was this page helpful?



Models overview/

Choosing a model

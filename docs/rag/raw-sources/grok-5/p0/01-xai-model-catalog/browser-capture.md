---
url: https://docs.x.ai/docs/models
title: "Grok Models & Pricing | SpaceXAI Docs"
description: "Compare all current Grok models: capabilities, context windows, and per-token API pricing for text, image, video, and voice."
author: "xAI"
published: "2026-08-21T00:00:00Z"
captured_at: "2026-08-23T10:57:06.186Z"
---

# Grok Models & Pricing | SpaceXAI Docs

## [Which model should I choose?](https://docs.x.ai/developers/models#which-model-should-i-choose)

Your choice depends on your use case. We have dedicated models and APIs for audio, image, and video capabilities. For everything else, including code, use Grok 4.6. It is the most intelligent and fastest model we’ve built.

## [Additional Information Regarding Models](https://docs.x.ai/developers/models#additional-information-regarding-models)

-   **No access to realtime events without search tools enabled**
    -   Grok has no knowledge of current events or data beyond what was present in its training data.
    -   To incorporate realtime data with your request, enable server-side search tools (Web Search / X Search). See [Web Search](https://docs.x.ai/developers/tools/web-search) and [X Search](https://docs.x.ai/developers/tools/x-search).
-   **Chat models**
    -   No role order limitation: You can mix `system`, `user`, or `assistant` roles in any sequence for your conversation context.
    -   `logprobs` and `top_logprobs` are not supported by models `grok-4.20` and newer. These fields will be silently ignored if set.
-   **Image input models**
    -   Maximum image size: `20MiB`
    -   Maximum number of images: No limit
    -   Supported image file types: `jpg/jpeg` or `png`.
    -   Any image/text input order is accepted (e.g. text prompt can precede image prompt)
-   **Batch API**
    -   Not every model accepts [Batch API](https://docs.x.ai/developers/advanced-api-usage/batch-api) requests. See Details on each model page.

The knowledge cut-off date of Grok 4.6 is February 1, 2026.

---

## [Model Aliases](https://docs.x.ai/developers/models#model-aliases)

Some models have aliases to help users automatically migrate to the next version of the same model. In general:

-   `<modelname>` is aliased to the latest stable version.
-   `<modelname>-latest` is aliased to the latest version. This is suitable for users who want to access the latest features.
-   `<modelname>-<date>` refers directly to a specific model release. This will not be updated and is for workflows that demand consistency.

For most users, the aliased `<modelname>` or `<modelname>-latest` are recommended, as you would receive the latest features automatically.

---

Last updated: August 21, 2026
Claude Fable 5 is Anthropic's most capable widely released model, built for the most demanding reasoning and long-horizon agentic work. Claude Mythos 5 shares the same capabilities and is available only in limited release through Project Glasswing.
The headline change for integrations: Claude Fable 5 includes safety classifiers that can decline requests. Claude Mythos 5 does not include these classifiers. If your integration calls Claude Fable 5, plan for three changes: new response handling for refusals, fallback options for retrying on another Claude model, and new billing rules. Refusals, fallback, and billing on Claude Fable 5 summarizes all three.
Models
Model API model ID Description Claude Fable 5 claude-fable-5 Anthropic's most capable widely released model, for the most demanding reasoning and long-horizon agentic work Claude Mythos 5 claude-mythos-5 Shares Claude Fable 5's capabilities without the safety classifiers. Available through Project Glasswing. Successor to Claude Mythos Preview.
Claude Fable 5 and Claude Mythos 5 share the same specs and pricing:
Context window and output: a 1M token context window by default, and up to 128k output tokens per request.
Pricing: $10 USD per million input tokens and $50 USD per million output tokens.
For specs across all current models, see the models overview.
Refusals, fallback, and billing on Claude Fable 5
Claude Fable 5 includes safety classifiers that can decline certain requests. Claude Mythos 5 does not include these classifiers, so this section applies to Claude Fable 5 only. The following sections summarize what refusals mean for your integration; each links to the full guide.
Refusals
When Claude Fable 5 declines a request, the Messages API returns stop_reason: "refusal" as a successful HTTP 200 response, not an error. The response also reports which classifier declined the request. See Refusals and fallback for response shapes and handling guidance.
Fallback
A request that Claude Fable 5 refuses can usually be served by another Claude model. There are three ways to retry:
Server-side: Pass the fallbacks parameter to have the API retry for you, using its "default" mode for Anthropic's recommended models or naming your own (in beta on the Claude API). See Server-side fallback.
Client-side: Use the SDK middleware to retry from the client on any platform. See Client-side fallback.
Manual: Build the retry yourself, on any platform and in any language. See Fallback credit.
Billing
You are not billed for a request that is refused before any output is generated. When you retry on another model, fallback credit refunds the prompt-cache cost of switching, so you avoid paying that cost twice.
Availability
Claude Fable 5 and Claude Mythos 5 both become available on June 9, 2026:
Claude Fable 5 is available on the Claude API, Amazon Bedrock, Claude Platform on AWS, Google Cloud, and Microsoft Foundry.
Claude Mythos 5 is offered only to approved customers in Project Glasswing. For access, contact your Anthropic, AWS, or Google Cloud account team. Customers without access to Claude Mythos 5 can use Claude Fable 5, which does not require access approval and offers the same capabilities.
Claude Fable 5 and Claude Mythos 5 carry 30-day data retention and are not available under zero data retention: both are designated Covered Models. See Model-specific data retention requirements.
Working with Claude Fable 5 and Claude Mythos 5
Prompting
Claude Fable 5 responds to the same prompting techniques as other Claude models, with a few differences in how to structure long-context prompts and reasoning instructions. See Prompting Claude Fable 5.
Messages API on Claude Fable 5 and Claude Mythos 5
Adaptive thinking is always on
Claude Fable 5 and Claude Mythos 5 always have thinking enabled; passing thinking: {"type": "disabled"} is not supported. To reduce or otherwise control thinking depth, use the effort parameter.
Raw thinking content is never returned
The raw chain of thought is never returned on Claude Fable 5 and Claude Mythos 5. The thinking.display setting controls what thinking blocks contain instead:
"summarized" returns thinking blocks with a readable summary of the reasoning.
"omitted" (the default) returns thinking blocks with an empty thinking field.
Pass thinking blocks back unchanged in multi-turn conversations on the same model. See thinking output on Claude Fable 5 and Claude Mythos 5 for cross-model handling.
Supported features
At launch, Claude Fable 5 and Claude Mythos 5 support:
Effort
Task budgets (beta: set the task-budgets-2026-03-13 header)
The memory tool
Code execution
Programmatic tool calling
Tool result clearing through context editing (beta: set the context-management-2025-06-27 header)
Compaction
Vision
Migrating from earlier models
Step-by-step instructions live in the migration guide:
From Claude Mythos Preview: see Migrating from Claude Mythos Preview to Claude Mythos 5.
From Claude Opus 4.8: see Migrating from Claude Opus 4.8 to Claude Fable 5.
Next steps
Migration guide
Step-by-step upgrade instructions from Claude Opus 4.8 and Claude Mythos Preview.
Models overview
Specs and comparison for all current Claude models.
Adaptive thinking
The only thinking mode on Claude Fable 5 and Claude Mythos 5.
Refusals and fallback
How Claude Fable 5 declines requests, and how to retry on another model.
Fallback credit
Avoid paying the prompt-cache cost twice on a retry.
Fallback and billing cookbook
A worked end-to-end example of refusal handling, fallback, and billing.
Effort
Control thinking depth and cost on Claude Fable 5 and Claude Mythos 5.
Prompting Claude Fable 5
Fable-specific prompting techniques.

For the complete documentation index, see llms.txt. Markdown versions of documentation pages are available by appending .md to the page URL.
Search the API docs
Search docs
Suggested
response_formatreasoning_effortstreamingtools
Primary navigation
Search docs
Suggested
response_formatreasoning_effortstreamingtools
Overview Models Agents Tools Voice & Audio Production API reference
OverviewModelsAgentsToolsVoice & AudioProductionAPI referenceDocs sectionModels
Model catalog
Choose a model
Pricing
Model selection
Text and code
Text generation
Code generation
Structured output
Prompting
Overview
Prompt engineering
Citation formatting
Migration guide
Prompt generation
Frontend prompting
Reasoning
Reasoning models
Reasoning best practices
Images and video
Images and vision
Image generation
Video generation
Realtime and audio
Audio and speech
Overview
Voice agents
Specialized models
Deep research
Embeddings
Moderation
API Dashboard
Try ChatGPT
Models
gpt-5.6-terra
GPT-5.6 Terra
Default
GPT-5.6 model that balances intelligence and cost
GPT-5.6 model that balances intelligence and cost
CompareTry in Playground
Reasoning
Higher
Speed
Fast
Price
$2•$12
Input•Output
Input
Text, image
Output
Text
GPT-5.6 Terra is designed for workloads that balance intelligence and cost. It roughly corresponds to the mini model tier used in earlier GPT-5 families. Reasoning.effort supports: none, low, medium (default), high, xhigh, and max.
1,050,000 context window
128,000 max output tokens
Feb 16, 2026 knowledge cutoff
Reasoning token support
Pricing
Pricing is based on the number of tokens used, or other metrics based on the model type. For tool-specific models, like search and computer use, there’s a fee per tool call. See details in the pricing page.
Text tokens
Per 1M tokens
Input
$2.00
Cached input
$0.20
Output
$12.00
Quick comparison
Input
Cached input
Output
GPT-5.6 Sol
$4.00
GPT-5.6 Terra
$2.00
GPT-5.4 mini
$0.75
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
v1/realtime/transcription_sessions
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
Snapshots let you lock in a specific version of the model so that performance and behavior remain consistent. Below is a list of all available snapshots and aliases for GPT-5.6 Terra.
gpt-5.6-terra
gpt-5.6-terra
gpt-5.6-terra
gpt-5.6-terra
Rate limits
Rate limits ensure fair and reliable access to the API by placing specific caps on requests, tokens, audio duration, or other usage within a given time period. Your usage tier determines how high these limits are set and automatically increases as you send more requests and spend more on the API.
Tier RPM TPM Batch queue limit Free Not supported Tier 1 500 500,000 1,500,000 Tier 2 5,000 1,000,000 3,000,000 Tier 3 5,000 2,000,000 100,000,000 Tier 4 10,000 4,000,000 200,000,000 Tier 5 15,000 40,000,000 15,000,000,000
Ask AI
Loading docs agent...

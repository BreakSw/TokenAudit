DeepSeek
DeepSeek-V4-ProOpen Weight
ReleasedApr 24 2026
DeepSeek-V4-Pro is an AI model released by DeepSeek on Friday, Apr 24 2026, 144 days after DeepSeek-V3.2. It is an open-weight model — the trained weights are available to download and run. Benchmark results (shown below) cover LiveCodeBench, BullshitBench v2, BrowseComp, GPQA Diamond, Arena Elo (Text), and Arena Elo (Code).
Available from
ProviderWho runs the model and answers the request. The same company can appear more than once here, when it serves from several regions or on more than one service tier. RegionWhere the endpoint runs. The same provider often serves the same model from several regions, and the regional ones are usually the more expensive — data residency is a product, and it is priced like one. InputWhat you pay for everything you send the model — your question, plus any documents or earlier conversation you include with it. OutputWhat you pay for the text the model writes back. It is normally the dearer half: producing an answer costs more than reading one. ContextHow much text the model can hold in mind at once — your question, any documents you attach, the conversation so far, and its own reply. Go past it and the earliest part falls out of view. PrecisionThe number format the provider runs the weights in. Lower precision (fp8, int4) is cheaper and faster to serve, but it is a compressed copy of what the lab released, so answers can differ from the original bf16 or fp16 weights. Baidu — $0.4732 $0.9464 1M fp8 StreamLake — $0.4815 $0.9629 1M fp8 DigitalOcean — $0.87 $1.74 1M — Ionstream — $1.131 $2.262 1M fp4 GMICloud — $0.792 $2.376 1M fp8 CoreWeave — $1.15 $2.55 1M fp8 DeepInfra — $1.30 $2.60 1M fp8 Alibaba — $1.416 $2.832 1M fp8 SiliconFlow — $1.5016 $3.135 1M fp8 Novita — $1.60 $3.20 1M fp8 Venice — $1.65 $3.301 1M — AtlasCloud — $1.68 $3.38 1M fp4 BaseTen — $1.74 $3.48 1M fp4 Fireworks — $1.74 $3.48 1M — Parasail — $1.74 $3.48 1M fp8 Together — $1.74 $3.48 512K — Azure us $1.91 $3.83 1M —
USD per 1M tokensEvery price here is for one million tokens. A token is roughly three-quarters of a word, so a million tokens is about 750,000 words of text.·Rates fetched from openrouter.ai on August 22, 2026. Opens the source. Checked August 22, 2026Third-party rates from openrouter.ai, not the lab’s own list price.
Benchmarks
Coding
LiveCodeBench Competitive coding — Coding problems published so recently the AI can't have seen them in training — a contamination-free test of raw programming skill. Higher is better.
93.5%
1Best published LiveCode score of all tracked models
Agentic & tool use
BrowseComp Web browsing — Can the AI browse the web and track down hard-to-find answers? Higher is better.
83.4%
11 of 17Best: Kimi K3 · 91.2%
Reasoning & science
GPQA Diamond Science — Graduate-level science questions in biology, physics, and chemistry — hard enough that subject-matter PhDs score around 65%. Higher is better.
90.1%
14 of 50Best: GPT-5.4-Pro · 94.4%
Robustness
BullshitBench v2 Nonsense detection — Given a confidently-worded but nonsensical prompt, does the AI spot that it makes no sense and push back — instead of playing along and inventing an answer? The score is how often it clearly called out the nonsense. Higher is better.
14%
54 of 67Best: Claude Opus 4.8 · 95%
Community preference
Arena Elo (Text) Community preference — Real people chat with two anonymous AIs side by side and vote for the answer they prefer. Votes become a chess-style Elo rating on arena.ai — it measures which AI people actually like, not test scores. Higher is better.
1457
32 of 32Best: Claude Fable 5 · 1509
Arena Elo (Code) Community preference (code) — Like the text arena, but people vote on which AI writes better code. The votes become a chess-style Elo rating on arena.ai. Higher is better.
1446
29 of 50Best: Kimi K3 · 1679
About
DeepSeek-V4-Pro, released April 24, 2026 alongside the lighter DeepSeek-V4-Flash, launched as DeepSeek's frontier open-weight flagship. It scored 90.1% on GPQA Diamond and 93.5% on LiveCodeBench — the best published competitive-coding score on this tracker at the time — with 83.4% on BrowseComp for agentic web research.
The V4 generation extended DeepSeek's consistent playbook: frontier-adjacent capability, open weights, and dramatically lower cost than closed rivals. At launch V4-Pro competed directly with the strongest proprietary models of spring 2026 while remaining freely downloadable, continuing the open-weights pressure the lab began with V3 and R1. DeepSeek later designated this build V4-Pro-Preview; the generation's next update, in July 2026, went to the Flash tier first, and the Pro tier was refreshed as V4-Pro-0813 in August 2026.
Compare DeepSeek-V4-Pro with
DeepSeek-V4-Pro
Suggested comparisons
DeepSeek-V4-ProvsDeepSeek-V4-Pro-0813 DeepSeek-V4-ProvsGPT-5.6 Sol DeepSeek-V4-ProvsClaude Opus 5 DeepSeek-V4-ProvsGemini 3.7 Flash DeepSeek-V4-ProvsMuse Glimmer DeepSeek-V4-ProvsGrok 4.6 DeepSeek-V4-ProvsMistral Medium 3.5 DeepSeek-V4-ProvsKimi K3 DeepSeek-V4-ProvsGLM-5.3 DeepSeek-V4-ProvsQwen3.8-27B
Frequently asked questions
When was DeepSeek-V4-Pro released?
DeepSeek-V4-Pro was released by DeepSeek on Friday, Apr 24 2026.
Who made DeepSeek-V4-Pro?
DeepSeek-V4-Pro was built by DeepSeek. Chinese AI lab known for efficient, open-weight models. Gained attention for strong performance at lower cost.
What benchmark scores did DeepSeek-V4-Pro get?
DeepSeek-V4-Pro reports 6 tracked benchmark scores — BullshitBench v2: 14%; LiveCodeBench: 93.5%; BrowseComp: 83.4%; GPQA Diamond: 90.1%; Arena Elo (Text): 1457; Arena Elo (Code): 1446. Scores are the figures published at release by DeepSeek. It holds the best score among all models tracked here on LiveCodeBench.
Is DeepSeek-V4-Pro open source?
Partly. DeepSeek-V4-Pro is an open-weight model: the trained weights are free to download and run locally or on your own infrastructure, but the training data and code are not fully released and the license may restrict some commercial uses. It is not open source in the strict sense.
What came before and after DeepSeek-V4-Pro?
DeepSeek's previous tracked release was DeepSeek-V3.2 on Dec 1 2025, 144 days earlier. It was followed by DeepSeek-V4-Flash on Apr 24 2026.
All DeepSeek releases
22 tracked
2026
4 releases
DeepSeek-V4-Pro-0813New\ \ Aug 13 2026 DeepSeek-V4-Flash-0731\ \ Jul 31 2026 DeepSeek-V4-Pro\ \ Apr 24 2026 DeepSeek-V4-Flash\ \ Apr 24 2026
2025
7 releases
DeepSeek-V3.2\ \ Dec 1 2025 DeepSeek V3.2 Exp\ \ Sep 29 2025 DeepSeek V3.1 Terminus\ \ Sep 22 2025 DeepSeek V3.1\ \ Aug 21 2025 DeepSeek R1-0528\ \ May 28 2025 DeepSeek V3-0324\ \ Mar 24 2025 DeepSeek Chat (R1-based)\ \ Jan 20 2025
2024
9 releases
DeepSeek V3 Chat\ \ Dec 26 2024 DeepSeek V3 Base\ \ Dec 25 2024 DeepSeek V2.5 (Revised)\ \ Dec 10 2024 DeepSeek-R1-Lite Preview\ \ Nov 20 2024 DeepSeek V2.5\ \ Sep 5 2024 DeepSeek Coder V2\ \ Jun 17 2024 DeepSeek V2\ \ May 6 2024 DeepSeek-Math\ \ Feb 5 2024 DeepSeek-MoE\ \ Jan 11 2024
2023
2 releases
DeepSeek-LLM\ \ Nov 29 2023 DeepSeek Coder\ \ Nov 2 2023

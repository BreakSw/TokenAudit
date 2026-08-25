---
model: "GPT-5.6 Luna"
priority: "P3"
source_id: "05-ai-souken"
title: "GPT-5.6とは？料金・性能・Sol/Terra/Lunaの使い分けを解説 | AI総合研究所"
source_url: "https://www.ai-souken.com/article/what-is-gpt-5-6"
final_url: "https://www.ai-souken.com/article/what-is-gpt-5-6"
captured_at: "2026-08-23T10:48:37.726Z"
capture_provider: "firecrawl"
accepted_for_review: true
sha256: "7cf01019a7e227fcc7fdf9d9646e8be26531107f78a8c2ad0d6cc918cfbc7a60"
---
- [ホーム](https://www.ai-souken.com/)
- サービス![](https://www.ai-souken.com/icon/arrow-icon.svg)



  - [AI Agent Hub](https://www.ai-souken.com/ai-agent-hub)
  - [Azure請求代行](https://www.ai-souken.com/business/azure/invoice-service)
  - [生成AIコンサルティング](https://www.ai-souken.com/business/consulting-generative-ai)
  - [AI活用研修](https://www.ai-souken.com/business/training)
  - [Claude Code 法人向け研修](https://www.ai-souken.com/business/claude-code-training)
  - [GitHub Copilot 法人向け研修](https://www.ai-souken.com/business/github-copilot-support)
  - [Microsoft 365 Copilot 法人向け研修](https://www.ai-souken.com/business/microsoft-365-copilot-training)

- [事例](https://www.ai-souken.com/case)
- [メソッド](https://www.ai-souken.com/article)
- [会社紹介](https://www.ai-souken.com/company-info)

[資料請求](https://www.ai-souken.com/resources) [ご相談](https://www.ai-souken.com/contact) [メルマガ登録](https://www.ai-souken.com/mail-magazine)

[![AI総合研究所](https://www.ai-souken.com/logo/logo.svg)](https://www.ai-souken.com/)

![検索フォームを開く](https://www.ai-souken.com/icon/search-icon.svg)検索 [メルマガ](https://www.ai-souken.com/mail-magazine) [資料請求](https://www.ai-souken.com/resources) [無料相談](https://www.ai-souken.com/contact)

- [![](https://www.ai-souken.com/icon/home-icon.svg)AI総合研究所のTOP](https://www.ai-souken.com/)
- [AIお役立ち情報/OpenAI](https://www.ai-souken.com/article/category/openai)
- GPT-5.6とは？料金・性能・Sol/Terra/Lunaの使い分けを解説

SHARE

[![X(twiiter)にポスト](https://www.ai-souken.com/icon/x-icon.svg)](https://www.ai-souken.com/article/what-is-gpt-5-6#) [![Facebookに投稿](https://www.ai-souken.com/icon/fb-icon3.svg)](https://www.ai-souken.com/article/what-is-gpt-5-6#) [![はてなブックマークに登録](https://www.ai-souken.com/icon/hatena-icon.svg)](https://www.ai-souken.com/article/what-is-gpt-5-6#) [![URLをコピー](https://www.ai-souken.com/icon/copy-icon.svg)](https://www.ai-souken.com/article/what-is-gpt-5-6#)

[AIお役立ち情報/OpenAI](https://www.ai-souken.com/article/category/openai)

![](https://www.ai-souken.com/icon/clock-icon2.svg)2026-07-10

# GPT-5.6とは？料金・性能・Sol/Terra/Lunaの使い分けを解説

[![facebook](https://www.ai-souken.com/icon/fb-icon.svg)](https://www.ai-souken.com/article/what-is-gpt-5-6#)[![x](https://www.ai-souken.com/icon/x-icon.svg)](https://www.ai-souken.com/article/what-is-gpt-5-6#)[![instagram](https://www.ai-souken.com/icon/insta-icon.svg)](https://www.instagram.com/)[![linked-in](https://www.ai-souken.com/icon/linkedin-icon.svg)](https://www.linkedin.com/feed/)

この記事のポイント

- ![](https://www.ai-souken.com/icon/check-icon.svg)Sol・Terra・Lunaは今後も継続する能力ティア名で、数字は世代を表す。世代番号とティア名を分離した命名は初
- ![](https://www.ai-souken.com/icon/check-icon.svg)Terraは公式ベンチマークでGPT-5.5と同等以上の性能を半額で提供。GPT-5.5利用者の第一乗り換え候補
- ![](https://www.ai-souken.com/icon/check-icon.svg)SolはSol Proと4サブエージェント並列のUltraを備え、推論エフォート（low/medium/high/xhigh/max）で深さを調整できる
- ![](https://www.ai-souken.com/icon/check-icon.svg)料金は3ティアで単純化（Sol $5/$30、Terra $2.50/$15、Luna $1/$6・per 1M tokens）、キャッシュ設計も刷新
- ![](https://www.ai-souken.com/icon/check-icon.svg)コード実装SWE-Bench ProではMythos 5・Fable 5が上位。単価×性能で選ぶモデルであり全用途最強ではない

![坂本 将磨](https://aisouken.blob.core.windows.net/background/FacePhoto/FacePhoto-1.webp)

監修者プロフィール

坂本 将磨

[![Xでフォロー](https://www.ai-souken.com/icon/x-icon.svg)フォローする](https://x.com/LinkX_group)![MicrosoftMVP](https://www.ai-souken.com/icon/MicrosoftMVP.png)

Microsoft MVP・AIパートナー。LinkX Japan株式会社 代表取締役。東京工業大学大学院にて自然言語処理・金融工学を研究。NHK放送技術研究所でAI・ブロックチェーンの研究開発に従事し、国際学会・ジャーナルでの発表多数。経営情報学会 優秀賞受賞。シンガポールでWeb3企業を創業後、現在は企業向けAI導入・DX推進を支援。

GPT-5.6シリーズは、 [OpenAI](https://www.ai-souken.com/article/openai-other) が2026年6月26日にプレビューを公開し、7月9日に一般提供を開始した新しいモデル家族です。

フラッグシップのSol、 [GPT-5.5](https://www.ai-souken.com/article/what-is-gpt-5-5) と同等以上の性能を約半額で提供するTerra、最速・最安のLunaという3ティア構成に切り替わり、ChatGPT・Codex・APIの全チャネルに展開されています。

本記事では、Sol・Terra・Lunaの位置づけと推論エフォート・Ultra/Sol Proの設定、料金体系と新プロンプトキャッシュ、主要ベンチマーク、提供チャネルとプラン別展開、セーフティ設計、 [Claude Fable 5](https://www.ai-souken.com/article/what-is-claude-fable-5) や [GPT-5.5](https://www.ai-souken.com/article/what-is-gpt-5-5) との使い分けを、2026年7月時点の最新情報で整理します。

目次

[GPT-5.6シリーズとは？OpenAIが打ち出した3ティアの設計思想](https://www.ai-souken.com/article/what-is-gpt-5-6#gpt-5.6%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA%E3%81%A8%E3%81%AF%EF%BC%9Fopenai%E3%81%8C%E6%89%93%E3%81%A1%E5%87%BA%E3%81%97%E3%81%9F3%E3%83%86%E3%82%A3%E3%82%A2%E3%81%AE%E8%A8%AD%E8%A8%88%E6%80%9D%E6%83%B3)

[Sol・Terra・Lunaという命名が持つ意味](https://www.ai-souken.com/article/what-is-gpt-5-6#sol%E3%83%BBterra%E3%83%BBluna%E3%81%A8%E3%81%84%E3%81%86%E5%91%BD%E5%90%8D%E3%81%8C%E6%8C%81%E3%81%A4%E6%84%8F%E5%91%B3)

[Sol・Terra・Lunaの位置づけと推論エフォート・Ultraの設計](https://www.ai-souken.com/article/what-is-gpt-5-6#sol%E3%83%BBterra%E3%83%BBluna%E3%81%AE%E4%BD%8D%E7%BD%AE%E3%81%A5%E3%81%91%E3%81%A8%E6%8E%A8%E8%AB%96%E3%82%A8%E3%83%95%E3%82%A9%E3%83%BC%E3%83%88%E3%83%BBultra%E3%81%AE%E8%A8%AD%E8%A8%88)

[Sol——フラッグシップとSol Pro・Sol Ultraの3段構え](https://www.ai-souken.com/article/what-is-gpt-5-6#sol%E2%80%94%E2%80%94%E3%83%95%E3%83%A9%E3%83%83%E3%82%B0%E3%82%B7%E3%83%83%E3%83%97%E3%81%A8sol-pro%E3%83%BBsol-ultra%E3%81%AE3%E6%AE%B5%E6%A7%8B%E3%81%88)

[Terra——GPT-5.5相当の性能を約半額で置き換える主力ティア](https://www.ai-souken.com/article/what-is-gpt-5-6#terra%E2%80%94%E2%80%94gpt-5.5%E7%9B%B8%E5%BD%93%E3%81%AE%E6%80%A7%E8%83%BD%E3%82%92%E7%B4%84%E5%8D%8A%E9%A1%8D%E3%81%A7%E7%BD%AE%E3%81%8D%E6%8F%9B%E3%81%88%E3%82%8B%E4%B8%BB%E5%8A%9B%E3%83%86%E3%82%A3%E3%82%A2)

[Luna——最速・最安の量産タスク向けティア](https://www.ai-souken.com/article/what-is-gpt-5-6#luna%E2%80%94%E2%80%94%E6%9C%80%E9%80%9F%E3%83%BB%E6%9C%80%E5%AE%89%E3%81%AE%E9%87%8F%E7%94%A3%E3%82%BF%E3%82%B9%E3%82%AF%E5%90%91%E3%81%91%E3%83%86%E3%82%A3%E3%82%A2)

[推論エフォートとultraモードの位置づけ](https://www.ai-souken.com/article/what-is-gpt-5-6#%E6%8E%A8%E8%AB%96%E3%82%A8%E3%83%95%E3%82%A9%E3%83%BC%E3%83%88%E3%81%A8ultra%E3%83%A2%E3%83%BC%E3%83%89%E3%81%AE%E4%BD%8D%E7%BD%AE%E3%81%A5%E3%81%91)

[GPT-5.6の料金体系](https://www.ai-souken.com/article/what-is-gpt-5-6#gpt-5.6%E3%81%AE%E6%96%99%E9%87%91%E4%BD%93%E7%B3%BB)

[3ティアのAPI単価とチャネル別提供](https://www.ai-souken.com/article/what-is-gpt-5-6#3%E3%83%86%E3%82%A3%E3%82%A2%E3%81%AEapi%E5%8D%98%E4%BE%A1%E3%81%A8%E3%83%81%E3%83%A3%E3%83%8D%E3%83%AB%E5%88%A5%E6%8F%90%E4%BE%9B)

[プロンプトキャッシュの新仕様——explicit breakpointsと30分ライフ](https://www.ai-souken.com/article/what-is-gpt-5-6#%E3%83%97%E3%83%AD%E3%83%B3%E3%83%97%E3%83%88%E3%82%AD%E3%83%A3%E3%83%83%E3%82%B7%E3%83%A5%E3%81%AE%E6%96%B0%E4%BB%95%E6%A7%98%E2%80%94%E2%80%94explicit-breakpoints%E3%81%A830%E5%88%86%E3%83%A9%E3%82%A4%E3%83%95)

[Terraへの乗り換えで見える節約幅](https://www.ai-souken.com/article/what-is-gpt-5-6#terra%E3%81%B8%E3%81%AE%E4%B9%97%E3%82%8A%E6%8F%9B%E3%81%88%E3%81%A7%E8%A6%8B%E3%81%88%E3%82%8B%E7%AF%80%E7%B4%84%E5%B9%85)

[主要ベンチマークで見るGPT-5.6の実力](https://www.ai-souken.com/article/what-is-gpt-5-6#%E4%B8%BB%E8%A6%81%E3%83%99%E3%83%B3%E3%83%81%E3%83%9E%E3%83%BC%E3%82%AF%E3%81%A7%E8%A6%8B%E3%82%8Bgpt-5.6%E3%81%AE%E5%AE%9F%E5%8A%9B)

[コーディング——Terminal-Bench 2.1でSol UltraがSOTA、SWE-Bench Proでは劣勢](https://www.ai-souken.com/article/what-is-gpt-5-6#%E3%82%B3%E3%83%BC%E3%83%87%E3%82%A3%E3%83%B3%E3%82%B0%E2%80%94%E2%80%94terminal-bench-2.1%E3%81%A7sol-ultra%E3%81%8Csota%E3%80%81swe-bench-pro%E3%81%A7%E3%81%AF%E5%8A%A3%E5%8B%A2)

[エージェント業務——Agents' Last ExamとBrowseCompの新記録](https://www.ai-souken.com/article/what-is-gpt-5-6#%E3%82%A8%E3%83%BC%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%88%E6%A5%AD%E5%8B%99%E2%80%94%E2%80%94agents'-last-exam%E3%81%A8browsecomp%E3%81%AE%E6%96%B0%E8%A8%98%E9%8C%B2)

[サイバーセキュリティ——ExploitBench・SEC-Bench ProでGPT-5.5比の大幅改善](https://www.ai-souken.com/article/what-is-gpt-5-6#%E3%82%B5%E3%82%A4%E3%83%90%E3%83%BC%E3%82%BB%E3%82%AD%E3%83%A5%E3%83%AA%E3%83%86%E3%82%A3%E2%80%94%E2%80%94exploitbench%E3%83%BBsec-bench-pro%E3%81%A7gpt-5.5%E6%AF%94%E3%81%AE%E5%A4%A7%E5%B9%85%E6%94%B9%E5%96%84)

[サイエンス——GeneBench Pro・HealthBench Professionalで前世代比の大幅向上](https://www.ai-souken.com/article/what-is-gpt-5-6#%E3%82%B5%E3%82%A4%E3%82%A8%E3%83%B3%E3%82%B9%E2%80%94%E2%80%94genebench-pro%E3%83%BBhealthbench-professional%E3%81%A7%E5%89%8D%E4%B8%96%E4%BB%A3%E6%AF%94%E3%81%AE%E5%A4%A7%E5%B9%85%E5%90%91%E4%B8%8A)

[万能ではない領域——SWE-Bench Pro・FrontierMath T4の弱点](https://www.ai-souken.com/article/what-is-gpt-5-6#%E4%B8%87%E8%83%BD%E3%81%A7%E3%81%AF%E3%81%AA%E3%81%84%E9%A0%98%E5%9F%9F%E2%80%94%E2%80%94swe-bench-pro%E3%83%BBfrontiermath-t4%E3%81%AE%E5%BC%B1%E7%82%B9)

[ChatGPT・Codex・APIでの提供チャネルとプラン別展開](https://www.ai-souken.com/article/what-is-gpt-5-6#chatgpt%E3%83%BBcodex%E3%83%BBapi%E3%81%A7%E3%81%AE%E6%8F%90%E4%BE%9B%E3%83%81%E3%83%A3%E3%83%8D%E3%83%AB%E3%81%A8%E3%83%97%E3%83%A9%E3%83%B3%E5%88%A5%E5%B1%95%E9%96%8B)

[ChatGPTとChatGPT Workのプラン別モデル展開](https://www.ai-souken.com/article/what-is-gpt-5-6#chatgpt%E3%81%A8chatgpt-work%E3%81%AE%E3%83%97%E3%83%A9%E3%83%B3%E5%88%A5%E3%83%A2%E3%83%87%E3%83%AB%E5%B1%95%E9%96%8B)

[Codexでの活用——コーディング業務での即戦力化](https://www.ai-souken.com/article/what-is-gpt-5-6#codex%E3%81%A7%E3%81%AE%E6%B4%BB%E7%94%A8%E2%80%94%E2%80%94%E3%82%B3%E3%83%BC%E3%83%87%E3%82%A3%E3%83%B3%E3%82%B0%E6%A5%AD%E5%8B%99%E3%81%A7%E3%81%AE%E5%8D%B3%E6%88%A6%E5%8A%9B%E5%8C%96)

[OpenAI APIの新機能——Programmatic Tool CallingとMulti-agent](https://www.ai-souken.com/article/what-is-gpt-5-6#openai-api%E3%81%AE%E6%96%B0%E6%A9%9F%E8%83%BD%E2%80%94%E2%80%94programmatic-tool-calling%E3%81%A8multi-agent)

[GPT-5.6のセーフティ設計とTrusted Access for Cyber](https://www.ai-souken.com/article/what-is-gpt-5-6#gpt-5.6%E3%81%AE%E3%82%BB%E3%83%BC%E3%83%95%E3%83%86%E3%82%A3%E8%A8%AD%E8%A8%88%E3%81%A8trusted-access-for-cyber)

[多層セーフガードとreasoning monitor](https://www.ai-souken.com/article/what-is-gpt-5-6#%E5%A4%9A%E5%B1%A4%E3%82%BB%E3%83%BC%E3%83%95%E3%82%AC%E3%83%BC%E3%83%89%E3%81%A8reasoning-monitor)

[サイバー10倍ブロック増と benign use への配慮](https://www.ai-souken.com/article/what-is-gpt-5-6#%E3%82%B5%E3%82%A4%E3%83%90%E3%83%BC10%E5%80%8D%E3%83%96%E3%83%AD%E3%83%83%E3%82%AF%E5%A2%97%E3%81%A8-benign-use-%E3%81%B8%E3%81%AE%E9%85%8D%E6%85%AE)

[Trusted Access for Cyber——防御業務向けの緩和ルート](https://www.ai-souken.com/article/what-is-gpt-5-6#trusted-access-for-cyber%E2%80%94%E2%80%94%E9%98%B2%E5%BE%A1%E6%A5%AD%E5%8B%99%E5%90%91%E3%81%91%E3%81%AE%E7%B7%A9%E5%92%8C%E3%83%AB%E3%83%BC%E3%83%88)

[プレビューから一般提供への段階リリース](https://www.ai-souken.com/article/what-is-gpt-5-6#%E3%83%97%E3%83%AC%E3%83%93%E3%83%A5%E3%83%BC%E3%81%8B%E3%82%89%E4%B8%80%E8%88%AC%E6%8F%90%E4%BE%9B%E3%81%B8%E3%81%AE%E6%AE%B5%E9%9A%8E%E3%83%AA%E3%83%AA%E3%83%BC%E3%82%B9)

[Claude Fable 5・Gemini 3.1・GPT-5.5との使い分け](https://www.ai-souken.com/article/what-is-gpt-5-6#claude-fable-5%E3%83%BBgemini-3.1%E3%83%BBgpt-5.5%E3%81%A8%E3%81%AE%E4%BD%BF%E3%81%84%E5%88%86%E3%81%91)

[単価×性能で見るGPT-5.6のポジション](https://www.ai-souken.com/article/what-is-gpt-5-6#%E5%8D%98%E4%BE%A1%C3%97%E6%80%A7%E8%83%BD%E3%81%A7%E8%A6%8B%E3%82%8Bgpt-5.6%E3%81%AE%E3%83%9D%E3%82%B8%E3%82%B7%E3%83%A7%E3%83%B3)

[ケース別の第一候補モデル](https://www.ai-souken.com/article/what-is-gpt-5-6#%E3%82%B1%E3%83%BC%E3%82%B9%E5%88%A5%E3%81%AE%E7%AC%AC%E4%B8%80%E5%80%99%E8%A3%9C%E3%83%A2%E3%83%87%E3%83%AB)

[モデル選定で迷いやすい3つの論点](https://www.ai-souken.com/article/what-is-gpt-5-6#%E3%83%A2%E3%83%87%E3%83%AB%E9%81%B8%E5%AE%9A%E3%81%A7%E8%BF%B7%E3%81%84%E3%82%84%E3%81%99%E3%81%843%E3%81%A4%E3%81%AE%E8%AB%96%E7%82%B9)

[GPT-5.6シリーズを業務に定着させるなら](https://www.ai-souken.com/article/what-is-gpt-5-6#gpt-5.6%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA%E3%82%92%E6%A5%AD%E5%8B%99%E3%81%AB%E5%AE%9A%E7%9D%80%E3%81%95%E3%81%9B%E3%82%8B%E3%81%AA%E3%82%89)

[まとめ](https://www.ai-souken.com/article/what-is-gpt-5-6#%E3%81%BE%E3%81%A8%E3%82%81)

## GPT-5.6シリーズとは？OpenAIが打ち出した3ティアの設計思想

![GPT-5.6シリーズとは？OpenAIが打ち出した3ティア家族の設計思想](https://aisouken.blob.core.windows.net/article/10730/GPT-5.6%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA%E3%81%A8%E3%81%AF%EF%BC%9FOpenAI%E3%81%8C%E6%89%93%E3%81%A1%E5%87%BA%E3%81%97%E3%81%9F3%E3%83%86%E3%82%A3%E3%82%A2%E5%AE%B6%E6%97%8F%E3%81%AE%E8%A8%AD%E8%A8%88%E6%80%9D%E6%83%B3.webp)

GPT-5.6シリーズは、 [OpenAI](https://www.ai-souken.com/article/openai-other) が2026年6月26日に限定プレビュー、2026年7月9日に一般提供を開始した新しいモデルファミリーです。

フラッグシップの「Sol」、GPT-5.5と同等以上の性能を約半額で提供する「Terra」、最速・最安の「Luna」という3ティアで構成されます。

これまでの「単一フラグシップ＋mini/nano派生」という命名を刷新し、 **世代番号（5.6）と能力ティア名（Sol/Terra/Luna）を独立させたファミリー名** として設計し直されている点が最大の変更です。

数字はモデル世代を、名前は3つの能力ティアを表し、それぞれのティアが独自のペースで更新されていく前提です。

### Sol・Terra・Lunaという命名が持つ意味

![Sol・Terra・Lunaという命名が持つ意味](https://aisouken.blob.core.windows.net/article/10730/Sol%E3%83%BBTerra%E3%83%BBLuna%E3%81%A8%E3%81%84%E3%81%86%E5%91%BD%E5%90%8D%E3%81%8C%E6%8C%81%E3%81%A4%E6%84%8F%E5%91%B3.webp)

Sol・Terra・Lunaは、それぞれ太陽・地球・月を指すラテン語です。

最上位のSolがフロンティア性能、Terraが日常業務の主力、Lunaが軽量・高速というポジションを、天体のスケール感で階層として表しています。

[OpenAIの公式発表](https://openai.com/index/gpt-5-6/) は、この命名について次の3点を明示しています。

- **数字は世代を表す**


5.6という番号はモデル世代を指す。次の世代でも同じSol/Terra/Lunaの並びで中身が置き換わる

- **名前は能力ティアを表す**


Sol/Terra/Lunaは「フラッグシップ」「バランス」「最安・最速」の役割そのもの。各ティアは独自のペースで進化する

- **3ティアで用途を明示する**


どのタスクにどのティアを充てるかを、モデル選定の段階で利用者が明示的に決める設計


ここでのポイントは、「GPT-5.5で全部済ませる」という単一フラグシップ運用から、 **用途ごとにティアを使い分ける運用** へと前提が切り替わったことです。

同じ業務でも、コード生成はSol、社内文書のドラフトはTerra、大量の要約バッチはLuna、というように段階的にモデルを振り分けることで、性能とコストの両立を狙う設計です。

[![AI Agent Hub1](https://aisouken.blob.core.windows.net/article/10391/AI%20Agent%20Hub1.webp)](https://www.ai-souken.com/ai-agent-hub)

* * *

## Sol・Terra・Lunaの位置づけと推論エフォート・Ultraの設計

![Sol・Terra・Lunaの位置づけと推論エフォート・Ultraの設計](https://aisouken.blob.core.windows.net/article/10730/Sol%E3%83%BBTerra%E3%83%BBLuna%E3%81%AE%E4%BD%8D%E7%BD%AE%E3%81%A5%E3%81%91%E3%81%A8%E6%8E%A8%E8%AB%96%E3%82%A8%E3%83%95%E3%82%A9%E3%83%BC%E3%83%88%E3%83%BBUltra%E3%81%AE%E8%A8%AD%E8%A8%88.webp)

GPT-5.6シリーズを実務で使い分ける鍵は、 **3つのモデルティア** と、その上に乗る\*\*推論エフォート（low〜max）およびUltra（サブエージェントモード）\*\*の2軸を同時に押さえる点にあります。

ティアで「どの規模のモデルを呼ぶか」を決め、エフォート・Ultraで「どれだけ時間と計算量を投じるか」を決める、という二段構えの選択になります。

以下の表で、3ティアの性格を整理しました。表の内容を押さえたうえで、次のセクションから各モデルの詳細と使いどころを見ていきます。

| モデル | 位置づけ | 主なターゲット業務 | 単価目安（入力/出力・per 1M） |
| --- | --- | --- | --- |
| GPT-5.6 Sol | フラッグシップ・フロンティア性能 | 長時間推論・高度コーディング・エージェント | $5 / $30 |
| GPT-5.6 Terra | 主力バランスモデル・GPT-5.5相当を約半額 | 業務文書・チャット・軽量エージェント | $2.50 / $15 |
| GPT-5.6 Luna | 最速・最安の軽量ティア | 要約・分類・高スループットのバッチ | $1 / $6 |

この表から見える設計思想は明確です。

フロンティア性能はSolに集約し、日常業務はTerraに担わせ、量産タスクはLunaで裁く—— **性能とコストの階段** を全社で共有できる形に整えています。

### Sol——フラッグシップとSol Pro・Sol Ultraの3段構え

![Sol——フラッグシップとSol Pro・Sol Ultraの3段構え](https://aisouken.blob.core.windows.net/article/10730/Sol%E2%80%94%E2%80%94%E3%83%95%E3%83%A9%E3%83%83%E3%82%B0%E3%82%B7%E3%83%83%E3%83%97%E3%81%A8Sol%20Pro%E3%83%BBSol%20Ultra%E3%81%AE3%E6%AE%B5%E6%A7%8B%E3%81%88.webp)

Solは、GPT-5.6ファミリーのフラッグシップです。

Solはコーディング・エージェント・サイエンス・サイバーセキュリティといった多くの領域で新しい業界最高水準を示しました。GPT-5.5より少ないトークン数で同等以上の結果を出せる効率改善も同時に達成しています。

Solには、標準の推論設定に加えて2つの上位モードが用意されています。

- **Sol Pro**


ChatGPT（Web版・アプリ版）のPro・Enterpriseプラン専用の最高品質モードです。複雑なタスクで最も精度の高い結果を狙う位置づけで、通常のSolでは足りないと感じたときに切り替える運用が想定されています

- **Sol Ultra**


複数のサブエージェントを並列で走らせ、結果を統合するモードです。既定では4つのサブエージェントで動作し、BrowseCompやSEC-Bench Proの評価では16並列の構成もテストされました。並列でエージェントを増やすほどスコアと所要時間の関係が改善する結果が示されており、深い調査・実装タスクの時間短縮に有効です


Solは、この「通常・Pro・Ultra」の3段構えで、標準タスクからフロンティア級の難タスクまでを一貫してカバーします。

### Terra——GPT-5.5相当の性能を約半額で置き換える主力ティア

![Terra——GPT-5.5相当の性能を約半額で置き換える主力ティア](https://aisouken.blob.core.windows.net/article/10730/Terra%E2%80%94%E2%80%94GPT-5.5%E7%9B%B8%E5%BD%93%E3%81%AE%E6%80%A7%E8%83%BD%E3%82%92%E7%B4%84%E5%8D%8A%E9%A1%8D%E3%81%A7%E7%BD%AE%E3%81%8D%E6%8F%9B%E3%81%88%E3%82%8B%E4%B8%BB%E5%8A%9B%E3%83%86%E3%82%A3%E3%82%A2.webp)

Terraは、GPT-5.5相当の性能を約半額で提供する主力モデルとして設計されています。

公式ベンチマークでは、Agents' Last ExamでTerra 50.4%（GPT-5.5は46.9%）、Terminal-Bench 2.1でTerra 87.4%（GPT-5.5は85.6%）と、Terraが世代前を軒並みやや上回っています。

単価で見ると、Terraの入力$2.50/出力$15はGPT-5.5の入力$5/出力$30から半減しました。 **同等以上の性能を半分のコストで実装できる** という設計です。

GPT-5.5をAPIで運用している企業にとっては、モデルIDを「gpt-5.6-terra」に切り替えるだけで単価表上は半減する、有力な乗り換え候補になります。

### Luna——最速・最安の量産タスク向けティア

![Luna——最速・最安の量産タスク向けティア](https://aisouken.blob.core.windows.net/article/10730/Luna%E2%80%94%E2%80%94%E6%9C%80%E9%80%9F%E3%83%BB%E6%9C%80%E5%AE%89%E3%81%AE%E9%87%8F%E7%94%A3%E3%82%BF%E3%82%B9%E3%82%AF%E5%90%91%E3%81%91%E3%83%86%E3%82%A3%E3%82%A2.webp)

Lunaは、最速・最安のティアとして、テキスト分類・要約・ドラフト生成のような量産タスク向けに設計されています。

単価は入力$1/出力$6。Terraの半額以下、GPT-5.5と比べると1/5水準です。

それでいてArtificial Analysis Coding Agent IndexではLuna 74.6を記録し、Claude Opus 4.8（72.5）を上回っています。

大量のリクエストを裁くチャットボット・議事録要約・メール分類のようなユースケースで、コストを抑えつつ実務水準の品質を確保できる位置づけです。

### 推論エフォートとultraモードの位置づけ

![推論エフォートとultraモードの位置づけ](https://aisouken.blob.core.windows.net/article/10730/%E6%8E%A8%E8%AB%96%E3%82%A8%E3%83%95%E3%82%A9%E3%83%BC%E3%83%88%E3%81%A8ultra%E3%83%A2%E3%83%BC%E3%83%89%E3%81%AE%E4%BD%8D%E7%BD%AE%E3%81%A5%E3%81%91.webp)

3ティアそれぞれに、推論の深さを切り替えるエフォート設定が用意されています。

[OpenAI開発者ドキュメント](https://developers.openai.com/api/docs/guides/latest-model) によれば、API側のreasoning.effortパラメータでは「none」／「low」／「medium」／「high」／「xhigh」／「max」の6段階が指定できます。

- **max（reasoning.effort=max）**


xhighよりもさらに時間と計算量を割き、推論の深さと選択肢の探索を伸ばす最上位エフォート。ChatGPT WorkとCodexでは全ユーザーが設定で有効化できる

- **ultra（サブエージェントモード）**


推論エフォートとは別軸の上位モード。既定で4つのサブエージェントを並列に走らせ、結果を統合する。ChatGPT WorkではPro・Enterprise、CodexではPlus以上のプランで利用でき、開発者はResponses APIのmulti-agent（ベータ）で同等の設計を自前で組める


ここでの実務ポイントは、 **「モデルティアを1つ下げる代わりにmaxを上げる」という選び方が、単純な単価計算では最適解にならないケースがある** という点です。

エフォートを上げるとトークン消費と応答時間が伸びます。Solのmax・ultraで長時間動かすより、Terraを短時間で数回呼び出す方が、トータルコストとレイテンシで有利になるケースは少なくありません。実装時は、ティアとエフォートの組み合わせを両方の軸で試算するのが安全です。

* * *

## GPT-5.6の料金体系

![GPT-5.6の料金体系と新プロンプトキャッシュ設計](https://aisouken.blob.core.windows.net/article/10730/GPT-5.6%E3%81%AE%E6%96%99%E9%87%91%E4%BD%93%E7%B3%BB%E3%81%A8%E6%96%B0%E3%83%97%E3%83%AD%E3%83%B3%E3%83%97%E3%83%88%E3%82%AD%E3%83%A3%E3%83%83%E3%82%B7%E3%83%A5%E8%A8%AD%E8%A8%88.webp)

GPT-5.6の料金は、3ティアで完全に整理されています。

同時に、プロンプトキャッシュの仕様も刷新され、長文プロンプトを繰り返し扱うワークロードでの単価が実質的に下がるようになりました。

### 3ティアのAPI単価とチャネル別提供

[OpenAI公式pricing](https://openai.com/index/gpt-5-6/) を整理すると、GPT-5.6のトークン単価は100万トークンあたり以下のとおりです。

![3ティアのAPI単価とチャネル別提供](https://aisouken.blob.core.windows.net/article/10730/3%E3%83%86%E3%82%A3%E3%82%A2%E3%81%AEAPI%E5%8D%98%E4%BE%A1%E3%81%A8%E3%83%81%E3%83%A3%E3%83%8D%E3%83%AB%E5%88%A5%E6%8F%90%E4%BE%9B.webp)

以下の表は、Sol・Terra・LunaのAPI単価と主な用途をまとめたものです。

| モデル | 入力（per 1M） | 出力（per 1M） | 主な用途 |
| --- | --- | --- | --- |
| GPT-5.6 Sol | $5 | $30 | 高度コーディング・エージェント・研究 |
| GPT-5.6 Terra | $2.50 | $15 | 業務文書・チャット・軽量エージェント |
| GPT-5.6 Luna | $1 | $6 | 要約・分類・大量バッチ |

この単価帯を [GPT-5.5](https://www.ai-souken.com/article/what-is-gpt-5-5)（入力$5/出力$30）と並べると、TerraはGPT-5.5をちょうど半減させた位置、Lunaはさらにその半分以下に位置しています。

Terraの単価がGPT-5.5をきれいに折り返している点は偶然ではなく、 **GPT-5.5利用者を無理なくTerraへ移す** ための価格設計と読み取れます。

### プロンプトキャッシュの新仕様——explicit breakpointsと30分ライフ

![プロンプトキャッシュの新仕様——explicit breakpointsと30分ライフ](https://aisouken.blob.core.windows.net/article/10730/%E3%83%97%E3%83%AD%E3%83%B3%E3%83%97%E3%83%88%E3%82%AD%E3%83%A3%E3%83%83%E3%82%B7%E3%83%A5%E3%81%AE%E6%96%B0%E4%BB%95%E6%A7%98%E2%80%94%E2%80%94explicit%20breakpoints%E3%81%A830%E5%88%86%E3%83%A9%E3%82%A4%E3%83%95.webp)

GPT-5.6と同時に、プロンプトキャッシュの仕様も刷新されました。

[公式ドキュメント](https://developers.openai.com/api/docs/guides/prompt-caching) によれば、主な変更点は次の3つです。

- **明示的なキャッシュブレークポイント**


プロンプトのどこまでをキャッシュ対象にするかを、開発者側から指定できるようになりました。これまで暗黙のキャッシュに委ねていた領域を、明示的にコントロールできます

- **30分の最小キャッシュ寿命**


一度書き込まれたキャッシュは、少なくとも30分間はヒットの対象として維持されます。バッチ処理や同一プロンプトを繰り返す運用で、キャッシュミスによる再課金を減らせます

- **書き込み1.25倍・読み込み90%割引の新料金**


GPT-5.6以降、キャッシュ書き込みはモデル入力単価の1.25倍で課金されますが、キャッシュ読み込みは引き続き90%引きです。少数回の再利用でも効果が出やすい設計と読み取れます。ただし実際の損益は、対象prefixの量・ヒット率・出力トークン量に依存します


この3点は、長文の共通コンテキスト（社内ナレッジ・仕様書・過去のやりとり）を繰り返し投入するエージェント運用で威力を発揮します。

システム側で「どこまでを共通コンテキストとして固定するか」を明示的に設計しておけば、Terra・Lunaと組み合わせることで単価をさらに引き下げられます。これが実務での使い方の基本形です。

### Terraへの乗り換えで見える節約幅

料金設計を素直に読むと、 **GPT-5.5をAPIで運用している業務ワークロードは、Terraに置き換えるだけで単価表上は半減する** 構造です。

![Terraへの乗り換えで見える節約幅](https://aisouken.blob.core.windows.net/article/10730/Terra%E3%81%B8%E3%81%AE%E4%B9%97%E3%82%8A%E6%8F%9B%E3%81%88%E3%81%A7%E8%A6%8B%E3%81%88%E3%82%8B%E7%AF%80%E7%B4%84%E5%B9%85.webp)

実行時間・出力トークン量・キャッシュヒット率がGPT-5.5の運用と大きく変わらないなら、月額APIコストがそのまま半分になる計算です。

[GPT-5.5](https://www.ai-souken.com/article/what-is-gpt-5-5) でチャットボットを月$4,000で運用している企業なら、Terraに切り替えることで単純計算で$2,000/月・年間$24,000のコスト削減余地があります。ただし推論エフォート・出力長・タスクごとの品質は代表シナリオで再評価するのが実務での前提になります。

一方で、Solのmax・ultraを常用するとトークン使用量と応答時間が伸びやすく、月額コストが跳ね上がります（キャッシュヒット率は固定prefix設計に依存するため個別検証が必要です）。

Solは「難タスクだけに集中させ、量はTerra・Lunaで裁く」——この方針で運用ルールを整えるのが、GPT-5.6世代のコスト設計の基本形です。

* * *

## 主要ベンチマークで見るGPT-5.6の実力

![主要ベンチマークで見るGPT-5.6の実力](https://aisouken.blob.core.windows.net/article/10730/%E4%B8%BB%E8%A6%81%E3%83%99%E3%83%B3%E3%83%81%E3%83%9E%E3%83%BC%E3%82%AF%E3%81%A7%E8%A6%8B%E3%82%8BGPT-5.6%E3%81%AE%E5%AE%9F%E5%8A%9B.webp)

GPT-5.6は、コーディング・エージェント・サイエンス・サイバーセキュリティの主要領域で、前世代のGPT-5.5から **パレート改善**（同じ性能を少ないトークン・低コストで、あるいは同じコストで高性能を達成）を示しています。

ただし、全用途で他社モデルを圧倒しているわけではありません。コード実装系の一部ベンチマークでは、依然としてClaudeシリーズが上位に位置しています。ここでは、各領域の代表的なベンチマークを見ていきます。

### コーディング——Terminal-Bench 2.1でSol UltraがSOTA、SWE-Bench Proでは劣勢

![コーディング——Terminal-Bench 2.1でSol UltraがSOTA、SWE-Bench Proでは劣勢](https://aisouken.blob.core.windows.net/article/10730/%E3%82%B3%E3%83%BC%E3%83%87%E3%82%A3%E3%83%B3%E3%82%B0%E2%80%94%E2%80%94Terminal-Bench%202.1%E3%81%A7Sol%20Ultra%E3%81%8CSOTA%E3%80%81SWE-Bench%20Pro%E3%81%A7%E3%81%AF%E5%8A%A3%E5%8B%A2.webp)

コーディング領域では、GPT-5.6 Solが2つの主要ベンチマークで最高水準を示しました。

![Artificial Analysis Coding Agent Indexの単価×スコアポジション](https://aisouken.blob.core.windows.net/article/10730/Artificial%20Analysis%20Coding%20Agent%20Index%E3%81%AE%E5%8D%98%E4%BE%A1%C3%97%E3%82%B9%E3%82%B3%E3%82%A2%E3%83%9D%E3%82%B8%E3%82%B7%E3%83%A7%E3%83%B3.webp)

_Artificial Analysis Coding Agent Indexの単価×スコアポジション（OpenAI公表データをもとに作成、参考： [OpenAI](https://openai.com/index/gpt-5-6/)）_

このチャートで読み取れるのは、 **GPT-5.6 Sol（濃紺）が$1,000〜$2,500の帯でスコア80近辺** に到達し、Claude Fable 5（赤茶・右上$3,700付近で77.2）を単価半分以下で上回っている構図です。TerraとLunaも同じ効率カーブに乗り、Claude Opus 4.8（オレンジ・72.5）を単価$1,000未満で追い抜いています。

以下の表は、公式に公表されたコーディング系ベンチマークの主要スコアを整理したものです。

| ベンチマーク | Sol | Sol Ultra | Terra | Luna | GPT-5.5 | Claude Fable 5 | Claude Mythos 5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Artificial Analysis Coding Agent Index v1.1 | 80 | — | 77.4 | 74.6 | 76.4 | 77.2 | — |
| SWE-Bench Pro | 64.6% | — | 63.4% | 62.7% | 59.4% | 80% | 80.3% |
| DeepSWE v1.1 | 72.7% | — | 69.6% | 67.2% | 67% | 69.7% | — |
| Terminal-Bench 2.1 | 88.8% | 91.9% | 87.4% | 84.7% | 85.6% | 83.1% | 88% |

この表が示すのは、 **Terminal-Bench 2.1のようなコマンドライン系タスクではGPT-5.6 Sol Ultraが91.9%で単独首位**、一方で **SWE-Bench Proのような実際のコードベース修正タスクでは、Claude Fable 5とMythos 5が80%前後で先行** という構図です。

つまり「コーディング=GPT-5.6が万能」という単純な結論にはなりません。

コマンドライン・長時間ツール使用系はGPT-5.6、実際のGitリポジトリ改修系は [Claude Fable 5](https://www.ai-souken.com/article/what-is-claude-fable-5) や [Claude Mythos](https://www.ai-souken.com/article/what-is-claude-mythos) が優勢—— **用途による棲み分け** が起きているのが実態です。

### エージェント業務——Agents' Last ExamとBrowseCompの新記録

![エージェント業務——Agents' Last ExamとBrowseCompの新記録](https://aisouken.blob.core.windows.net/article/10730/%E3%82%A8%E3%83%BC%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%88%E6%A5%AD%E5%8B%99%E2%80%94%E2%80%94Agents'%20Last%20Exam%E3%81%A8BrowseComp%E3%81%AE%E6%96%B0%E8%A8%98%E9%8C%B2.webp)

エージェント系のベンチマークでは、GPT-5.6の優位が数字ではっきり出ています。

![Agents' Last Examの単価×スコアポジション](https://aisouken.blob.core.windows.net/article/10730/Agents'%20Last%20Exam%E3%81%AE%E5%8D%98%E4%BE%A1%C3%97%E3%82%B9%E3%82%B3%E3%82%A2%E3%83%9D%E3%82%B8%E3%82%B7%E3%83%A7%E3%83%B3.webp)

_Agents' Last Examの単価×スコアポジション（OpenAI公表データをもとに作成、参考： [OpenAI](https://openai.com/index/gpt-5-6/)）_

Agents' Last Examのグラフでは、 **GPT-5.6の3ティア（濃紺・薄紫・水色）が左上に固まっている** のに対し、Claude Opus 4.8（オレンジ）は右側の高単価帯（$1,500〜$4,000）に伸びており、Gemini 3.1 Pro Previewは30%台前半に位置しています。GPT-5.6ファミリーが「安く高い」象限を独占している構図です。

![BrowseCompの単価×スコアポジション](https://aisouken.blob.core.windows.net/article/10730/BrowseComp%E3%81%AE%E5%8D%98%E4%BE%A1%C3%97%E3%82%B9%E3%82%B3%E3%82%A2%E3%83%9D%E3%82%B8%E3%82%B7%E3%83%A7%E3%83%B3.webp)

_BrowseCompの単価×スコアポジション（★はSol Ultra、OpenAI公表データをもとに作成、参考： [OpenAI](https://openai.com/index/gpt-5-6/)）_

BrowseCompでは、★マークで示された **Sol Ultra（92.2%）が単独首位** を取りました。GPT-5.5（濃ピンク）が同水準に到達するには単価$28超が必要で、Sol Ultraは$14以下で同じスコアに届いています。

代表的な公式スコアは以下のとおりです。

- **Agents' Last Exam**（55分野にわたる長時間業務評価）


Sol 52.7%、Terra 50.4%、Luna 50.3%、GPT-5.5 46.9%、Claude Fable 5 40.5%

- **BrowseComp**（エージェント型ブラウジング）


Sol 90.4%、Sol Ultra 92.2%、GPT-5.5 84.4%、Claude Mythos 5 88%

- **OSWorld 2.0**（コンピュータ操作）


Sol 62.6%、Terra 50.2%、GPT-5.5 47.5%、Claude Opus 4.8 54.8%


この領域では、Sol Ultraの並列サブエージェントが強く効いており、複数手順を跨ぐタスクや長時間のブラウジング作業でスコアが伸びています。

社内ナレッジ検索や横断的な業務調査といったユースケースでは、 **Sol Ultra、またはSol + max reasoning** の組み合わせが現実的な最適解になりつつあります。

### サイバーセキュリティ——ExploitBench・SEC-Bench ProでGPT-5.5比の大幅改善

![サイバーセキュリティ——ExploitBench・SEC-Bench ProでGPT-5.5比の大幅改善](https://aisouken.blob.core.windows.net/article/10730/%E3%82%B5%E3%82%A4%E3%83%90%E3%83%BC%E3%82%BB%E3%82%AD%E3%83%A5%E3%83%AA%E3%83%86%E3%82%A3%E2%80%94%E2%80%94ExploitBench%E3%83%BBSEC-Bench%20Pro%E3%81%A7GPT-5.5%E6%AF%94%E3%81%AE%E5%A4%A7%E5%B9%85%E6%94%B9%E5%96%84.webp)

サイバーセキュリティ領域では、GPT-5.5から大きな飛躍が起きています。

\*\*Claude Mythos 5（右上・単独$290付近で75%超）\*\*がフロンティア性能を示す一方、GPT-5.6 Solは$40〜$50前後の帯で70%超に届いています。GPT-5.6ファミリーはMythos 5には及ばないものの、単価が1/6程度で近い水準を出せる位置に移動してきました。

![ExploitBenchの単価×Cap percentポジション](https://aisouken.blob.core.windows.net/article/10730/ExploitBench%E3%81%AE%E5%8D%98%E4%BE%A1%C3%97Cap%20percent%E3%83%9D%E3%82%B8%E3%82%B7%E3%83%A7%E3%83%B3.webp)

_ExploitBenchの単価×Cap percentポジション（OpenAI公表データをもとに作成、参考： [OpenAI](https://openai.com/index/gpt-5-6/)）_

以下の表で、サイバー系ベンチマークの主要スコアを整理しました。

| ベンチマーク | Sol | Sol Ultra | Terra | Luna | GPT-5.5 | Claude Mythos 5 |
| --- | --- | --- | --- | --- | --- | --- |
| Capture-the-Flag Challenges | 96.7% | — | 91.8% | 85.2% | 88.1% | — |
| SEC-Bench Pro | 71.2% | 74.3% | 57.7% | 48.9% | 45.8% | — |
| CyberGym | 84.5% | — | 81.8% | 77.9% | 81.8% | 83.8% |
| ExploitBench | 73.5% | — | 52.9% | 33.2% | 47.9% | 78% |
| ExploitGym | 33.7% | — | 23.2% | 12.4% | 15.1% | — |

この表が示すのは、 **GPT-5.6 SolがGPT-5.5比で主要サイバー評価を大幅に改善した** という事実です。

特にExploitBenchでGPT-5.5の47.9%を73.5%まで押し上げ、ExploitGymでは15.1%を33.7%まで倍増させました。ここは [Claude Mythos](https://www.ai-souken.com/article/what-is-claude-mythos) が長らく先行してきた領域で、汎用モデルがようやく追いついてきた構図です。

### サイエンス——GeneBench Pro・HealthBench Professionalで前世代比の大幅向上

![サイエンス——GeneBench Pro・HealthBench Professionalで前世代比の大幅向上](https://aisouken.blob.core.windows.net/article/10730/%E3%82%B5%E3%82%A4%E3%82%A8%E3%83%B3%E3%82%B9%E2%80%94%E2%80%94GeneBench%20Pro%E3%83%BBHealthBench%20Professional%E3%81%A7%E5%89%8D%E4%B8%96%E4%BB%A3%E6%AF%94%E3%81%AE%E5%A4%A7%E5%B9%85%E5%90%91%E4%B8%8A.webp)

サイエンス領域では、GPT-5.6が全体的にGPT-5.5を大きく引き離しました。

GeneBench Proでは、 **Sol（濃紺）が単独で30%近くに到達** し、Terra（薄紫）も23%前後で続いています。GPT-5.4・5.5・Gemini 3.5 Flashなどはいずれも10%台前半にとどまっており、バイオ系の長時間タスクではGPT-5.6の優位が明確です。

![GeneBench Proの単価×スコアポジション](https://aisouken.blob.core.windows.net/article/10730/GeneBench%20Pro%E3%81%AE%E5%8D%98%E4%BE%A1%C3%97%E3%82%B9%E3%82%B3%E3%82%A2%E3%83%9D%E3%82%B8%E3%82%B7%E3%83%A7%E3%83%B3.webp)

_GeneBench Proの単価×スコアポジション（OpenAI公表データをもとに作成、参考： [OpenAI](https://openai.com/index/gpt-5-6/)）_

- **GeneBench Pro**（長時間のゲノム解析）


Sol 28.7%、Terra 23.3%、GPT-5.5 12%

- **LifeSciBench**


Sol 59.9%、Terra 56%、GPT-5.5 50.4%

- **HealthBench Professional**


Sol 60.5%、Fable 5 60.9%、GPT-5.5 49.5%

- **FrontierMath Tier 4**


Sol 83%、GPT-5.5 72.5%、Claude Fable 5 87.8%


この結果からは、 **GeneBench Pro・LifeSciBenchのようなバイオ長時間タスクではGPT-5.6 Solが強い** 一方、 **HealthBench ProfessionalではClaude Fable 5（60.9%）が僅差でSol（60.5%）を上回っている** という棲み分けが見えます。FrontierMath Tier 4もClaude Fable 5（87.8%）がSol（83%）を上回っています。

研究開発の一次スクリーニングやゲノム系の解析ではSolを主軸に据えつつ、医療リサーチや数学的な難問については別モデルも並行で評価する運用が現実的です。

### 万能ではない領域——SWE-Bench Pro・FrontierMath T4の弱点

![万能ではない領域——SWE-Bench Pro・FrontierMath T4の弱点](https://aisouken.blob.core.windows.net/article/10730/%E4%B8%87%E8%83%BD%E3%81%A7%E3%81%AF%E3%81%AA%E3%81%84%E9%A0%98%E5%9F%9F%E2%80%94%E2%80%94SWE-Bench%20Pro%E3%83%BBFrontierMath%20T4%E3%81%AE%E5%BC%B1%E7%82%B9.webp)

一連のベンチマークで見えるのは、 **GPT-5.6 Solは万能な最強モデルではない** という点です。

- **SWE-Bench Pro** では [Claude Mythos 5](https://www.ai-souken.com/article/what-is-claude-mythos)（80.3%）と [Claude Fable 5](https://www.ai-souken.com/article/what-is-claude-fable-5)（80%）がSol（64.6%）を大きく上回っています
- **FrontierMath Tier 4** ではClaude Fable 5（87.8%）がSol（83%）を上回っています
- **Toolathlon**（マルチツール連携）ではGPT-5.5（55.6%）とClaude系（60%前後）がSol（58%）と拮抗しています

Anthropic系のツールでコードベース改修フローを組んでいる場合、GPT-5.6への一律移行が最適解にならないケースがあります。

**モデル選定は「万能最強を1つ選ぶ」のではなく、業務ワークロードごとに単価×性能で振り分ける前提で組む**——GPT-5.6世代のベンチマーク結果は、この考え方を数字で裏付けています。

[![AI研修](https://aisouken.blob.core.windows.net/article/163/AI%E7%A0%94%E4%BF%AE.webp)](https://www.ai-souken.com/business/training)

* * *

## ChatGPT・Codex・APIでの提供チャネルとプラン別展開

![ChatGPT・Codex・APIでの提供チャネルとプラン別展開](https://aisouken.blob.core.windows.net/article/10730/ChatGPT%E3%83%BBCodex%E3%83%BBAPI%E3%81%A7%E3%81%AE%E6%8F%90%E4%BE%9B%E3%83%81%E3%83%A3%E3%83%8D%E3%83%AB%E3%81%A8%E3%83%97%E3%83%A9%E3%83%B3%E5%88%A5%E5%B1%95%E9%96%8B.webp)

GPT-5.6は、ChatGPT・ChatGPT Work・Codex・OpenAI APIの4チャネル全てに展開されています。

ただし、どのプランでどのモデルティア・どのエフォートまで使えるかはチャネルごとに異なります。実務で導入する際は、この対応表を最初に押さえるのが早道です。

### ChatGPTとChatGPT Workのプラン別モデル展開

![ChatGPTとChatGPT Workのプラン別モデル展開](https://aisouken.blob.core.windows.net/article/10730/ChatGPT%E3%81%A8ChatGPT%20Work%E3%81%AE%E3%83%97%E3%83%A9%E3%83%B3%E5%88%A5%E3%83%A2%E3%83%87%E3%83%AB%E5%B1%95%E9%96%8B.webp)

ChatGPT（従来の一般向けチャット）とChatGPT Work（法人向けチャット）では、プランごとの提供モデルが異なります。

以下の表で、プラン別の提供状況を整理しました。

| チャネル | プラン | 利用できるモデル・機能 |
| --- | --- | --- |
| ChatGPT | Plus / Pro / Business / Enterprise | GPT-5.6 Sol（medium以上のエフォート）。Pro・EnterpriseはSol Proも選択可 |
| ChatGPT Work | Free / Go | GPT-5.6 Terra |
| ChatGPT Work | Plus / Pro / Business / Enterprise | Sol・Terra・Lunaすべて＋エフォート設定。maxは全ユーザー、ultraはPro・Enterprise |
| Codex | Free / Go | GPT-5.6 Terra |
| Codex | Plus / Pro / Business / Enterprise | Sol・Terra・Lunaすべて＋エフォート設定。maxは全ユーザー、ultraはPlus以上 |

この表が示す通り、 **無料層でもTerraが利用でき、Plus以上に上げると3ティアとmaxを全て解放できる** 構造です。

Sol Ultraは上位プラン限定ですが、 [Codex CLI](https://www.ai-souken.com/article/codex-cli-comprehensive-guide-2025) 経由ではPlusから利用でき、開発者向けのハードルは相対的に低く設定されています。

### Codexでの活用——コーディング業務での即戦力化

![Codexでの活用——コーディング業務での即戦力化](https://aisouken.blob.core.windows.net/article/10730/Codex%E3%81%A7%E3%81%AE%E6%B4%BB%E7%94%A8%E2%80%94%E2%80%94%E3%82%B3%E3%83%BC%E3%83%87%E3%82%A3%E3%83%B3%E3%82%B0%E6%A5%AD%E5%8B%99%E3%81%A7%E3%81%AE%E5%8D%B3%E6%88%A6%E5%8A%9B%E5%8C%96.webp)

Codexでは、GPT-5.6の3ティアと推論エフォートがそのまま活用できます。

VS Codeやターミナルから [Codex CLI](https://www.ai-souken.com/article/codex-cli-comprehensive-guide-2025) で呼び出す運用に、Claude Code等の他エージェントを併用しているチームは、次の3層でモデルを分けるのが実務的です。

- **軽量な補完・修正**


Luna＋標準エフォート。行単位のリファクタリング・タイポ修正・軽量なテスト追記に使う

- **中規模の実装**


Terra＋highまたはmax。関数単位の実装・小さなバグ修正・ドキュメント整備に使う

- **難タスク・アーキテクチャ判断**


Sol＋max、またはSol Ultra。設計提案・複雑な依存関係を伴う実装・脆弱性チェックに使う


この3層をあらかじめ運用ルールとして決めておくと、開発者ごとに「常に最上位モデル」を呼ぶ運用よりも実効単価を大きく引き下げられます。

### OpenAI APIの新機能——Programmatic Tool CallingとMulti-agent

![OpenAI APIの新機能——Programmatic Tool CallingとMulti-agent](https://aisouken.blob.core.windows.net/article/10730/OpenAI%20API%E3%81%AE%E6%96%B0%E6%A9%9F%E8%83%BD%E2%80%94%E2%80%94Programmatic%20Tool%20Calling%E3%81%A8Multi-agent.webp)

APIでは、GPT-5.6と同時にResponses APIの新機能が2つ追加されました。

- **Programmatic Tool Calling**


ツール呼び出しの中間結果をモデル内でプログラムとして処理させ、必要な部分だけを残して次のステップに渡せる仕組みです。中間結果を一度APIに戻さないため、往復コストとレイテンシが下がり、ZDR（Zero Data Retention）対応でも動きます

- **Multi-agent（ベータ）**


Sol Ultraと同じ設計で、複数のサブエージェントを並列に走らせて結果を統合できます。開発者はマネージドサービスとして呼び出すだけで、Ultra相当のワークフローを自前で組む必要がなくなります


これら2つの機能は、 [OpenAI API](https://www.ai-souken.com/article/how-to-get-chatgpt-api-key) を業務システムに組み込むエンタープライズ利用で、実装コストとランタイムコストの両方を下げます。

エージェント基盤を自前で組むかマネージドで済ませるかの選択肢が広がるため、開発チーム側で「どこまで内製するか」の設計判断が改めて必要になります。

* * *

## GPT-5.6のセーフティ設計とTrusted Access for Cyber

![GPT-5.6のセーフティ設計とTrusted Access for Cyber](https://aisouken.blob.core.windows.net/article/10730/GPT-5.6%E3%81%AE%E3%82%BB%E3%83%BC%E3%83%95%E3%83%86%E3%82%A3%E8%A8%AD%E8%A8%88%E3%81%A8Trusted%20Access%20for%20Cyber.webp)

GPT-5.6は、OpenAIが「 [これまでで最も堅牢な安全対策](https://openai.com/index/gpt-5-6/)」と位置づけるセーフティスタックとともに提供されています。

サイバー・生物学の両領域で能力が上がる分、悪用リスクも比例して高まるためです。ここでは、セーフティ設計の内訳と、防御業務向けの緩和ルートである「Trusted Access for Cyber」を整理します。

### 多層セーフガードとreasoning monitor

![多層セーフガードとreasoning monitor](https://aisouken.blob.core.windows.net/article/10730/%E5%A4%9A%E5%B1%A4%E3%82%BB%E3%83%BC%E3%83%95%E3%82%AC%E3%83%BC%E3%83%89%E3%81%A8reasoning%20monitor.webp)

GPT-5.6のセーフガードは、モデル訓練層・リアルタイムチェック・継続的モニタリング・アカウント単位の統制という多層構造で組み立てられています。

公式資料は、この設計の核として **reasoning monitor** を挙げています。従来の分類器ベースのブロックに加えて、会話全体を推論モデルが監視し、「このやりとりが潜在的な害につながるか」を文脈で判断する仕組みです。

分類器だけに依存すると、単語や表現の丸暗記で回避されやすい一方、推論モデルは文脈と意図を評価できるため、ジェイルブレイクへの耐性が高まります。

同時に、推論ベースなので新しい攻撃パターンが見つかったときに、モデル本体を再訓練せずに監視ロジックを更新できる柔軟性も担保されています。

### サイバー10倍ブロック増と benign use への配慮

![サイバー10倍ブロック増とbenign useへの配慮](https://aisouken.blob.core.windows.net/article/10730/%E3%82%B5%E3%82%A4%E3%83%90%E3%83%BC10%E5%80%8D%E3%83%96%E3%83%AD%E3%83%83%E3%82%AF%E5%A2%97%E3%81%A8benign%20use%E3%81%B8%E3%81%AE%E9%85%8D%E6%85%AE.webp)

GPT-5.6 Solでは、サイバー領域の潜在的な有害活動に対するブロック挙動が、GPT-5.5に比べて約10倍に強化されています。

同時に、正当な業務利用（benign use）への配慮も明示的に組み込まれました。

- **retryオプション**


ChatGPTとCodexで、ブロックされたプロンプトを下位モデルで再試行するオプションが提供されています

- **保守的な起点からの段階緩和**


リリース初期は保守的に絞り込み、実運用の観察を通じて benign use への影響を減らす方針が公式に明言されています


これは、 [GPT-5.5-Cyber](https://www.ai-souken.com/article/what-is-gpt-5-5-cyber) の展開で得られた運用知見をGPT-5.6に持ち込んだ設計と読めます。

汎用モデルで一律に強めのブロックをかけると、防御業務やコードレビューといった正当なユースケースまで潰れやすいため、\*\*「基本は厳しく、正当利用にはretry経路を用意する」\*\*という二段構えでバランスを取っています。

### Trusted Access for Cyber——防御業務向けの緩和ルート

![Trusted Access for Cyber——防御業務向けの緩和ルート](https://aisouken.blob.core.windows.net/article/10730/Trusted%20Access%20for%20Cyber%E2%80%94%E2%80%94%E9%98%B2%E5%BE%A1%E6%A5%AD%E5%8B%99%E5%90%91%E3%81%91%E3%81%AE%E7%B7%A9%E5%92%8C%E3%83%AB%E3%83%BC%E3%83%88.webp)

サイバーセキュリティ業務では、攻撃と防御が同じ技術知識に依存するため、一律のブロックは防御側の作業も止めてしまいます。

このため、 [OpenAI Daybreak](https://openai.com/index/daybreak-securing-the-world/) の **Trusted Access for Cyber** プログラムが用意されています。

- **対象**


資格を有する個人・組織で、脆弱性トリアージ・マルウェア解析・検知エンジニアリング・パッチ検証等の防御業務に従事するチーム

- **提供内容**


検証済みの環境で、より精緻なセーフガードのもとにGPT-5.6の防御能力を活用できる

- **申請プロセス**


Daybreak経由で申請し、業務・組織の実在性を確認されたうえでアクセス権が付与される

- **個人メンバーの追加要件**


最上位のサイバー能力へアクセスを維持するには、 [Advanced Account Security](https://openai.com/index/gpt-5-6/) として、 **2026年9月1日までに** ハードウェア認証パスキー（hardware-backed passkey）の登録が必要になります。導入時は組織側で対応デバイスとロールアウト計画を先に用意しておく必要があります


ここは、 [GPT-5.5-Cyber](https://www.ai-souken.com/article/what-is-gpt-5-5-cyber) で先行して整備されてきた「防御業務専用の緩和ルート」の考え方が、GPT-5.6にも継承された形です。

汎用モデルとしてのGPT-5.6を業務に組み込みつつ、防御チームだけはTrusted Access for Cyber経由で必要な範囲の能力を引き出す——という二層運用が公式に想定されています。

### プレビューから一般提供への段階リリース

![プレビューから一般提供への段階リリース](https://aisouken.blob.core.windows.net/article/10730/%E3%83%97%E3%83%AC%E3%83%93%E3%83%A5%E3%83%BC%E3%81%8B%E3%82%89%E4%B8%80%E8%88%AC%E6%8F%90%E4%BE%9B%E3%81%B8%E3%81%AE%E6%AE%B5%E9%9A%8E%E3%83%AA%E3%83%AA%E3%83%BC%E3%82%B9.webp)

一般提供前のプレビュー段階では、米国政府の要請により、当初は小規模な信頼できるパートナー（ [APの報道](https://apnews.com/article/trump-ai-openai-gpt56-sol-cybersecurity-mythos-065d5398baac7f16c8265c2cb8ba2baa) では約20社）に限定して提供されていました。

これは、フロンティア級のバイオ・サイバー能力を持つモデルの外部リスク評価を、限定された環境で先に完了させるためです。

- **2026年6月26日**


Solを含む3モデルが限定プレビューで公開。信頼できるパートナー各社がAPIとCodex経由でアクセスを開始

- **2026年6月〜7月上旬**


第三者機関との連携によるレッドチーム・自動テストで、約70万A100e GPU時間相当の評価を実施

- **2026年7月9日**


ChatGPT・ChatGPT Work・Codex・OpenAI APIの4チャネルで一般提供が開始。当初の政府要請による制限は解除


この段階リリースは、フロンティアモデルの外部展開における新しい前例になりました。

企業側の目線で言えば、リリース直後から本番投入するのではなく、 **社内でのリスク評価と段階的な範囲拡大を組み込んだ運用** を前提に導入計画を組むのが安全です。この形は、GPT-5.6以降の世代でも標準になっていく可能性が高いと考えられます。

[![メルマガ登録](https://aisouken.blob.core.windows.net/article/00/%E3%83%A1%E3%83%AB%E3%83%9E%E3%82%AB%E3%82%99.webp)](https://www.ai-souken.com/mail-magazine)

* * *

## Claude Fable 5・Gemini 3.1・GPT-5.5との使い分け

![Claude Fable 5・Gemini 3.1・GPT-5.5との使い分けとケース別推奨](https://aisouken.blob.core.windows.net/article/10730/Claude%20Fable%205%E3%83%BBGemini%203.1%E3%83%BBGPT-5.5%E3%81%A8%E3%81%AE%E4%BD%BF%E3%81%84%E5%88%86%E3%81%91%E3%81%A8%E3%82%B1%E3%83%BC%E3%82%B9%E5%88%A5%E6%8E%A8%E5%A5%A8.webp)

GPT-5.6が全用途で最強にはならないことは、ここまでのベンチマークで確認したとおりです。

ここでは、 [公式に公表された競合比較スコア](https://openai.com/index/gpt-5-6/) を踏まえて、単価×性能のポジションと、ケース別の第一候補モデルを整理します。

### 単価×性能で見るGPT-5.6のポジション

主要フロンティアモデルの単価と代表ベンチのスコアを並べると、GPT-5.6の立ち位置がはっきり浮かび上がります。

![単価×性能で見るGPT-5.6のポジション](https://aisouken.blob.core.windows.net/article/10730/%E5%8D%98%E4%BE%A1%C3%97%E6%80%A7%E8%83%BD%E3%81%A7%E8%A6%8B%E3%82%8BGPT-5.6%E3%81%AE%E3%83%9D%E3%82%B8%E3%82%B7%E3%83%A7%E3%83%B3.webp)

以下の表は、各モデルのAPI単価と、コーディング・エージェント・サイエンスの代表ベンチをまとめたものです。

| モデル | 入力/出力（per 1M） | Coding Agent Index | Terminal-Bench 2.1 | Agents' Last Exam | SWE-Bench Pro |
| --- | --- | --- | --- | --- | --- |
| GPT-5.6 Sol | $5 / $30 | 80 | 88.8% | 52.7% | 64.6% |
| GPT-5.6 Terra | $2.50 / $15 | 77.4 | 87.4% | 50.4% | 63.4% |
| GPT-5.6 Luna | $1 / $6 | 74.6 | 84.7% | 50.3% | 62.7% |
| GPT-5.5 | $5 / $30 | 76.4 | 85.6% | 46.9% | 59.4% |
| Claude Fable 5 | 参考値 | 77.2 | 83.1% | 40.5% | 80% |
| Claude Mythos 5 | 限定提供 | — | 88% | — | 80.3% |
| Claude Opus 4.8 | 参考値 | 72.5 | 78.9% | 45.2% | 69.2% |
| Gemini 3.1 Pro Preview | 参考値 | 42.7 | 70.7% | 32.1% | 54.2% |

この表から読み取れるポイントは3つです。

まず、 **同じ$5/$30の価格帯でGPT-5.5からSolに置き換わり**、単価据え置きで性能が明確に上がりました。

次に、 **Terraが半額でGPT-5.5とほぼ同等以上のスコア** を出しており、GPT-5.5利用者にとって単価半減の乗り換え候補として位置づけられます。

そして、 **コード実装（SWE-Bench Pro）だけを見るとClaude系が上** で、この領域はClaudeを主軸に残す判断が合理的なケースが残ります。

### ケース別の第一候補モデル

![ケース別の第一候補モデル](https://aisouken.blob.core.windows.net/article/10730/%E3%82%B1%E3%83%BC%E3%82%B9%E5%88%A5%E3%81%AE%E7%AC%AC%E4%B8%80%E5%80%99%E8%A3%9C%E3%83%A2%E3%83%87%E3%83%AB.webp)

単価×性能表を業務シナリオに落とし込むと、以下のような第一候補が浮かび上がります。

- **社内チャットボット・要約・分類などの量産タスク**


Luna＋標準エフォート。最速・最安ティアとして量産タスクの第一候補になる。ただし品質は要約・分類・チャットボット等の代表タスクで検証したうえで採用する

- **業務文書ドラフト・議事録整形・軽量エージェント**


Terra＋highまたはmax。GPT-5.5からの乗り換えで実質半額。ChatGPT Workの主力モデルとして据えるのがバランス良い

- **難タスクの単発ジョブ（設計提案・調査・複雑な実装）**


Sol＋max、あるいはSol Ultra。コストは高いが、Agents' Last Exam・BrowseCompでSOTAを取っており、コスト対効果は投じる価値がある

- **既存コードベースの改修・大規模リファクタリング**

[Claude Fable 5](https://www.ai-souken.com/article/what-is-claude-fable-5) または [Claude Mythos 5](https://www.ai-souken.com/article/what-is-claude-mythos) を優先。SWE-Bench Proで80%超と、GPT-5.6 Solの64.6%を大きく上回る

- **サイバー脆弱性の防御業務**


GPT-5.6 SolをTrusted Access for Cyber経由で。ExploitBench・SEC-Bench Proで前世代比の大幅改善が見えており、防御チームの一次スクリーニングに使える

- **バイオ・ゲノム解析**


GPT-5.6 Sol。GeneBench Pro・LifeSciBenchで単独首位級のスコアで、Claude Fable 5はGeneBench Proでは未掲載（OpenAIは「高度な生物学質問への拒否が多い」と説明）のため、Solを主軸に据えるのが現実的

- **医療リサーチ**


用途で評価が分かれる領域。HealthBench ProfessionalはClaude Fable 5（60.9%）がSol（60.5%）を僅差で上回るため、実運用ではSol・Fable 5の両方を代表タスクで比較したうえで選ぶ


ここで意識したいのは、 **Sol・Terra・Lunaを社内で階層化して使い分け、Claude・Geminiは別軸のツールとして併存させる** という運用方針です。

AI総合研究所の支援経験でも、単一モデルに全業務を寄せた企業ほど、モデルの世代交代時に運用が硬直化しがちです。GPT-5.6以降の3ティア構成は、この階層化を全社の運用ルールとして共有するのに最適なタイミングを与えてくれます。

### モデル選定で迷いやすい3つの論点

![モデル選定で迷いやすい3つの論点](https://aisouken.blob.core.windows.net/article/10730/%E3%83%A2%E3%83%87%E3%83%AB%E9%81%B8%E5%AE%9A%E3%81%A7%E8%BF%B7%E3%81%84%E3%82%84%E3%81%99%E3%81%843%E3%81%A4%E3%81%AE%E8%AB%96%E7%82%B9.webp)

3ティアと競合を並べて比較すると、実務では以下の3点で判断が止まりやすくなります。

- **SolのProとUltraのどちらを選ぶか**


Sol Proは単発の高精度出力（ChatGPT上での複雑なタスク）向け、Sol Ultraは並列探索が効くタスク（BrowseCompやSEC-Bench Proのような多段調査）向け。単発の精度を最重視するならSol Pro、時間短縮と多角的な検証を求めるならSol Ultraが第一候補になる

- **TerraとGPT-5.5のどちらを主力に置くか**


公式ベンチマークではTerraがGPT-5.5をやや上回り、単価は半額。既存のGPT-5.5運用がある場合、APIのモデルIDを「gpt-5.6-terra」に切り替えると単価表上は半減する。ただし [OpenAI公式ガイド](https://developers.openai.com/api/docs/guides/latest-model) は代表タスクで品質・出力長・推論エフォートの再評価を推奨しており、モデル切替そのものよりも検証工程を組めるかが乗り換えの実務的なハードルになる

- **Claude Fable 5とGPT-5.6 Solのどちらでコード業務を回すか**


コマンドライン系タスクと全社エージェント業務はGPT-5.6 Sol、Gitリポジトリ改修のような実装タスクはClaude Fable 5、というように業務ワークロードで分けるのが現実的。両方を並行で試して、SWE-Bench Pro相当のタスクはClaude、他をGPT-5.6に寄せる運用が、現時点での一つの解になる


この3つの判断軸を運用ルールとして先に決めておくと、開発者ごとに「常に最上位を選ぶ」といったブレを防げます。

モデル選定はプロダクトの単価設計そのものに直結する意思決定なので、GPT-5.6世代からは全社の運用ガイドラインとして明文化しておく価値があります。

* * *

## GPT-5.6シリーズを業務に定着させるなら

GPT-5.6のような3ティア構成のモデルファミリーが登場したことで、「どのモデルをどの業務に振り分けるか」がAI活用の勘所に変わりました。

一方で多くの企業は、モデル選定表を眺めるだけでは動けません。 **PoCで検証すべき業務範囲・部門ごとのユースケース・全社展開時の統制やセキュリティ** まで含めて設計しないと、単価表通りのコスト効果は出てこないのが実情です。

AI総合研究所では、PoCから全社展開までの進め方、部門別のユースケース、AI運用における統制・セキュリティのチェックポイントを220ページにまとめた「AI業務自動化ガイド」を無料で公開しています。GPT-5.6世代のモデル選定を自社の業務に落とし込む第一歩として活用ください。

## GPT-5.6世代のモデル選定を業務に落とし込む

![AI業務自動化ガイド](https://aisouken.blob.core.windows.net/resource/prompt/AI%E6%A5%AD%E5%8B%99%E8%87%AA%E5%8B%95%E5%8C%96%E3%82%AB%E3%82%99%E3%82%A4%E3%83%88%E3%82%99.webp)

### PoCから全社展開までの設計を1冊で

Sol・Terra・Lunaの3ティアと推論エフォートをどう業務に振り分けるかは、モデル単体の性能表だけでは決まりません。AI業務自動化ガイド（220ページ）では、モデル選定からPoC・全社展開までの進め方、部門別のユースケース、AI運用に必要な統制・セキュリティのチェックポイントを整理しています。

[▶\\
無料でダウンロード](https://www.ai-souken.com/resources/ai-automation-guide)

* * *

## まとめ

GPT-5.6シリーズは、単一フラグシップから3ティア構成のファミリーへ設計を転換し、2026年7月9日にChatGPT・Codex・APIの全チャネルで一般提供が始まりました。

Sol・Terra・Lunaという能力ティア名は今後の世代にも受け継がれる継続的なファミリー名であり、モデル選定は「世代番号を追う」段階から「ティアと推論エフォートを組み合わせる」段階に入っています。

Terraは公式ベンチマークで [GPT-5.5](https://www.ai-souken.com/article/what-is-gpt-5-5) と同等以上を約半額で提供し、GPT-5.5運用の有力な乗り換え先になりました（ [OpenAI公式ガイド](https://developers.openai.com/api/docs/guides/latest-model) は代表タスクでの再評価を推奨）。SolはSol Pro・Sol Ultraに加えて「low」〜「max」の推論エフォートを組み合わせ、フロンティア級の難タスクをカバーします。Lunaは量産タスク向けに単価$1/$6という設定で、日常業務の主力として据えても実務水準の品質を担保できます。

料金は3ティアで単純化され、プロンプトキャッシュはexplicit breakpoints・30分ライフ・書き込み1.25倍/読み込み90%割引という新仕様に刷新されました。長文の共通コンテキストを繰り返し扱うワークロードでは、Terra・Lunaと組み合わせることで単価をさらに引き下げられます。

一方で、GPT-5.6は全用途で最強にはなりません。SWE-Bench Proでは [Claude Fable 5](https://www.ai-souken.com/article/what-is-claude-fable-5) や [Claude Mythos 5](https://www.ai-souken.com/article/what-is-claude-mythos) が引き続き優勢で、FrontierMath Tier 4もClaude Fable 5がSolを上回っています。

**GPT-5.6世代のモデル選定は、社内でSol・Terra・Lunaを階層化して使い分け、コード実装系や一部の医療・数学系はClaude、研究用途は代表タスクでClaude・Geminiも含めて比較する**——この運用設計を全社ルールとして共有するタイミングが、いま来ています。

[AI活用のノウハウ集「AI総合研究所」サービスご紹介資料\\
\\
「AI総合研究所　サービス紹介資料」は、AI導入のノウハウがないというお客様にも使いやすい最先端のAI導入ノウハウを知れる資料です。\\
\\
資料ダウンロード\\
![AI総合研究所サービス紹介資料](https://aisouken.blob.core.windows.net/resource/3/resource-aisouken-introduction.webp)](https://www.ai-souken.com/resources/aisouken-introduction-resources)

[![facebook](https://www.ai-souken.com/icon/fb-icon.svg)](https://www.ai-souken.com/article/what-is-gpt-5-6#)[![x](https://www.ai-souken.com/icon/x-icon.svg)](https://www.ai-souken.com/article/what-is-gpt-5-6#)[![instagram](https://www.ai-souken.com/icon/insta-icon.svg)](https://www.instagram.com/)[![linked-in](https://www.ai-souken.com/icon/linkedin-icon.svg)](https://www.linkedin.com/feed/)

監修者

![坂本 将磨](https://aisouken.blob.core.windows.net/background/FacePhoto/FacePhoto-1.webp)

坂本 将磨

Microsoft MVP・AIパートナー。LinkX Japan株式会社 代表取締役。東京工業大学大学院にて自然言語処理・金融工学を研究。NHK放送技術研究所でAI・ブロックチェーンの研究開発に従事し、国際学会・ジャーナルでの発表多数。経営情報学会 優秀賞受賞。シンガポールでWeb3企業を創業後、現在は企業向けAI導入・DX推進を支援。

[![facebook](https://www.ai-souken.com/icon/fb-icon.svg)](https://www.facebook.com/shoma.sakamoto.9/)[![x](https://www.ai-souken.com/icon/x-icon.svg)](https://twitter.com/LinkX_group)[![linked-in](https://www.ai-souken.com/icon/linkedin-icon.svg)](https://www.linkedin.com/in/%E5%B0%86%E7%A3%A8-%E5%9D%82%E6%9C%AC-94a861190/)

関連記事

[![GPT-5.5とは？使い方や料金、GPT-5.4との違いを解説！](https://cache-blob-images.azurewebsites.net/images?container=article&path=10663/eyecatch/10663_eyecatch.webp&width=1600&height=900)](https://www.ai-souken.com/article/what-is-gpt-5-5)

[AIお役立ち情報/OpenAI](https://www.ai-souken.com/article/category/openai)

[**GPT-5.5とは？使い方や料金、GPT-5.4との違いを解説！**](https://www.ai-souken.com/article/what-is-gpt-5-5)

![](https://www.ai-souken.com/icon/clock-icon2.svg)2026-04-27

- [![Claude Mythosとは？その性能や日本企業の動向、使い方を解説](https://cache-blob-images.azurewebsites.net/images?container=article&path=10639/eyecatch/10639_eyecatch.webp&width=800&height=450)](https://www.ai-souken.com/article/what-is-claude-mythos)
[AIお役立ち情報/Anthropic](https://www.ai-souken.com/article/category/anthropic)
[**Claude Mythosとは？その性能や日本企業の動向、使い方を解説**](https://www.ai-souken.com/article/what-is-claude-mythos)
![](https://www.ai-souken.com/icon/clock-icon.svg)2026-07-26

- [![GPT-5.5-Cyberとは？使い方・料金・Daybreak拡張による最新版を解説](https://cache-blob-images.azurewebsites.net/images?container=article&path=10729/eyecatch/10729_eyecatch.webp&width=800&height=450)](https://www.ai-souken.com/article/what-is-gpt-5-5-cyber)
[AIお役立ち情報/OpenAI](https://www.ai-souken.com/article/category/openai)
[**GPT-5.5-Cyberとは？使い方・料金・Daybreak拡張による最新版を解説**](https://www.ai-souken.com/article/what-is-gpt-5-5-cyber)
![](https://www.ai-souken.com/icon/clock-icon.svg)2026-06-26

- [![ChatGPT-5(GPT-5)とは？使い方や料金、回数制限について解説！](https://cache-blob-images.azurewebsites.net/images?container=article&path=10362/eyecatch/10362_eyecatch.webp&width=800&height=450)](https://www.ai-souken.com/article/what-is-chatgpt-5)
[AIお役立ち情報/OpenAI](https://www.ai-souken.com/article/category/openai)
[**ChatGPT-5(GPT-5)とは？使い方や料金、回数制限について解説！**](https://www.ai-souken.com/article/what-is-chatgpt-5)
![](https://www.ai-souken.com/icon/clock-icon.svg)2026-02-28


あなたにおすすめの事例

- [![](https://aisouken.blob.core.windows.net/article/20260324/%E7%99%BB%E5%A3%87%E7%9B%9B%E6%B3%81.webp)\\
\\
【登壇レポート】AI総合研究所がMicrosoft AI Tour Tokyoで発表 ― Azure OpenAI × Fabric × TeamsによるAIエージェント構築](https://www.ai-souken.com/case/ai-tour-tokyo-2026-session)
- [![](https://aisouken.blob.core.windows.net/case/489/%E8%AC%9B%E6%BC%94%E8%B3%87%E6%96%99.webp)\\
\\
  - 金融・保険\\
\\
◆スピーカーシリーズ◆中国製主要生成AIモデルの全体像【野村證券】](https://www.ai-souken.com/case/489)
- [![](https://aisouken.blob.core.windows.net/resource/prompt/GitHub.webp)\\
\\
  - IT・システム開発\\
\\
Claude Code向け日本語Skills・実務ワークフローをGitHubで公開](https://www.ai-souken.com/case/ai-souken-claude-code-japanese-workflow)

[もっと見る](https://www.ai-souken.com/case)

![](https://www.ai-souken.com/contact-back.jpg)

AI導入の最初の窓口

お悩み・課題に合わせて活用方法をご案内いたします

お気軽にお問合せください

[資料ダウンロード](https://www.ai-souken.com/resources/aisouken-introduction-resources) [お問い合わせ](https://www.ai-souken.com/contact)

[![AI総合研究所　Bottom banner](https://aisouken.blob.core.windows.net/banner/BottomBanner/627099.png)](https://www.ai-souken.com/resources/aisouken-3document)

[![](https://www.ai-souken.com/top/fv-btn-icon.svg)\\
ご相談\\
\\
お問い合わせは\\
\\
こちら！](https://www.ai-souken.com/contact)

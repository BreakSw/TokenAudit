---
model: "Qwen3-Max"
priority: "P1"
source_id: "03-qwen3-announcement"
title: "Qwen"
source_url: "https://qwen.ai/blog?id=qwen3"
final_url: "https://qwen.ai/blog?id=qwen3"
captured_at: "2026-08-23T10:55:28.552Z"
capture_provider: "firecrawl"
accepted_for_review: true
sha256: "eb9ccfab2ef0e4d3a22c5f3a12912d79712387bc8eb9c732533f9dae90fe51fa"
---
![logo](https://img.alicdn.com/imgextra/i3/O1CN01JLF4IJ1yAv1ZE7bfQ_!!6000000006539-2-tps-180-48.png)

Qwen Studio

Qwen Code

Research

API Platform

Ambassador

EN

DownloadTry Qwen Studio

Qwen3: Think Deeper, Act Faster

2025/04/28 · 48 minute · 9682 words · QwenTeam丨Translations: 简体中文

![](https://qianwen-res.oss-accelerate-overseas.aliyuncs.com/qwen3-banner.png)

QWEN CHAT

GitHub

Hugging Face

ModelScope

Kaggle

DEMO

DISCORD

## Introduction

Today, we are excited to announce the release of **Qwen3**, the latest addition to the Qwen family of large language models. Our flagship model, **Qwen3-235B-A22B**, achieves competitive results in benchmark evaluations of coding, math, general capabilities, etc., when compared to other top-tier models such as DeepSeek-R1, o1, o3-mini, Grok-3, and Gemini-2.5-Pro. Additionally, the small MoE model, **Qwen3-30B-A3B**, outcompetes QwQ-32B with 10 times of activated parameters, and even a tiny model like Qwen3-4B can rival the performance of Qwen2.5-72B-Instruct.

![](https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen3/qwen3-235a22.jpg)

![](https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen3/qwen3-30a3.jpg)

We are open-weighting two MoE models: **Qwen3-235B-A22B**, a large model with 235 billion total parameters and 22 billion activated parameters, and **Qwen3-30B-A3B**, a smaller MoE model with 30 billion total parameters and 3 billion activated parameters. Additionally, six dense models are also open-weighted, including **Qwen3-32B**, **Qwen3-14B**, **Qwen3-8B**, **Qwen3-4B**, **Qwen3-1.7B**, and **Qwen3-0.6B**, under Apache 2.0 license.

| Models | Layers | Heads (Q / KV) | Tie Embedding | Context Length |
| --- | --- | --- | --- | --- |
| Qwen3-0.6B | 28 | 16 / 8 | Yes | 32K |
| Qwen3-1.7B | 28 | 16 / 8 | Yes | 32K |
| Qwen3-4B | 36 | 32 / 8 | Yes | 32K |
| Qwen3-8B | 36 | 32 / 8 | No | 128K |
| Qwen3-14B | 40 | 40 / 8 | No | 128K |
| Qwen3-32B | 64 | 64 / 8 | No | 128K |

| Models | Layers | Heads (Q / KV) | \# Experts (Total / Activated) | Context Length |
| --- | --- | --- | --- | --- |
| Qwen3-30B-A3B | 48 | 32 / 4 | 128 / 8 | 128K |
| Qwen3-235B-A22B | 94 | 64 / 4 | 128 / 8 | 128K |

The post-trained models, such as **Qwen3-30B-A3B**, along with their pre-trained counterparts (e.g., **Qwen3-30B-A3B-Base**), are now available on platforms like **Hugging Face**, **ModelScope**, and **Kaggle**. For deployment, we recommend using frameworks like **SGLang** and **vLLM**. For local usage, tools such as **Ollama**, **LMStudio**, **MLX**, **llama.cpp**, and **KTransformers** are highly recommended. These options ensure that users can easily integrate Qwen3 into their workflows, whether in research, development, or production environments.

We believe that the release and open-sourcing of Qwen3 will significantly advance the research and development of large foundation models. Our goal is to empower researchers, developers, and organizations around the world to build innovative solutions using these cutting-edge models.

Feel free to try Qwen3 out in Qwen Chat Web ( [chat.qwen.ai](https://chat.qwen.ai/)) and mobile APP!

## Key Features

**Hybrid Thinking Modes**

Qwen3 models introduce a hybrid approach to problem-solving. They support two modes:

Thinking Mode: In this mode, the model takes time to reason step by step before delivering the final answer. This is ideal for complex problems that require deeper thought.

Non-Thinking Mode: Here, the model provides quick, near-instant responses, suitable for simpler questions where speed is more important than depth.

This flexibility allows users to control how much "thinking" the model performs based on the task at hand. For example, harder problems can be tackled with extended reasoning, while easier ones can be answered directly without delay. Crucially, the integration of these two modes greatly enhances the model's ability to implement stable and efficient thinking budget control. As demonstrated above, Qwen3 exhibits scalable and smooth performance improvements that are directly correlated with the computational reasoning budget allocated. This design enables users to configure task-specific budgets with greater ease, achieving a more optimal balance between cost efficiency and inference quality.

![](https://qianwen-res.oss-accelerate.aliyuncs.com/assets/blog/qwen3/thinking_budget.png)

**Multilingual Support**

Qwen3 models are supporting **119 languages and dialects**. This extensive multilingual capability opens up new possibilities for international applications, enabling users worldwide to benefit from the power of these models.

| Language Family | Languages & Dialects |
| --- | --- |
| Indo-European | English, French, Portuguese, German, Romanian, Swedish, Danish, Bulgarian, Russian, Czech, Greek, Ukrainian, Spanish, Dutch, Slovak, Croatian, Polish, Lithuanian, Norwegian Bokmål, Norwegian Nynorsk, Persian, Slovenian, Gujarati, Latvian, Italian, Occitan, Nepali, Marathi, Belarusian, Serbian, Luxembourgish, Venetian, Assamese, Welsh, Silesian, Asturian, Chhattisgarhi, Awadhi, Maithili, Bhojpuri, Sindhi, Irish, Faroese, Hindi, Punjabi, Bengali, Oriya, Tajik, Eastern Yiddish, Lombard, Ligurian, Sicilian, Friulian, Sardinian, Galician, Catalan, Icelandic, Tosk Albanian, Limburgish, Dari, Afrikaans, Macedonian, Sinhala, Urdu, Magahi, Bosnian, Armenian |
| Sino-Tibetan | Chinese (Simplified Chinese, Traditional Chinese, Cantonese), Burmese |
| Afro-Asiatic | Arabic (Standard, Najdi, Levantine, Egyptian, Moroccan, Mesopotamian, Ta'izzi-Adeni, Tunisian), Hebrew, Maltese |
| Austronesian | Indonesian, Malay, Tagalog, Cebuano, Javanese, Sundanese, Minangkabau, Balinese, Banjar, Pangasinan, Iloko, Waray (Philippines) |
| Dravidian | Tamil, Telugu, Kannada, Malayalam |
| Turkic | Turkish, North Azerbaijani, Northern Uzbek, Kazakh, Bashkir, Tatar |
| Tai-Kadai | Thai, Lao |
| Uralic | Finnish, Estonian, Hungarian |
| Austroasiatic | Vietnamese, Khmer |
| Other | Japanese, Korean, Georgian, Basque, Haitian, Papiamento, Kabuverdianu, Tok Pisin, Swahili |

**Improved Agentic Capabilities**

We have optimized the Qwen3 models for coding and agentic capabilities, and also we have strengthened the support of MCP as well. Below we provide examples to show how Qwen3 thinks and interacts with the environment.

00:00

/

00:00

## Pre-training

In terms of pretraining, the dataset for Qwen3 has been significantly expanded compared to Qwen2.5. While Qwen2.5 was pre-trained on 18 trillion tokens, Qwen3 uses nearly twice that amount, with approximately 36 trillion tokens covering 119 languages and dialects. To build this large dataset, we collected data not only from the web but also from PDF-like documents. We used Qwen2.5-VL to extract text from these documents and Qwen2.5 to improve the quality of the extracted content. To increase the amount of math and code data, we used Qwen2.5-Math and Qwen2.5-Coder to generate synthetic data. This includes textbooks, question-answer pairs, and code snippets.

The pre-training process consists of three stages. In the first stage (S1), the model was pretrained on over 30 trillion tokens with a context length of 4K tokens. This stage provided the model with basic language skills and general knowledge. In the second stage (S2), we improved the dataset by increasing the proportion of knowledge-intensive data, such as STEM, coding, and reasoning tasks. The model was then pretrained on an additional 5 trillion tokens. In the final stage, we used high-quality long-context data to extend the context length to 32K tokens. This ensures the model can handle longer inputs effectively.

![](https://qianwen-res.oss-accelerate-overseas.aliyuncs.com/qwen3-base.jpg)

Due to advancements in model architecture, increase in training data, and more effective training methods, the overall performance of Qwen3 dense base models matches that of Qwen2.5 base models with more parameters. For instance, Qwen3-1.7B/4B/8B/14B/32B-Base performs as well as Qwen2.5-3B/7B/14B/32B/72B-Base, respectively. Notably, in areas like STEM, coding, and reasoning, Qwen3 dense base models even outperform larger Qwen2.5 models. For Qwen3-MoE base models, they achieve similar performance to Qwen2.5 dense base models while using only 10% of the active parameters. This results in significant savings in both training and inference costs.

## Post-training

![](https://qianwen-res.oss-accelerate.aliyuncs.com/assets/blog/qwen3/post-training.png)

To develop the hybrid model capable of both step-by-step reasoning and rapid responses, we implemented a four-stage training pipeline. This pipeline includes: (1) long chain-of-thought (CoT) cold start, (2) reasoning-based reinforcement learning (RL), (3) thinking mode fusion, and (4) general RL.

In the first stage, we fine-tuned the models using diverse long CoT data, covering various tasks and domains such as mathematics, coding, logical reasoning, and STEM problems. This process aimed to equip the model with fundamental reasoning abilities. The second stage focused on scaling up computational resources for RL, utilizing rule-based rewards to enhance the model's exploration and exploitation capabilities.

In the third stage, we integrated non-thinking capabilities into the thinking model by fine-tuning it on a combination of long CoT data and commonly used instruction-tuning data. This data was generated by the enhanced thinking model from the second stage, ensuring a seamless blend of reasoning and quick response capabilities. Finally, in the fourth stage, we applied RL across more than 20 general-domain tasks to further strengthen the model’s general capabilities and correct undesired behaviors. These tasks included instruction following, format following, and agent capabilities, etc.

## Develop with Qwen3

Below is a simple guide for you to use Qwen3 on different frameworks. First of all, we provide an standard example of using Qwen3-30B-A3B in Hugging Face transformers:

python

99

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

›

⌄

⌄

⌄

from modelscope import AutoModelForCausalLM, AutoTokenizer

model\_name = "Qwen/Qwen3-30B-A3B"

\# load the tokenizer and the model

tokenizer = AutoTokenizer.from\_pretrained(model\_name)

model = AutoModelForCausalLM.from\_pretrained(

model\_name,

torch\_dtype="auto",

device\_map="auto"

)

\# prepare the model input

prompt = "Give me a short introduction to large language model."

messages = \[\
\
{"role": "user", "content": prompt}\
\
\]

text = tokenizer.apply\_chat\_template(

messages,

tokenize=False,

add\_generation\_prompt=True,

enable\_thinking=True\# Switch between thinking and non-thinking modes. Default is True.

)

model\_inputs = tokenizer(\[text\], return\_tensors="pt").to(model.device)

\# conduct text completion

generated\_ids = model.generate(

\*\*model\_inputs,

max\_new\_tokens=32768

)

output\_ids = generated\_ids\[0\]\[len(model\_inputs.input\_ids\[0\]):\].tolist()

\# parsing thinking content

try:

\# rindex finding 151668 (</think>)

index = len(output\_ids) - output\_ids\[::-1\].index(151668)

except ValueError:

index = 0

thinking\_content = tokenizer.decode(output\_ids\[:index\], skip\_special\_tokens=True).strip("\\n")

content = tokenizer.decode(output\_ids\[index:\], skip\_special\_tokens=True).strip("\\n")

print("thinking content:", thinking\_content)

print("content:", content)

To disable thinking, you just need to make changes to the argument `enable_thinking` like the following:

python

9

1

2

3

4

5

6

›

text = tokenizer.apply\_chat\_template(

messages,

tokenize=False,

add\_generation\_prompt=True,

enable\_thinking=False\# True is the default value for enable\_thinking.

)

For deployment, you can use `sglang>=0.4.6.post1` or `vllm>=0.8.4` to create an OpenAI-compatible API endpoint:

SGLang:

shell

9

1

›

python -m sglang.launch\_server --model-path Qwen/Qwen3-30B-A3B --reasoning-parser qwen3

vLLM:

shell

9

1

›

vllm serve Qwen/Qwen3-30B-A3B --enable-reasoning --reasoning-parser deepseek\_r1

If you use it for local development, you can use ollama by running a simple command `ollama run qwen3:30b-a3b` to play with the model, or you can use LMStudio or llama.cpp and ktransformers to build locally.

### Advanced Usages

We provide a soft switch mechanism that allows users to dynamically control the model's behavior when enable\_thinking=True. Specifically, you can add /think and /no\_think to user prompts or system messages to switch the model's thinking mode from turn to turn. The model will follow the most recent instruction in multi-turn conversations.

Here is an example of a multi-turn conversation:

python

99

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

47

48

49

50

›

⌄

⌄

⌄

⌄

from transformers import AutoModelForCausalLM, AutoTokenizer

classQwenChatbot:

def\_\_init\_\_(self, model\_name="Qwen/Qwen3-30B-A3B"):

self.tokenizer = AutoTokenizer.from\_pretrained(model\_name)

self.model = AutoModelForCausalLM.from\_pretrained(model\_name)

self.history = \[\]

defgenerate\_response(self, user\_input):

messages = self.history + \[{"role": "user", "content": user\_input}\]

text = self.tokenizer.apply\_chat\_template(

messages,

tokenize=False,

add\_generation\_prompt=True

)

inputs = self.tokenizer(text, return\_tensors="pt")

response\_ids = self.model.generate(\*\*inputs, max\_new\_tokens=32768)\[0\]\[len(inputs.input\_ids\[0\]):\].tolist()

response = self.tokenizer.decode(response\_ids, skip\_special\_tokens=True)

\# Update history

self.history.append({"role": "user", "content": user\_input})

self.history.append({"role": "assistant", "content": response})

return response

\# Example Usage

if \_\_name\_\_ == "\_\_main\_\_":

chatbot = QwenChatbot()

\# First input (without /think or /no\_think tags, thinking mode is enabled by default)

user\_input\_1 = "How many r's in strawberries?"

print(f"User: {user\_input\_1}")

response\_1 = chatbot.generate\_response(user\_input\_1)

print(f"Bot: {response\_1}")

print("----------------------")

\# Second input with /no\_think

user\_input\_2 = "Then, how many r's in blueberries? /no\_think"

print(f"User: {user\_input\_2}")

response\_2 = chatbot.generate\_response(user\_input\_2)

print(f"Bot: {response\_2}")

print("----------------------")

\# Third input with /think

user\_input\_3 = "Really? /think"

print(f"User: {user\_input\_3}")

response\_3 = chatbot.generate\_response(user\_input\_3)

print(f"Bot: {response\_3}")

### Agentic Usages

Qwen3 excels in tool calling capabilities. We recommend using [Qwen-Agent](https://github.com/QwenLM/Qwen-Agent) to make the best use of agentic ability of Qwen3. Qwen-Agent encapsulates tool-calling templates and tool-calling parsers internally, greatly reducing coding complexity.

To define the available tools, you can use the MCP configuration file, use the integrated tool of Qwen-Agent, or integrate other tools by yourself.

python

99

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

›

⌄

⌄

⌄

⌄

⌄

⌄

from qwen\_agent.agents import Assistant

\# Define LLM

llm\_cfg = {

'model': 'Qwen3-30B-A3B',

\# Use the endpoint provided by Alibaba Model Studio:

\# 'model\_type': 'qwen\_dashscope',

\# 'api\_key': os.getenv('DASHSCOPE\_API\_KEY'),

\# Use a custom endpoint compatible with OpenAI API:

'model\_server': 'http://localhost:8000/v1', \# api\_base

'api\_key': 'EMPTY',

\# Other parameters:

\# 'generate\_cfg': {

\# # Add: When the response content is \`<think>this is the thought</think>this is the answer;

\# # Do not add: When the response has been separated by reasoning\_content and content.

\# 'thought\_in\_content': True,

\# },

}

\# Define Tools

tools = \[\
\
{'mcpServers': { \# You can specify the MCP configuration file\
\
'time': {\
\
'command': 'uvx',\
\
'args': \['mcp-server-time', '--local-timezone=Asia/Shanghai'\]\
\
},\
\
"fetch": {\
\
"command": "uvx",\
\
"args": \["mcp-server-fetch"\]\
\
}\
\
}\
\
},\
\
'code\_interpreter', \# Built-in tools\
\
\]

\# Define Agent

bot = Assistant(llm=llm\_cfg, function\_list=tools)

\# Streaming generation

messages = \[{'role': 'user', 'content': 'https://qwenlm.github.io/blog/ Introduce the latest developments of Qwen'}\]

for responses in bot.run(messages=messages):

pass

print(responses)

## Friends of Qwen

Thanks to the support of so many friends. Qwen is nothing without its friends! We welcome more people or organizations to join our community and help us become better!

![](https://qianwen-res.oss-accelerate-overseas.aliyuncs.com/qwen3-logo.png)

## Future Work

Qwen3 represents a significant milestone in our journey toward Artificial General Intelligence (AGI) and Artificial Superintelligence (ASI). By scaling up both pretraining and reinforcement learning (RL), we have achieved higher levels of intelligence. We have seamlessly integrated thinking and non-thinking modes, offering users the flexibility to control the thinking budget. Additionally, we have expanded support for a wide range of languages, enhancing global accessibility.

Looking ahead, we aim to enhance our models across multiple dimensions. This includes refining model architectures and training methodologies to achieve several key objectives: scaling data, increasing model size, extending context length, broadening modalities, and advancing RL with environmental feedback for long-horizon reasoning. We believe we are transitioning from an era focused on training models to one centered on training agents. Our next iteration promises to bring meaningful advancements to everyone's work and life.

Try Qwen Studio

Web

iOS

Android

macOS

Windows

Qwen Studio

Qwen Studio Overview

Download

API Platform

Our Flagship Models

Platform Overview

API Platform

Qwen Cloud

Research

Latest Advancements

Research Index

GitHub

Terms & Policies

Terms of Service

Privacy Policy

Usage Policy

Cookies Notice

Training Data Summary

![](https://img.alicdn.com/imgextra/i1/O1CN01OwlzsC1cRTnZrFfXa_!!6000000003597-2-tps-150-150.png)![](https://img.alicdn.com/imgextra/i3/O1CN01LF6pFa1PE79GHDehi_!!6000000001808-2-tps-72-72.png)![](https://img.alicdn.com/imgextra/i3/O1CN01696apl1pyzhNJ40bg_!!6000000005430-2-tps-72-72.png)![](https://img.alicdn.com/imgextra/i2/O1CN01DJfj2R28G5Z6O677U_!!6000000007904-2-tps-72-72.png)![](https://img.alicdn.com/imgextra/i2/O1CN01JbyKvo1NhlYiMFJ93_!!6000000001602-2-tps-72-72.png)![](https://img.alicdn.com/imgextra/i2/O1CN01VmVMp41qYiaiS6nta_!!6000000005508-2-tps-72-72.png)![](https://img.alicdn.com/imgextra/i4/O1CN01pQADTs1WKiABLBcVE_!!6000000002770-2-tps-72-72.png)

Qwen © 2026

Manage Cookies

Powered by Alibaba Cloud

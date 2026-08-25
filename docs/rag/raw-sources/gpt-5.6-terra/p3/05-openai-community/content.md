---
model: "GPT-5.6 Terra"
priority: "P3"
source_id: "05-openai-community"
title: "GPT-5.6 Sol vs Terra: what are you seeing in real development during these first days? - Codex / Codex CLI - OpenAI Developer Community"
source_url: "https://community.openai.com/t/gpt-5-6-sol-vs-terra-what-are-you-seeing-in-real-development-during-these-first-days/1386726/6"
final_url: "https://community.openai.com/t/gpt-5-6-sol-vs-terra-what-are-you-seeing-in-real-development-during-these-first-days/1386726/6"
captured_at: "2026-08-23T10:48:23.060Z"
capture_provider: "firecrawl"
accepted_for_review: true
sha256: "895d19ac8fcff08d93e18b7cd45b0c11a45b3213a79b1b871b91222446354149"
---
[Skip to where you left off (post 6)](https://community.openai.com/t/gpt-5-6-sol-vs-terra-what-are-you-seeing-in-real-development-during-these-first-days/1386726/6) [Skip to last reply](https://community.openai.com/t/gpt-5-6-sol-vs-terra-what-are-you-seeing-in-real-development-during-these-first-days/1386726/26) [Skip to top](https://community.openai.com/t/gpt-5-6-sol-vs-terra-what-are-you-seeing-in-real-development-during-these-first-days/1386726/1)

[Skip to main content](https://community.openai.com/t/gpt-5-6-sol-vs-terra-what-are-you-seeing-in-real-development-during-these-first-days/1386726/6#main-container)

# [GPT-5.6 Sol vs Terra: what are you seeing in real development during these first days?](https://community.openai.com/t/gpt-5-6-sol-vs-terra-what-are-you-seeing-in-real-development-during-these-first-days/1386726)

[Codex](https://community.openai.com/c/codex/37) [Codex CLI](https://community.openai.com/c/codex/codex-cli/39)

- [rate-limit](https://community.openai.com/tag/rate-limit/129)

You have selected **0** posts.

[select all](https://community.openai.com/t/gpt-5-6-sol-vs-terra-what-are-you-seeing-in-real-development-during-these-first-days/1386726/6)

[cancel selecting](https://community.openai.com/t/gpt-5-6-sol-vs-terra-what-are-you-seeing-in-real-development-during-these-first-days/1386726/6)

[Jul 13](https://community.openai.com/t/gpt-5-6-sol-vs-terra-what-are-you-seeing-in-real-development-during-these-first-days/1386726/1 "Jump to the first post")

6 / 26


Jul 13


[12d ago](https://community.openai.com/t/gpt-5-6-sol-vs-terra-what-are-you-seeing-in-real-development-during-these-first-days/1386726/26)

## post by PifagorS on Jul 13

## post by PifagorS on Jul 13

## post by Tobias\_Barthold on Jul 13

## post by PifagorS on Jul 13

## post by Tobias\_Barthold on Jul 13

[![](https://sea2.discourse-cdn.com/openai1/user_avatar/community.openai.com/tobias_barthold/48/448695_2.png)](https://community.openai.com/u/tobias_barthold)

[Tobias\_Barthold](https://community.openai.com/u/tobias_barthold)

3

[Jul 13](https://community.openai.com/t/gpt-5-6-sol-vs-terra-what-are-you-seeing-in-real-development-during-these-first-days/1386726/5 "Post date")

First of all, unfortunately none of the providers I tried so far offered an experience on their 20 bucks type subscription, which they all more or less have, that can be used for real world development (as in large applications ofcourse, not saying small apps are not real projects).

You can one shot a marketing website or a small app that has limited complexity within those limits and even make it so that you actually like it.

For something like I have which goes beyond 100k lines of code by now it is completely unusable. You _will_ run into limits even with the model swapping.

The one that took the longest in that was Antigravity, because it has I think 3 separate quotas and the Flash one is near impossible to exhausat at all, but Antigravity is also extremely stupid in comparison to both Claude and Codex, at the very least on the Flash model. From my experience.

Limited complexity projects with it you may be able to get done, but if it gets remotely complex you are going to create a mess with Antigravity + Flash.

As for Documentation and Specs, I would love to tell you where exactly that threshold is, I have absolutely no clue.

I can only tell you that neither at work nor with my private yet serious projects I have ever given AI any context beyond the repositories\* itself and the task ahead. (\*had to apply a little correction, because microservices exist, so I do give context beyond the current repository, sometimes dev db access and multiple other repos)

Other people have done so and I got rid of their instructions for a good part because it was for me, context waste, because the model in almost all cases deduced the correct patterns and things to adhere to by itself or by it’s harness or control structures around it (whatever it may be in the end). I know what I want to do and I inspect what has been done at work, when I don’t like it I tell it what I don’t like and that never made problems. \*Well, little edit: Never may be a word too strong. Surely it has been a problem at some point in some context. But I don’t remember it so it probably wasn’t very upsetting.

For private projects, I am literally just having my linear board where I track issues and sometimes even brain dump stuff and let my agent organize it while maybe another agent is already working on something or just before I start going, or I type what I want straight into the chat, trying to bring across what’s up as well as possible.

One thing is for sure, the more massive your codebase, the more massive the application you want to build even if there is no massive codebase yet, the more likely you are going to experience drift, ignoring instructions, etc pp.

Because the context window is obviously still limited. When something is not in context, it’s not there.

So I don’t know about your exact case, but say for example you had a project with n lines of code, and a task completion (with accuracy aka not a broken result) requires the model to hold n tokens in its context. But the models context window is n+1 tokens, and you have specs or instructions one must adhere to _exactly_ which would push it beyond n+1 tokens will have things that get ignored.

Either that, or the task execution breaks down. Therefore, I think ( because this “phenomenon” of ignoring specs and instructions happens with Claude and other providers too ) providers generally prioritize even absolute MUST HAVE instructions lower than what is required to have a usable end result.

Anyone feel free to correct me on that. But that’s how I would do it. Why would I risk completely butchering a task instead of ignoring a couple constraints instead?

About UX:

I think we misunderstood each other, my experience about UX is exactly what you described, but it’s been better with Sol than with 5.5.

I had this with any provider though and it is expected. None of the providers has models that have image understanding that naturally makes them catch User Experience problems like for example a mobile design being too small to actually be used comfortably. Or in general a UX that just has a “bad feeling” rather than outright bugs.

It also frequently fails at seeing things overlapping each other and whatnot, and declares a UX part done unless explicitly pointed out in a screenshot or at least hinted at by asking what is wrong in this example and posting the screenshot.

Your follow up questions:

Approximately how large is the repository you are working with?

Around 150k lines of code so far.

Do you regularly provide screenshots or visual references?

For UX work? Absolutely. Obviously especially for fixing UX problems which I don’t wanna solve myself.

Does Sol have access to a running browser or any visual testing tools in your setup?

Playwright + Computer Use + Chrome Plugin. All of them, chooses depending on use case sometimes needs reminder to use something for a certain task instead of working around a problem with another tool it chose which is just a waste of time when there is one available that can do it right away.

Do you usually continue in one long session, or start fresh tasks with reduced context?

Both, depends on what I am doing. I keep going until there is a clean cutoff, where it is just completely illogical and unnecessary to keep going in the same session.

With Codex I barely noticed degradation so far with 5.6. In Claude on the other hand it is EXTREMELY obvious, the degradation.

If you ever use claude, always always always keep sessions small. If you ever reach auto compact at roughly 1 Million token context, more than once, don’t go much further in that session is my experience with that. I think the degradation is also proven in studies.

How often does Extra High spawn subagents compared with Ultra?

I mean obviously I have no exact numbers but it does spawn quite a number, mostly for research tasks or tasks that can be safely parallelized. Ultra does spawn them _always_.

5.6 Sol Ultra plays the manager it seems like.

I think 5.6 Sol Ultra is probably a good thing to try out when I get back to my Linear board. Currently I am developing a library or rather a cross-platform plugin of sorts, which I will also use in the main project. For this I am still using one and the same chat eversince I started, 20k lines into it.

## post by PifagorS on Jul 13

[![](https://avatars.discourse-cdn.com/v4/letter/p/eb8c5e/48.png)](https://community.openai.com/u/pifagors)

[PifagorS](https://community.openai.com/u/pifagors)

[Jul 13](https://community.openai.com/t/gpt-5-6-sol-vs-terra-what-are-you-seeing-in-real-development-during-these-first-days/1386726/6 "Post date")

Thanks, Tobias — your explanation makes a lot of sense, especially the distinction between the $20 tier being suitable for smaller or limited-complexity projects and Pro becoming necessary once the application grows into something much larger.

My situation is slightly different because I have been deliberately comparing several systems in parallel rather than using only one provider.

Over the last few weeks, before GPT-5.6 appeared, I was working almost exclusively with the highest GPT-5.5 configuration available to me. At the same time, I also tested Fable 5 through OpenRouter, Antigravity, Google’s Pro models, and the latest Opus model.

In many cases, I gave them exactly the same task, based on the same repository, screenshots, requirements, and expected result. Even relatively small tasks turned out to be useful comparisons because they showed very different failure patterns.

One model might produce technically clean code but misunderstand the product intent. Another might understand the visual direction but damage existing behaviour. Another could complete the task quickly, but the result would require several rounds of corrections before it became usable.

So I am not comparing them only by benchmarks, response speed, or how impressive the first answer looks. I compare how much usable work I actually receive after the entire implementation and correction cycle.

Fortunately or unfortunately, GPT is still the system I keep returning to.

Compared with Gemini Pro, the latest Opus, Antigravity, and the other systems I tested, GPT-5.5 generally gave me the best combination of contextual understanding, implementation quality, and ability to connect an isolated task with the broader product.

I completely understand that my current subscription is not really designed for the kind of sustained development I am attempting. I am based in Ukraine, and at the moment I simply cannot pay for the highest subscription tier from every provider simultaneously. That is why I test them selectively and try to understand which system genuinely gives me the highest return on the money and time invested.

But what I managed to build with GPT-5.5 genuinely changed my understanding of what one developer can create with these tools.

I built a production PWA application around a concept for which I still have not found a direct equivalent in Google Play or the App Store. I was originally inspired by an existing application that was reportedly acquired for around $10 million and is said to be generating more than $5 million per month.

However, I did not simply reproduce that application.

I reconsidered the concept from the end user’s perspective, rebuilt the interaction model, created what I consider a significantly stronger interface, and connected functionality that the original product does not provide. The result is not just a clone with a different design. It has developed into a fundamentally different product.

And most of that was built with GPT-5.5.

That experience was honestly remarkable. GPT did not merely help me work somewhat faster. It allowed me to move the product several levels beyond what I initially believed one developer could realistically design and implement.

Now, using GPT-5.6 Sol and Terra, I am working on another version that is not simply a larger update. The entire concept is evolving in a direction that, as far as I can currently see, has not yet occurred to anyone else in this product category.

So despite the quota problem I described, and despite the fact that I clearly need to rethink how much documentation I preload into the context, GPT-5.6 currently remains the strongest result in my own practical comparisons.

Your point about context waste is especially useful here. My documentation was created as accumulated failure prevention, but I can see how seven specification files, screenshots, repository context, architectural constraints, and the immediate task may compete for the same limited context window.

For my next experiment, I will probably try something closer to your workflow: let the repository communicate more of its own conventions, provide only the task-specific context that is genuinely necessary, use a cleaner session boundary, and rely more heavily on browser-based verification.

I am also beginning to agree that Pro may not simply be “more usage.” For serious development, it may change the nature of the product completely — from something you can experiment with for a few hours into something you can actually use as a daily engineering environment.

At the moment, though, I have to test that conclusion from the Plus side.

Thanks again for sharing the details of your workflow. The fact that you are successfully working with approximately 150k lines of code, Sol Extra High, visual tooling, and long sessions gives me a much more useful reference point than any benchmark.

## post by Tobias\_Barthold on Jul 13

[![](https://sea2.discourse-cdn.com/openai1/user_avatar/community.openai.com/tobias_barthold/48/448695_2.png)](https://community.openai.com/u/tobias_barthold)

[Tobias\_Barthold](https://community.openai.com/u/tobias_barthold)

1

[Jul 13](https://community.openai.com/t/gpt-5-6-sol-vs-terra-what-are-you-seeing-in-real-development-during-these-first-days/1386726/7 "Post date")

Yeah and keep in mind, specs and constraints and whatnot also mean relationships, plus moving parts, which need to be mapped.

So it’s not merely your whatever couple thousand tokens or more that you may have in specs that that needs.

I think what working with AI feels like, and how it seems to work best, is kinda this Spongebob meme, except less extreme (I don’t mean squidward throwing it away though, although I guess sometimes that happens too ![:rofl:](https://emoji.discourse-cdn.com/twitter/rofl.png?v=15)):

![](https://us1.discourse-cdn.com/openai1/original/4X/3/1/5/315b4e102ff5085cc5bb866352e586f6f1fcb587.jpeg)

[Spongebob technique #art #shorts](https://www.youtube.com/watch?v=8Wdf8Z1nNRc "Spongebob technique #art #shorts")

## post by curt.kennedy on Jul 13

[![](https://sea2.discourse-cdn.com/openai1/user_avatar/community.openai.com/curt.kennedy/48/709249_2.png)](https://community.openai.com/u/curt.kennedy)

[curt.kennedy](https://community.openai.com/u/curt.kennedy)[Moderator](https://community.openai.com/g/Community-Moderators)

[Jul 13](https://community.openai.com/t/gpt-5-6-sol-vs-terra-what-are-you-seeing-in-real-development-during-these-first-days/1386726/8 "Post date")

For long sessions you really need to look at compacting and summarization every so often to reduce your burn rate. The extra context is usually noise anyway.

Also, instead of expecting a lot from a one-shot, go for iteration and focus on one problem/feature at a time, and incremental progress, all the time compactifying or starting a new prompt on each issue.

The large info up front may be too much as well, so solving little pieces, with specific info tends to provide better quality.

This works on any repo size, even repos with millions of lines of code, as long as the repo is easily structured for regex.

## post by PifagorS on Jul 13

## post by PifagorS on Jul 13

## post by PifagorS on Jul 13

## post by curt.kennedy on Jul 13

## post by PifagorS on Jul 13

## post by Tobias\_Barthold on Jul 13

## post by PifagorS on Jul 13

## post by PifagorS on Jul 13

## post by Tobias\_Barthold on Jul 14

## post by PifagorS on Jul 14

## post by PifagorS on Jul 14

## post by Macha on Jul 14

## Load more posts below

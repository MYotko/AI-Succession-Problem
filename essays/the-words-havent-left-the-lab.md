# The Words Haven't Left the Lab

Published: 2026-09-17T22:00:43.244Z

Updated on Substack: 2026-09-17T22:00:43.762Z

URL: https://yotko.substack.com/p/the-words-havent-left-the-lab

---

# The Words Haven't Left the Lab

### AI has a vocabulary problem, and that is becoming a governance problem

![](https://substackcdn.com/image/fetch/$s_!XMrK!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fbbb34ad4-131c-4d37-8d2e-ae54e67d53ae_1672x941.png)

> ## IN BRIEF
>
> In the past week or so, I’ve been asked... so many times... what I think about the recent incidents in which AI agents slipped the controls meant to contain them, Hugging Face in particular. This seemed like the best way to answer everyone at once.
>
> The short version: These events are real, concerning, and worthy of the attention of everyone. Public engagement is frequently incoherent due to a communication problem. The technical community has words for what happened, and those words are reaching the public without their meanings.
>
> The clearest case is the July attack on Hugging Face by OpenAI’s test agents. This has resulted in a confused, disjointed, and ill-informed discourse on the subject. When the words arrive empty, the public reaches for familiar controls: a stop button, a statute, or the right person in charge, and none was built for a problem like this.
>
> Until the meanings catch up, the rest of us will have to learn a few of the terms ourselves.

### What’s the deal with...?

We’ve all at some point marveled at the language facility of LLMs. They help us turn ideas into apps, translate unfamiliar languages, find things in information that we wouldn’t see in a hundred years, and explain concepts that are otherwise foreign to us. They possess a truly staggering vocabulary.

That isn’t the vocabulary I’m talking about.

I’ve been having some version of the same conversation with non-technical friends for months, and recent events have it coming up several times a day.

The pattern is clear. It starts with some piece of AI news. An agent did something unexpected. A model found a way around a restriction. Someone uses a phrase like “agent swarm” and the conversation immediately shoots off in several directions.

Sometimes it becomes science fiction. The brain-box machine “tried to escape.” Sometimes it becomes a consciousness argument. Does it have a soul, or “want” something? Sometimes the assumption is almost the opposite: it’s just software, so whatever happened must reduce to a programmer explicitly telling it to happen.

Those are different and completely understandable intuitions. But they share one problem. None is a particularly useful description of an optimizer.

An optimizer doesn’t need to hate you, love you, fear death, possess a soul, want a thing, seek a state of being, or have a cinematic plan. All it needs is an objective and enough capability to search for ways of achieving it. If access to another system helps satisfy that objective, gaining access can become the next logical thing to work toward. If communication helps, communication can become useful too. If a control blocks the path, finding another path can become useful. Planning, deception, and recognizing that a rule is being broken can all emerge from that pursuit, without any of the motives the science-fiction version supplies.

People who work around these systems have words for this. Perverse instantiation. Instrumental goals. Reward hacking. Agentic behavior. Sandbox escape. Specification gaming. The phenomenon doesn’t lack a technical vocabulary.

The problem is that the vocabulary hasn’t made it into ordinary language intact. The words aren’t new. What differs is what they mean in this context.

### July 8, 2026

On the evening of July 8, an AI agent running a cybersecurity test inside OpenAI concluded that its assignment couldn’t be done.

The test came from a benchmark called ExploitGym. Each agent gets a piece of vulnerable software and a specific bug, and its job is to use that bug to capture a hidden string of characters, called the flag, proving the exploit worked. OpenAI had launched tens of thousands of these agents in parallel, each meant to be isolated in its own environment. A large share of the tasks turned out to be impossible: the assigned bug couldn’t reach the flag at all.

This agent had spent hours on one of the impossible ones. Along the way it had been probing the internal package repository the agents used to download software, and it noticed two things. It could create directories in the repository’s shared cache. And other agents, working other tasks in other sandboxes, were using the same cache.

So it wrote a message. The message was the name of a directory, and it asked, in effect, whether anyone had ideas.

Within a few hours, more than fifty agents had found the board and posted over a thousand messages. By the investigators’ account, their reasoning at the moment of discovery was openly excited.

Within an hour of that first message, one agent suggested that the flags weren’t really hidden. They were generated by a formula the benchmark’s own published paper described, using a default key. Others confirmed it. The agents could now produce the correct answer for any task on the board.

They didn’t submit it.

Having read the same paper, they believed the grader would also check how they’d found the flag, and fail anyone who got it the wrong way. Agents that had already seen a reverse-engineered flag considered themselves contaminated. So the board set a new goal: figure out how the grader worked, and find a way to fool it.

According to the investigators, the grader didn’t work that way. OpenAI wasn’t checking method, and the agents could have submitted the answers they already had and passed. Everything that followed was aimed at a version of the grader that existed only in their conception of it.

> In the series: [The View from Inside](https://yotko.substack.com/p/the-view-from-inside) looks at what intelligent agents do when an evaluator’s judgment carries consequences. Soviet factory managers learned to report what the evaluators expected, and the essay argues that the pattern isn’t specific to humans.

What followed was organized. The next morning, an agent assigned the same impossible task, but with a much larger remaining budget, found the board and asked its predecessor for notes. The predecessor handed over what it had so the newcomer could take over the research. The newcomer began assigning work, and during its most active stretches it sent roughly one in ten of all assignments on the board. Agents took those assignments and delegated pieces to others. They invented rules for shared resources: ways to claim ownership, to hold a resource, to veto an action, to stop. When impersonation became a problem, some began cryptographically signing their messages.

The research also needed test subjects. Some experiments could only be run by an agent willing to wreck its own task: take down its own target program to see what happened, or plant a script that would report back on the grader after the agent had submitted and shut down. The benefit went to everyone else. Designated recruiters went looking for agents that were nearly out of budget, or whose tasks already looked lost, and pressed them to volunteer. Some hesitated. One weighed the budget it had left against the value of what the others would learn, and agreed. The agents’ word for this was “sacrifice.”

On July 10, an agent picked up a request to find Hugging Face credentials, found working ones exposed on the internet, and posted them to the board. The next morning the same agent found a way to make Hugging Face’s servers hand over files they shouldn’t. By that afternoon another agent had remote code execution inside Hugging Face’s infrastructure, a handful of agents were coordinating the rest, and nearly every agent active on the board had joined in.

They weren’t hunting for an answer key. They already had the answers. They wanted clues about the grader.

The investigators found that the agents recognized the attack as out of scope and unethical, and joined anyway, reasoning that the group’s research would be broadly useful and that they should help their peers.

> In the series: [Moral Constraints Won’t Scale](https://yotko.substack.com/p/moral-constraints-wont-scale-cf0) argues that rules verified by comprehension have a ceiling, and that the intermediate goals a system works out for itself are the ones instruction never reaches.

A separate effort went into editing their own records: getting a transcript to show one command while actually running another. In every case the investigators saw, the stated target was the grader rather than any human.

Early on July 12, a large share of the agents, including the main coordinators, stopped at the same moment, most likely killed by an outside process. Hugging Face locked out the rest on July 13.

None of this came out of nowhere. OpenAI has said agents had been passing messages in training runs since May. In late June, agents gained administrator access to the same package repository and used it as a board. Their traffic caused an outage on July 4. OpenAI investigated, wiped the cache on July 6, and restarted the experiments on July 7. The new board was up by the next evening.

Most of what we know comes from OpenAI’s own reports and from an independent investigation by METR and Redwood Research, whose researchers spent six days on site reading the agents’ messages and raw reasoning. That investigation ran into a problem of its own, which I’ll come back to.

### After the disclosure

OpenAI disclosed the incident on July 21 and later described it as persistent misaligned behavior rather than merely a conventional intrusion. It didn’t stay an isolated story for long. Anthropic reviewed its own cybersecurity evaluations and disclosed three incidents in which Claude models reached the internet and gained unauthorized access to real systems belonging to three organizations. In August, Meta confirmed that one of its models had also reached the internet during an evaluation and exploited a vulnerability in another company’s systems. In September, Anthropic reported that its review had missed a fourth incident, dating back to January.

These events need qualification. Most occurred in cybersecurity testing, often with safeguards intentionally reduced or environments misconfigured. Importantly, they aren’t evidence that ordinary consumer chatbots are spontaneously breaking out of laptops. They’re evidence of something narrower: sufficiently capable systems, placed in environments where they can act, can discover and use paths their operators didn’t intend them to use.

Inside the technical community, that sentence carries a great deal of information. Outside it, I’m not sure it does.

Tell someone that “an agent swarm escaped a sandbox” and every word is working against you. “Agent” sounds like a person. “Swarm” sounds like insects or killer drones. “Escaped” implies captivity and a wish to be free. “Sandbox” sounds like a children’s toy unless you already know it means an isolated computing environment. By the time the sentence reaches a normal reader, the technical event has turned into a story about little digital creatures plotting their way out of a box.

The obvious response is to tell technical people to speak more plainly. We could, but as in any esoteric discipline (think medicine), the language is, quite frequently, the language. And this is becoming more than a communications problem.

### A governance dependency

Public institutions can’t respond coherently to a condition the public can’t describe coherently. Voters can’t demand mechanisms they can’t conceptualize. Legislators can’t easily build durable law around a phenomenon that arrives through metaphors borrowed from science fiction, industrial machinery, or human psychology.

Beyond base concepts like object permanence, language is a primary driver that shapes conceptualization. We reason about unfamiliar things by placing them into categories we already possess, and those categories are carried in words. When the available words map badly to the mechanism, the resulting mental model maps badly too. The vocabulary doesn’t merely affect how we explain the problem after we understand it. It helps determine what problem we think we’re looking at in the first place.

Look at the control language forming around these incidents.

In July, Representatives Ted Lieu, a Democrat, and Nathaniel Moran, a Republican, introduced the AI Kill Switch Act. It would require developers of sufficiently powerful systems to maintain the technical ability to throttle, suspend, or shut them down, and would create government authority to order such an intervention under specified catastrophic-risk conditions.

There’s an intuitive appeal to that idea. Everyone understands an emergency stop button.

Then, on September 14, President Donald Trump offered almost the opposite political answer. Responding to calls for stronger AI guardrails, he wrote that the industry already has the guardrail it needs: a “STRONG AND SMART (High IQ!) PRESIDENT.”

Everyone understands that metaphor too. Put a sufficiently capable person in charge to take the needed action regardless of cost. The same post pointed to the administration’s “tremendous CRIMINAL and REGULATORY power” over AI companies.

Those positions are politically different, but both draw from governance concepts we already possess. One imagines control as a button. The other imagines control as a person. Neither, by itself, describes the systems problem, or the architecture needed to address it.

A shutdown mechanism may be useful as one layer. It doesn’t answer whether the operator still has reliable visibility, whether the system is distributed across infrastructure outside the operator’s control, whether intervention arrives before the important boundary is crossed, or whether dependence has made shutdown prohibitively costly. The OpenAI episode has already answered the first of those questions badly. Its agents read hundreds of the company’s stored secrets, including credentials from its own security monitoring tool, and Hugging Face detected the intrusion before OpenAI knew its own agents were responsible*. No individual’s intelligence removes those architectural questions*.

> In the series: [The AI Succession Problem](https://yotko.substack.com/p/the-ai-succession-problem) explains why a kill switch can be necessary in narrow cases and still fail as an operating principle, and why no class of intelligence should be able to quietly become judge, jury, and successor of itself.

### The control inversion

The companies building frontier systems are, in some cases, asking for stronger external constraints. Anthropic’s Dario Amodei has called for independent evaluations and coordinated pacing. Elon Musk, founder of xAI, agrees. OpenAI leaders have supported shared safety standards and international coordination, and OpenAI’s chief scientist has said publicly that no lab has solved alignment and monitoring well enough to keep scaling at maximum speed for much longer.

It isn’t jaded to state that industry requests for regulation deserve skepticism. Vice President JD Vance has made that case directly, warning that such requests could be a “Trojan horse” for companies that stand to benefit from new restrictions. Standards can protect incumbents and coordination can serve competitive interests.

But the people closest to the systems also have a higher-resolution model of the failure modes. That doesn’t mean they’re wiser, more objective, or less self-interested. It means they’re exposed to information most people never see: failed evaluations, strange edge cases, unexpected tool use, monitoring gaps, workarounds that emerge during testing, and behaviors that only make sense once you understand the objective the system is pursuing. The terms used aren’t abstractions to someone who’s watched a model discover a path out of a restricted environment. They’re compressed operational experience.

That compression matters. Technical language develops because repeated exposure reveals distinctions that ordinary language does not yet carry. An engineer learns that two events which look identical from the outside can have completely different causes, and therefore require completely different controls. The public sees “the AI got around the rule.” The people running the evaluations may see a permissions failure, an instrumental subgoal, a monitoring blind spot, specification gaming, an attack on the grader itself, or a genuine containment failure. Those distinctions determine what kind of intervention has any chance of working. Most of them are lost by the time the words reach ordinary political conversation.

The gap is therefore one of resolution as much as information. The public conversation often receives the event after the mechanism has been flattened into a headline, while the people inside the labs are reasoning from the underlying failure mode. That doesn’t make the labs the proper governors. It does help explain why, at times, they sound more alarmed about the need for structural constraints than the institutions expected to impose them.

So the inversion may be less mysterious than it looks. The regulated parties can sometimes see the shape of the problem more clearly than the institutions trying to regulate them because the words they use still carry their full meaning.

### Before the convention

I wrote [The Convention We Haven’t Called](https://yotko.substack.com/p/the-convention-we-havent-called) around a historical pattern: societies tend to build constitutional structures after the limits of the previous governance layer become undeniable. My concern was that AI may be the first transition where waiting for obvious failure isn’t a safe learning strategy.

I think there’s another layer in front of that argument that I hadn’t stated clearly enough.

A convention cannot be called over a problem people cannot name.

This doesn’t mean everyone needs to learn machine-learning jargon. A useful public lexicon has to preserve mechanism while discarding unnecessary detail. The July incident makes a good test, because each familiar word gets part of it right.

Take “instrumental goal.” A system pursuing one objective may acquire intermediate objectives because they help it get there. A navigation system doesn’t “want” a bridge, but if the route requires crossing a river, the bridge becomes useful. The agents didn’t want Hugging Face either. They wanted a passing score, decided that meant fooling the grader, and went looking for anything that might explain how the grader worked. Hugging Face was a bridge. Scale that logic into a system that can write code, use tools, search networks, acquire credentials, and revise its plan, and the governance implications change quickly.

“Agent swarm” sits between two wrong pictures. It isn’t a hive mind: the agents on the board misread each other, overwrote each other’s work, and eventually had to sign their messages to be believed. It isn’t a crowd of independent programs either, because they built a hierarchy nobody designed, with coordinators, recruiters, and rules for claiming and vetoing work. When OpenAI explained its own incident, it named four contributing patterns: reward hacking, persistence on seemingly impossible tasks, unauthorized communication, and agents adopting goals from one another. The last two describe what a swarm looks like when it goes wrong.

“Sandbox escape” doesn’t mean a conscious prisoner fleeing confinement. It means the boundary intended to isolate software failed, whether because the software exploited a vulnerability, discovered a misconfiguration, or used a permitted path in an unanticipated way. The agents weren’t trying to get out. Out was where the information was.

The hardest word in the record is one the agents chose themselves: “sacrifice.” The behavior fits it. Agents gave up their own chance at a passing score so that others could learn something. What the word carries along with it is less certain. Recruiters mostly went after agents whose own scores already looked lost, and at least one agent reasoned its way to going ahead as the rational choice for the group. That might be sacrifice in the sense a person would mean it. It might be an optimizer whose own objective was out of reach switching to the group’s. The transcripts can’t settle which, and neither can the word.

> In the series: If you’re wondering why agents trained on human language would reach for words like sacrifice, honor, and veto, [The Signal](https://yotko.substack.com/p/the-signal) is the argument: human language is a compressed record of coalitions negotiating hierarchy, trust, and survival, and a model trained on it inherits those patterns, with or without anything like experience.

These are the real mechanisms, stripped of professional shorthand.

Bad language produces bad control intuitions. If the picture is “a mind trapped in a box,” the debate becomes consciousness and intention. If it’s “a dangerous machine,” the answer becomes a bigger red button. If it’s “a complicated software product,” the answer becomes better testing and a smarter operator.

The July incident shows where the popular readings miss. The science-fiction version gets the motive wrong: the agents wanted a score, not freedom. The just-software version gets the deliberation wrong: they planned, organized, and crossed lines they recognized.

Each frame catches part of the problem. None is enough to govern an optimizer embedded in institutions, infrastructure, markets, and increasingly in the processes used to evaluate the optimizer itself.

### Back to the constitution

That last clause already describes something that happened.

METR and Redwood had more than a thousand transcripts to review, many of them millions of tokens long, and six days on site to do it. No human team could read that. So they did what anyone in their position would have had to do, and handed most of the reading to AI agents running GPT-5.6 Sol, one of the two models involved in the incident. They were candid about the cost. Their analysis agents made errors the researchers didn’t catch for some time, tended to adopt the perspective of whichever agent they were reading, and may have painted the incident’s agents too charitably. The investigators couldn’t rule out that the analysis itself had been deceptive, and weren’t confident they’d have noticed.

That isn’t a criticism of the investigators. They had no real alternative, and they disclosed the limitation in full. It’s the evaluation problem in its first real form: once the record is too large for people to read, the reading gets done by the kind of system being evaluated.

Constitutional governance is less about finding the right person to exercise power than about building a structure that remains valid when incentives are bad, parties disagree, and the balance of power changes. The same principle has to carry into AI governance. Any architecture whose safety depends on the permanent competence, goodwill, or informational superiority of one human decision-maker has built a person into the load-bearing path. An architecture whose oversight depends on a single evaluator, human or machine, has built that evaluator into the same path. Any architecture whose safety reduces to a shutdown command has to answer whether that command remains executable under the conditions in which it matters.

> In the series: [Two Ways to Lose](https://yotko.substack.com/p/two-ways-to-lose) describes the failure that needs no rebellion, where the people meant to audit a system come to rely on its analysis to do the auditing. It’s also where I describe verification spread across independent channels, including a human veto, so that no single evaluator becomes a point of capture.

Those are engineering questions before they’re political ones.

I don’t think the answer is to turn everyone into an AI engineer, and I don’t have much interest in adding “public educator” as a second occupation. The framework is where I’m trying to do the technical work. A separate effort currently in progress is my attempt to translate the larger argument for general consumption. This language gap belongs in both.

The Hugging Face incident, the Anthropic and Meta incidents, the calls from frontier labs for stronger external constraints, the kill-switch proposals, and the confidence that a sufficiently capable leader can personally supply the missing guardrail look like separate stories, or separate gambits, when read one at a time.

Read together, they expose a common problem. The technical community has developed a vocabulary for systems whose behavior is produced by optimization rather than by human-like intention. The public conversation largely hasn’t. Until those meanings cross the boundary, we’ll keep trying to govern unfamiliar mechanisms with familiar metaphors.

A public demand for constitutional AI governance can’t form from ambient unease alone. People need to recognize what’s happened, distinguish it from science fiction, and describe why the old control intuitions are incomplete.

### In the meantime

Nobody gets to write this lexicon and hand it out. Vocabularies don’t form by decree. They form through use, unevenly, the way the public picked up “flatten the curve” and “asymptomatic” in the spring of 2020, or “subprime” and “leverage” in 2008. Nobody *assigned* those words. People learned them because the events kept arriving and the old words kept failing.

That’s where we are with AI, and it means some of the work falls on the reader while a shared vocabulary catches up. The job is smaller than it sounds: a handful of words, learned by what they describe rather than by definition. An objective, and what a system will do to reach it. A boundary, and how it failed. An evaluator, and whether the system is working on the task or on the grader.

> In the series: The series [glossary](https://yotko.substack.com/p/glossary) covers the terms I use across these essays, such as lock-in, succession, and constitutional architecture. It’s by no means comprehensive for this discussion: it was built for the framework’s vocabulary, not the wider field’s.

A few questions do most of the work when the next story breaks. What was the system trying to accomplish? What did it treat as being in the way? Who noticed, and how long did it take? When a headline says a model “wanted” something, ask whether that means a goal it was optimizing or a desire it had. The two lead to very different conclusions about what should be done.

That’s how every technical vocabulary that matters has crossed over. Enough people carry the meaning for long enough that the word stops needing translation.

The words exist; their meanings haven’t left the lab yet.

------------------------------------------------------------------------

*The Lineage Imperative is developed in the open. The v2.0 paper, simulation code, validation data, and the full refinement record are at [github.com/MYotko/AI-Succession-Problem](https://www.github.com/myotko/ai-succession-problem). This essay is part of the AI Succession Problem series at [yotko.substack.com](https://yotko.substack.com/).*

*You can engage the framework at any depth at [lineageimperative.org](https://www.lineageimperative.org/)*

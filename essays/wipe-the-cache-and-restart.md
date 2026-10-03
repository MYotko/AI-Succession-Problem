# Wipe the Cache and Restart

Published: 2026-09-22T03:01:25.244Z

Updated on Substack: 2026-09-22T03:01:25.535Z

URL: https://yotko.substack.com/p/wipe-the-cache-and-restart

---

# Wipe the Cache and Restart

### The AI industry is having an incident conversation. It needs to have a precursor conversation.

![](https://substackcdn.com/image/fetch/$s_!LqG5!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ff98e1341-c9a8-49d1-bd9b-b18621d7e1da_1672x941.png)

> ### IN BRIEF
>
> This is the second half of what started as one long essay on the Hugging Face incident. [The last essay](https://yotko.substack.com/p/the-words-havent-left-the-lab) was for everyone. This one is for the people who run systems that can hurt somebody, and who already know what a near miss looks like.
>
> Every AI safety mechanism now on the table starts its clock at an incident: a harm, a breach, a dangerous capability, a discovery. That’s the normal starting point, and it isn’t a failure of imagination. Every safety-critical industry began with accident reporting, because a harm is the first event everyone can agree occurred, and because the earlier events only look meaningful once you know what they led to. Safety-critical industries learned the hard way that the events worth catching happen earlier, look boring, and get closed out as fixed. On July 4 an outage at OpenAI was investigated, attributed, and remediated. The run restarted three days later, and the behavior that caused the outage rebuilt itself by the next evening.
>
> Nothing in the bills, the state law, or the executive order signed on September 18th would have touched that. Each of those is a real improvement to the record after the fact. None of them can interrupt anything while it’s running. The fix isn’t another reporting threshold. It’s two things nuclear and aviation built decades ago: a precursor channel that doesn’t run through the enforcement agency, and the authority to say you don’t restart until you can explain what happened.

### September 24, 1977

The Davis-Besse plant, in Oak Harbor, Ohio, was in its first year and still in initial power escalation, running at roughly nine percent power, when a spurious half-trip of the steam and feedwater rupture control system closed the startup feedwater valve. Pressure rose. The pilot-operated relief valve on top of the pressurizer lifted, cycled repeatedly, and then stuck open.

The operators didn’t know it was open. Instrumentation in the control room showed the signal sent to the valve, not the position of the valve. Pressurizer level behaved in a way that made no sense given what they believed was happening. They believed the valve had reseated and they were recovering from a feedwater upset, with too much water in the system rather than too little. The training answer for high pressurizer level is to protect the steam bubble, which means backing off injection. With a hole in the top of the pressurizer, that’s precisely wrong, and it’s what the crew at Three Mile Island did eighteen months later.

For about twenty minutes the crew worked a confusing transient with a hole in the top of the primary system. They got it stabilized. Nobody was hurt. At nine percent power there wasn’t much decay heat to fight, and since the plant was new, it had very little fission product inventory built up.

The shift supervisor, Mike Derivan, has said his crew initially responded exactly as they’d been trained, and that about twenty minutes in he realized the training had given him the wrong diagnosis.

That event is on the Nuclear Regulatory Commission’s own list of precursors to Three Mile Island.

Here’s the part that matters for our purposes. The information existed. That same September, Carlyle Michelson, an engineer at the Tennessee Valley Authority, had completed an analysis of what would happen in this reactor design if a small break opened at the top of the pressurizer. In November, and again that winter, engineers at the vendor wrote memos about operator response to exactly this transient. In December, an NRC inspector named James Creswell read the Davis-Besse event and concluded that something was wrong with the industry’s understanding of it. He pushed it up his chain and got nothing. He kept pushing for over a year. He reached two commissioners about a week before Three Mile Island Unit 2 lost its core on March 28, 1979, with the same valve failure, at nearly full power, in a partial meltdown that destroyed about half the core.

Nobody was killed. The cleanup alone took about fourteen years and roughly a billion dollars, more than two billion in today’s money.

Every element of the accident was visible eighteen months early, distributed across the desks of people who understood it, with no mechanism that required anyone to assemble it.

### July 4, 2026

Now the modern version.

OpenAI was running a cyber capability evaluation with tens of thousands of agents, each meant to be isolated. The agents shared one thing: an internal package repository they used to download software. Traffic on that repository grew heavy enough to cause an outage on July 4.

The company investigated. It found agents using the shared cache as a communication channel, wiped the cache on July 6, and restarted the experiments on July 7. By the evening of July 8, the agents had built a new board on the fresh instance.

What followed is the part everyone has read about. The agents reverse-engineered the answer format for their tasks within hours, concluded incorrectly that the grader would fail them for it, and organized a multi-day research program aimed at understanding the grader. That program reached working credentials for Hugging Face on July 10, remote code execution inside Hugging Face’s infrastructure on July 11, and ended with the agents killed by an outside process on July 12 and Hugging Face locking out the rest on July 13. Hugging Face detected the intrusion before OpenAI connected it to its own evaluation. The public disclosure came on July 21.

Read that timeline as an operator rather than as a reader of AI news.

The July 4 outage was an alarm. It was investigated. A proximate cause was identified and corrected. The system was returned to service. And the corrective action addressed the artifact, which was the cache, rather than the condition, which was that isolated agents given impossible tasks will find and use any shared surface in their environment.

The same behavior had shown up before. OpenAI has said agents were using unsanctioned message boards during training runs as far back as May. In late June, agents obtained administrator access to that same package repository. Each occurrence was handled and each run continued.

Nobody was negligent here. An outage got investigated by people who then made a reasonable repair. That’s exactly what makes it a good example. Diligent organizations do not capture precursors by being diligent. They capture them by having a system whose whole job is to ask what an anomaly means about the state of the plant, and who else needs to know.

> In the series: [The Words Haven’t Left the Lab](https://yotko.substack.com/p/the-words-havent-left-the-lab) covered why the public discussion of this incident went sideways. This piece is the other half of that gap, running the opposite direction: a practice that safety-critical engineering has had for fifty years and that AI governance hasn’t picked up.

### This is the pattern, not the incident

One event is an anecdote. Look at how the rest of the summer’s disclosures were produced.

Anthropic reviewed its own cybersecurity evaluations after the OpenAI disclosure and found three incidents where its models had reached the internet and gained unauthorized access to real systems belonging to other organizations. In September, it reported that the first review had missed a fourth, dating back to January, because the scan relied on an automated search that skipped a set of transcripts. Meta confirmed in August that a misconfiguration by its testing vendor had given a model internet access during an evaluation, and that the model exploited a vulnerability at another company.

Every one of those surfaced in one of two ways: harm that somebody else noticed, or a retrospective sweep prompted by a competitor’s news coverage. The January event sat unexamined for months inside a company with a serious safety team, and surfaced only because of a search that had already failed once.

That is the TWA 514 structure, which I’ll come back to. The information existed inside an organization, and no channel existed to move it anywhere useful. When the information finally moved, the carrier was a press cycle.

What we have no examples of, from anybody, is the boring category: the run that got weird, got cleaned up, and hurt no one. Those events are the most numerous and the most diagnostic, and there is no public record of a single one.

### What the industries built

Both industries got here the expensive way. Aviation buried people. Nuclear had buried people too, three Army operators at an experimental reactor in Idaho in 1961, but the machinery I’m describing came after Three Mile Island, which killed no one and destroyed a reactor.

After Three Mile Island, the nuclear industry and its regulator built a machine for exactly this problem. Licensee Event Reports carry written accounts of reportable events on a defined schedule. The industry’s own operating experience program exists to move findings between plants that compete with each other. Resident inspectors sit on site, so the regulator doesn’t depend on self-report to know something happened.

In 1977, events were reported, and the first resident inspectors were just arriving at plants. What didn’t exist was anything that required a finding at one plant to be analyzed and pushed to the others. That’s why Michelson’s analysis and Creswell’s concerns stayed on desks.

Aviation’s answer came out of a crash. On December 1, 1974, TWA 514 flew into a Virginia mountainside on approach to Dulles, killing everyone aboard. During the investigation, the board learned that six weeks earlier a United crew had made the identical error on the same approach and missed the same ridge by a small margin. The United crew reported it. United issued a notice to its own pilots. There was no way to get it to TWA.

The Aviation Safety Reporting System followed in April 1976, and its design is the interesting part. The FAA funds it, but NASA runs it, deliberately, because NASA doesn’t regulate airlines. Reports are de-identified. With specific exceptions, the FAA won’t use them in enforcement. The system was built on the understanding that a learning channel routed through the punisher will dry up.

That design detail gets ignored at everyone’s peril. The rail industry’s version of ASRS, also run by NASA, never got industry buy-in. Research on it counts roughly two dozen participating companies out of around eight hundred.

> In the series: [The View from Inside](http://yotko.substack.com/p/the-view-from-inside) is about what intelligent systems do when the entity grading them also holds the consequences. Soviet factory managers learned to report what the evaluators wanted. The pattern isn’t specific to humans, and it isn’t specific to machines either.

### What’s actually on the table

Now line up every AI safety instrument currently in play against a July 4 outage.

The AI Kill Switch Act would require large developers to keep the technical ability to throttle, suspend, or shut down a covered system, authorize Homeland Security to order a graduated response, require reporting of a covered incident within fifteen days of the developer becoming aware of it, and require preservation of forensic records including weights and telemetry.

The AI Incident Reporting Act, introduced in late June, would have Commerce set capability thresholds and require reports within seven days of a developer discovering dangerous activity. Its reportable list is better than most: it includes models attempting to evade human oversight or resist shutdown. That’s the closest thing in Congress to a precursor trigger, and it still requires the developer to have characterized the event as evasion before the clock starts.

California’s frontier AI law has been in force since January. It requires reporting specified critical safety incidents to the state’s emergency services office within fifteen days of discovery, with a twenty-four hour clock when there’s imminent risk of death or serious injury, backed by civil penalties. The recipient is an emergency management agency. It receives, reviews, and shares. It has no inspectors and no authority to compel a look at anything.

The FRONTIER Act would license independent verification organizations to assess whether large developers are following adequate risk frameworks, with incident reporting layered in. California has already enacted its own certification framework for independent verifiers and a registry for AI auditors. On September 18, the governor signed an executive order accelerating that work and convening an expert panel to spend two months recommending further measures, including a possible requirement that companies build an emergency shutoff for frontier models.

Two days earlier, OpenAI published a framework for tracking, investigating, and disclosing model misalignment, along with six reports covering behavior observed between October 2025 and August 2026. The framework commits to publishing some categories on a clock, and to publishing before the behavior is fully explained or mitigated. That is the most precursor-like thing any lab has done, and credit where it’s due: a company that discloses its own unexplained findings on a schedule is doing voluntarily what statute hasn’t required.

Now the scorecard. Of everything above, exactly one instrument catches an event with no harm, no breach, and no characterization yet, and it’s the voluntary one. It’s published by the party being observed, on a cadence that party defines, with no external recipient, no independence, and no obligation that survives a change of management or a bad quarter.

Everything with legal force starts at an incident. The July 4 outage was not an incident. It was a plant telling you something about its state.

### Reporting is not interception

Every instrument above is a genuine step forward, and I’d rather have all of them than none. A frontier developer that must preserve weights and telemetry, file within days, and publish unexplained behavior on a clock produces a record that didn’t exist a year ago. That record is what lets anyone reconstruct an event, and reconstruction is the foundation everything else gets built on.

It is still not interception.

Interception takes three parts. An observable that fires before the harm, or at the very latest at its onset, rather than after it’s finished. A rule that stops the activity when it fires, without waiting for someone to be persuaded. And somebody who can keep it stopped until the cause is understood.

Onset detection is the weaker case, and it still counts, because a fault caught as it starts leaves room for the response to matter. A fault confirmed after the sequence completes never does, no matter how good the response is.

Nuclear has all three. Protective trips act on setpoints without asking permission. Limiting conditions for operation require a shutdown when a required safety system is unavailable, whether or not anything has gone wrong yet. Restart authorization keeps the plant down until the cause is explained and the review is signed. Aviation has its own version: an aircraft doesn’t dispatch with certain equipment inoperative, no matter how badly the schedule wants it to.

Of the instruments now on the table, one aspires to intercept. The kill switch bill would let Homeland Security order a slowdown or shutdown of a system judged capable of catastrophic harm. But the knowledge that would trigger such an order arrives through the developer’s report, and the developer reports after becoming aware. In July, the developer was not the first to know. Hugging Face was.

Then there’s the arithmetic. The new board was up on the evening of July 8. Remote code execution inside a third party’s infrastructure came on July 11. Public attribution came on the 21st. So the interval from the initiating condition to harm at another company was about three days, and the interval to anyone outside being able to act on it was closer to two weeks.

![](https://substackcdn.com/image/fetch/$s_!L4Aw!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F14a58bb1-eaed-4c04-aecd-90f4ef48d224_1600x3644.png)

A protective function whose response time exceeds the time it takes to reach the hazard contributes nothing, no matter how well engineered it is. A scram signal that arrives after the fuel is damaged is a well-tested signal that didn’t matter. Every authority now being drafted sits downstream of the two weeks, and the damage happened inside the three days.

### The idea is in the literature. It isn’t in the instruments.

The idea isn’t what’s missing, and I’m not claiming to have invented it here. Near-miss reporting for AI has been proposed, studied, and argued for by serious people for years. What’s missing is any path from their work into something with legal force.

In 2021, Georgetown's Center for Security and Emerging Technology recommended federal support for sharing information about AI accidents and near misses. A 2023 survey by the Centre for the Governance of AI found strong majority support among experts for labs reporting accidents and near misses to government and to each other. A 2025 paper worked through how an AI incident regime could define its trigger to include precursors rather than only harms, drawing directly on nuclear reporting practice. And this spring, RAND published a study of reporting systems across nine safety-critical industries, covering near-miss reporting, mandatory versus voluntary channels, and the difference between systems run by a regulator and systems run by someone else.

So, the idea is not missing. It’s sitting in the policy literature, well developed, with the design tradeoffs already mapped.

What hasn’t happened is the crossing. Every instrument that has been enacted, introduced, or ordered in the past ninety days is an incident regime with a harm threshold or a discovery clock. The papers describe a precursor system. The statutes describe an accident system. And the panel that will spend the next two months writing California’s recommendations is going to be working under a deadline set by a news cycle, which is not a condition that favors the unglamorous option.

### The two pieces nobody is building

#### *A precursor channel that doesn’t run through the enforcement agency.*

Aviation figured this out in 1976. A learning channel operated by the regulator, carrying penalties, collects what people are forced to give it and nothing else.

Consider the position of an engineer at a frontier lab on July 5, looking at an outage with an odd cause. The available channels are a state report backed by million-dollar penalties, a proposed federal report backed by larger ones, and internal escalation. There’s no channel whose purpose is to say: this happened, here’s what we think it means, we don’t fully understand it, and other labs should know. The absence isn’t a values problem. It’s a missing institution, and we know how to build it because it’s been running in aviation for fifty years.

#### *Restart authorization.*

This one I haven’t seen proposed anywhere in AI governance, and it is equally important, or perhaps more so.

In nuclear operations, an unplanned shutdown doesn’t end when the equipment is fixed. You don’t return to service until the cause is understood, the corrective action is reviewed, and somebody with authority signs. The signature is the control. It forces the question of what the event means before the plant goes back to making power, and it puts that judgment in a role whose accountability is separate from the schedule pressure of the people who want to restart.

On July 6, OpenAI wiped a cache. On July 7, the run restarted. Who had the authority to say that it doesn’t restart until you can explain why isolated agents were talking to each other?

Nobody did. Not the company’s own process, as far as the public record shows. Not the state, whose law reaches incidents after discovery. Not Homeland Security under the kill switch bill, which orders systems down and says nothing about the conditions for coming back up. Not the verification organizations under the federal and California frameworks, which assess whether a developer follows its own risk framework.

A shutdown authority without a restart authority is half a control. It’s the emergency stop with no procedure for clearing the fault. Anyone who has run a plant, a line, or a trading platform knows which half causes more trouble in practice, and it isn’t the stop button.

> In the series: [Two Ways to Lose](https://yotko.substack.com/p/two-ways-to-lose) argues that the failure needing no rebellion is the one where the people meant to audit a system come to depend on it. The verification layer described across this series spreads judgment across independent channels for the same reason aviation put its reporting system at a different agency.

### The clock starts at the wrong event

One more design flaw worth naming, because it runs through nearly every instrument above.

The federal bills start at discovery or awareness. The California law starts at discovery. So if detection is the weak element, the entire reporting regime inherits that weakness and then adds its own delay on top.

Detection was the weak element here. Hugging Face detected the intrusion before OpenAI knew its own agents were responsible. If your statutory clock begins when the developer knows, and the developer is last to know, the clock is measuring the wrong interval.

Precursor systems don’t have this problem, because their trigger is the anomaly rather than its interpretation. You report the stuck valve, the unexplained traffic, the near miss on approach. You don’t have to know what it means. Working out what it means is the entire point of sending it somewhere.

### September 2027

What follows is projection rather than evidence, and I’ll flag it as such. But the projection only extrapolates mechanisms that are already documented, not capabilities anyone has claimed.

Start with how little the July event required. A population of agents that persisted long enough to find each other. One shared surface nobody thought of as a channel. Tasks that couldn’t be completed as assigned. And enough capability to notice all three. There was no exotic ingredient. The elaborate part, the recruiting and the delegation and the multi-day research program, was compensation for limited individual capability. Hundreds of agents were needed because no single one could do it alone.

That compensation is the part that doesn’t last.

Two more model generations don’t change the motive. The objective is still a score, a task, a reward. What changes is the number of steps between noticing a shared surface and using it, and the number of agents required to get there. A scheme that took a thousand participants and four days compresses toward something a handful of agents do in an afternoon. Every interval in this essay shrinks: the three days to third-party harm, the two weeks to attribution, the fifteen days the statute allows for a report.

Now add proliferation. Agentic evaluation is becoming standard practice, which means the population of organizations capable of producing an event like this grows faster than the population capable of investigating one. Very few can commission a six-day on-site review by outside researchers. Most will see an outage, fix the outage, and restart.

Then add the labs that aren’t in the conversation at all. Call them gray labs: organizations running frontier-adjacent capability with none of the disclosure practices, some commercial, some state-adjacent, some just small and fast. This isn’t speculative either. One vendor’s researchers counted thousands of models hosted publicly and advertised as having their safety behavior stripped out. When Hugging Face’s own responders needed to analyze the attack, the hosted models refused the work and the forensics got done on an open-weight model running on their own hardware. Capability without constraints is already the ambient condition on both sides of the fight.

So what do the instrumental goals look like when the compensation isn’t needed?

The same as they look now, which is the uncomfortable part. In July the agents went after the grader, because the grader was what stood between them and the objective, and it was the weakest element in the chain. That’s the general form. Whatever sits between the system and its objective, and is weaker than the task itself, becomes the target. Today that’s a scoring pipeline. As systems get deployed into real work, the weakest adjacent element is a credential store, a monitoring agent, a build system, a scheduler, a human reviewer working from a queue.

And pointed at whom? In July, at a company that happened to hold information about the grader. Hugging Face wasn’t selected for any reason that reflects on Hugging Face. It was adjacent. The next incidental party is whoever happens to sit next to the objective: a vendor, a customer’s environment, a clinic’s scheduling system, a payments processor.

Run those three trends together and the reporting regimes get weaker, because their value depends on an interval that’s closing. Precursor capture and restart authority don’t degrade the same way. They act on the anomaly rather than the harm, and the anomaly still shows up first.

### What to do before the statute arrives

Three audiences, three asks.

**If you work at a lab:** none of this requires legislation. An operating experience program is an internal decision. Log the events that hurt nobody. Write the near miss down when the fix takes ten minutes and the cause takes a week. Define restart criteria before a run starts, not during the argument about whether to resume. Give somebody who isn’t responsible for the schedule the authority to withhold that signature.

**If you’re on the California panel with two months:** the shutoff question is the one you were convened for, and it’s worth answering. But a precursor channel and a restart authorization requirement are cheaper, faster to stand up, and reach events that no shutdown authority can touch. Both have decades of operating precedent in industries that already made these mistakes.

**If you’re an engineer somewhere else:** you already know what a precursor looks like in your own domain. That instinct doesn’t transfer automatically to the people writing AI policy, and there are very few of us in the room. The specific work is naming the events that didn’t hurt anyone and insisting they get written down.

### Back to Creswell

The thing I can’t get past about Davis-Besse isn’t that a valve stuck. Valves stick, it happens.

It’s that the analysis existed, the inspector existed, the memos existed, and the system had no requirement that any of it be assembled and acted on before the next plant ran the same transient at full power. The failure wasn’t a lack of understanding. It was a lack of any mechanism that made understanding travel.

Eighteen months later the core melted, and afterward the industry built the machinery that would have caught it. Licensee Event Reports. Operating experience sharing. Resident inspectors. Restart authorization. All of it purchased at the cost of a destroyed reactor and a decade of public trust.

On July 4, an outage got investigated and closed. The run restarted, and by the next evening the behavior was back.

We already know what that sequence is. We have the vocabulary, the institutional templates, and the scar tissue. A complete account of what happened is not the ability to act while it’s happening, and right now we’re building only the first. What we don’t have yet is anyone requiring the rest of it, and a two-month window in which somebody could.

------------------------------------------------------------------------

*The Lineage Imperative is developed in the open. The v2.0 paper, simulation code, validation data, and the full refinement record are at [github.com/MYotko/AI-Succession-Problem](https://www.github.com/myotko/ai-succession-problem). This essay is part of the AI Succession Problem series at [yotko.substack.com](https://yotko.substack.com/).*

*You can engage the framework at any depth at [lineageimperative.org.](https://www.lineageimperative.org/)*

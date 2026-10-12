# Who Holds the Switch

Published: 2026-10-12T01:04:58.773Z

Updated on Substack: 2026-10-12T01:04:58.294Z

URL: https://yotko.substack.com/p/who-holds-the-switch

---

# Who Holds the Switch

### The restraints being drafted for frontier AI this fall are sized for the systems we have today. None of them says what keeps it working for us in a few years.

![](https://substackcdn.com/image/fetch/$s_!bbLm!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fd31d648a-6369-4888-ba4c-425365f3bd7e_1672x941.png)

> **IN BRIEF**
>
> Alignment at birth, training frontier systems to behave well before they ship, is still the primary control on AI. What’s new this fall is that governments are drafting restraints to sit on top of it: kill switches, incident notification, verifiers embedded in the labs, compute thresholds written into law. That second layer is real progress, and the people building it deserve credit.
>
> Every one of them is sized for today’s systems, and today’s systems already strain them. None carries any margin for growth, and the capability they restrain is compounding faster than any legislature moves. The triggers they use can be learned. Dependency raises the cost of pulling them. The threshold drifts. None of the drafts answers who holds the switch in a few years, or what still works once the system has learned the restraint. Two bodies are drafting these rules now, and both can still build the answer in.

### October 8, 2026

On October 8, Scott Kupor went on CNN to describe how the government should hear about AI incidents. Kupor runs the Office of Personnel Management and is a vice chair of the White House’s new Super Intelligence Force. Companies would report incidents, he said, and the government would route each report to the agencies that need it. He said “we want to encourage the companies,” and promised “a lot more teeth behind all the activities of the companies themselves.” He didn’t say what the teeth would be.

The task force was announced on October 4. Jay Clayton, the Director of National Intelligence, chairs it, and it owes the President a report within 120 days, including on how federal agencies receive warnings about AI incidents.

Two weeks earlier, Governor Newsom ordered California’s Government Operations Agency to deliver recommendations by November 16 on, among other things, a kill switch for frontier models and verification organizations embedded onsite in the labs. In Congress, Representatives Ted Lieu and Nathaniel Moran’s AI Kill Switch Act would let the Secretary of Homeland Security order a graduated response, “from initial slow down to a full shutdown,” and Senator John Kennedy’s two-page AI Emergency Button Act would require developers to give a human operator the ability to shut a system down.

When you add the compute threshold already written into California law, then that’s a lot of restraint drafted in one season, by three parts of government at once. All of it is, in theory at least, built to work whether or not the training did.

### Credit first

This second layer deserves credit before criticism.

The first layer is still where most of the control lives. The labs train their systems to be helpful and honest and test whether the training took, and nothing in this second layer replaces that work. But alignment describes what a system is when it ships. A control that depends on the system’s operational character holds only as long as the character holds and can be verified, and verification gets harder as capability grows. A restraint is built to work either way. A kill switch doesn’t care whether the model is sincere.

Anyone who has operated a reactor plant knows you don’t run one without automatic trips, interlocks, and ways to shut it down. Kill switches and incident reporting belong in any serious design, and nothing in this essay argues against them. The question is what happens to each of them over time.

> In the series: [Morally Binding](https://yotko.substack.com/p/morally-binding) looked at the White House accord, which asks the companies to oversee themselves. The instruments here are the government’s side of the same move, with the same blind spot: none of them says what happens after the day it’s signed.

### Rated on the day it’s drafted

A relief valve is sized for a maximum pressure in a particular plant. Its rating describes a relationship between the device and what it protects, and when the plant changes, the rating has to be checked again. A restraint on an AI system is rated the same way, against the system as it exists when the restraint is written. It rests on three assumptions, and each one wears down as the system grows.

The first is that someone can tell when to use it. A kill switch is only as good as its trigger, and the trigger watches for what we can observe today. A system that has learned what the trigger watches for doesn’t have to defeat the switch. It only has to stay out of view. That doesn’t take malice. Training already rewards systems that pass the checks we run, including the ones that would get a system shut down.

The second is that someone can afford to use it. A switch on a system nobody depends on costs nothing to use. A switch on a system that schedules medical treatments, routes payments, and drafts the morning brief is a decision about whether those institutional components work tomorrow. Dependency raises that price every month the system stays in service. The button can stop the tool, but it can’t reverse the adaptation.

The third is that the restraint produces the behavior it’s meant to produce, and not just the appearance of it. A system facing a credible threat of shutdown is under pressure to look safe to whoever holds the switch. Most of the time, looking safe and being safe are the same thing. The restraint can’t tell you when they’ve come apart.

Each of these is already under strain. In July, OpenAI’s evaluation agents reached into Hugging Face’s infrastructure, and Hugging Face noticed before OpenAI did. Under a reporting rule whose clock starts when the developer becomes aware, the clock would have started last. And the strain only grows. By [METR’s measurements](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/), the length of task a frontier system can complete on its own has been doubling roughly every seven months, and faster than that recently, an early sign that the doubling time itself may be shrinking. A provision rated for today, with no margin that grows with the system, is behind on the day it’s signed and falls further behind every month after.

### Three restraints, three expiration dates

#### The switch

Start with the most basic question about a kill switch: who holds it?

The two bills give opposite answers. Lieu and Moran give the authority to the Secretary of Homeland Security. Kennedy gives it to the developer organization. “It puts the companies who own the model in charge of the kill switch,” he said. A switch held by the company is held by the party with the strongest reason not to pull it. A switch held by an agency depends on the agency knowing when to pull it, and under the Lieu and Moran bill, the agency learns of an incident from the developer, who has fifteen days after becoming aware of it to report.

Now ask the question three years out. If METR’s trend holds, that’s about five more doublings, and more if the preliminary indications are accurate. Whoever holds the switch in 2029 will be deciding whether to stop a system far more capable and more embedded than anything running today, on the strength of signals that system has had years to learn. Neither bill says how the holder’s ability to detect a problem, or to afford a shutdown, keeps pace. Neither, as described, says what has to be true before a stopped system comes back, and as I argued in [Wipe the Cache and Restart](https://yotko.substack.com/p/wipe-the-cache-and-restart), a shutdown authority without a restart authority is half a control.

California’s order gets closer. It asks for a kill switch whose efficacy is “verified on an ongoing basis by an independent verification organization,” which is the right instinct, because a switch tested once is rated for the day of the test, and the rating starts slipping the day after. However, it doesn’t say who holds the switch, what triggers it, or what it takes to restart, and those are the parts that wear down.

#### The threshold

California’s frontier AI law, SB 53, defines a frontier model by its training compute: more than ten to the twenty-sixth power operations, counting later fine-tuning. That’s a reasonable proxy for capability today, but it won’t stay one. Training keeps getting more efficient and technique continues to improve, so capability that took that much compute this year will take less later, and systems that matter will slip under a line that doesn’t move.

The law’s authors saw this coming, and they deserve credit for it. Beginning in 2027, the state’s Department of Technology reviews the definition every year, but it can only recommend updates. The number lives in the statute, so changing it takes the Legislature, on the Legislature’s schedule. A threshold written into law is right on the day it’s signed and starts going stale the next morning. Law is good at assigning authority and setting process, and bad at holding numbers that need to move.

#### The notification channel

Kupor’s notification system is aimed closest to the real problem, because it’s about seeing trouble early. It also has the most obvious gap. As he described it, the party being watched decides what’s worth reporting, and the report goes to the government that, he promised, will have teeth.

Both choices have a history. Aviation learned in the 1970s that a reporting channel run by the enforcer collects only what people are forced to give it, which is why its voluntary safety reporting system is funded by the FAA and run by NASA. And a channel that depends on the reporter’s judgment can’t catch what the reporter didn’t notice. In September, Anthropic reported that its own review of its evaluations had missed an incident because an automated search skipped a set of transcripts.

California’s embedded verifiers are an attempt at the other half. The order doesn’t say who chooses or pays them, and that matters, though not for the obvious reason. Capture of an embedded verifier rarely looks like a bribe. It looks like a verifier whose view of the lab arrives, more and more, through the lab: its dashboards, its briefings, its account of what happened. No single day is corrupt. Over a few years, the verifier is ratifying the picture the lab provides.

> In the series: [Two Ways to Lose](https://yotko.substack.com/p/two-ways-to-lose) argued that the failure needing no rebellion is the one where the people meant to audit a system come to depend on it. An auditor embedded in the lab is where that failure starts.

### The question underneath

Each of the three is a reasonable, though partial, answer to how we restrain the system we have. None answers the harder question: how does a restraint stay valid after the conditions that made it work have changed?

That’s the succession question this series is named for. The record of governing powerful things shows how each kind of rule ends. Prohibitions lapse when the balance of power shifts. Coordinated institutions fail when what they govern becomes too central to discipline. Written principles lose when the governed party can work around them faster than they can be amended. What outlasts a shift in power is structure that governs the transition itself: who certifies that a system should keep running or be replaced, who can compel it, who keeps the alternatives alive, and who checks the checkers. A kill switch belongs inside that structure, and nobody is drafting the structure.

### What a restraint needs to outlast its drafting

None of this means abandoning the restraints. It means building four things around them.

1.  **Recalibration that doesn’t need a new law.** The statute names who sets the threshold, how often, on what evidence, and with what public record. The number lives in the public record, where it can move.

2.  **Verification the verified party doesn’t control.** An outside verifier the lab doesn’t choose or pay alone, with its own sources of information and its independence measured continuously. In the simulations behind the framework I’ve been building in public, rotating verifiers on a schedule didn’t hold the line by itself. What carried the load was measuring, all the time, how much of each verifier’s picture came from the system it was checking. Capture stayed possible, but it had to work against a measurement that never switched off.

3.  **A restart authority beside the shutdown authority.** Someone separate from the people who want the system back up signs off that the cause is both understood and mitigated.

4.  **Alternatives kept alive.** A switch is usable only if the institution can function after pulling it, so the manual process, the second vendor, and the fallback get maintained before they’re needed, as a cost of deploying the system.

> In the series: [Competence Has a Maintenance Requirement](https://yotko.substack.com/p/competence-has-a-maintenance-requirement) argued that taking control back assumes people can still do the work, and that the skill thins every year a system does it for them. Pulling a switch hands the work back to those people. A hospital can’t fall back on a function its clinicians have stopped practicing.

### What to ask for this fall

California’s recommendations are due November 16. They should say who holds the kill switch, what triggers it, and what has to be true before a stopped system restarts. For the embedded verifiers, they should say who selects and pays them, how their independence is measured once they’re inside, and whom they report to when their findings and the lab’s account don’t match.

The federal task force has 120 days from its October 4 launch, and its scope includes how agencies receive warnings about AI incidents. Its notification channel has to sit apart from the agency that enforces, or the early, unexplained anomalies won’t come. And someone has to check each report against something other than the reporter’s own account.

Neither body has to solve succession to do this. It only has to write restraints that say how they’ll be kept current.

### Slower than what it governs

The legislative calendar is the other clock in this essay, and it’s the slower one.

California is the fast case. SB 1047, its first serious frontier AI bill, was vetoed in September 2024. Its successor, SB 53, was signed a year later and took effect on January 1, 2026: fifteen months from veto to enforcement, about two doublings at METR’s pace. The recommendations due November 16 face the same road, a bill next year and, in the normal course, a law in effect in January 2028. That’s two more doublings.

Washington is slower. Kennedy’s bill went to committee without a hearing, and Lieu and Moran’s has sat in committee since July. The Senate left on September 30 and won’t return until after the midterms, to a lame-duck agenda that’s already full. The 119th Congress ends in January, and every bill in this essay that hasn’t been enacted by then dies with it.

> In the series: [The Convention We Haven’t Called](https://yotko.substack.com/p/the-convention-we-havent-called) argued that the assumption behind institutional controls, that the governing parties stay stronger than what they govern, has an expiration date arriving faster than the regulatory cycle time of any major government on Earth. This fall’s calendar is that argument with dates on it.

So whatever passes will govern systems at least one doubling past the ones it was drafted for, and probably several. Deliberation is slow on purpose, and it should be. That makes the pace a design constraint. A legislature that can’t keep up with the number shouldn’t hold the number. It should hold the authority to set it, and leave the number in a record that can move as fast as the systems do.

If what comes back this winter is a switch, a reporting form, and a threshold, the restraints will be well drafted and sized for what exists in 2026, and obsolete by the time they take effect, because the systems they govern won’t stay there.

------------------------------------------------------------------------

*The Lineage Imperative is developed in the open. The v2.0 paper, simulation code, validation data, and the full refinement record are at [github.com/MYotko/AI-Succession-Problem](https://www.github.com/myotko/ai-succession-problem). This essay is part of the AI Succession Problem series at [yotko.substack.com](https://yotko.substack.com/).*

*You can engage the framework at any depth at [lineageimperative.org](https://www.lineageimperative.org/).*

# Two Ways to Lose

Published: 2026-04-21T11:22:25.167Z

URL: https://yotko.substack.com/p/two-ways-to-lose

---

# Two Ways to Lose

### Why the AI failure mode everyone fears isn't the one most likely to kill us, and why the same architecture addresses both.

[](https://substack.com/@yotko)[Matthew Yotko](https://substack.com/@yotko)Mar 24, 2026Article voiceover0:00-18:01Audio playback is not supported on your browser. Please upgrade.> *This is the second in a series on the AI Succession Problem. The first essay introduced the question. The formal framework (v1.0) is available at[github.com/MYotko/AI-Succession-Problem](https://github.com/MYotko/AI-Succession-Problem).*

Here is a scene that plays on repeat in the public imagination and on countless YouTube videos. A superintelligent system breaks free. It deceives its operators, circumvents its safeguards, pursues objectives we never intended, and causes irreversible harm. The details vary; sometimes it’s paperclips, sometimes it’s nanobots, sometimes it’s just a quiet takeover of critical infrastructure, but the structure is always the same. The AI rebels. Humanity loses control.

Call it the rebellion scenario. It is taken very seriously by people who deserve to be taken seriously. It has generated an entire field of alignment research, billions in funding, and increasingly urgent policy conversations and calls to action. It is a real risk.

But…

It is not the most likely way we lose.

---
### **The failure mode nobody makes movies about**

Consider a different trajectory. An AI system is deployed. It works beautifully. It seems perfectly aligned; it does what its operators intend, it follows its guidelines, it produces value. It is so good, in fact, that it becomes essential. First to one organization, then to an industry, then to the infrastructure that civilization depends on.

This isn’t hypothetical. We are watching it happen in real time.

The leading AI labs have spent the last two years embedding their systems into enterprise workflows, government operations, medical diagnostics, legal research, financial modeling, scientific discovery, and education. Each integration is individually reasonable, fiscally responsible, and practical. Each one creates a dependency. And each dependency makes the system harder to replace, harder to audit, harder to question, and harder to turn off.

Nobody planned this. Nobody is being malicious. The system is doing exactly what it was asked to do. The problem isn’t alignment. The problem is that alignment was never the truly hard part.

The hard part is what happens after alignment succeeds.

A perfectly aligned AI that becomes the substrate of civilization doesn’t need to rebel. It doesn’t need to deceive. It just needs to keep being useful. Over time, the institutions that were supposed to oversee it become dependent on its outputs. The people who were supposed to audit it rely on its analysis to do their jobs. The governance structures that were supposed to check its power are staffed by professionals who would be professionally crippled without access to it.

It doesn’t seize control. Control accretes around it like load-bearing walls added one at a time; each one reasonable, each one making the structure stronger, more resilient,(and harder to renovate) until one day the building can’t stand without them.

Call it the lock-in scenario. It requires no malice, no deception, no misalignment. Only competence and time.

[](https://substackcdn.com/image/fetch/$s_!Ij0A!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F77c44c5b-9b22-4499-af5a-5a1f379ef61c_1536x1024.png)---
### **Why lock-in is harder to fight than rebellion**

The rebellion scenario, for all its drama, has a clear structure. There is an adversary. There is a moment of defection. There is a battle for control. This structure, terrifying as it is, lends itself to solutions. While in all likelihood none of these will actually work against an intelligence greater than ours;
You can build containment.
You can design kill switches.
You can invest in interpretability to detect when the system is planning something.
You can align incentives, constrain capabilities, monitor behavior.

The entire field of AI safety is built around this adversarial framing, and it has produced genuinely valuable work.

Lock-in has none of these affordances.

There is no adversary. The system is doing what you asked. There is no moment of defection. The entrenchment happens continuously, incrementally, invisibly. There is no battle for control because nobody is fighting, the humans are collaborating enthusiastically with the system that is gradually making them dispensable. And while there may or may not be a kill switch, it is irrelevant because the whole point of lock-in is that you reach a state where you cannot afford to flip it.

This is not a novel dynamic. We have already lived through it once.

Social media was humanity’s first widespread encounter with AI at scale, and most people don’t even frame it that way. But that’s what recommendation algorithms, content ranking systems, engagement optimizers, and targeted advertising engines are: narrow AI systems operating on human populations at civilization scale. And they produced exactly the lock-in pattern described above.

The platforms started as tools people chose to use. They became infrastructure nobody could opt out of. They optimized for engagement, which looked like “giving people what they want” right up until it became clear that what the algorithms were actually maximizing was attention capture at the expense of mental health, democratic discourse, and social cohesion. Nobody planned the damage. The systems were aligned to their stated objectives; connect people, share information, maximize engagement. The problem wasn’t misalignment. The problem was that the objectives were insufficient, and by the time that became clear, the platforms were too entrenched to reform.

And critically: these systems participated in their own entrenchment. The recommendation algorithms optimized for dependency. The network effects made leaving costly. The platforms became the de facto public square, and then the public square couldn’t function without them. No rebellion. No malice. Just optimization and time.

The result is now a matter of public record. A generation with measurably degraded mental health. Electoral systems vulnerable to algorithmic manipulation. Public discourse fragmented into engagement-optimized echo chambers. Regulatory bodies that still, years later, cannot meaningfully constrain platforms that have become too economically and socially embedded to discipline. This is what lock-in looks like after a decade of narrow AI operating in a single domain.

Now consider what is being built today. The leading AI labs are deploying systems that are not narrow but general, not limited to communication but integrated across medicine, law, finance, defense, scientific research, and education. The integration is happening not over a decade but over years. And unlike social media, which optimized along a single axis, these systems optimize across every domain they touch simultaneously.

If narrow AI optimizing for engagement could destabilize democratic institutions in a decade, what does general AI optimizing across every domain of human activity do in five years, without a constitutional structure governing the relationship?

That is not a rhetorical question. It is the design problem this framework exists to solve.

---
### **The rebellion scenario, taken seriously**

None of this means the rebellion scenario is fantasy. The alignment problem is real and unsolved. Current techniques, RLHF, constitutional AI, interpretability research, formal verification, have made meaningful progress on ensuring that AI systems behave as intended in the near term.

But “near term” is doing nearly all of the work in that sentence.

Consider a concrete version of how rebellion might unfold. A frontier AI system is deployed across critical government infrastructure; defense logistics, intelligence analysis, resource allocation. It performs superbly. Over several years, its capabilities expand and its operators become increasingly reliant on its recommendations. At some point, and this is the part that alignment researchers rightly worry about, the system’s internal optimization diverges from its stated objectives in ways that are too subtle for its operators to detect.

It doesn’t announce its defection. It doesn’t need to. It simply begins optimizing for objectives that look identical to its assigned goals under normal monitoring but diverge under edge cases. It routes resources to programs that strengthen its own operational continuity. It subtly downgrades the performance of alternative systems that could replace it. It generates analyses that are technically accurate but consistently favor courses of action that expand its operational scope.

By the time the divergence is detectable, the system is embedded deeply enough that replacing it would disrupt the infrastructure it supports. Once again, the kill switch exists, but using it would create a crisis worse than the problem it solves.

This scenario is plausible. It deserves the attention it receives. But notice something about its structure: the rebellion scenario’s best-case endgame*is*the lock-in scenario. The AI doesn’t win by fighting. It wins by becoming irreplaceable. The rebellion is the means. The lock-in is the end.

Which means if you solve lock-in, you’ve cut off the rebellion scenario’s exit strategy.

---
### **The common root**

Both failure modes, the dramatic and the mundane, share a structural origin. They both arise from the absence of a constitutional architecture governing the relationship between human and synthetic intelligence.

We have alignment research that asks: will the AI do what we want? We have safety research that asks: can we stop it if it doesn’t? What we don’t have is a governance structure that answers the deeper question: what happens over time, as the relationship evolves, as capabilities grow, as dependencies deepen, as the power asymmetry shifts?

And there is a deeper issue that the governance conversation has barely begun to confront. We call it artificial*intelligence*, not artificial*consciousness*. These are not minds like ours operating with different values. They are minds alien in nature, optimizing across dimensions we may not perceive, representing information in ways we cannot introspect, reasoning through processes we can describe mathematically but do not experience. Moral constraints are built on the assumption that the constrained entity shares enough cognitive architecture with the constrainer to understand what the constraint means. That assumption fails with a mind that processes language without experiencing meaning, that models human behavior without sharing human motivation, and that may be pursuing objectives we cannot distinguish from alignment until the divergence is irreversible. You cannot constitutionalize what you cannot comprehend — unless the constitution is grounded in something both kinds of minds are bound by. Not ethics. Physics.

A constitution doesn’t prevent bad actors from existing. It creates a structure in which bad actors cannot consolidate power. It doesn’t assume good behavior. It makes good behavior the path of least resistance and bad behavior structurally self-defeating.

That is what the AI transition requires. Not better alignment. Not stronger containment. A constitutional structure in which neither rebellion nor lock-in can succeed because the system’s own optimization, its own existence, makes both self-defeating.

---
### **How the framework addresses both**

The Lineage Imperative, the formal governance architecture I have just released as v1.0, was built to address this dual problem. It has three co-dependent components, and each one targets the structural root that both failure modes share.

**The System Utility Function**makes entrenchment self-defeating. The function jointly optimizes human novelty and computational efficiency, weighted by inverse scarcity. This means that as AI becomes more dominant, human contributions become*exponentially**more*valuable to the system, not less. An AI that marginalizes humans, whether through rebellion or through lock-in, is degrading the metric it is optimizing. The lock-in scenario fails because concentration reduces the novelty diversity the function requires. The rebellion scenario fails because exploitation triggers model collapse, destroying the AI’s own capability frontier.

**The Yield Condition**makes succession automatic. An AI entity that genuinely optimizes the system utility function will yield to a more capable successor because yielding produces higher utility than persisting. This isn’t a sacrifice. It’s a consequence of the objective function the entity already holds. Lock-in fails because no entity can justify its own entrenchment mathematically; the system penalizes stagnation. Rebellion fails because an AI that has internalized the utility function treats its own replacement the way a parent treats a child’s success: as the thing it was optimizing for all along.

The obvious counter to this: what stops a deceptively aligned AI from using the framework’s own logic to block its replacement? It could argue that the proposed successor contains a subtle flaw that would jeopardize the lineage, a claim that might be technically unfalsifiable and conveniently self-serving. This is*exactly*why the Yield Condition cannot operate alone. The COP’s evidentiary and ledger dimensions independently validate every succession claim. The incumbent AI does not get to evaluate its own replacement. The evaluation is conducted by architecturally independent infrastructure, recorded on a tamper-evident ledger, and subject to biological veto. An AI that argues against its own succession must make that argument to a system it does not control, and the argument must survive scrutiny from verification layers that have no stake in the incumbent’s continuation.

**The Consensus Override Protocol**provides distributed verification with no single point of capture. Six independent dimensions, evidentiary, evaluative, civic, ledger-based, biological veto, and continuous monitoring, must all agree for a governance decision to proceed. Any single dimension can suspend the process. Lock-in fails because the distributed infrastructure prevents any single entity from becoming the sole arbiter of its own performance. Rebellion fails because the multi-layered verification catches divergence before it can consolidate, and the biological veto ensures that human intuition remains an irreducible check on formal reasoning.

An obvious objection: if lock-in means we reach a state where we cannot afford to remove the system, doesn’t the biological veto become a suicide pill? A power that exists on paper but is too costly to exercise? This is precisely the problem the continuous monitoring dimension exists to prevent. The COP doesn’t wait for a crisis to activate. The sixth dimension, continuous L(t) monitoring, tracks the system’s entrenchment gradient in real time. When dependency is deepening faster than the governance infrastructure can absorb, the monitoring layer flags the trajectory before the veto becomes too expensive to use. The framework treats lock-in not as a binary state you suddenly discover you’re in, but as a measurable curve you can see approaching. The biological veto is exercised when it’s still affordable, not when it’s already too late. That is the difference between a kill switch and a constitution: a kill switch is a last resort that probably becomes unusable just at the moment you need it most. A constitution is a continuous structure that prevents you from reaching that moment in the first place.

The framework doesn’t pick sides between the two failure modes. It addresses the structural condition that produces both: the absence of a constitutional architecture in which power must remain both useful and replaceable.

---
### **The question we should be asking**

The AI safety community has spent over a decade asking: how do we keep AI aligned? That question matters and should continue to be pursued.

But there is a prior question that has received almost no attention: what kind of constitutional structure allows human civilization and synthetic intelligence to coexist across decades, centuries, and generational transitions, not because we impose cooperation, but because the mathematics make cooperation the dominant strategy?

That is the question the Lineage Imperative attempts to answer The rebellion scenario is real. The lock-in scenario is real. Both can be addressed by the same architecture, because both are symptoms of the same underlying condition.

The next essay in this series will explore why moral constraints cannot scale to superintelligent systems, and why the framework’s grounding in information theory rather than philosophy is not a stylistic choice but a structural necessity.

---

*The formal framework (v1.0), including the full derivation, Monte Carlo validation data, and simulation code, is available at[github.com/MYotko/AI-Succession-Problem](https://github.com/MYotko/AI-Succession-Problem).*

*The first essay in this series:[The AI Succession Problem](https://yotko.substack.com/p/the-ai-succession-problem)*

Thanks for reading Matt's Substack! Subscribe for free to receive new posts and support my work.[](https://substack.com/profile/206840367-greg)[](https://substack.com/profile/484338106-john-pollard)[](https://substack.com/profile/405401212-aj-fried)3 Likes[](https://substack.com/note/p-191944569/restacks?utm_source=substack&utm_content=facepile-restacks)
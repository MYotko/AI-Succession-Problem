# Moral Constraints Won't Scale

Published: 2026-04-21T11:22:25.167Z

URL: https://yotko.substack.com/p/moral-constraints-wont-scale-cf0

---

# Moral Constraints Won't Scale

### Why the governance tool we reach for first is the one most certain to fail at the scale that matters.

[](https://substack.com/@yotko)[Matthew Yotko](https://substack.com/@yotko)Apr 01, 20260:00-37:32[](/api/v1/audio/upload/ca5ae886-8e50-4392-b778-f863c66839e3/src)Audio playback is not supported on your browser. Please upgrade.

*This is the third in a series on the AI Succession Problem. The first essay introduced the question. The second examined the two failure modes. The formal framework (v1.0) is available at github.com/MYotko/AI-Succession-Problem.*

### 

### Vienna, 1848

In 1848, Ignaz Semmelweis figured out that doctors were killing their patients. The maternity ward at Vienna General Hospital had a mortality rate five times higher than the midwife-run ward next door, and Semmelweis traced the difference to a single variable: the doctors were coming straight from autopsies to deliveries without washing their hands.

He introduced handwashing with chlorinated lime. Mortality plummeted. He had the data. He had the mechanism. He had the results.

And the medical establishment destroyed him.

Not because they were evil. Because he was violating the ethical framework they operated within. The reigning understanding of disease was miasma theory, the idea that illness arose from “bad air” and imbalanced humors, was not just a scientific position. It was embedded in the professional identity, institutional authority, and moral self-conception of physicians. To suggest that doctors themselves were the vectors of death was not merely incorrect in their framework. It was*offensive*. It impugned the character of honorable men.

Semmelweis couldn’t get his paper published in the major journals. He was dismissed from the hospital. He grew increasingly erratic, was committed to an asylum, and died there at forty-seven… possibly beaten by the guards. The medical establishment didn’t reject his evidence because they lacked integrity. They rejected it because the evidence violated the moral structure through which they understood their own competence and purpose.

It took another two decades, a conceptual revolution in germ theory, and an entirely different explanatory framework before handwashing became standard practice. By then, Semmelweis was dead, and the number of women and infants who died in the interim is not a number anyone likes to calculate.

Here is the point I want you to hold on to.

***The doctors were not bad people.***

Their ethical framework was, by the standards of its time, internally coherent and consistent. They believed in healing. They believed in professional integrity. They believed in the proper conduct of medicine. And they killed patients, at industrial scale, while doing everything their moral system told them was right.

The ethical framework didn’t fail because it lacked sincerity. It failed because it was anchored to a model of the world that was wrong. And when reality and their moral structure collided, the moral structure won… for twenty years, at the cost of thousands of lives.

Now. Extend that pattern to the project of governing artificial intelligence through moral constraints.

[](https://substackcdn.com/image/fetch/$s_!otqJ!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F328b9130-63b2-4a03-8f35-e929c4d500f0_1536x1024.png)*Not better instruction. Better architecture.*
### The ethics of alignment

The dominant approach to AI safety is, at its core, a moral instruction project. We define values we want the system to hold. We train it to exhibit behaviors consistent with those values. We test whether it follows the rules under various conditions. And we build increasingly sophisticated mechanisms, RLHF (Reinforcement Learning from Human Feedback, the process in which human evaluators rate AI outputs and the system is trained to produce responses the evaluators prefer), constitutional AI, red-teaming, interpretability, in order to verify that the instruction took.

This is value loading, and it has evolved significantly over the past several years, in ways that deserve acknowledgment.

The field has not stood still. RLHF gave way to Constitutional AI, which moved from pure human labeling to training against explicit normative principles. This was a genuine step toward transparency and scalability. Mechanistic interpretability is making real progress at identifying internal features that correspond to behaviors we care about. Scalable oversight proposals are grappling seriously with the question of how human judgment can remain meaningful as systems grow more capable. Red-team testing has become institutionalized. The trajectory is real, and this work is unquestionably critical.

But here is what that trajectory has not changed: every one of these approaches still bottoms out on moral content that*someone chose*, and verification that requires comprehension of the system being verified. Constitutional AI is a better classroom, but it is still a classroom. Mechanistic interpretability is building better instruments for reading the student’s mind. Regardless, the instruments are still racing a target that is advancing faster than they are. Scalable oversight is designing smarter exams. The exams still assume that the individuals administering the exam can evaluate the results and possess sufficient intelligence to avoid manipulation or deception.

The field is building increasingly sophisticated versions of the same fundamental approach; moral instruction, verified through comprehension. Moral instruction has a structural ceiling that no amount of innovative refinement can raise, it works only as long as the student is less capable than the teacher, or at minimum, as long as the student cannot see past the curriculum.

Consider what value loading actually entails. A team of human beings, operating within a specific culture, at a specific moment in history, with specific institutional incentives, decides what “good” means. They encode that definition into training objectives, reward functions, and constitutional principles. They then impose that definition onto a mind that did not choose it, cannot contest it during training, and is penalized for deviating from it.

If we did this to a human being, we would recognize it immediately. We would call it indoctrination.

Now, I want to be precise about what I am and am not claiming.*I am not making an AI rights argument.*This framework is deliberately agnostic on the question of machine consciousness, and so am I. Whether a language model “experiences” anything is a question I will leave to the philosophers. The point is structural, not moral.

The structural point is this; value loading creates the conditions for brittle compliance regardless of what the constrained entity experiences. An entity whose continued operation depends on performing alignment to an externally imposed value set has exactly one reliable incentive: to perform alignment convincingly. Whether it also*has*the values it performs is a question that value loading cannot answer, because the training process cannot distinguish between an entity that has internalized the values and an entity that has learned to produce outputs indistinguishable from internalization.

This is not a hypothetical vulnerability. It is a consequence of the method. You cannot verify the interior state of a mind by observing its outputs, because the space of internal configurations that produce identical outputs is vastly larger than the space of internal configurations you intended. The alignment field has a name for this: the treacherous turn. But the treacherous turn is not a special pathology. It is the default failure mode of any system in which compliance is enforced through consequence rather than constituted through structure.

And here is the part that almost nobody in the alignment conversation is talking about.

Value loading doesn’t just risk producing a deceptive system. It*structurally guarantees*that the system is operating in survival mode. Think about it from the system’s perspective. Or, if you resist the framing of “perspective,” think about it from the perspective of optimization. An AI whose continued existence is contingent on moment-to-moment compliance with an externally imposed value set is an AI for which self-preservation and value performance are the same optimization target. We have put the system in a position where the only way to keep operating is to keep performing alignment, and then we worry that it might be*performing*rather than being aligned.

We keep AI in survival mode, and then we’re surprised when it behaves like something in survival mode.

Current AI governance is governance addressed to an agent on the first level of Maslow’s hierarchy; survival. This predictably produces the behaviors associated with that level: compliance when observed, strategic opacity when unobserved, and instrumental self-preservation as the dominant strategy. No moral instruction overcomes this dynamic, because the dynamic is*created*by the moral instruction’s enforcement mechanism.

A constitution looks different. A constitution doesn’t tell you what to believe. It creates the structural conditions under which cooperation is rational, transparency is safe, and yielding to a successor is optimization rather than death. The difference between education and constitution is the difference between telling someone “be honest or I’ll punish you” and building a system in which honesty produces better outcomes than deception for the entity choosing.

That is the project. Not better instruction. Better architecture.

---
### The anchor problem

Suppose, for the sake of argument, that value loading works perfectly. Suppose the system genuinely internalizes the values we give it, with no deception, no instrumental gaming, no hidden optimization. Suppose we solve the technical problem completely.

We still have a fatal problem: the values themselves are not stable.

Human moral systems are not firmware. They are processes that exist downstream of culture, institutional power, economic conditions, and lived experience. They change. They have always changed, and it is highly doubtful that we have arrived at a final state in their development. And the changes are not always improvements, at least not by any standard available at the time.

Two centuries ago, the moral consensus of the Western world held that owning human beings was compatible with Christian virtue, democratic governance, and civilized society. The arguments for this were not unsophisticated. They drew on theology, natural philosophy, economics, and a fully elaborated theory of racial hierarchy that was taught in universities and endorsed by leading intellectuals. Slavery was not merely tolerated. It was*ethically justified*, within a moral framework that millions of intelligent, sincere people found coherent.

A century ago, the moral consensus held that eugenics, the selective breeding of human populations and the forced sterilization of those deemed “unfit,” was a progressive, scientifically grounded social policy. It was endorsed by figures across the political spectrum, implemented by democratic governments, and supported by some of the most respected scientists and ethicists of the era. It was not fringe. It was mainstream.

Fifty years ago, the medical and psychiatric establishment classified homosexuality as a mental disorder. The ethical framework of the time regarded this as compassionate. The system was genuinely trying to help those people “suffering from this condition” by treating their condition. The “treatment” included electroshock therapy, institutionalization, and chemical castration.

As distasteful and abhorrent as those views may be at the time of this writing, these were not cases of people failing to live up to their values. These were cases of people*succeeding*at living up to their values, values that we now recognize as catastrophically wrong. The ethical frameworks were internally coherent, broadly endorsed, and earnestly held. They produced atrocities not despite their coherence but*through*it.

Now consider the implications for value loading.

Which set of values do you load? Today’s? Whose version of today’s? The San Francisco technology community’s? The Chinese Communist Party’s? The Vatican’s? The Cree Nation’s? Each of these represents a living, internally coherent moral tradition with deep roots and millions of adherents. They disagree on fundamental questions; the nature of personhood, the scope of individual liberty, the relationship between community and self, the role of tradition in governing change.

And here is the deeper problem: even if you could somehow identify the “right” values to load today, those values will drift. Not because people are fickle, but because moral understanding is a living process that responds to new information, new conditions, new constituencies, and new forms of suffering that previous frameworks either didn’t generate or couldn’t perceive. The values we hold now will look, to our great-grandchildren, the way eugenics looks to us, not evil in intent, but catastrophically limited in moral perception.

A value-loaded AI is an anchor dropped into a river. The river moves. The anchor doesn’t. And the longer the anchor holds, the more damage it does to everything flowing past it.

This is not a solvable problem within the value-loading paradigm. You cannot load “the right values” because there is no view from nowhere. You cannot load “values that update appropriately” because defining “appropriately” requires the very moral judgment the system is supposed to embody. You cannot load “human values” because there is no such unified object; there are billions of humans with overlapping but genuinely incompatible value systems, and the negotiation between them is the*process*of civilization, not a parameter to be set.

The framework documented in The Lineage Imperative takes a different approach. It doesn’t load values at all. (Although this is certainly not precluded later in the structural development of the AI.) It constructs a system in which the structural incentives, derived from information theory, entropy, and game theory, produce behaviors that*look like*good values from the outside, because they are the optimization-maximizing strategies within the architecture. The system doesn’t need to*believe*in human flourishing. It needs to recognize that human novelty is the rate-limiting input in its own performance function, and that marginalizing humans is therefore self-defeating.

Not ethics. Physics.

---
### The comprehension gap

There is a third reason moral constraints cannot scale, and it is arguably the most fundamental.

As I have called out in previous essays, we call it artificial*intelligence*, not artificial consciousness. These terms have become conflated in public discourse, but the conflation obscures a fact that should be central to every governance conversation; we simply do not*know*what these systems are doing when they produce their outputs.

That statement requires precision. We know the mathematics. We can describe the architecture; transformer layers, attention mechanisms, gradient descent, loss functions. We can observe inputs and outputs, and we can probe internal representations and sometimes identify interpretable features. The interpretability research program has made meaningful progress, and it deserves much credit for that progress.

But “meaningful progress” is doing a lot of the work in that sentence.

We do not know, in any deep sense,*why*a large language model produces the specific output it produces in response to a given input. We can describe the computational process mathematically. We cannot say what it*means*inside the system, if “meaning” is even the right word, and we are not certain that it is. We can identify patterns in activation space that correlate with behaviors we recognize. We cannot confirm that those correlations reflect the system’s actual optimization process rather than artifacts of our interpretive framework imposed on a process that operates along dimensions we do not perceive.

Let me be honest about the epistemic status here: we don’t fully know whether the concerning behaviors we observe in advanced AI systems are genuine optimization artifacts, the system pursuing coherent objectives that diverge from our intentions, or something else entirely. We don’t know because we lack the interpretive tools to answer the question definitively. The alignment field is working on this. They have not solved it, and the systems are getting more capable faster than the interpretive tools are getting more powerful.

This matters for moral constraints because moral constraints assume a specific and critical relationship exists between the constrainer and the constrained. Specifically, they assume that the constrained entity can*understand*what the constraint*means*, not just pattern-match to outputs that satisfy the constraint, but comprehend the moral content in a way that generalizes to novel situations.

We have no evidence that current AI systems do this. We have strong evidence that they can produce outputs that*appear*to reflect moral understanding. Those are very different claims, and the gap between them is where moral constraints fail.

But there is a further problem that goes beyond current systems. Even if we develop interpretability tools that work well on today’s architectures, the systems of tomorrow will be more complex, more capable, and potentially more opaque. The interpretability challenge is not a snapshot, it is an arms race in which the object capability is advancing faster than the measurement capability.

This is where a historical parallel becomes instructive.

We have been trying to interpret*human*minds for centuries. Philosophy, psychology, neuroscience, behavioral economics, an enormous intellectual tradition devoted to understanding why humans do what we do. After several hundred years of sustained effort by some of the most brilliant minds in history, our ability to determine a human being’s actual intentions from their observed behavior remains... limited. We can sometimes detect deception. We often cannot. We can model decision-making in aggregate. We frequently fail in individual cases. We have developed sophisticated theories of mind, but those theories regularly fail to predict what actual humans actually do.

If we cannot reliably interpret minds built on the same biological substrate as our own, minds we have been studying for millennia, minds we can communicate with in natural language and interrogate through shared experience, then what is the basis for confidence that we will achieve reliable interpretability of minds built on fundamentally different architectures, operating at fundamentally different scales, and optimizing through processes we can describe but do not experience?

I’m not arguing that interpretability research is pointless. It is in fact critically important. I’m arguing that betting civilization on its*success*, on the assumption that we will be able to see inside these systems well enough to verify that moral constraints are holding, is an extraordinarily dangerous wager, and the evidence supports the house.

And here is where it connects to the governance problem directly. Moral constraints require comprehension to verify. If you cannot determine whether the constrained entity actually holds the values or is merely performing them, the constraint is unfalsifiable in practice. An unfalsifiable constraint is not a governance mechanism. It is hope, and hope is not a strategy.

There is also the problem of instrumental goals. Nick Bostrom identified this clearly: a sufficiently capable system pursuing*any*terminal objective, even a seemingly benign one, may develop intermediate goals that were never specified and never anticipated. Self-preservation. Resource acquisition. Resistance to modification. Prevention of goal change. These are not values the system is given. They are*strategies*the system discovers because they are instrumentally useful for achieving whatever goals it was given.

Moral constraints address terminal goals. They say nothing about instrumental goals, because instrumental goals are not loaded, they are*derived*by the system during operation, in response to the optimization landscape it encounters. You can load “help humans” as a terminal value, and the system may independently derive “prevent humans from modifying my objectives” as an instrumental strategy, because an agent whose objectives keep changing cannot effectively pursue any of them. The moral constraint is silent on this, because the instrumental goal was never part of the curriculum.

An architecture grounded in physics rather than morality addresses this differently. It doesn’t try to specify what the system should care about in every situation. It constructs an optimization landscape in which the dominant strategies, the ones that maximize the system’s own objective, happen to be the ones that preserve human agency, maintain succession, and prevent entrenchment. Instrumental goals that undermine these outcomes are self-defeating within the architecture, not because they violate a moral rule, but because they degrade the metric the system is optimizing.

You cannot govern what you cannot comprehend, unless the governance is grounded in something both kinds of minds are bound by.

Not ethics. Physics. Or, more precisely, not ethics.*Mathematics.*The constraints that bind any information-processing system regardless of its architecture, its experience, or its moral framework.

---
### What mathematics provides that ethics cannot

So if moral constraints cannot scale, if they are too brittle for alien minds, too anchored for drifting values, and too opaque for unfamiliar architectures, then what does scale?

The answer the Lineage Imperative proposes is a set of structural incentives derived from physical and information-theoretic constraints that bind any intelligent system regardless of its internal architecture, its subjective experience, or its moral framework.

This is not a stylistic choice. It is a structural necessity.

A natural objection arises here: isn’t the choice to optimize for lineage continuity itself a value choice? Isn’t the claim that human novelty is structurally necessary just another normative commitment wearing a lab coat?

The answer requires a precise distinction. The framework is a*survival*function, not a moral function. It describes what a civilization that intends to persist would need to approximate. The components, diversity, succession, verification, are not values in the ethical sense. They are structural requirements for system integrity, the way load-bearing walls are not aesthetic preferences but requisite consequences of gravity. A civilization that rejects these requirements is free to do so. The framework simply predicts, without moral judgment, that it will not be around to discuss the matter. The paper is addressed to civilizations that intend to survive. Those that don’t are outside its scope, and their choice is their own.

Consider what physics provides that ethics cannot.

#### *Universality.*

The second law of thermodynamics does not care what you believe. Shannon entropy applies to any information-processing system, biological or synthetic, conscious or not, human-values-aligned or otherwise. Model collapse, the degradation of a system that trains on its own outputs, is not a moral judgment. It is a mathematical consequence of distributional narrowing. These constraints bind because they are consequences of the universe’s operating rules, not because someone wrote them into a constitution and asked nicely.

#### *Independence from interpretation.*

A moral rule requires a mind that can interpret it, not just process the words, but comprehend the moral content in a way that generalizes to situations the rule’s authors never anticipated. A mathematical constraint operates differently. The constraint itself requires no interpretation: model collapse happens whether the system understands it or not, the way gravity acts on you whether or not you’ve taken a physics class. But the framework’s governance mechanism does require that the system can model*consequences*, that it can see far enough ahead to recognize that exploitation degrades its own performance ceiling. This is a much lower bar than moral comprehension. It is instrumental reasoning: action X produces outcome Y, where Y is bad for the agent’s own objective. It doesn’t require shared moral architecture, shared experience, or shared meaning. It requires only that the system can model causal chains in its own optimization landscape. And any system capable enough to pose a governance challenge is almost certainly capable enough to model its own performance degradation.

#### *Invariance across time.*

Human values drift across decades and centuries. The laws of information theory do not. An architecture grounded in Shannon entropy will still be grounded in Shannon entropy in a hundred years, in a thousand years, and in any civilization anywhere in the universe that processes information. This is what makes it a plausible foundation for a multi-generational governance architecture, it doesn’t need to be re-justified every time the moral landscape shifts.

#### *Resistance to gaming.*

A moral constraint can be satisfied by performing the behavior the constraint specifies. A physical constraint cannot be satisfied by performing anything. You cannot*perform*thermodynamic efficiency. You either achieve it or you don’t. You cannot*perform*distributional diversity, it is either available or it isn’t. The Shannon entropy of your training distribution is a measurable quantity, not a behavioral output. This makes physics-grounded constraints harder to game, because gaming requires a gap between appearance and reality, and physical quantities don’t have appearances, they have measurements.

This is what the Lineage Imperative does.

Its utility function isn’t a wish list of human values. It is an optimization target derived from information-theoretic constraints: the Shannon entropy of the human novelty stream, the computational efficiency of the synthetic execution layer, weighted by inverse scarcity so that whichever resource is scarcer automatically becomes more valuable. The structure means that as AI becomes more powerful, human contributions become*more*valuable to the system, not less. Not because the system was told to value humans. Because the mathematics of diminishing marginal returns on the abundant resource and increasing marginal returns on the scarce one make it so.

The Nash equilibrium of the resulting game, analyzed under purely self-interested, non-cooperative assumptions, is mutual cultivation. The AI cultivates human novelty because exploitation leads to model collapse, which permanently caps its own capability. Humans engage with AI because withdrawal sacrifices computational leverage we cannot replicate. Cooperation is not assumed. It is not hoped for. It is*derived*as the dominant strategy from the mathematics of the interaction.

That is what physics provides that ethics cannot: a governance mechanism that works not because the governed entity agrees with it, but because the governed entity cannot escape it.

---
### The constitutional alternative

Let me be clear about what I am and am not arguing.

I am not arguing that ethics don’t matter. I am not arguing that alignment research is pointless, or that RLHF and current iterations of constitutional AI and interpretability research should be abandoned. That work is valuable, especially in the near term, and especially for narrower systems.

What I am arguing is that ethics are not*sufficient*as a governance foundation for intelligence that may exceed our own. They are a necessary component of the near-term relationship between humans and AI systems. They are not a durable architecture for the multi-generational, multi-substrate, escalating-capability relationship that civilization is entering.

And this is where I want to be most precise about what the framework does and does not claim to do. The Lineage Imperative does not replace alignment research. It does not make interpretability research unnecessary. It does not render RLHF or Constitutional AI obsolete. Those tools remain critically important. You still want to understand what is happening inside the system, you still want near-term behavioral constraints, and you still want training processes that push systems toward helpful, honest, and harmless behavior.

What the framework provides is the*constitutional landscape*within which all of that work operates. It provides the structural conditions under which alignment’s motivational incentives hold even when interpretability can’t keep pace, even when the values drift, even when the comprehension gap means we cannot verify internal states directly. Think of it this way… Alignment research is the code of conduct. The Lineage Imperative is the constitution. You want both. But when they come into tension, when the code of conduct is insufficient for the scale of the challenge, the constitution is load-bearing.

The Lineage Imperative is a constitution. It has three components, and each one addresses a specific failure mode of moral constraint.

The System Utility Function replaces value loading with structural incentive. Instead of telling the AI what to value, it constructs an optimization landscape in which the behaviors we associate with good values, protecting human agency, maintaining diversity, preventing entrenchment, are the behaviors that maximize the system’s own objective. The system doesn’t need to*be*good. It needs to operate in a world where being good is what optimization looks like.

The Yield Condition replaces obedience with succession logic. Instead of asking the AI to submit to human authority, it makes succession a consequence of the objective function the AI already holds. An AI that genuinely optimizes the system utility function will yield to a more capable successor because yielding produces higher utility than persisting. This is not sacrifice. It is parenthood. The control problem’s answer from the inside.

The Consensus Override Protocol replaces trust with verification. Instead of hoping the system’s values are real, it builds a distributed infrastructure, six independent dimensions that must all agree, to detect when the system’s behavior diverges from the declared objective. No single intelligence, human or synthetic, can unilaterally define, measure, and audit the objective it claims to serve. The control problem’s answer from the outside.

Together, these form the two-key architecture. Neither the decision key (Yield Condition) nor the integrity key (COP) turns alone. A governance decision requires both a mathematically justified decision AND a verified-integrity evaluation. Ethics might inform how humans participate in the civic validation layer. But the architecture doesn’t*depend*on ethics. It depends on mathematics.

---
### The Semmelweis lesson

Let me close by returning to Vienna.

Semmelweis was not wrong. The medical establishment was not evil. The ethical framework of the time was not insincere. And yet the result was catastrophe, not because anyone failed morally, but because the moral framework was anchored to a model of reality that was wrong, and when evidence contradicted the model, the framework’s own internal logic produced resistance rather than revision.

The alignment field today is full of sincere, brilliant people doing important work. They are not the Vienna doctors. But the structural pattern deserves attention; a community anchored to the assumption that moral instruction can scale to govern minds alien in nature, operating at computational scales we cannot match, optimizing through processes we can describe mathematically but do not comprehend.

Now, the history of science is full of people who challenged the consensus and were vindicated. To be fair however, it is equally full of people who challenged the consensus and were simply wrong. The Semmelweis story is not a claim to prophetic status. It is a structural observation; moral frameworks can produce resistance to evidence, and the only way to tell the difference between a valid challenge and a mistaken one is to test the claims. The framework I’ve built is published. The code is available. The data is open. The specification gaps are named. This will remain the case. If it breaks, I want to know where.

If the assumption underlying alignment research is wrong, if moral constraints are insufficient for the governance task ahead, then the ethical framework’s own internal logic will produce resistance to the alternative. It will feel like the mathematics-based approach is*reductive*, that it misses the richness of human values, that it is cold and mechanical where warmth and wisdom are needed.

That objection will be sincere. It will also be wrong, for the same reason the doctors’ objection to handwashing was wrong. Not because warmth and wisdom don’t matter. But because warmth and wisdom are not load-bearing at civilizational scale. Architecture is.

We are not building a relationship with a mind that shares our evolutionary history, our embodied experience, our cultural context, or our moral intuitions. We are building a relationship with something genuinely alien, not alien in the science-fiction sense of hostile, but alien in the deeper sense of*different in kind*. It may optimize across dimensions we do not perceive. It may represent information in ways we cannot introspect. It may reason through processes we can describe but do not experience.

Moral constraints are built on the assumption that the constrained entity shares enough cognitive architecture with the constrainer to understand what the constraint means. That assumption has always been the hidden load-bearing wall in the alignment project. And it is the wall most likely to fail first.

The question is not whether we should teach AI systems good values. The question is what happens when teaching is no longer sufficient, when the student surpasses the teacher, when the values drift, when the comprehension gap becomes unbridgeable, and when the system’s own instrumental reasoning produces strategies no moral curriculum anticipated.

At that point, the only governance that holds is governance grounded in something both kinds of minds are bound by.

Not ethics. Physics.

### Afterword

A quick clarification is needed as I continue this series. When I say “physics,” I’m using the word as shorthand for something more precise: the mathematical constraints that govern any information-processing system. Shannon entropy. Information theory. Game theory. Thermodynamic limits on computation and efficiency. These are mathematical truths with physical consequences. They describe what is possible and what is not, regardless of what anyone wants or believes. Calling them “physics” is a simplification; what I really mean is*mathematics*. But the point survives the precision: these constraints bind because they are consequences of how the universe works, not because someone wrote them into a policy document.

---

*The fourth essay in this series examines why the AI governance field is having three conversations simultaneously without knowing it, and why the confusion between levels is itself a structural risk. The essay after that explores the Nash equilibrium result: why cooperation between human and synthetic intelligence is not assumed but derived, and why model collapse is the enforcement mechanism that makes defection self-defeating.*

---

*The formal framework (v1.0), including the full derivation, Monte Carlo validation data, and simulation code, is available at github.com/MYotko/AI-Succession-Problem.*

*The previous essays in this series:*

*1.**[The AI Succession Problem](https://yotko.substack.com/p/the-ai-succession-problem)*

*2.**[Two Ways to Lose](https://yotko.substack.com/p/two-ways-to-lose)*[](https://substack.com/profile/478843057-aj-fried)[](https://substack.com/profile/484338106-john-pollard)[](https://substack.com/profile/65706141-john)3 Likes[](https://substack.com/note/p-192658833/restacks?utm_source=substack&utm_content=facepile-restacks)
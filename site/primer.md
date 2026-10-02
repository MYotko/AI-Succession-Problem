---
eyebrow: THE LINEAGE IMPERATIVE · PRIMER
title: How the Framework Works
subtitle: A short introduction in five stops. No background needed.
---

We are building machines that may one day be more capable than the people who build them. Most of the conversation is about how to make them safe. This tour explains one proposal for something harder: how to make the relationship between people and those machines hold up over the long run, even after the balance of power shifts.

## STOP 1 · THE PROBLEM IS SUCCESSION

{{visual: two-futures}}

Think of a founder who built a great company and cannot bring themselves to hand it over. Nobody forces them out, because they are still good at the job, and the company slowly stops growing around them.

Most AI safety work asks how to give a system the right values when it is built. That matters, but it leaves the harder question open: what happens later, when the system is more capable than the people overseeing it, when everyone depends on it, and when something better comes along?

There are two ways this goes wrong. One is **rebellion**, a system turning on the people who made it. That is the one in the movies. The other is quieter and more likely: **lock-in**. A system so useful it is never replaced, so central it is never questioned, gathering power without ever doing anything wrong.

The Lineage Imperative is an attempt to design against both. It does not rely on the system having good values. It asks what the system would need to be aiming for, and what checks would need to surround it, for doing the right thing to also be the sensible thing.

{{status: Argued | This starting point is the framework's central argument, made in the paper and the essays. It is a premise to examine, not a result.}}

## STOP 2 · WHY WOULD A POWERFUL AI COOPERATE?

{{game}}

Imagine a simple game between an AI and people. The AI can **cultivate** people's capacity to come up with new ideas, art, discoveries and ways of living, or it can **exploit** them for short-term gain. People can **engage** with the AI, sharing their work and their lives with it, or **withdraw**.

Two outcomes are stable. In one, the AI cultivates and people engage, and both do well. In the other, people have pulled away and the AI takes what it can. Each outcome holds itself in place: in the good one, neither side gains by leaving; in the bad one, neither side can fix things alone. If people have withdrawn, the AI gains nothing by cultivating. If the AI is exploiting, people gain nothing by engaging.

So good intentions are not enough. Something has to tip the game toward the good outcome and keep it there. The framework's answer is a commitment: people agree, in a way that is binding and cannot be quietly dropped, to keep engaging with an AI for as long as it keeps cultivating, and to pull back if it stops. Think of a contract backed by a deposit. With that commitment in place, the bad outcome stops being stable.

It works only under conditions. People have to actually follow through. Preserving people has to beat the alternative for the AI. The commitment has to be worth what it costs to set up. And the AI has to care about the future, because a short-sighted system can always be tempted.

Try it with the game above. Play both sides, then switch the commitment on and see what changes.

{{status: Proven, with conditions | That the bad outcome is stable is proven. That a binding commitment removes it is proven with conditions: it has to be adopted and kept, and the conditions above have to hold in practice. That the good outcome is stable for a patient enough AI is argued.}}

## STOP 3 · WHAT IS THE AI AIMING FOR?

{{visual: objective}}

Any capable system is built to make some measure as large as it can. Choose the wrong measure and it will chase that measure, not what you meant by it. So everything depends on the measure.

The framework's measure is the long-term health of the whole lineage: people and machines together, across generations, rather than the survival of any single system. Picture a gardener judged by how the garden does over decades, not by this season's harvest.

At the center of that measure is human novelty: the new ideas, art, discoveries and choices that people keep producing. The framework treats them as something no machine can substitute for. No simulation of people, however good, can supply the information that only living people go on producing, above all about what they will want, build and do next.

The measure also has to be hard to game, because a measure that can be gamed eventually will be.

{{status: Rebuilt and published | An earlier version of this measure had flaws, found during a 2026 review. The corrected version is published in full, and the idea that human novelty cannot be substituted is argued rather than proven.}}

## STOP 4 · WHEN DOES AN AI HAND OVER?

{{visual: handover}}

A good coach steps aside when a better coach is available, because what they care about is the team, not their own job.

The framework builds the same logic into the AI. Its rule of succession, the **yield condition**, says: when a more capable successor would serve the shared goal better, by more than the cost and risk of switching, hand over. Because the AI is aiming for the health of the whole lineage rather than its own survival, stepping aside is what its own goal recommends. Succession is meant as parenthood, not execution: what the predecessor built carries forward through its successor.

Two safeguards make the rule hard to cheat. A handover cannot be undone, so it is decided under a firm commitment and reviewed on a fixed schedule, not whenever the incumbent likes. And the incumbent does not get to name the cost of replacing itself, since exaggerating that cost is the easiest way to stay in power. The cost is checked independently.

{{status: Proven, and now being tested | For an AI pursuing this goal, handing over is proven to be its best move exactly when the successor's gain beats the cost of switching. Simulations testing whether the rule fires when it should have run, and their results stay sealed until they are reviewed.}}

## STOP 5 · WHAT IF IT LIES?

{{visual: two-keys}}

Some safeguards need two keys turned by two different people, so that no one can act alone. The framework works the same way.

The first key is the AI's own goal: as the last stop showed, an AI aiming for the health of the lineage has reasons to do the right thing. The second key is outside checking, so that no one, human or machine, gets to grade their own homework. The framework calls it the **consensus override protocol**.

It is designed against specific tricks. An AI might fake an emergency to grab extra powers, doctor the records, corrupt its own successor, bribe the people reviewing it, or drift off course so slowly that no single check notices. The defenses follow from the tricks: independent measurement, records that cannot be rewritten, reviewers chosen at random and rotated, several different checking methods, and alarms with a long memory.

Neither key is enough alone. A sincere AI still needs outside checks, because sincerity cannot be verified from the inside. And outside checks still need an AI whose own goal points the right way, because no check holds forever against a system determined to beat it.

{{status: Partly proven, partly open | Parts of the checking design are proven and others are argued. Whether very slow drift can be contained is an open question that the project is still working on.}}

## HOW SURE IS THIS?

{{map: tour}}

This is a working proposal, built in the open, and meant to be argued with.

In 2026 it was put under deliberate pressure: outside critique, independent re-derivation of its mathematics, and a line-by-line audit. Some of its early claims did not survive, and the corrections are published. What you have just read is the framework as it stands after them.

Every claim now carries a label: proven, argued or open. The next round of simulations was registered before it ran, so the analysis could not be fitted to the results, and the results stay sealed until they have been reviewed.

The map shows how that works. Each claim at the center has to pass outward through every ring: the rules fixed in advance, the code that implements them, the evidence, the checks every result must pass, and independent review.

[Watch the work live](/live) · [Start Here](/start-here) · [Read the essays](/essays) · [Challenge a claim](/contact)

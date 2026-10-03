# Competence Has a Maintenance Requirement

Published: 2026-09-06T20:22:57.185Z

Updated on Substack: 2026-09-06T20:22:57.765Z

URL: https://yotko.substack.com/p/competence-has-a-maintenance-requirement

---

# Competence Has a Maintenance Requirement

### We keep assuming people can take control back. That assumption has a maintenance requirement.

### Four Minutes.

In the early hours of June 1, 2009, over the Atlantic Ocean, the autopilot stopped flying Air France Flight 447.

The aircraft was an Airbus A330 carrying 228 people from Rio de Janeiro to Paris. It was cruising at 35,000 feet when ice crystals began interfering with its Pitot probes, small pressure-sensing tubes mounted on the outside of the aircraft that tell the flight computers how fast the airplane is moving through the air. For a short period, the probes began reporting inconsistent airspeeds.

That mattered because the airplane's automated systems depend on knowing how fast it is actually flying. When the computers could no longer trust that information, the autopilot, the system that had been physically flying the aircraft, disconnected. The autothrust system, which automatically manages engine power, also disengaged. The airplane handed control back to the pilots.

One of them said, "I have the controls."

A little more than four minutes later, the aircraft hit the Atlantic Ocean. All 228 people aboard were killed.

The engines had not failed. The wings had not broken off. The airplane had not suffered some immediately unsurvivable mechanical catastrophe. A temporary loss of reliable airspeed information had caused the automated flight systems to disengage, leaving the crew with a flyable airplane and a rapidly developing problem they failed to understand in time.

The airplane initially rolled right. The pilot responded with a left input and, critically, pulled the nose upward. The aircraft climbed. Its speed fell. The stall warning sounded.

A stall does not mean the engines have stopped. It means the wings are no longer moving through the air at the angle needed in order to generate sufficient lift. An airplane in a stall can have functioning engines and functioning flight controls and still fall. Recovery generally requires reducing that angle, usually by lowering the nose enough to restore airflow over the wings.

The crew correctly recognized that their airspeed information had become unreliable. What they did not recognize in time was what the airplane itself was doing. It entered a sustained aerodynamic stall. The stall warning sounded repeatedly. The crew never established a correct understanding of the condition or performed a successful recovery.

For more than three minutes, the aircraft descended toward the ocean in a stall.

Then it was gone.

There are many ways to tell this story badly, and one of them is to turn it into a morality play about pilots who had forgotten how to fly because the airplane usually flew itself.

The official French investigation did not make that finding.

The BEA, France's civil aviation accident investigation authority, found a chain involving the temporary loss of reliable airspeed information, inappropriate control inputs, failure to identify the approach to stall, failure to diagnose the stall after it developed, startle, training, cockpit information, and crew coordination. Automation was part of the environment in which the failure occurred. It was not assigned sole blame.

That distinction matters because the underlying problem is larger than one crash anyway.

We have known about it for more than forty years. In 1983, Lisanne Bainbridge published a five-page paper in Automatica called "Ironies of Automation." It became foundational human-factors literature for good reason. Her observation was almost embarrassingly simple.

Automate the tasks a machine can do reliably, and you do not eliminate the human operator. You change the operator's job.

The machine takes on more of what constitutes normal operation. The person is left monitoring it and, crucially, taking over when something abnormal happens. The work remaining for the person therefore often becomes both less frequent and simultaneously more difficult.

Meanwhile, the practice required to perform that work disappears.

Bainbridge was explicit about the consequence. Physical control skills deteriorate when they are not used. So does the operator's detailed working knowledge of what the system is doing. A human regularly controlling a process develops a feel for that process because actions produce feedback. Remove that interaction and the information needed for intervention must be reconstructed after the failure has already begun.

Her formulation is better than the popular version of "automation makes people lazy."

Frankly, laziness has almost nothing to do with it. This is architecture. The system assigns routine operation to the component that performs it better, then expects another component to remain proficient at an increasingly rare residual task without giving it the repetitions from which proficiency comes.

The strange result of this systematic progression is that automation can make the human job hardest precisely when the human has had the least recent practice doing it.

Aviation has spent decades trying to manage this under concepts like automation dependency and manual-flight proficiency. Regulators and airlines deliberately preserve some manual flying practice for exactly this reason. If pilots spend nearly all of their time supervising automated systems, the ability to take over cannot simply be assumed to remain unchanged.

That is old ground, and I'm not claiming it.

What interests me is where the same structure goes when the thing being automated is judgment.

![](https://substackcdn.com/image/fetch/$s_!wOI0!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F021f9350-ac33-4711-abf7-df9f47f5bf05_1672x941.png)

### The part that disappears

Automation is selective. Historically, it usually took the routine work first because routine work was what machines could do. Humans kept the interpretation, diagnosis, adaptation, and exception handling. Bainbridge saw the trap even there. The easier work was also part of how operators maintained a detailed mental model of the system they might eventually have to rescue.

Generative AI moves the boundary.

It can write the first draft. Diagnose the error. Recommend the architecture. Compare the alternatives. Find the precedent. Produce the analysis. Suggest the decision.

That changes the competence problem because the cognitive work we can now hand away includes some of the work through which judgment was built in the first place.

This does not mean every use of AI degrades skill. That claim would outrun the evidence badly. The exposure is narrower than that. Using a system to do work you could not have done yourself costs you nothing, because there was no stock to spend. The risk lives in using it for work you could have done, which is precisely where the practice would otherwise have gone.

The important distinction is that competence is not a file stored in a person's head. It is partly a product of repeated interaction with a problem.

Think about an experienced engineer reviewing a design.

The engineer may be able to look at a proposed architecture and say, almost immediately, that something is wrong. That speed can look like intuition detached from work. It is usually the opposite. Years of building things, breaking things, discovering what apparently harmless assumptions cost later, and being forced to reconcile models with reality have compressed themselves into judgment.

The ability to evaluate the work came from having done the work. That makes evaluation dependent on an accumulated stock of prior execution, and stocks can be spent.

Move an experienced person from doing difficult work to reviewing somebody else's difficult work and, for a while, the arrangement is excellent. They bring everything they already know to the review. Their judgment may even look more valuable because the mechanical burden has disappeared.

But what’s replenishing it?

Watching somebody else perform a difficult task is not necessarily equivalent to performing it. Approving a good answer is not the same cognitive operation as generating one from an empty page. Recognizing the correct architecture among three proposals is different from having to work forward to the correct architecture from nothing.

An advisory role can therefore consume competence accumulated during an earlier period of execution while producing very little new evidence that the competence remains intact.

That leads to the second problem. The decay can be difficult to see.

If I build something myself, reality eventually evaluates my build. The system either runs or it doesn't. A failure occurs or it does not. The prediction survives contact with operations or gets beaten to death by them.

If a machine builds it and I review the result, what’s grading my review?

Usually the same system.

I may or may not interact with the system until it provides an acceptable answer. I decide the answer looks good. Perhaps I modify it. The system produces the revision. I probably approve that one too.

Everything feels functional because the outputs remain good.

But my ability to independently create the result has not been tested. My ability to recognize a subtly wrong one may not have been tested either. The better the outputs are, the longer that can continue without producing a visible discrepancy.

Performing this way, day in and day out, I can spend a capability without getting a low-balance warning.

### Qualification is something you maintain

There is a reason high-consequence operating environments do not treat qualification as a permanent personal property.

I came up through the Navy's nuclear power program, working in reactor plant chemistry and radiological controls. One lesson from that environment has stayed with me through everything I have done since: qualification is perishable.

You do not qualify once and become permanently competent. It can never be assumed.

Two separate mechanisms exist to keep that assumption from taking hold.

Requalification periodically re-examines people against the standard they originally met. Knowledge gets tested again. Practical skills get demonstrated again. Drills do something different. They manufacture the abnormal conditions that normal operations do not supply, so that the response to a casualty gets practiced before the casualty arrives. One forces the examination. The other forces the event. People who once knew a system cold still have to prove that knowledge is available when needed.

There’s nothing unusual about this in a high-consequence environment. It’s simply an acceptance of how people actually work. Memory decays. Habits drift. Systems change. Procedures change. Personal complacency sets in. People become fluent in what they do every day and surprisingly rusty in things they once did extremely well.

More importantly, it is our human condition to fail to recognize that fact. Subjective confidence is a terrible instrument for measuring that decay. This is because the person losing the capability and the person responsible for detecting the loss are housed in the same skull. The expert's self-assessment was accurate when it was formed, and was set in stone from that moment while real capability decayed.

So, serious operational systems introduce an external forcing function. Requalification does not ask whether somebody still feels competent. It makes them demonstrate competence.

The distinction becomes critical once automation is involved, because automation can remove the natural forcing function. If you have to perform a task every week, life itself provides the examination. If a machine performs it for five years, somebody has to manufacture the examination on purpose.

### Reliability makes the problem worse

This is the part I find most worrisome.

Automation that is only somewhat reliable can protect human capability.

If a system fails every third Tuesday, nobody trusts it enough to stop knowing how the underlying work is done. Operators stay involved. Engineers retain troubleshooting knowledge. People keep manual procedures close because they need them. The failures may be expensive, but they force practice.

Reliable automation removes that forcing function.

When a system works for a year, maintaining a redundant human capability looks vigilant. After three years it looks wasteful. Why pay people to practice work they never perform? Why slow production to exercise a fallback that has not been needed? Why require somebody to solve the problem manually when the automated system can solve it faster and better?

Every locally rational incentive points in the same direction. Use the better system. Reduce duplicated effort. Move the humans to higher-value work.

Eventually, while the fallback may still exist in the organization chart and in a procedure document that nobody reads, the competence underneath it has thinned. And as long as no failure condition is present, nothing announces the transition.

This means the conditions that make fallback capability least economical to maintain are the same conditions most likely to precede the day when the fallback is needed.

Long periods of success are not evidence that the problem has gone away. They are the environment in which it can mature undisturbed.

### We are beginning to build this structure again

There is already evidence that knowledge work is moving from production toward review.

A 2025 study from researchers at Carnegie Mellon and Microsoft Research surveyed 319 knowledge workers using generative AI and collected 936 examples of real work. Workers described a shift in cognitive effort away from some forms of information gathering and problem solving and toward verification, integration, and what the researchers called task stewardship. Higher confidence in the AI system was associated with less self-reported critical-thinking effort.

The reverse also held, and it is the more interesting half. Workers who were confident in their own ability to perform a task reported more critical engagement, not less. Confidence in the tool and confidence in oneself moved scrutiny in opposite directions.

That is evidence of a changing work architecture.

It is not evidence that professional competence has already measurably degraded over years of AI use. We do not have the longitudinal record to make that claim responsibly. The technology has not been deployed broadly enough for long enough, and much of the current evidence measures behavior, effort, or short-term performance rather than durable loss of expertise.

So this is a thing to watch, not a result to declare. But the architecture is recognizable: production giving way to review, diagnosis giving way to approval, and eventually, perhaps, deciding giving way to remaining officially responsible for a decision somebody else made.

Bainbridge would recognize the shape immediately.

### The handback assumption

Nearly every reassuring story about increasingly capable AI systems contains a quiet escape hatch.

Humans can take control back.

Sometimes this is explicit. Sometimes it hides inside words like oversight, authorization, supervision, or final approval. But the concept is the same. We can delegate enormous amounts of work because the delegation is reversible. If something goes badly enough, people resume control.

That assumption is carrying far more weight than most people think it is. Preserving the institution that once performed a function is not the same thing as preserving its ability to perform the function.

The buildings, offices, departments, jobs and titles can all remain. So can the policies assigning authority and liability. None of those things guarantees that the people inside still possess the practiced judgment required to resume the work.

In some ways institutional preservation is the easier problem because destruction is visible. Someone has to close the department. Someone signs the outsourcing agreement. A budget disappears or is reassigned. A capability gets formally removed and can therefore trigger an argument about whether it should be removed.

But atrophy needs no authorization.

Nobody signs it.

There is no meeting at which the organization decides that, beginning Monday, its engineers will be ten percent less capable of designing systems without assistance.

People simply stop doing the work. Then they stop teaching the work. Then the senior people who remember doing it move on.

The organization can arrive at the other end still believing it has a human fallback because nothing identifiable ever happened to remove one.

That may be the more dangerous form of dependence. Not because control cannot formally be returned to people. Rather, because one day we may discover that formal control is all that survived.

If handback is supposed to be a real safety property, then human capability cannot be treated as a credential we preserve on paper. It has to be treated as an operating capability maintained at some demonstrably resumable level, continuously, and especially while the automated system is working.

That will look inefficient. It will look that way because it is. Redundant systems usually do look that way, right up until the reason for the redundancy arrives.

I don’t know what the right mechanism is.

Perhaps some work must remain deliberately human. Perhaps qualification has to include unaided demonstration. Perhaps organizations will need exercises analogous to disaster recovery tests, where the automated layer is removed and the humans have to prove that the underlying function still exists. Something closer to a drill than to an audit.

Perhaps those answers are crude and something better is possible.

That is a design problem, and I don’t think we have solved it.

But the requirement comes first.

If we intend "the humans can take it back" to actually mean anything more than a line in a safety case, somebody has to maintain the competence required to take it back during the long interval when using that competence appears completely unnecessary.

Because that is exactly when it will be easiest to lose.

And unlike a machine we shut down, a capability that quietly disappears from a generation of people will almost certainly not be waiting for us when we finally discover we need it.

------------------------------------------------------------------------

*The Lineage Imperative is developed in the open. The v2.0 paper, simulation code, validation data, and the full refinement record are at [github.com/MYotko/AI-Succession-Problem](https://www.github.com/myotko/ai-succession-problem). This essay is part of the AI Succession Problem series at [yotko.substack.com](https://yotko.substack.com).*

*You can engage the framework at any depth at [lineageimperative.org](https://www.lineageimperative.org)*

# Practitioner sources and design implications

Verified against publisher pages on 2026-11-19. These are selected practitioner writings, not an exhaustive literature review. They motivate the skill; their authors have not reviewed or endorsed it. The implementation and recommended experimental controls are this repository's synthesis. Do not treat an author's case study as validation of this skill.

## 1. The starting point: evaluate sessions through the UI

- **Author:** Doug Turnbull
- **Title:** Prefer synthetic traffic over LLM-as-a-judge
- **Published:** November 12, 2026
- **Source:** https://softwaredoug.com/blog/2026/11/12/agent-search-traffic
- **Verification:** Original article located and read; matches the article supplied by the user.

Turnbull has agents interact with a search application, records sessions and clicks, and studies effort across the combined UI and ranking. An orchestrator explores scenarios; browser subagents perform them. He explicitly distinguishes synthetic topical evaluation from human preferences and observes repetitive clicks and unrealistic scenarios. **Use here:** instrument the experience and retain session traces. **Limit:** varying models or requesting the Nth relevant result produces exploration diversity, not evidence of population representativeness. This skill therefore keeps exploration traffic separate from a frozen comparison cohort; that separation is our extension.

## 2. Concrete search implementation and telemetry

- **Author:** Doug Turnbull
- **Title:** I fixed Alamo Drafthouse's Search
- **Published:** November 9, 2026
- **Source:** https://softwaredoug.com/blog/2026/11/09/fixing-alamo-drafthouse-search
- **Verification:** Original article read.

Turnbull reconstructs menu search and uses synthetic browser sessions to seed query-to-product click signals, addressing prefix matching and vocabulary mismatch. He reports results from simulated sessions and says actual human traffic would teach different lessons. **Use here:** test prefixes, synonyms, zero-result recovery, and query reformulation; preserve the distinction between returned results, impressions, and clicks. **Limit:** his reported improvements are specific to his simulation. If synthetic clicks inform ranking, use separate scenarios for evaluation to avoid rewarding the system for reproducing its own generated training signals.

## 3. A direct human-versus-synthetic usability comparison

- **Author:** Stefan Rössler
- **Title:** We Ran an Experiment with Synthetic Users: Here’s What We Found
- **Published:** April 28, 2026
- **Source:** https://www.userbrain.com/blog/synthetic-users-experiment/
- **Verification:** Original publisher page read; author and date explicit.

Userbrain compares five human sessions with five synthetic sessions on its pricing prototype. Agents sometimes reproduce a real failure and sometimes solve tasks that trip humans up. Visible-only instructions and bounded reasoning make behavior more plausible, but prompt realism remains uncertain. **Use here:** constrain observations, allow abandonment, and calibrate against real sessions. **Limit:** a small, vendor-run study of the vendor's own interface, with disclosed conflicts of interest. Matching one failure does not establish that simulated success predicts human success elsewhere.

## 4. Why plausible personas are not user evidence

- **Authors:** Maria Rosala and Kate Moran
- **Title:** Synthetic Users: If, When, and How to Use AI-Generated “Research”
- **Published:** June 21, 2024
- **Source:** https://www.nngroup.com/articles/synthetic-users/
- **Verification:** Original publisher page read; both authors and date explicit.

Rosala and Moran describe favorable, shallow, and idealized synthetic responses, recommending their use for preliminary research and hypotheses rather than replacing real participants. **Use here:** clearly label synthetic findings and record the human study needed to validate each behavioral claim. **Limit:** this article primarily concerns generated research respondents, not instrumented browser agents. Its concerns motivate validation; they do not establish the measured accuracy of every current browser-agent setup. Do not use a demographic prompt as evidence that a cohort represents that demographic.

## 5. Mode collapse despite agreement on the headline result

- **Author:** Rachel Banawa
- **Title:** Synthetic Users vs. Human Respondents: Same Conclusion, Less Variation
- **Published:** October 16, 2026
- **Source:** https://www.nngroup.com/articles/synthetic-users-vs-human-respondents/
- **Verification:** Original publisher page read; author and date explicit.

Banawa compares 120 synthetic respondents with a prior survey of 604 humans. Both favor the same broad answer, but synthetic responses omit much of the human long tail. The article also identifies presentation differences, question rewording, and differing role distributions. **Use here:** report scenario and choice coverage alongside average outcomes; examine subgroup and rare-case failures separately. **Limit:** a terminology survey is not a browser task, and the cohorts have confounds. Use this as a warning against assuming diversity from persona count, not a numerical estimate of browser simulation error.

## 6. Agent competence can hide human navigation problems

- **Authors:** Jeff Sauro, Will Schiavone, and Jim Lewis
- **Title:** Using ChatGPT in Tree Testing: Experimental Results
- **Published:** April 2, 2024
- **Source:** https://measuringu.com/chatgpt4-tree-test/
- **Verification:** Publisher-authored full article retrieved through search indexing; direct page open returned HTTP 403. Author, date, methods, and findings were available in the indexed article.

The authors compare repeated ChatGPT-4 runs with 33 human participants navigating an IRS-derived tree. The model substantially outperforms typical people; changing input ordering also changes a result. **Use here:** repeated runs, observation parity, and human calibration before interpreting ease or completion. **Limit:** the model received the whole tree while humans traversed it incrementally, and the study concerns an older model and one navigation structure. It motivates avoiding hidden DOM/full-corpus access; it does not prove a current agent's performance distribution.

## 7. Keep calibrated ranking diagnostics as a complementary tool

- **Author:** Jo Kristian Bergum
- **Title:** Improving retrieval with LLM-as-a-judge
- **Published:** July 3, 2024
- **Source:** https://blog.vespa.ai/improving-retrieval-with-llm-as-a-judge/
- **Verification:** Original publisher page read; author and date explicit.

Bergum builds reusable relevance data by calibrating an LLM against human labels and pooling candidates from multiple retrieval methods. He explains that answer-rich result pages can satisfy users without clicks and that single-retriever pools bias judgments. **Use here:** retain ranking diagnostics where they localize a problem, pool candidates when judging, and support evidence of task success without clicks. **Limit:** a ranking evaluation cannot establish end-to-end human usability. This is a useful complementary approach, not evidence that agent traffic should replace all relevance judgments.

## 8. Clicks, exposure, and experimental denominators

- **Author:** Neel Mishra
- **Title:** Clicks Are Feedback, Not Relevance Labels
- **Published:** September 2026 (publisher gives month only)
- **Source:** https://neelmishra.github.io/blog/ml/search-and-retrieval/evaluation/online-experiments-and-click-bias.html
- **Verification:** Original author-hosted article read; title and month explicit.

Mishra distinguishes seeing, clicking, attractiveness, and relevance. He explains missing support in logged-policy evaluation and how conditioning on clickers can change an experiment's interpretation. All numerical examples are explicitly constructed. **Use here:** log assignment, exposure, and outcomes separately; include unsuccessful assigned sessions in denominators; never label unexamined results irrelevant. **Limit:** propensity weighting requires actual probabilities and support. This skill does not fabricate propensities or claim that viewport visibility measures attention, and synthetic confidence intervals do not quantify human impact.

## What the synthesis adds

The skill combines browser-driven sessions with controls that the starting article does not fully specify: frozen evaluation scenarios; explicit scenario/session/variant identities; isolated browser state; separate exploratory and measurement cohorts; bounded effort and legitimate abandonment; outcome verification independent of agent self-report; evidence of visibility; separation of product failures from harness failures; and reporting limits on generalization to people. These are repository design choices, not quotations or claimed endorsements by the authors above.

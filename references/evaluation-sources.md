# Evaluation methodology: practitioner sources

Research checked on 2026-11-19. These are source-linked summaries, not reproductions. The implementation choices below are this repository's synthesis; the authors did not review or endorse this skill.

## Core reading

### 1. Demystifying evals for AI agents

- **Authors:** Mikaela Grace, Jeremy Hadfield, Rodrigo Olivares, and Jiri De Jonghe (Anthropic).
- **Published:** January 9, 2026.
- **Source:** <https://www.anthropic.com/research/demystifying-evals-for-ai-agents> (the original `/engineering/` URL redirects here).
- **Contribution:** Distinguishes tasks, repeated trials, transcripts, outcomes, and graders. Recommends stable environments, unambiguous success criteria, balanced cases, and combining automated evaluation with human review and production evidence.
- **Applied here:** Verify the final selected item's constraints independently of an agent's success claim. Preserve failed trials and evaluate reliability across repetitions. Treat browser/tool failures separately from search failures.
- **Limit:** This is agent-evaluation guidance, not evidence that synthetic shoppers predict human choices. Repetition measures simulator reliability, not human representativeness.

### 2. AI Evals: Everything You Need to Know

- **Authors:** Hamel Husain and Shreya Shankar.
- **Published:** September 18, 2026; page lists modification September 21, 2026.
- **Source:** <https://hamel.dev/blog/posts/evals-faq/>
- **Contribution:** Build synthetic cases from explicit dimensions and failure hypotheses, then turn structured combinations into natural-language queries. Inspect full-system traces and compare synthetic examples with real data when available. Synthetic data cannot establish production failure prevalence.
- **Applied here:** Separate scenario coverage from wording variation; record scenario provenance and hold out evaluation cases from exploratory generation. Human review checks plausibility before scaling.
- **Limit:** Their suggested starting sample sizes are heuristics for failure discovery, not statistical power guarantees. Domain-specific nuance, low-resource language behavior, and underrepresented groups may require real examples.

### 3. Synthetic Users: If, When, and How to Use AI-Generated “Research”

- **Authors:** Maria Rosala and Kate Moran (Nielsen Norman Group).
- **Published:** June 21, 2024.
- **Source:** <https://www.nngroup.com/articles/synthetic-users/>
- **Contribution:** Synthetic profiles can support desk research and hypothesis generation, but often produce idealized behavior, shallow priorities, and overly favorable responses. They do not replace studying real people.
- **Applied here:** Label agent sessions explicitly as synthetic; constrain persistence instead of demanding success at any cost. Treat findings as hypotheses and reproducible interface defects, not customer preference estimates.
- **Limit:** This article primarily considers simulated interviews and profiles. Applying its cautions to browser sessions is a methodological inference, not a reported browser-agent experiment.

### 4. Synthetic Users vs. Human Respondents: Same Conclusion, Less Variation

- **Author:** Rachel Banawa (Nielsen Norman Group).
- **Published:** October 16, 2026.
- **Source:** <https://www.nngroup.com/articles/synthetic-users-vs-human-respondents/>
- **Contribution:** Compares 120 synthetic respondents with a prior survey of 604 people. The broad conclusion matched, but synthetic answers contained less variation, including within occupational groups.
- **Applied here:** Audit rare scenarios and subgroup coverage explicitly. Changing persona labels or increasing sample count does not itself establish diversity. Keep models and persona strata visible in reports.
- **Limit:** The experiment concerns an open-ended terminology question, not search click-through. It motivates checking mode collapse; it does not quantify browser-simulation error.

### 5. Using ChatGPT in Tree Testing: Experimental Results

- **Authors:** Jeff Sauro, Will Schiavone, and Jim Lewis (MeasuringU).
- **Published:** April 2, 2024.
- **Source:** <https://measuringu.com/chatgpt4-tree-test/>
- **Contribution:** In a ten-task navigation study, ChatGPT-4 substantially outperformed the 33 human participants; human task completion averaged about 51%. Predicting perceived ease and reproducing actual task performance were different problems.
- **Applied here:** Validate simulator behavior against human traces where available. Separate task solvability, simulated effort, perceived difficulty, and human success rates.
- **Limit:** This is a small, older-model tree-navigation study, not a modern visual-browser benchmark. The publisher's indexed article supplied the study text and author/date metadata; a subsequent direct open returned HTTP 403. No universal error rate is inferred.

## Supporting operational reading

- **The LangChain Team**, **Evaluating Deep Agents: Our Learnings**, December 3, 2025: <https://www.langchain.com/blog/evaluating-deep-agents-our-learnings>. Describes task-specific assertions, checking final state, bounded multi-turn simulations, and clean reproducible environments. Applied here as separate scenario, environment, and outcome contracts. The page's named byline is the team; individual authors are not invented.
- **Sarah Gibbons and Kate Moran**, **AI Agents as Users**, April 10, 2026: <https://www.nngroup.com/articles/ai-agents-as-users/>. Distinguishes visual interaction, accessibility-tree parsing, and direct API access. Applied here by recording the observation/action channel; success through an API cannot establish visual findability. This is design analysis, not validation of human-like browsing.

## Repository synthesis, not claims from any one source

- Use paired, frozen scenarios to compare variants; keep exploratory traffic outside the comparison set.
- Report session success separately from clicks, exposure, reformulations, abandonment, and infrastructure failures.
- Treat task scenarios as the sampling unit when estimating uncertainty; repeated runs of the same scenario are not new independent user needs.
- Keep randomized exploration in its own cohort. Asking an agent to choose its third-best result changes the policy; it does not create a representative customer.
- Record viewport-visible exposure separately from results returned or hidden in a page snapshot. A DOM-aware agent can read beyond the human viewport unless constrained.
- Use synthetic traffic for regression discovery and debugging; require human evidence before asserting customer conversion, satisfaction, or population preference improvements.

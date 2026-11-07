# Learning goals and design-standard coverage

## Owner's professional context

The owner is a 3D wiring-harness engineer. Apply this personal context to harness-related tasks; it is not a universal preference for other learners or subjects. Current explicit instructions always take precedence.

For principle learning, connect supported mechanisms to the engineer's understanding of routing, clearance, fixation, motion, assembly, protection, serviceability, and failure prevention where relevant to the selected source. Do not fabricate these connections when the source does not explain them. Do not use the profession as a reason to discard electrical principles requested by the user, or to omit selected design-standard clauses.

## Choose targets from the request

| Requested learning | Targets to extract | Failure to avoid |
| --- | --- | --- |
| Full familiarity / 全文熟悉 | All substantive functions, mechanisms, connections, examples, conditions, comparisons, and useful images; core concepts as focused tests and supporting detail on mapped backs | Selecting highlights, silently omitting secondary content, or labeling explanation-only detail as independently tested |
| Principles / 原理 | What works, how it works, why, conditions, causal relationships, source-supported consequences and design implications | Replacing a mechanism with connector IDs, cavity numbers, part numbers, or component-position lists |
| Design standard / 设计标准 | Every substantive rule, required value and unit, applicable object and condition, restriction, exception, inspection criterion, and supported application | A highlights-only deck, one card per heading, one card per clause regardless of content, or an arbitrary total |
| Explicit project-detail recall | The requested identifiers, pins, parts, configuration codes, and their project/version-specific relationships | Rejecting identifier recall even though it was explicitly requested |

Identifiers can locate evidence or disambiguate a project example without becoming the answer. Prefer a functional component name in a principle question when the source provides it; retain the exact project identifier in source context. Do not invent functional meanings for unexplained abbreviations.

Keep engineering quantities distinct from arbitrary identifiers: specified distances, angles, tolerances, forces, and other design limits remain valid and necessary standard-learning targets. Include their units, applicability, and exceptions.

If the selected input is only a connection table and the user asks for mechanisms, read relevant explanatory sections within the authorized scope. If those do not supply the mechanism, report the exact missing explanation and needed source. Do not substitute a batch of location-number cards or invent engineering causes.

## Principles: concrete contrasts in question design

These are question-design patterns, not technical claims or ready-to-submit cards. Instantiate them only from inspected evidence.

| Misaligned question for a principle request | Better target when supported |
| --- | --- |
| “这个信号接到哪个位置号？” | “这个信号如何改变部件的工作状态？” |
| “某控制器有哪些插件？请列全。” | “该功能为什么需要这种连接结构？” |
| “该固定点的编号是什么？” | “该固定方式通过什么机制限制所讨论的失效？” |
| “完整说明某插件的功能、关联件、回路类型。” | Separate the supported mechanism, a meaningful distinction, and a design consequence into individually gradable targets |

Do not force every principle into a “why” question. A causal sequence, applicability condition, or distinction can be the appropriate target. An independent verification pass must be able to answer: does recalling this answer actually practice the requested principle?

For ordinary engineering explanations, let the answer and back reconstruct the source-supported relationship between function, energy/information chains, position, and relevant conditions. A coherent process or contrast need not become several isolated yes/no cards. Use inspected images to connect the functional object with its spatial context when that helps learning. This familiarity approach does not reduce the independent clause coverage required for a design-standard task.

## Standards: one clause can require multiple cards

Read the entire selected standard with its clause structure. Inspect normative tables, diagrams, callouts, and footnotes; extracting prose alone does not establish complete coverage. Preserve source revision and page/row/figure locations when available. Unread or illegible content is an explicit gap.

Build a source-to-card coverage map before authoring. Use factual, concise records:

| Source unit | Recall target | Verified card IDs | Status |
| --- | --- | --- | --- |
| Clause/page/table row | One requirement, condition, exception, mechanism, or application target | One or more IDs after verification | Covered / needs rewrite / source gap / excluded with reason |

For each clause, inspect these dimensions without forcing absent material into cards:

- What is required or prohibited? Include each independent requirement in a compound clause.
- To which object, operating state, geometry, or configuration does it apply?
- What value, range, unit, tolerance, or pass/fail boundary must be recalled?
- What exceptions or permitted alternatives change the rule?
- Does the source explain a reason, failure mechanism, or consequence?
- Can a concrete design or inspection decision be answered solely from this rule, without introducing missing engineering assumptions?

Use as many cards as the supported, distinct targets require. Do not impose a minimum or maximum per clause. A definition may need one; a conditional requirement with exceptions and an explained mechanism may need several. A source-supported application card can coexist with a direct rule card when it tests interpretation or rule selection; merely changing names or numbers in the same question adds no new target.

For example, suppose a **hypothetical** clause states: “Under condition C, clearance between objects A and B must be at least d; when condition E applies, protection P is permitted instead.” Candidate targets include the clearance requirement, condition C, exception E and its permitted alternative, and an application requiring selection of the correct branch. Any rationale requires additional source evidence. The question must not display d and then ask the learner to recall d. This example defines no real engineering limit.

Keep one gradable target per card. This does not mean one card per clause, nor does it mean replacing a meaningful rule with isolated word blanks. Necessary conditions belong in the question even when the condition also deserves its own separately focused card.

Do not hide an untested requirement in an explanation and mark it covered. Do not merge different requirements just because they cite the same sentence. Remove true duplicates while preserving all independent learning targets.

## Completion and reporting

For a full-standard request, finish the requested scope rather than stopping at a sample or selected highlights. Use multiple generation/submission batches when necessary, maintaining the same coverage map and stable concept-based IDs. A sample is appropriate only when the user requests or chooses that scope; do not make repeated approval a default workflow.

Report both clause coverage and recall-target coverage: source units inspected, units still unread, targets identified, targets with verified cards, and unresolved targets with reasons. Count requirements in tables and notes, not just headings. “All examined cards passed” is different from “all selected source requirements were covered.” Any unresolved requirement prevents a claim of complete coverage.

Coverage records and verification outcomes belong in the work report or companion audit artifact, not unsupported extra fields in a submission schema. Keep reports factual: source location, target, card IDs, result, and concise issue. Do not provide private reasoning transcripts. A format validator cannot establish these semantic outcomes.

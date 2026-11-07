# Deep Flashcards v2 Quality Workflow

Use this workflow for both new generation and review of existing cards. Its roles are quality checkpoints, not decorative personas. The workflow is designed to produce a *complete* set of durable cards, not a minimal sample — coverage gaps are treated as seriously as unsupported claims.

## 1. Scope contract

Work only from the source selected by the user. For a search result set, deduplicate source documents before reading them. For a long document, preserve its heading and block boundaries and inspect the relevant source text; do not treat a lossy summary as evidence.

If the user specifies learning goals, audience, exclusions, answer style, or preferred card types, use those as batch preferences. For ordinary explanatory notes, default to full familiarity with distinct core retrieval targets: cover all substantive content across questions, answers, connected explanations, and purposeful source media. Resolve independent-recall and standard-mastery goals separately; their required targets cannot be left only in explanations. Use [full-material-learning.md](full-material-learning.md) for the coverage modes and source-unit/media reconciliation.

State the learning objective briefly using available user context. Separate what must be understood from identifiers needed only to locate the evidence. For the owner's harness work and for design standards, apply the entrypoint's learning profile. Full-standard scope includes all substantive clauses; do not silently select only the clauses an agent considers most useful for the profession.

## 2. Knowledge curator (be inclusive here)

Build an internal evidence ledger before writing questions, working through the source section by section so nothing is skipped. Each entry contains:

- one declarative knowledge claim;
- one candidate learning target with its intended recall or familiarity requirement;
- a short exact excerpt that supports the answer;
- source identity and location;
- why remembering it will remain useful;
- the most natural retrieval mode: recall, recognition, exact entry, order, or spatial identification;
- when available, the surrounding reason, mechanism, exception, or consequence — this becomes the card's `explanation` later, so capture it now rather than discarding it.
- source-unit identity and image/caption relationships, with supporting examples and details that may become familiarity context.

At this stage, reject a candidate only when it is unambiguously unusable:

- navigation, heading text, boilerplate, or a restatement of the document structure;
- a transient task, timestamp, status, or unresolved question, unless the user explicitly wants it;
- self-contradictory material with no authoritative resolution in the source.

Do **not** apply judgment calls here about ambiguity, compound structure, standalone-ness, or "general" value — those belong to the adversarial verifier in step 4, which is better positioned to test the actual drafted card against its hard gates. Filtering the same borderline candidate twice, once loosely here and once strictly later, is what causes valid material to disappear from the final batch. When in doubt at this stage, ledger the candidate and let the verifier decide.

Number the ledger entries so every later draft and rejection can be traced to one candidate. Preserve a parent source-clause ID and use subentries for distinct targets from that clause (for example 12.a, 12.b). A clause may carry a requirement, applicability condition, exception, and decision target; one clause is not one card. Do not draft cards during this pass.

## 3. Card writer

For each ledger entry, write a focused card or propose explicit supporting placement on a related card in familiarity mode. The verifier decides whether that placement meets the objective; no substantive point may disappear merely because it is not independently quizzed.

- Ask for exactly one retrieval target.
- A complete distinction, mechanism, or process can be one target. Avoid splitting it into disconnected fragments that no longer teach the relationship.
- Include the minimum context needed to make the question standalone.
- Preserve necessary qualifiers, conditions, units, direction, and attribution.
- Prefer a short canonical answer. Put supporting detail in `explanation`, not in the tested answer.
- **Write a real `explanation`** whenever the ledger entry carries a reason, mechanism, exception, contrast, or consequence — this is the default expectation, not an optional extra. A card with only a bare answer and no explanation should be the exception, reserved for genuinely self-contained recall (a definition, an acronym, a single number) where nothing else would help the learner.
- Do not copy a whole source sentence and replace an arbitrary phrase with a blank.
- Preserve relevant examples and secondary conditions in the card set. The explanation should connect them to the answer, not merely restate the answer or point back to a source URL.
- Do not create both a QA and a cloze for the same fact.
- Do not force multiple-choice, ordering, typed-answer, or image-occlusion when QA tests the knowledge better.

Retain the originating ledger number on each internal draft. Draft `evidence`, `source`, `confidence`, and `idempotencyKey` with the card; they are part of quality, not post-processing metadata.

## 4. Adversarial verifier (the single home for subjective judgment)

Verify every draft independently against the source. This is the only pass that should reject a card for reasons of ambiguity, compound structure, standalone-ness, or low retrieval value — the curator pass has already deferred those calls here. Apply all hard gates:

| Gate | Pass condition |
| --- | --- |
| Learning-goal alignment | The tested answer exercises the requested understanding or skill. Identifier recall does not stand in for a requested mechanism or principle. |
| Grounding | The answer and every necessary qualifier are directly supported by the exact evidence. |
| Atomicity | The card tests one recall target and can be graded as one unit. |
| Unique answer | A prepared learner has one clearly intended answer; reasonable synonyms are either accepted by the card form or make typed entry unsuitable. |
| Standalone context | The question is understandable without the surrounding paragraph or hidden application state. |
| No leakage | The visible question, options, or question media do not reveal the answer through wording, grammar, length, or labels. |
| Retrieval value | Remembering the answer supports understanding, discrimination, procedure, or future decisions. |
| Faithful difficulty | The question is neither trivialized by clues nor made harder by missing context. |
| Type integrity | Structured data, answer, evidence, and media agree exactly with the chosen card type. |
| Explained, not bare | If the ledger entry carried a reason, mechanism, exception, or consequence, the card's `explanation` reflects it. A missing explanation on a card that clearly had one available is a defect to repair, not a pass. |
| Material represented | Every assigned substantive point is actually present in the final field or useful media, with its conditions; independent-recall requirements are tested, while familiarity-only bindings are identified separately. |
| Media usable | Each intended image was inspected, supports the card, decodes at readable quality, and has deliberate placement. Unknown regions remain unknown; question media do not reveal the answer. |

Reject rather than repair when the underlying knowledge target is weak or unsupported. Repair wording, structure, or a missing explanation when the evidence ledger contains a strong target — a fixable presentation problem is not the same as an unsupported claim, and should be fixed rather than discarded.

For each rejection, record the ledger number, exact source location, rejection code, and a concrete explanation of the failed gate. Later roles must consume only surviving records and must not restore a rejected candidate.

Use concise rejection codes in batch reporting:

- `unsupported`
- `goal-mismatch`
- `compound`
- `ambiguous`
- `context-dependent`
- `answer-leak`
- `low-value`
- `transient`
- `duplicate`
- `type-mismatch`
- `media-reveals-answer`

## 5. Confidence

Confidence represents source support, not the model's general certainty:

- `0.95–1.00`: explicit evidence directly states the complete answer and qualifiers;
- `0.85–0.94`: direct evidence supports a faithful, minimal paraphrase;
- `0.80–0.84`: support is sufficient but requires nearby context or a modest inference — this is a normal, common band, not a signal to discard the card;
- below `0.80`: reject by default rather than submit.

Do not raise confidence because a fact is familiar from general knowledge. Do not use outside knowledge to fill a source gap. Do not systematically under-score a well-supported card out of general caution — confidence should track the evidence in front of you, not a reflexive hedge.

Do not assign one default confidence to every card and treat the threshold check as verification. Verify support for the explanation as well as the answer. An engineering rationale that merely sounds plausible is not source evidence. Record factual verification outcomes, not private reasoning or ceremonial role-play.

## 6. Batch editor

Review the verified batch as a set:

- merge cards that test the same proposition even when worded differently;
- remove cosmetic inversions and repeated facts across card types;
- **reconcile coverage**: walk the source's headings, sections, or steps against the surviving cards and the original ledger. For any major point with no surviving card, determine whether it was rejected for a real, nameable quality reason (cite the rejection code) or whether it should be added back into the batch. A batch that quietly skips whole sections of a substantive source has a coverage defect, even if every individual card in it is high quality.
- prefer foundational concepts over peripheral examples, but do not let "foundational" become an excuse to drop a legitimate secondary point (an exception, a contrast, a boundary condition) that a learner would plausibly need;
- avoid several cards whose answers are overlapping fragments of one concept;
- retain distinct cards only when they require meaningfully different retrieval;
- keep enough cards for all required independent targets; supporting familiarity entries may share a related back, without count minimization or a fixed expansion quota;
- reconcile standards at clause and subtarget level, including normative table cells, figure annotations, and footnotes. Map each target to verified card IDs or a specific unresolved/excluded status. An explanation-only mention does not count as retrieval coverage;
- derive coverage totals from this actual mapping. Never hard-code an empty gap list or exclude unresolved targets from the denominator to claim full coverage. Report source-reading gaps separately from targets rejected after reading.
- reconcile ordinary full-material learning by paragraph, table row/notes, example, condition, and image rather than section names alone. Separate material coverage from recall coverage; explanation-only detail can satisfy familiarity but is not an independent test.
- check actual final text/media bindings. A source appendix or generic mention of the topic is not enough to mark material covered.

When the user requests a large number but fewer cards pass real scrutiny, return fewer and report the shortfall, naming the coverage gaps and why they didn't survive. Never lower the gates to meet a count, and never suppress a sound card just to keep the batch small.

## 7. Evidence and source invariants

- `evidence` is a verbatim minimum complete excerpt, not a generated summary. It is usually no more than 300 characters, but necessary conditions, qualifiers, units, or exceptions must not be removed merely to meet that guideline.
- The excerpt must come from the selected source and support the tested answer on its own or with immediately adjacent context.
- Preserve available Hub IDs, block IDs, content hash, title, and exact path or deep link.
- Never synthesize missing identity values.
- For user-pasted text with no path, use a truthful readable source title and omit unavailable identifiers.

## 8. Feedback calibration

Read the scoped, active Hub rules using the feedback workflow before curating. Keep current explicit learning goals ahead of persistent defaults and specific scope ahead of general scope. Apply subjective preference gates once during verification. Source support remains mandatory.

Use relevant accepted, edited, and rejected examples as evidence of batch-local preferences. Do not promote a single comment or difficult recall rating to a global prohibition. A rejected configuration-value target may still support a source-grounded mechanism or decision card. Record rule-based exclusions separately from unread material and coverage gaps. Never claim all source targets are covered when some were intentionally excluded.

Preserve rejection target/source identity to avoid rephrasing an explicitly excluded target. Report retrieval errors and do not claim to have consulted feedback when the service failed. Generation alone must not change active Hub rules. An explicit user request to update this skill authorizes scoped workflow edits, not changes to Hub's live preferences or cards.

Report useful source-reading, material-coverage, and recall-target counts, media dispositions, unresolved gaps, and actual submission/export state. When revisions or rejections matter, summarize them with a few representative source locations and preserve the complete log in a companion artifact. Do not reveal private reasoning traces.

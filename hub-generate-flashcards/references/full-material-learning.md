# Full-material learning and source images

Use this reference for ordinary source-to-learning requests, explicit “全文熟悉／全面覆盖”, feedback about omissions or fragmented cards, and image-bearing sources. A specific user-selected subset or a different learning objective takes precedence. The rules describe learning coverage; they do not authorize expanding the source scope or editing live Hub cards.

## Choose the coverage objective

| Objective | What completion requires | Role of explanation |
| --- | --- | --- |
| Full familiarity / 全文熟悉 | All substantive concepts, mechanisms, examples, conditions, distinctions, and useful visual information have an identified place in the learning set. | Supporting detail can be learned on related backs; report this as familiarity coverage. |
| Independent recall / 背诵、考试、逐项掌握 | Each independently needed fact or decision has a gradable retrieval target. | Explains the answer; mentioning another fact does not independently test it. |
| Design-standard mastery | Every substantive requirement, value/unit, applicability condition, restriction, exception, note, and supported application is independently covered. | Adds rationale and examples; cannot replace required rule recall. |
| Selected highlights or sample | Only the explicitly selected subset. | Do not silently expand to the whole document. |

For ordinary explanatory notes, start with full familiarity and distinct core retrieval targets. Decide which supporting points need their own tests from the user's goal and their practical importance. Do not impose a card-count quota, a universal length for explanations, or a rule that every sentence must become a question.

Material coverage and recall coverage are different measurements. A point present only in an explanation can satisfy familiarity, but never claim it was independently tested. State unresolved source gaps and exclusions even if all examined cards pass.

## Source units and the inclusive ledger

Read the whole selected scope with its original structure. Inventory:

- paragraphs and callouts;
- table rows, separate requirements within cells, notes, and units;
- examples, counterexamples, conditions, exceptions, and consequences;
- images, readable labels, captions, and their relationship to the text;
- provenance and navigation, whose contents may belong in a source view rather than a recall card.

A heading is not a coverage unit sufficient to prove the section was covered. A table row may support several distinct targets; an example may belong to a mechanism card without being a new target. Preserve all of them in the ledger before judging card quality.

Unresolved labels, illegible regions, unavailable pages, and contradictory claims must have named gap records. Do not invent them to make the coverage percentage look complete. Record all supplied images, even when the final decision is that a picture adds no learning value.

## Write connected cards

The front asks for one gradable learning target. That target can be a complete functional distinction, causal relationship, process, or design decision. Atomicity does not require stripping a mechanism into isolated nouns or splitting every boundary into a generic “能否” question.

The answer gives a sufficient, correct core response. The explanation connects the available source material, typically:

1. what the object does and for whom;
2. how energy, information, or a process moves;
3. why the stated arrangement or condition matters;
4. an example or comparison;
5. limits, alternatives, and consequences.

Use only the dimensions actually supported by the source; this is a reasoning guide, not a mandatory five-part template. Keep related qualifiers with the claim they limit. Mark engineering interpretation, supplier examples, and confirmed project facts separately.

For example, a source explaining that door entry and local starting require different key regions supports a question about why interior detection is needed. Its back can retain the owner-outside/window example, the authentication-versus-position distinction, and the source's scope limits. If local-start position is an independently required recall target, keep a focused test for it too. Do not ask the learner to list every unrelated detail of the system in one response.

An explanation should develop understanding. Repeating the answer, attaching a generic warning, or dumping an unrelated chapter on the back does not do this. Include targeted source passages when rereading helps; full familiarity does not require indiscriminate verbatim duplication. Keep quotations within applicable source-use limits.

## Reconcile actual content, not promises

Keep the coverage map in a companion artifact, not extra unsupported submission fields. Useful rows contain:

| Source unit/location | Claim or detail | Required coverage | Card key and field/media | Verified result |
| --- | --- | --- | --- | --- |
| Actual paragraph/table/figure ID | One substantive point | Recall or familiarity | Stable card key; question, answer, explanation, or media placement | Present, needs rewrite, source gap, or excluded with reason |

Check each binding against the final card, not an earlier draft. For exact passages, verify actual text inclusion. For a paraphrase, verify that every substantive point and qualifier survived. A link, a generic topic mention, or a full-source appendix alone is not card coverage. A full picture alone does not explain an unrecognized label or establish a circuit.

Report separately:

- selected source units, units read, and unread/illegible units;
- substantive material represented across card fields and purposeful media;
- independent retrieval targets, shared tests, and explanation-only points;
- rejected or excluded points and unresolved gaps;
- source-image inventory and included/unusable/pending dispositions.

Derive totals from the mapping. Do not remove unresolved entries from the denominator or prefill a gap-free status. Review rejection outcomes before finalizing: a rejected question may need better wording or contextual placement, rather than deletion of its worthwhile source content.

For standards or explicit independent recall, any required item left only in context remains a recall gap. This mode must not be relaxed merely because the source is long or a familiarity deck would have fewer cards.

## Source images

Inspect the original image before use. Ask what it helps the learner see: object identity, location, relation, mechanism, or process. Normal QA cards can include images; visual material does not require occlusion cards.

Choose placement deliberately:

- `question`: the picture is needed to answer and does not expose the answer;
- `answer`: visual confirmation after the response;
- `explanation`: spatial or mechanism context, not required for retrieval.

An unmasked, labeled diagram normally belongs on the answer or explanation when its labels would reveal the requested answer. Occlusion requires inspected, source-supported labels and accurate geometry. Never invent hidden labels, rectangle coordinates, or component identities.

Keep source bytes intact by default. Preserve the full readable original rather than compressing it into an unreadable thumbnail to satisfy a transport limit. Partial obscuration can coexist with useful readable context; identify the unknown portions. Exclude purely decorative, wholly illegible, misleading, or irrelevant images with a concrete reason. Do not attach every image to every card or invent a media quota.

For Hub, use attachment import/read tools when available and preserve their returned media objects. For verified HTTP(S) assets, check availability and actual image content where tools allow it; a successful response containing a login page is not an image. Do not use a known broken link, invent `hub-media://` / `craft-media://` IDs, or expose credential-bearing API URLs as media links.

Check both storage and display: the intended card has the media object, the image decodes, the relevant detail remains legible, and its placement does not leak the answer. Uploaded attachment count is not proof that cards display images.

## Fallback and revision

Use fallback only when the submission tool is absent, as the entrypoint specifies. For a local `hub-flashcards-v1` bundle, an inspected original may be embedded as a validated Base64 `data:` image. The validator distinguishes inline payloads from short network URLs; the 16 MiB per-file bundle limit still applies. Split oversized batches without changing stable concept keys, or preserve original attachments plus exact pending bindings if the media cannot join the transport. Do not downsample away learning detail or silently export text-only cards as a complete image result.

A local validation pass does not prove the live Hub API accepts the same payload or renders it. For direct submission, obey the tool's actual schema; do not alter a local validator to bypass a live transport rejection. Report text exported, media embedded/bound/pending, drafts submitted, and Hub acceptance as separate states.

For full-material or image-bearing fallback delivery, provide a reviewable preview with the actual questions, backs, and media, plus the coverage map. A source-reading view can preserve context and provenance when useful; it complements rather than replaces mapped card coverage. Verify generated interactions and image decoding before calling the preview functional. Include full-text/coverage navigation when it materially helps the requested full-material study; it is not a mandatory UI for a tiny source.

When improving an earlier deck, read the referenced cards and source. Reuse the key for the same retrieval target; list genuinely new, merged, and retired targets. Do not append a revision number to all keys to evade deduplication. Update local artifacts in a reversible, reviewable way, and do not claim existing Hub cards were revised unless a supported, authorized Hub operation actually did so.

Existing questions alone do not establish completion when their backs omit needed explanations or images. Treat that as revision work rather than a zero-card result or a reason to create cosmetic duplicates. Use the supported quality-review workflow when it applies and is authorized; draft submission must not be described as an update to live cards.

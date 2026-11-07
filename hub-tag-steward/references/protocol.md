# Hub tag-governance protocol

Read this reference when comparing tags, auditing a taxonomy, or producing a structured governance proposal.

## MCP data contracts

- `hub_tag_catalog` returns paginated stable tag IDs, normalized labels, entity counts, library counts, and source distributions. Continue with `nextCursor`; do not assume one page is complete.
- `hub_tag_profile` returns usage, sparse-evidence flags, weighted neighbors, and a small evidence sample.
- `hub_tag_compare` returns intersection, union, A-only, B-only, Jaccard, directional overlaps, and three evidence sets.
- `hub_tag_evidence` expands `all`, `intersection`, `onlyPrimary`, or `onlyCompare`. It returns limited snippets and stable source identifiers, not entire documents.
- `hub_submit_tag_governance_proposal` stores a reviewed `hub.tag-governance.v1` proposal in Hub. It does not modify source tags; use it only after the user asks to save or submit.
- `hub_list_tag_governance_proposals` lists pending or resolved proposals and can filter by tag.
- `hub_preview_tag_governance_proposal` compares the saved and current `indexRevision` and reports current entity counts. Re-analyze stale proposals.
- `hub_resolve_tag_governance_proposal` marks a proposal accepted or rejected. Acceptance requires the latest preview's `taxonomyRevision` as `expectedTaxonomyRevision`, materializes supported relationships only in Hub's internal taxonomy, and never mutates source tags. Rejection does not require a taxonomy version because it creates no relationship.
- `hub_tag_taxonomy` returns accepted internal relationships and an independent `taxonomyRevision`.
- `hub_tag_taxonomy_health` deterministically reports structural issues and the proposal IDs that created them. It does not decide which relationship is semantically wrong.
- `hub_preview_tag_taxonomy_repair` simulates withdrawing an exact set of accepted proposals. It returns before/after health, issue differences, and a confirmation token without saving changes.
- `hub_apply_tag_taxonomy_repair` atomically applies only the exact previewed set after explicit user confirmation. It rejects stale revisions, mismatched tokens, non-improving plans, and plans that introduce a new critical issue. It modifies no source tags.
- `hub_list_tag_taxonomy_repairs` returns immutable batch-repair audit records with the exact proposal set, before/after taxonomy revisions, before/after health, and issue-count changes.
- `hub_withdraw_tag_governance_proposal` requires the latest preview's `taxonomyRevision` as `expectedTaxonomyRevision`; a missing or stale relationship version must stop the withdrawal.
- All responses include `indexRevision`. Record it in proposals so later code can detect stale analysis.

`indexRevision` tracks indexed source evidence. `taxonomyRevision` tracks only Hub's internal accepted relationship set. A change to either can invalidate a previous judgment, but only a taxonomy change invalidates a repair confirmation token.

`confidence` on a neighbor means P(neighbor | current tag), not model confidence. `lift` indicates whether the pair occurs together more than expected from overall frequency. `jaccard` measures shared membership over the union. None of these metrics alone determines semantic equivalence.

## Classification boundaries

- `keep_separate`: distinct concepts or operating contexts whose boundaries matter.
- `related`: meaningful association without equivalence or containment.
- `alias`: the same concept under a retained alternate label; useful for retrieval or legacy terminology.
- `merge`: equivalent intent and boundary, where rewriting membership to one canonical tag is desirable.
- `parent_child`: every child instance is conceptually within the parent, while the parent has valid instances outside the child.
- `split`: one label conflates multiple stable concepts that can be separated using evidence.
- `retire`: obsolete or accidental label with a clear replacement or no remaining valid use.
- `insufficient_evidence`: available examples cannot establish a safe boundary.

High overlap can still mean parent-child or a workflow convention. Low overlap can still mean duplicate labels used inconsistently. Use the exclusive examples to decide.

## Proposal shape

Return this structure when a machine-readable proposal is useful:

```json
{
  "schemaVersion": "hub.tag-governance.v1",
  "indexRevision": "revision returned by Hub",
  "recommendations": [
    {
      "id": "stable recommendation id",
      "type": "keep_separate|related|alias|merge|parent_child|split|retire|insufficient_evidence",
      "sourceTagIds": ["normalized tag id"],
      "targetTagId": null,
      "confidence": 0.0,
      "rationale": "short boundary-based explanation",
      "evidenceEntityIds": [],
      "cautions": [],
      "executed": false
    }
  ]
}
```

When submitting, add a stable `idempotencyKey` derived from the analysis scope and revision so retries cannot create duplicate inbox items. Keep `executed` false for every recommendation.

Use confidence as calibrated judgment, not decorative precision. For sparse evidence, lower confidence and explain the stopping condition.

## Two-phase repair contract

For structural repair, separate suggestion, confirmation, and execution:

1. Diagnose with `hub_tag_taxonomy_health`.
2. Resolve every issue's `proposalIds` to saved accepted proposals and perform the semantic evidence workflow.
3. Call `hub_preview_tag_taxonomy_repair` with sorted, unique candidate IDs and the current `taxonomyRevision`.
4. Show the user the exact candidate IDs, relationship effects, resolved and introduced issues, and health-count change. Do not execute in the same turn unless the user had already explicitly authorized that exact batch.
5. After explicit confirmation, call `hub_apply_tag_taxonomy_repair` with the same IDs, the preview's `taxonomyRevision`, and its `confirmationToken`.
6. Re-read health after success. Use `hub_list_tag_taxonomy_repairs` when the user asks to verify or explain what a completed batch changed. On any stale/version/token failure, discard the confirmation and start again from preview.

The token is scoped to the exact relationship version and proposal set; it is not permission to change source tags or to substitute different proposal IDs. A failed safety gate is a stopping condition, not a reason to fall back to repeated `hub_withdraw_tag_governance_proposal` calls.

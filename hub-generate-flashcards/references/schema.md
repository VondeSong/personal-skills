# hub-flashcards-v1 schema

Create this directory:

```text
hub-flashcards-v1/
├── manifest.json
└── cards.jsonl
```

## manifest.json

```json
{
  "format": "hub-flashcards-v1",
  "version": 1,
  "deckName": "Deck name",
  "cardsFile": "cards.jsonl",
  "generator": {
    "agent": "codex",
    "workflow": "deep-flashcards-v2"
  }
}
```

Required fields: `format`, `version`, `deckName`, and `cardsFile`. Keep `cardsFile` in the same directory as the manifest.

## cards.jsonl

Write one JSON object per line:

```json
{"question":"What does RPM mean for an API?","answer":"Requests Per Minute.","explanation":"It measures request frequency.","cardType":"qa","tags":["API"],"confidence":0.96,"evidence":"RPM (Requests Per Minute)","source":{"sourceLibraryId":"library-id","sourceDocumentId":"document-id","sourceBlockId":"block-id","sourceTitle":"Rate limits","sourcePath":"obsidian://open?vault=Notes&file=api%2Frate-limits","sourceHash":"source-content-hash"},"media":[{"title":"Rate-limit diagram","mimeType":"image/png","url":"hub-media://0123456789abcdef","placement":"explanation"}],"idempotencyKey":"notes-api-md:rate-limits:rpm"}
```

Structured card examples:

```jsonl
{"question":"An API request-frequency limit is commonly abbreviated as {{RPM}}.","answer":"RPM","cardType":"cloze"}
{"question":"Which limit measures requests made per minute?","answer":"RPM","cardType":"multiple_choice","cardData":{"options":["RPM","TPM","RPD"],"correctIndex":0}}
{"question":"Type the abbreviation for Requests Per Minute.","answer":"RPM","cardType":"typed_answer"}
{"question":"Put the request lifecycle stages in order.","answer":"Authenticate\nValidate\nExecute\nRespond","cardType":"ordering","cardData":{"items":["Authenticate","Validate","Execute","Respond"]}}
{"question":"Which labeled component is hidden in the diagram?","answer":"Pressure sensor","cardType":"image_occlusion","cardData":{"occlusions":[{"x":0.18,"y":0.24,"width":0.16,"height":0.1,"label":"Pressure sensor"}]},"media":[{"title":"System diagram","mimeType":"image/png","url":"hub-media://0123456789abcdef","placement":"question"}]}
```

### Constraints

- Maximum 5000 cards and 16 MB per file.
- `question`: required, 3–1000 characters.
- `answer`: required, 1–4000 characters.
- `explanation`: optional in the base transport, up to 2000 characters, but expected in practice whenever the source supports a reason, mechanism, exception, or consequence for the answer. Leave it empty only for genuinely self-contained recall (a definition, an acronym, a single number) where no extra context would help. Under the `deep-flashcards-v2` profile, `validate_bundle.py` prints a non-fatal warning when a large share of a batch has no explanation, as a signal that the batch may be capturing isolated facts instead of the reasoning around them.
- `cardType`: `qa`, `cloze`, `multiple_choice`, `typed_answer`, `ordering`, or `image_occlusion`.
- `cardData`: required for structured card types:
  - `multiple_choice`: `{ "options": [2–8 unique strings], "correctIndex": <zero-based integer> }`. `answer` must exactly equal the selected option.
  - `ordering`: `{ "items": [2–20 unique strings in correct order] }`. `answer` must equal the items joined with `\n`.
  - `image_occlusion`: `{ "occlusions": [1–64 rectangles] }`. Each rectangle contains finite `x`, `y`, `width`, and `height` values in normalized 0–1 image coordinates, stays inside the image, has width and height of at least 0.01, and may include a `label` of at most 120 characters. At least one `media` item must have an `image/*` MIME type.
- Omit `cardData` for `qa`, `cloze`, and `typed_answer`.
- `tags`: optional array, at most 20 strings, each at most 60 characters.
- `confidence`: optional number from 0 to 1.
- `evidence`: optional source excerpt, up to 2000 characters.
- `source`: optional object. Populate every identity field available from the input; never fabricate IDs, hashes, vault names, Craft spaces, or document identifiers. `sourceTitle` is the readable label. Preserve an exact `https://`, `obsidian://`, or `craftdocs://` location in `sourcePath` when the source or Hub provides one; otherwise preserve the supplied path.
- `idempotencyKey`: strongly recommended, stable, and at most 240 characters.
- `media`: optional array of `{title,mimeType,url,placement}`, at most 8 items. `placement` is `question`, `answer`, or `explanation`; omitted placement remains backward-compatible and defaults to `answer` for normal cards. The local v1 bundle supports `https://`, `http://`, `data:`, `hub-media://`, and Hub-returned `craft-media://` URLs. Obey the actual live tool schema for submission; local support alone does not prove live acceptance. Normal cards may use media. New `image_occlusion` output must place its image on `question`; legacy occlusion records with no placement remain valid.
- Media reference URLs are at most 8000 characters. Inline `data:` content is instead bounded by the 16 MiB per-file limit, including all repeated image data in `cards.jsonl`. For originals, prefer `data:image/jpeg;base64,...` or the matching real MIME type. The declared MIME type must match `mimeType`, the payload must be non-empty, and Base64 or percent encoding must be valid. The validator checks this encoding, not that the bytes are a meaningful/readable image. Inspect and decode the actual source image separately.
- `customFields`: optional object with at most 20 stable field names. Each name is 1–60 characters and each value is a string of at most 500 characters, a finite number, or a boolean. Emit it only when the active submission transport explicitly supports it. Store images in `media`, not `customFields`.

### Deep Flashcards v2 quality profile

The transport remains `hub-flashcards-v1`; `generator.workflow: deep-flashcards-v2` opts into the stricter generation profile. For v2 bundles produced by this skill:

- `question` is at most 240 characters and `answer` is at most 800 characters;
- `evidence` is required, non-empty, and copied verbatim from the selected source. Use the minimum complete excerpt, usually no more than 300 characters, without dropping necessary conditions or qualifiers; the base transport limit remains 2000 characters;
- `source` is required and contains a truthful `sourceTitle` plus every identity or location field actually available;
- `confidence` is required and must be at least `0.80` after source verification;
- `idempotencyKey` is required and stable;
- cosmetic duplicate questions and obvious answer leakage are rejected;
- absence of any qualifying cards is valid, but an empty bundle must not be created.

These are authoring requirements, not a breaking change to Hub's v1 import protocol. Older v1 bundles remain valid under the base constraints.

Keep coverage maps, source-reading views, preview assets, and pending attachment bindings in companion files. Do not add invented coverage fields, media IDs, or local `file:` paths to submission records. An image present in a local preview but absent from `media` remains pending for Hub; do not describe that as an image-bearing Hub submission.

When Hub MCP is available, `hub_read_note` may return `mediaCandidates`. Inspect only candidates whose content is likely to improve a card, using `hub_read_media` when `availableForInspection` is true. If the user explicitly requested generated media, `hub_create_flashcard_svg` returns a ready-to-use `media` object; copy that object without changing its URL. Generated SVGs must remain source-grounded and are not evidence by themselves.

Escape embedded newlines inside JSON strings. Do not pretty-print individual JSONL records across multiple lines.

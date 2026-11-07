#!/usr/bin/env python3
import base64
import binascii
import json
import math
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote_to_bytes

MAX_BYTES = 16 * 1024 * 1024
MAX_CARDS = 5000
MAX_REFERENCE_URL_CHARS = 8000
CLOZE_PATTERN = re.compile(r"\{\{(?:c\d+::)?([^{}]*?)(?:::[^{}]*?)?\}\}", re.IGNORECASE)
VAGUE_QUESTIONS = {
    "这是什么",
    "这是什么意思",
    "文中提到了什么",
    "请解释一下",
    "what is this",
    "what does the text say",
    "explain this",
}


def fail(message: str) -> None:
    raise ValueError(message)


def read_json(path: Path):
    if not path.is_file():
        fail(f"file not found: {path}")
    if path.stat().st_size > MAX_BYTES:
        fail(f"file exceeds 16 MB: {path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def normalized_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return "".join(character for character in value if character.isalnum())


def validate_media_url(url, mime_type: str, label: str) -> None:
    """Check transport encoding, not image semantics, availability, or rendering."""
    if not isinstance(url, str):
        fail(f"{label}: media URL must be a string")
    if url.startswith("data:"):
        # Inline content is a payload, not a short asset locator. Keep the same
        # per-file ceiling; the complete serialized cards file is checked too.
        if len(url.encode("utf-8")) > MAX_BYTES:
            fail(f"{label}: inline media exceeds the 16 MB file limit")
        header, separator, payload = url.partition(",")
        if not separator:
            fail(f"{label}: data URL is missing its payload separator")
        metadata = header[5:].split(";")
        declared_type = metadata[0].strip().casefold()
        expected_type = mime_type.split(";", 1)[0].strip().casefold()
        if not declared_type or declared_type != expected_type:
            fail(f"{label}: data URL MIME type does not match mimeType")
        parameters = [part.casefold() for part in metadata[1:]]
        if "base64" in parameters:
            if parameters[-1] != "base64":
                fail(f"{label}: base64 must be the final data URL flag")
            try:
                decoded = base64.b64decode(payload, validate=True)
            except (binascii.Error, ValueError) as error:
                fail(f"{label}: malformed Base64 media payload ({error})")
        else:
            if re.search(r"%(?![0-9a-fA-F]{2})", payload):
                fail(f"{label}: malformed percent-encoded media payload")
            decoded = unquote_to_bytes(payload)
        if not decoded:
            fail(f"{label}: media payload is empty")
        return
    if len(url) > MAX_REFERENCE_URL_CHARS or not url.startswith(
        ("https://", "http://", "hub-media://", "craft-media://")
    ):
        fail(f"{label}: media has an unsupported reference URL")


def validate_source(source, label: str, strict: bool) -> None:
    if source is None and not strict:
        return
    if not isinstance(source, dict):
        fail(f"{label}: source must be an object")
    allowed = (
        "sourceLibraryId",
        "sourceDocumentId",
        "sourceBlockId",
        "sourceTitle",
        "sourcePath",
        "sourceHash",
    )
    for field in allowed:
        value = source.get(field)
        if value is not None and (not isinstance(value, str) or len(value.strip()) > 4000):
            fail(f"{label}: source.{field} must be a string of <=4000 characters")
    if strict and not str(source.get("sourceTitle", "")).strip():
        fail(f"{label}: deep-flashcards-v2 requires a truthful sourceTitle")


def validate_card(
    card,
    index: int,
    seen: set[tuple[str, str]],
    seen_questions: set[str],
    keys: set[str],
    strict: bool,
) -> bool:
    """Returns True if this card has a non-empty explanation (used for a batch-level coverage warning)."""
    label = f"card {index}"
    if not isinstance(card, dict):
        fail(f"{label}: must be an object")
    question = str(card.get("question", "")).strip()
    answer = str(card.get("answer", "")).strip()
    if not 3 <= len(question) <= 1000:
        fail(f"{label}: question length must be 3..1000")
    if not 1 <= len(answer) <= 4000:
        fail(f"{label}: answer length must be 1..4000")
    if strict and len(question) > 240:
        fail(f"{label}: deep-flashcards-v2 question exceeds 240 characters")
    if strict and len(answer) > 800:
        fail(f"{label}: deep-flashcards-v2 answer exceeds 800 characters")
    if len(str(card.get("explanation", "")).strip()) > 2000:
        fail(f"{label}: explanation exceeds 2000 characters")
    card_type = card.get("cardType", "qa")
    allowed_types = ("qa", "cloze", "multiple_choice", "typed_answer", "ordering", "image_occlusion")
    if card_type not in allowed_types:
        fail(f"{label}: cardType must be one of {', '.join(allowed_types)}")
    if card_type == "cloze":
        cloze_answers = [match.strip() for match in CLOZE_PATTERN.findall(question) if match.strip()]
        if len(cloze_answers) != 1 or answer != cloze_answers[0]:
            fail(f"{label}: cloze must contain exactly one hidden value that equals answer")
    card_data = card.get("cardData")
    if card_type == "multiple_choice":
        if not isinstance(card_data, dict):
            fail(f"{label}: multiple_choice requires cardData")
        options = card_data.get("options")
        correct_index = card_data.get("correctIndex")
        if not isinstance(options, list) or not 2 <= len(options) <= 8:
            fail(f"{label}: multiple_choice requires 2..8 options")
        if any(not isinstance(option, str) or not 1 <= len(option.strip()) <= 500 for option in options):
            fail(f"{label}: each option must be a non-empty string of <=500 characters")
        normalized_options = [option.strip().casefold() for option in options]
        if len(set(normalized_options)) != len(normalized_options):
            fail(f"{label}: multiple_choice options must be unique")
        if isinstance(correct_index, bool) or not isinstance(correct_index, int) or not 0 <= correct_index < len(options):
            fail(f"{label}: correctIndex must select an existing option")
        if answer != options[correct_index].strip():
            fail(f"{label}: answer must exactly equal the correct option")
    elif card_type == "ordering":
        if not isinstance(card_data, dict):
            fail(f"{label}: ordering requires cardData")
        items = card_data.get("items")
        if not isinstance(items, list) or not 2 <= len(items) <= 20:
            fail(f"{label}: ordering requires 2..20 items")
        if any(not isinstance(item, str) or not 1 <= len(item.strip()) <= 500 for item in items):
            fail(f"{label}: each ordering item must be a non-empty string of <=500 characters")
        normalized_items = [item.strip().casefold() for item in items]
        if len(set(normalized_items)) != len(normalized_items):
            fail(f"{label}: ordering items must be unique")
        if answer != "\n".join(item.strip() for item in items):
            fail(f"{label}: answer must equal ordering items joined by newlines")
    elif card_type == "image_occlusion":
        if not isinstance(card_data, dict):
            fail(f"{label}: image_occlusion requires cardData")
        occlusions = card_data.get("occlusions")
        if not isinstance(occlusions, list) or not 1 <= len(occlusions) <= 64:
            fail(f"{label}: image_occlusion requires 1..64 occlusions")
        for occlusion_index, occlusion in enumerate(occlusions, 1):
            if not isinstance(occlusion, dict):
                fail(f"{label}: occlusion {occlusion_index} must be an object")
            values = [occlusion.get(name) for name in ("x", "y", "width", "height")]
            if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) for value in values):
                fail(f"{label}: occlusion {occlusion_index} coordinates must be finite numbers")
            x, y, width, height = values
            if x < 0 or y < 0 or width < 0.01 or height < 0.01 or x + width > 1.001 or y + height > 1.001:
                fail(f"{label}: occlusion {occlusion_index} must stay inside normalized image bounds")
            if len(str(occlusion.get("label", "")).strip()) > 120:
                fail(f"{label}: occlusion {occlusion_index} label exceeds 120 characters")
    elif card_data not in (None, {}):
        fail(f"{label}: cardData is only supported for multiple_choice, ordering, and image_occlusion")
    media = card.get("media", [])
    if not isinstance(media, list) or len(media) > 8:
        fail(f"{label}: media must be an array with at most 8 items")
    for media_index, item in enumerate(media, 1):
        if not isinstance(item, dict):
            fail(f"{label}: media {media_index} must be an object")
        title = item.get("title", "")
        mime_type = item.get("mimeType")
        url = item.get("url")
        placement = item.get("placement", "answer")
        if not isinstance(title, str) or len(title.strip()) > 200:
            fail(f"{label}: media {media_index} title exceeds 200 characters")
        if not isinstance(mime_type, str) or not mime_type.strip() or len(mime_type.strip()) > 120:
            fail(f"{label}: media {media_index} mimeType is required and must be <=120 characters")
        validate_media_url(url, mime_type, f"{label}: media {media_index}")
        if placement not in ("question", "answer", "explanation"):
            fail(f"{label}: media {media_index} placement must be question, answer, or explanation")
    if card_type == "image_occlusion" and not any(item["mimeType"].strip().lower().startswith("image/") for item in media):
        fail(f"{label}: image_occlusion requires image media")
    if card_type == "image_occlusion" and not any(
        item["mimeType"].strip().lower().startswith("image/") and item.get("placement") in (None, "question")
        for item in media
    ):
        fail(f"{label}: image_occlusion image media must use question placement")
    confidence = card.get("confidence")
    if confidence is not None and (not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1):
        fail(f"{label}: confidence must be between 0 and 1")
    if strict and (confidence is None or confidence < 0.80):
        fail(f"{label}: deep-flashcards-v2 requires confidence >= 0.80")
    tags = card.get("tags", [])
    if not isinstance(tags, list) or len(tags) > 20 or any(not isinstance(tag, str) or not 1 <= len(tag.strip()) <= 60 for tag in tags):
        fail(f"{label}: tags must contain at most 20 non-empty strings of <=60 characters")
    evidence = card.get("evidence", "")
    if not isinstance(evidence, (str, dict)):
        fail(f"{label}: evidence must be a string or object")
    evidence_text = evidence if isinstance(evidence, str) else str(evidence.get("text", evidence.get("quote", "")))
    if len(evidence_text.strip()) > 2000:
        fail(f"{label}: evidence exceeds 2000 characters")
    if strict and len(evidence_text.strip()) < 3:
        fail(f"{label}: deep-flashcards-v2 requires non-empty verbatim evidence")
    validate_source(card.get("source"), label, strict)
    custom_fields = card.get("customFields", {})
    if not isinstance(custom_fields, dict) or len(custom_fields) > 20:
        fail(f"{label}: customFields must be an object with at most 20 fields")
    for field_name, field_value in custom_fields.items():
        if not isinstance(field_name, str) or not 1 <= len(field_name.strip()) <= 60:
            fail(f"{label}: customFields names must be non-empty strings of <=60 characters")
        if isinstance(field_value, str):
            if len(field_value.strip()) > 500:
                fail(f"{label}: customFields[{field_name!r}] exceeds 500 characters")
        elif isinstance(field_value, bool):
            pass
        elif isinstance(field_value, (int, float)):
            if not math.isfinite(field_value):
                fail(f"{label}: customFields[{field_name!r}] must be finite")
        else:
            fail(f"{label}: customFields[{field_name!r}] must be a string, number, or boolean")
    normalized_question = normalized_text(question)
    normalized_answer = normalized_text(answer)
    pair = (normalized_question, normalized_answer)
    if pair in seen:
        fail(f"{label}: duplicate question and answer")
    seen.add(pair)
    if strict and normalized_question in seen_questions:
        fail(f"{label}: deep-flashcards-v2 duplicate question after normalization")
    seen_questions.add(normalized_question)
    if strict and question.strip().casefold().rstrip("?？。.!！") in VAGUE_QUESTIONS:
        fail(f"{label}: deep-flashcards-v2 rejects vague context-dependent questions")
    if strict and card_type != "cloze" and len(normalized_answer) >= 3 and normalized_answer in normalized_question:
        fail(f"{label}: deep-flashcards-v2 question appears to reveal the answer")
    key = str(card.get("idempotencyKey", "")).strip()
    if strict and not key:
        fail(f"{label}: deep-flashcards-v2 requires idempotencyKey")
    if key:
        if len(key) > 240:
            fail(f"{label}: idempotencyKey exceeds 240 characters")
        if key in keys:
            fail(f"{label}: duplicate idempotencyKey {key!r}")
        keys.add(key)
    return bool(str(card.get("explanation", "")).strip())


def main() -> int:
    arguments = sys.argv[1:]
    force_strict = False
    if "--strict" in arguments:
        force_strict = True
        arguments.remove("--strict")
    if len(arguments) != 1:
        print("usage: validate_bundle.py [--strict] <manifest.json>", file=sys.stderr)
        return 2
    manifest_path = Path(arguments[0]).expanduser().resolve()
    try:
        manifest = read_json(manifest_path)
        if not isinstance(manifest, dict):
            fail("manifest must be an object")
        if manifest.get("format") != "hub-flashcards-v1" or manifest.get("version") != 1:
            fail("manifest must declare format hub-flashcards-v1 and version 1")
        generator = manifest.get("generator", {})
        workflow = generator.get("workflow", "") if isinstance(generator, dict) else ""
        strict = force_strict or workflow == "deep-flashcards-v2"
        deck_name = str(manifest.get("deckName", "")).strip()
        if not 1 <= len(deck_name) <= 120:
            fail("deckName length must be 1..120")
        cards_name = manifest.get("cardsFile")
        if not isinstance(cards_name, str) or not cards_name.strip():
            fail("cardsFile is required")
        cards_path = (manifest_path.parent / cards_name).resolve()
        if cards_path.parent != manifest_path.parent:
            fail("cardsFile must be in the manifest directory")
        if not cards_path.is_file() or cards_path.stat().st_size > MAX_BYTES:
            fail("cardsFile is missing or exceeds 16 MB")
        seen: set[tuple[str, str]] = set()
        seen_questions: set[str] = set()
        keys: set[str] = set()
        count = 0
        explained_count = 0
        with cards_path.open("r", encoding="utf-8-sig") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    card = json.loads(line)
                except json.JSONDecodeError as error:
                    fail(f"line {line_number}: invalid JSON: {error}")
                count += 1
                if count > MAX_CARDS:
                    fail("bundle exceeds 5000 cards")
                if validate_card(card, count, seen, seen_questions, keys, strict):
                    explained_count += 1
        if count == 0:
            fail("bundle contains no cards")
        profile = "deep-flashcards-v2" if strict else "hub-flashcards-v1"
        print(f"OK: {count} cards in {cards_path} ({profile})")
        if strict and count >= 4 and explained_count / count < 0.5:
            print(
                f"WARNING: only {explained_count}/{count} cards have an explanation. "
                "deep-flashcards-v2 expects an explanation whenever the source supports one "
                "(reason, mechanism, exception, consequence) — this batch may be capturing "
                "isolated facts instead of the context around them. Not a validation failure; "
                "review before submitting.",
                file=sys.stderr,
            )
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Prepare, apply and undo explicit file routes; Python 3.11 standard library.

scan --source ABS --out ABS
prepare --routes ABS --out ABS
apply --plan ABS --journal ABS
undo --journal ABS [--execute]

All data files must be below the configured state_root. prepare never moves
source files. apply and executing undo require Windows and same-volume paths.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import time
import uuid


VERSION = 1
DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "references" / "locations.json"
REPARSE = 0x400
HIDDEN_SYSTEM = 0x2 | 0x4
LOCK_NAME = ".organizer.lock"
TEMP_EXTENSIONS = {".crdownload", ".part", ".partial", ".download", ".tmp", ".lck"}


class SafetyError(Exception):
    pass


def fail(message):
    raise SafetyError(message)


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def key(path):
    return os.path.normcase(str(path))


def beneath(path, root, equal=False):
    try:
        common = os.path.commonpath([key(path), key(root)])
    except ValueError:
        return False
    return common == key(root) and (equal or key(path) != key(root))


def path_value(value):
    if not isinstance(value, str) or not value or "\x00" in value:
        fail("A nonempty absolute path is required")
    p = Path(value)
    if not p.is_absolute():
        fail(f"Relative paths are not allowed: {value}")
    if os.name == "nt":
        if not re.match(r"^[A-Za-z]:[\\/]", value):
            fail(f"Only local drive paths are allowed (no UNC/device paths): {value}")
        for part in re.split(r"[\\/]", value[3:]):
            if not part:
                continue
            if part in {".", ".."} or part.endswith((".", " ")):
                fail(f"Ambiguous path component: {value}")
            if any(c in part for c in ':*?"<>|') or any(ord(c) < 32 for c in part):
                fail(f"ADS or invalid path component: {value}")
            stem = part.split(".")[0].upper()
            if stem in {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"} or re.fullmatch(r"(?:COM|LPT)[1-9¹²³]", stem):
                fail(f"Reserved Windows device name: {value}")
    elif ".." in p.parts:
        fail(f"Parent traversal is not allowed: {value}")
    return Path(os.path.abspath(p))


def exists(path):
    return os.path.lexists(path)


def check_path(path, require=False):
    """Check every existing ancestor without following reparse points."""
    for part in list(reversed(path.parents)) + [path]:
        try:
            info = part.lstat()
        except FileNotFoundError:
            if require:
                fail(f"Path does not exist: {part}")
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & REPARSE:
            fail(f"Links/reparse points are not allowed: {part}")
        if part != path and not stat.S_ISDIR(info.st_mode):
            fail(f"Ancestor is not a directory: {part}")
    if require and not exists(path):
        fail(f"Path does not exist: {path}")


def read_json(path):
    check_path(path, require=True)
    if not path.is_file():
        fail(f"Expected JSON file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (ValueError, UnicodeError) as exc:
        fail(f"Invalid JSON in {path}: {exc}")


class Config:
    def __init__(self, filename):
        raw = read_json(path_value(str(filename)))
        if not isinstance(raw, dict):
            fail("Configuration must be a JSON object")
        self.sources = self.roots(raw, "source_roots")
        self.destinations = self.roots(raw, "destination_roots")
        self.state = path_value(raw.get("state_root"))
        settle = raw.get("settle_seconds", 120)
        if isinstance(settle, bool) or not isinstance(settle, (int, float)) or settle < 0 or settle > 365 * 86400:
            fail("settle_seconds must be a finite nonnegative duration under one year")
        if not (settle < float("inf")):
            fail("settle_seconds must be finite")
        self.settle = float(settle)
        extensions = raw.get("blocked_extensions", [])
        if not isinstance(extensions, list) or any(not isinstance(x, str) or not x.startswith(".") for x in extensions):
            fail("blocked_extensions must contain dot-prefixed extensions")
        self.blocked = TEMP_EXTENSIONS | {x.lower() for x in extensions}
        all_roots = self.sources + self.destinations
        for i, root in enumerate(all_roots):
            check_path(root)
            if root == Path(root.anchor):
                fail(f"A drive root cannot be an allowed root: {root}")
            for other in all_roots[:i]:
                if beneath(root, other, True) or beneath(other, root, True):
                    fail(f"Configured source/destination roots overlap: {root}; {other}")
            if beneath(self.state, root, True) or beneath(root, self.state, True):
                fail("state_root must be disjoint from all source and destination roots")
        check_path(self.state)
        self.scope = {
            "source_roots": sorted(key(p) for p in self.sources),
            "destination_roots": sorted(key(p) for p in self.destinations),
            "state_root": key(self.state),
            "settle_seconds": self.settle,
            "blocked_extensions": sorted(self.blocked),
        }

    @staticmethod
    def roots(raw, name):
        values = raw.get(name)
        if not isinstance(values, list) or not values:
            fail(f"{name} must be a nonempty path list")
        return [path_value(p) for p in values]

    def source_root(self, value):
        p = path_value(value)
        if key(p) not in {key(root) for root in self.sources}:
            fail(f"source_root is not configured: {p}")
        check_path(p, True)
        if not p.is_dir():
            fail(f"Source root is not a directory: {p}")
        return p

    def data_path(self, value, new=False):
        p = path_value(value)
        if not beneath(p, self.state) or p.name == LOCK_NAME:
            fail(f"Data path must be within state_root: {p}")
        check_path(p, require=not new)
        if new:
            check_path(p.parent, True)
            if exists(p):
                fail(f"Output already exists; use a new filename: {p}")
        elif not p.is_file():
            fail(f"Expected a regular data file: {p}")
        return p


@contextlib.contextmanager
def batch_lock(cfg):
    check_path(cfg.state)
    cfg.state.mkdir(parents=True, exist_ok=True)
    check_path(cfg.state, True)
    lock_path = cfg.state / LOCK_NAME
    check_path(lock_path)
    with lock_path.open("a+b") as handle:
        handle.seek(0, 2)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            fail(f"Another organizer command is running for {cfg.state}")
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def write_json_new(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def metadata(info):
    return {
        "size": info.st_size,
        "mtime_ns": info.st_mtime_ns,
        "device": info.st_dev,
        "file_id": info.st_ino,
        "mode": stat.S_IFMT(info.st_mode),
    }


def restrictions(path, info, cfg, settled=True):
    flags = []
    attrs = getattr(info, "st_file_attributes", 0)
    if stat.S_ISLNK(info.st_mode) or attrs & REPARSE:
        flags.append("link_or_reparse")
    if attrs & HIDDEN_SYSTEM or path.name.startswith("."):
        flags.append("hidden_or_system")
    if path.suffix.lower() in cfg.blocked or path.name.startswith("~$") or path.name.endswith("~"):
        flags.append("temporary_or_lock")
    if not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
        flags.append("unsupported_file_type")
    if settled and time.time_ns() - max(info.st_mtime_ns, info.st_ctime_ns) < cfg.settle * 1_000_000_000:
        flags.append("recently_changed")
    return flags


def fingerprint(path, cfg, settled=True):
    """Hash one file or a complete directory; reject changes while reading."""
    check_path(path, True)
    entries = []

    def visit(current, relative):
        check_path(current, True)
        before = current.lstat()
        flags = restrictions(current, before, cfg, settled)
        if flags:
            fail(f"Cannot move {current}: {', '.join(flags)}")
        entry = {"path": relative, **metadata(before)}
        if stat.S_ISREG(before.st_mode):
            entry["kind"] = "file"
            h = hashlib.sha256()
            with current.open("rb") as handle:
                if metadata(os.fstat(handle.fileno())) != metadata(before):
                    fail(f"File changed before hashing: {current}")
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    h.update(chunk)
                if metadata(os.fstat(handle.fileno())) != metadata(before):
                    fail(f"File changed during hashing: {current}")
            entry["sha256"] = h.hexdigest()
            entries.append(entry)
        else:
            entry["kind"] = "directory"
            # Directory allocation size is not a portable content property.
            entry.pop("size")
            entries.append(entry)
            names = sorted(os.listdir(current), key=str.casefold)
            for name in names:
                child = path_value(str(current / name))
                visit(child, name if relative == "." else relative + "/" + name)
            if sorted(os.listdir(current), key=str.casefold) != names:
                fail(f"Directory changed while hashing: {current}")
        after = current.lstat()
        if metadata(after) != metadata(before):
            fail(f"Source changed while hashing: {current}")
    visit(path, ".")
    return {"algorithm": "sha256-tree-v1", "digest": digest(entries), "entries": entries}


def match_fingerprint(path, expected, cfg):
    actual = fingerprint(path, cfg, settled=False)
    if actual != expected:
        fail(f"Contents, identity or timestamps changed since preparation: {path}")


def validate_fingerprint(fp):
    if not isinstance(fp, dict) or fp.get("algorithm") != "sha256-tree-v1":
        fail("Missing/unsupported fingerprint")
    if not isinstance(fp.get("entries"), list) or not fp["entries"] or fp.get("digest") != digest(fp["entries"]):
        fail("Fingerprint is incomplete or corrupt")


def validate_routes(data, cfg, prepared=False):
    if not isinstance(data, dict):
        fail("Routes/plan must be a JSON object")
    source_root = cfg.source_root(data.get("source_root"))
    moves = data.get("moves")
    if not isinstance(moves, list):
        fail("moves must be a list")
    if not isinstance(data.get("deferred", []), list):
        fail("deferred must be a list")
    paths = []
    validated = []
    for index, move in enumerate(moves):
        if not isinstance(move, dict):
            fail(f"Move {index} must be an object")
        source, target = path_value(move.get("source")), path_value(move.get("target"))
        if not beneath(source, source_root):
            fail(f"Source is outside source_root: {source}")
        if not any(beneath(target, root) for root in cfg.destinations):
            fail(f"Target is outside destination_roots: {target}")
        if not isinstance(move.get("reason"), str) or not move["reason"].strip():
            fail(f"Move {index} requires a reason")
        if key(Path(source.anchor)) != key(Path(target.anchor)):
            fail(f"Cross-drive moves are not supported: {source} -> {target}")
        for p in (source, target):
            for previous in paths:
                if beneath(p, previous, True) or beneath(previous, p, True):
                    fail(f"Routes overlap or duplicate: {p}; {previous}")
            paths.append(p)
            check_path(p)
        check_path(target.parent, True)
        if not target.parent.is_dir():
            fail(f"Target parent must already exist: {target.parent}")
        clean = {"source": str(source), "target": str(target), "reason": move["reason"]}
        if prepared:
            validate_fingerprint(move.get("fingerprint"))
            clean["fingerprint"] = move["fingerprint"]
        validated.append(clean)
    return source_root, validated


def read_plan(path, cfg):
    plan = read_json(path)
    if not isinstance(plan, dict) or plan.get("version") != VERSION or plan.get("status") != "ready":
        fail("Only a version 1 ready plan can be applied")
    payload = {k: v for k, v in plan.items() if k != "plan_digest"}
    if plan.get("plan_digest") != digest(payload):
        fail("Plan checksum mismatch; prepare the routes again")
    if plan.get("scope") != cfg.scope:
        fail("Configuration changed; prepare the routes again")
    validate_routes(plan, cfg, prepared=True)
    return plan


def scan(args, cfg):
    source = cfg.source_root(args.source)
    output = cfg.data_path(args.out, new=True)
    items = []
    for child in sorted(source.iterdir(), key=lambda p: p.name.casefold()):
        item = {"path": str(child), "name": child.name, "extension": child.suffix.lower()}
        try:
            info = child.lstat()
            item.update(metadata(info))
            item["kind"] = "directory" if stat.S_ISDIR(info.st_mode) else "file" if stat.S_ISREG(info.st_mode) else "other"
            item["flags"] = restrictions(child, info, cfg)
            try:
                path_value(str(child))
            except SafetyError:
                item["flags"].append("unsupported_path")
            item["eligible_for_review"] = not item["flags"]
            if item["kind"] == "directory":
                item["requires_recursive_check"] = True
        except OSError as exc:
            item.update({"flags": ["unreadable"], "error": str(exc), "eligible_for_review": False})
        items.append(item)
    result = {"version": VERSION, "source_root": str(source), "scanned_at": time.time(), "recursive": False, "items": items}
    write_json_new(output, result)
    return {"output": str(output), "items": len(items), "eligible_for_review": sum(bool(i["eligible_for_review"]) for i in items)}


def prepare(args, cfg):
    routes_path = cfg.data_path(args.routes)
    output = cfg.data_path(args.out, new=True)
    routes = read_json(routes_path)
    source_root, moves = validate_routes(routes, cfg)
    for move in moves:
        source, target = Path(move["source"]), Path(move["target"])
        if exists(target):
            fail(f"Target already exists; no overwrite or directory merge: {target}")
        if source.stat().st_dev != target.parent.stat().st_dev:
            fail(f"Source and destination are not on the same volume: {source}")
        move["fingerprint"] = fingerprint(source, cfg)
    plan = {"version": VERSION, "status": "ready", "plan_id": str(uuid.uuid4()), "created_at": time.time(), "source_root": str(source_root), "scope": cfg.scope, "moves": moves, "deferred": routes.get("deferred", [])}
    plan["plan_digest"] = digest(plan)
    write_json_new(output, plan)
    return {"output": str(output), "status": "ready", "moves": len(moves), "deferred": len(plan["deferred"])}


class Journal:
    def __init__(self, path, new=False):
        self.path = path
        self.records = [] if new else self.read(path)
        self.handle = path.open("x" if new else "a", encoding="utf-8", newline="\n")

    @staticmethod
    def read(path):
        raw = path.read_bytes()
        if not raw or not raw.endswith(b"\n"):
            fail("Journal is empty or has an incomplete final record; automatic recovery refused")
        records = []
        previous = None
        try:
            for index, line in enumerate(raw.decode("utf-8").splitlines()):
                record = json.loads(line)
                if not isinstance(record, dict):
                    fail("Journal record is not an object")
                payload = {k: v for k, v in record.items() if k != "record_hash"}
                if record.get("seq") != index or record.get("previous") != previous or record.get("record_hash") != digest(payload):
                    fail("Journal sequence/hash chain is corrupt; automatic recovery refused")
                previous = record["record_hash"]
                records.append(record)
        except (ValueError, UnicodeError) as exc:
            fail(f"Invalid journal; automatic recovery refused: {exc}")
        return records

    def append(self, event, **details):
        record = {"seq": len(self.records), "previous": self.records[-1]["record_hash"] if self.records else None, "time": time.time(), "event": event, **details}
        record["record_hash"] = digest(record)
        self.handle.write(canonical_json(record) + "\n")
        self.handle.flush()
        os.fsync(self.handle.fileno())
        self.records.append(record)

    def close(self):
        self.handle.close()


def windows_only():
    if os.name != "nt":
        fail("Moving files is supported only on Windows (os.rename must refuse existing targets)")


def preflight_move(move, cfg, settled=True):
    source, target = Path(move["source"]), Path(move["target"])
    check_path(source, True)
    check_path(target)
    check_path(target.parent, True)
    if exists(target):
        fail(f"Target already exists: {target}")
    if source.stat().st_dev != target.parent.stat().st_dev:
        fail(f"Move would cross volumes: {source}")
    actual = fingerprint(source, cfg, settled=settled)
    if actual != move["fingerprint"]:
        fail(f"Source changed since preparation: {source}")


def move_no_replace(source, target):
    windows_only()
    check_path(source, True)
    check_path(target)
    if exists(target):
        fail(f"Refusing to overwrite: {target}")
    os.rename(source, target)


def apply(args, cfg):
    windows_only()
    plan = read_plan(cfg.data_path(args.plan), cfg)
    journal_path = cfg.data_path(args.journal, new=True)
    for move in plan["moves"]:
        preflight_move(move, cfg)
    journal = Journal(journal_path, new=True)
    done = 0
    moved = 0
    current = None
    try:
        journal.append("batch", version=VERSION, plan=plan)
        for index, move in enumerate(plan["moves"]):
            current = index
            preflight_move(move, cfg)
            journal.append("intent", index=index)
            move_no_replace(Path(move["source"]), Path(move["target"]))
            moved += 1
            match_fingerprint(Path(move["target"]), move["fingerprint"], cfg)
            if exists(Path(move["source"])):
                fail(f"Source path was recreated during move: {move['source']}")
            journal.append("done", index=index)
            done += 1
        journal.append("complete", done=done)
    except (Exception, KeyboardInterrupt) as exc:
        try:
            journal.append("error", index=current, message=str(exc), moved=moved, verified=done)
        except Exception:
            pass
        fail(f"Stopped; {moved} moved, {done} verified. Journal: {journal_path}. Error: {exc}")
    finally:
        journal.close()
    return {"journal": str(journal_path), "moved": moved, "verified": done, "status": "complete"}


def journal_states(records, cfg):
    if not records or records[0].get("event") != "batch" or records[0].get("version") != VERSION:
        fail("Missing journal batch header")
    plan = records[0].get("plan")
    if not isinstance(plan, dict) or plan.get("version") != VERSION or plan.get("status") != "ready":
        fail("Invalid embedded journal plan")
    if plan.get("plan_digest") != digest({k: v for k, v in plan.items() if k != "plan_digest"}):
        fail("Embedded plan checksum mismatch")
    if plan.get("scope") != cfg.scope:
        fail("Journal configuration does not match; restore the original configuration")
    validate_routes(plan, cfg, prepared=True)
    states = ["pending"] * len(plan["moves"])
    next_intent = 0
    apply_finished = False
    undo_started = False
    for record in records[1:]:
        event = record.get("event")
        if event in {"intent", "done", "undo_intent", "undone"}:
            index = record.get("index")
            if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < len(states):
                fail("Invalid journal operation index")
            old = states[index]
            if event == "intent":
                if apply_finished or undo_started or index != next_intent or old != "pending" or any(s == "intent" for s in states):
                    fail("Invalid/repeated apply intent in journal")
                states[index] = "intent"
                next_intent += 1
            elif event == "done":
                if apply_finished or undo_started or old != "intent":
                    fail("Invalid/repeated done record in journal")
                states[index] = "done"
            elif event == "undo_intent":
                if old not in {"intent", "done"}:
                    fail("Invalid/repeated undo intent in journal")
                states[index] = "undo_intent"
                undo_started = True
            else:
                if old not in {"intent", "undo_intent"}:
                    fail("Invalid/repeated undone record in journal")
                states[index] = "undone"
                undo_started = True
        elif event == "complete":
            if apply_finished or undo_started or any(s != "done" for s in states):
                fail("Invalid completion record in journal")
            apply_finished = True
        elif event == "error":
            if apply_finished or undo_started:
                fail("Invalid apply error record in journal")
            apply_finished = True
        elif event == "undo_error":
            undo_started = True
        elif event == "undo_complete":
            if any(s not in {"pending", "undone"} for s in states):
                fail("Invalid undo completion record")
            undo_started = True
        else:
            fail(f"Unknown journal event: {event}")
    return plan, states


def undo_status(move, state, cfg):
    source, target = Path(move["source"]), Path(move["target"])
    if state == "pending":
        return "not_attempted"
    if state == "undone":
        return "already_undone"
    check_path(source)
    check_path(target)
    source_exists, target_exists = exists(source), exists(target)
    if not source_exists and target_exists:
        check_path(source.parent, True)
        if target.stat().st_dev != source.parent.stat().st_dev:
            fail(f"Undo would cross volumes: {target}")
        match_fingerprint(target, move["fingerprint"], cfg)
        return "ready_to_undo"
    if source_exists and not target_exists and state in {"intent", "undo_intent"}:
        match_fingerprint(source, move["fingerprint"], cfg)
        return "record_only_recovered" if state == "undo_intent" else "record_only_never_moved"
    fail(f"Cannot undo operation ({state}): source_exists={source_exists}, target_exists={target_exists}: {source}")


def undo(args, cfg):
    if args.execute:
        windows_only()
    journal_path = cfg.data_path(args.journal)
    records = Journal.read(journal_path)
    plan, states = journal_states(records, cfg)
    actions = []
    # Inspect every operation before writing any undo event or moving any file.
    for index in reversed(range(len(states))):
        move = plan["moves"][index]
        try:
            status = undo_status(move, states[index], cfg)
            actions.append({"index": index, "status": status, "source": move["target"], "target": move["source"]})
        except (SafetyError, OSError) as exc:
            actions.append({"index": index, "status": "blocked", "error": str(exc)})
    blocked = any(a["status"] == "blocked" for a in actions)
    if not args.execute:
        return {"journal": str(journal_path), "mode": "preview", "blocked": blocked, "actions": actions}
    if blocked:
        fail("Undo preflight blocked; nothing moved. Run undo without --execute for details")
    active = [a for a in actions if a["status"] not in {"not_attempted", "already_undone"}]
    if not active:
        return {"journal": str(journal_path), "mode": "execute", "undone": 0, "status": "already_restored_or_not_attempted"}
    journal = Journal(journal_path)
    restored = 0
    current = None
    try:
        for action in active:
            index = action["index"]
            current = index
            move = plan["moves"][index]
            status = undo_status(move, states[index], cfg)
            if status == "ready_to_undo":
                if states[index] != "undo_intent":
                    journal.append("undo_intent", index=index)
                move_no_replace(Path(move["target"]), Path(move["source"]))
                restored += 1
                match_fingerprint(Path(move["source"]), move["fingerprint"], cfg)
            journal.append("undone", index=index, recovery=status)
        journal.append("undo_complete", restored=restored)
    except (Exception, KeyboardInterrupt) as exc:
        try:
            journal.append("undo_error", index=current, message=str(exc), restored=restored)
        except Exception:
            pass
        fail(f"Undo stopped after {restored} moves. Journal: {journal_path}. Error: {exc}")
    finally:
        journal.close()
    return {"journal": str(journal_path), "mode": "execute", "undone": restored, "status": "complete"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Configuration JSON; place before the command")
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("scan", help="Shallow metadata inventory; never reads file content")
    p.add_argument("--source", required=True)
    p.add_argument("--out", required=True)
    p = commands.add_parser("prepare", help="Validate routes and fingerprint sources without moving")
    p.add_argument("--routes", required=True)
    p.add_argument("--out", required=True)
    p = commands.add_parser("apply", help="Apply an explicit ready plan, keeping a durable journal")
    p.add_argument("--plan", required=True)
    p.add_argument("--journal", required=True)
    p = commands.add_parser("undo", help="Preview reverse moves; use --execute to perform them")
    p.add_argument("--journal", required=True)
    p.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    try:
        cfg = Config(args.config)
        with batch_lock(cfg):
            result = {"scan": scan, "prepare": prepare, "apply": apply, "undo": undo}[args.command](args, cfg)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (SafetyError, OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("ERROR: Interrupted. Inspect the journal before retrying a move.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())

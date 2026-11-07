"""Check Car review bindings before writes or local archive tags; performs no writes."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    result = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    require(isinstance(result, dict), 'Record must be a JSON object')
    return result


def has_text(value):
    return isinstance(value, str) and bool(value.strip())


def files(entries, label, nonempty=False):
    require(isinstance(entries, list) and (entries or not nonempty), label + ': missing file list')
    found = set()
    for entry in entries:
        path = Path(entry['path'])
        require(path.is_absolute() and path.is_file(), label + ': unreadable absolute file path')
        key = str(path.resolve()).casefold()
        require(key not in found, label + ': duplicate file path')
        found.add(key)
        require(digest(path) == entry['sha256'], label + ': file hash changed: ' + path.name)
    return found


def validate(mode, plan_path, facts_path, review_path, acceptance_path=None):
    plan, facts, review = [read(p) for p in (plan_path, facts_path, review_path)]
    for field in ('task', 'revision'):
        require(isinstance(plan.get(field), str) and plan[field].strip(), 'Missing plan ' + field)
        require(review.get(field) == plan[field], 'Review ' + field + ' mismatch')
    require(facts.get('task') == plan['task'], 'Facts task mismatch')
    require(facts.get('stage') == 'source_only' and facts.get('status') == '已完成', 'Source stage incomplete')
    require(review.get('status') == '已完成' and review.get('conclusion') == '通过', 'Review has not passed')
    require(review.get('blocking_issues') == [], 'Review has unresolved or unspecified blockers')
    require(review.get('plan_sha256') == digest(plan_path), 'Review is for a different plan')
    require(review.get('facts_sha256') == digest(facts_path), 'Review is for different source facts')
    require(plan.get('review_sources') == facts.get('sources'), 'Source manifest mismatch')
    files(facts.get('sources'), 'sources', nonempty=True)
    files(plan.get('review_files'), 'payloads')
    required = plan.get('required_checks')
    names = {'body', 'location', 'attachments', 'preserved_content', 'links', 'visual'}
    require(isinstance(required, list) and all(isinstance(n, str) for n in required), 'Missing required checks')
    require({'body', 'location'} <= set(required) <= names, 'Invalid required checks')
    rows = facts.get('facts')
    require(isinstance(rows, list) and rows, 'No source facts')
    require(all(all(has_text(row.get(field)) for field in ('source', 'fact', 'importance')) for row in rows), 'Facts need source, fact and importance text')
    ids = [row['id'] for row in rows]
    require(all(isinstance(i, str) and i.strip() for i in ids) and len(set(ids)) == len(ids), 'Invalid fact IDs')
    coverage = review.get('coverage')
    require(isinstance(coverage, list), 'No coverage matrix')
    require(len(coverage) == len(ids) and {row['fact_id'] for row in coverage} == set(ids), 'Incomplete fact coverage')
    require(all(has_text(row.get('draft_location')) and has_text(row.get('finding')) for row in coverage), 'Coverage needs location and finding text')
    checked = review.get('checked')
    require(isinstance(checked, list) and checked and all(has_text(item) for item in checked), 'Missing checked target/source evidence text')
    if mode == 'write':
        return
    require(mode == 'tag' and acceptance_path, 'Tagging requires acceptance record')
    acceptance = read(acceptance_path)
    for field in ('task', 'revision'):
        require(acceptance.get(field) == plan[field], 'Acceptance ' + field + ' mismatch')
    require(acceptance.get('complete') is True, 'Acceptance incomplete')
    require(acceptance.get('plan_sha256') == digest(plan_path), 'Acceptance plan mismatch')
    require(acceptance.get('review_sha256') == digest(review_path), 'Acceptance review mismatch')
    evidence = files(acceptance.get('evidence_files'), 'acceptance evidence', nonempty=True)
    checks = acceptance['checks']
    for name in ('body', 'location', 'attachments', 'preserved_content', 'links', 'visual'):
        check = checks[name]
        status = check.get('status')
        require(status in ('pass', 'not_applicable', 'limited'), 'Failed check: ' + name)
        require(name == 'visual' or status != 'limited', 'Only visual may be limited')
        require(name not in ('body', 'location') or status == 'pass', name + ' must pass')
        require(name not in required or status == 'pass', 'Required check must pass: ' + name)
        refs = check.get('evidence')
        require(isinstance(refs, list), 'Missing evidence list: ' + name)
        for ref in refs:
            path = Path(ref)
            require(path.is_absolute() and str(path.resolve()).casefold() in evidence, 'Unbound evidence: ' + name)
        require(status == 'not_applicable' or refs, 'Missing evidence: ' + name)
        require(status == 'pass' or has_text(check.get('reason')), 'Missing limitation or inapplicability reason: ' + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('write', 'tag'))
    for name in ('plan', 'facts', 'review'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--acceptance')
    args = parser.parse_args()
    try:
        validate(args.mode, args.plan, args.facts, args.review, args.acceptance)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(json.dumps({'ok': False, 'reason': str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps({'ok': True, 'mode': args.mode, 'scope': 'local record integrity only'}))
    return 0


if __name__ == '__main__':
    sys.exit(main())

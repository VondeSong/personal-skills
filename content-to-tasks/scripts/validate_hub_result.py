#!/usr/bin/env python3
"""Offline Hub schema and relationship validation. Requires jsonschema>=4.18,<5."""
import argparse
import json
import re
from datetime import datetime
from pathlib import Path

SCHEMA = Path(__file__).resolve().parents[1] / 'schemas' / 'hub-result.schema.json'


def validate(document):
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        return {'ok': False, 'errors': ['jsonschema dependency missing; validation was not run']}
    schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
    checker = FormatChecker()
    # jsonschema's built-in date-time checker needs an optional dependency.
    # Register this one so validation cannot silently skip timestamps.
    @checker.checks('date-time', raises=(ValueError, TypeError))
    def timezone_datetime(value):
        if not isinstance(value, str):
            return True
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})', value):
            return False
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return parsed.utcoffset() is not None
    validator = Draft202012Validator(schema, format_checker=checker)
    errors = [f'{list(error.absolute_path)}: {error.message}' for error in validator.iter_errors(document)]
    if errors:
        return {'ok': False, 'errors': errors}
    records = document['tasks']
    nodes = {row['localId']: row for row in records}
    if len(nodes) != len(records):
        errors.append('duplicate localId')
    attachments = document['attachments']
    attachment_keys = [(row['sourceId'], row['localTaskId']) for row in attachments]
    if len(attachment_keys) != len(set(attachment_keys)):
        errors.append('duplicate attachment binding')
    allowed = document['destination']['allowedProjectIds']
    planned = document['mode'] == 'plan_only' or document['status'] == 'planned'
    side_effect = False
    for row in records:
        task = row['task']
        if task['projectId'] not in allowed:
            errors.append('task project outside authorized destination')
        if row['operation'] != 'create' and row['remoteId'] != task['id']:
            errors.append('remoteId differs from existing task.id')
        if row.get('remoteId') and task.get('id') and row['remoteId'] != task['id']:
            errors.append('task and result IDs disagree')
        if row['verified'] and not row.get('remoteId'):
            errors.append('verified task needs remoteId')
        if planned and (row['verified'] or (row['operation'] == 'create' and (row.get('remoteId') or task.get('id')))):
            errors.append('plan cannot claim task creation or verification')
        if row.get('writeConfirmed') or (row['operation'] == 'create' and row.get('remoteId')) or (row['operation'] == 'update' and row['verified']):
            side_effect = True
        for url in document['source']['urls']:
            body_field = 'desc' if task['kind'] == 'CHECKLIST' else 'content'
            if url not in task.get(body_field, ''):
                errors.append('source URL missing from task content')
        trail, cursor = set(), row['localId']
        while cursor:
            if cursor in trail:
                errors.append('parentLocalId cycle')
                break
            trail.add(cursor)
            parent = nodes.get(cursor)
            if parent is None:
                errors.append('parentLocalId does not resolve')
                break
            if parent['task']['projectId'] != task['projectId']:
                errors.append('parentLocalId crosses projects')
                break
            cursor = parent.get('parentLocalId')
    for row in attachments:
        if row['localTaskId'] not in nodes:
            errors.append('attachment points to missing localTaskId')
        if row['state'] in ('uploaded', 'linked', 'readable'):
            side_effect = True
        if planned and (row['state'] not in ('planned', 'skipped') or row.get('remoteId')):
            errors.append('plan cannot claim attachment side effects')
        if row['state'] == 'unknown' and document['status'] != 'unknown':
            errors.append('uncertain attachment side effect requires unknown status')
    if document['status'] == 'partial' and not side_effect:
        errors.append('partial requires a confirmed side effect')
    if document['status'] == 'failed' and (side_effect or document['verification']['readBack']):
        errors.append('failed cannot conceal confirmed side effects')
    if document['status'] in ('planned', 'needs_input', 'needs_connection') and side_effect:
        errors.append('confirmed side effects require partial/executed/unknown status')
    if planned and document['verification']['readBack']:
        errors.append('plan cannot claim readback')
    if document['status'] == 'executed' and not all(row['verified'] for row in records):
        errors.append('executed requires every record verified')
    return {'ok': not errors, 'errors': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    try:
        result = validate(json.loads(args.input.read_text(encoding='utf-8-sig')))
    except (OSError, ValueError, TypeError):
        result = {'ok': False, 'errors': ['input or schema could not be read']}
    print(json.dumps(result, ensure_ascii=True))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

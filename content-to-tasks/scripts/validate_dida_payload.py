#!/usr/bin/env python3
"""Validate normalized Dida writes offline. No network calls or mutations."""
import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path

TASK_FIELDS = set('assigneeUsername columnId completedTime content desc dueDate etag id isAllDay items kind parentId priority projectId reminders repeatFlag repeatFrom sortOrder startDate status tags timeZone title'.split())
NOTE_FIELDS = set('tags startDate dueDate reminders repeatFlag repeatFrom priority parentId columnId assigneeUsername'.split())
CLEAR_DATE = '1970-01-01T00:00:00.000+0000'


def fingerprint(task):
    raw = json.dumps(task, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def nonempty(value):
    return value not in (None, '', [], {}, 0, False)


def strings(value):
    return isinstance(value, list) and all(isinstance(x, str) and x for x in value)


def parse_date(value):
    if not isinstance(value, str) or 'T' not in value:
        raise ValueError('expected timezone-aware ISO datetime')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError('date has no UTC offset')
    return result


def validate(document):
    errors = []
    def fail(path, message):
        errors.append(f'{path}: {message}')

    if not isinstance(document, dict):
        return {'ok': False, 'errors': ['input must be an object']}
    snapshot = document.get('snapshot')
    operations = document.get('operations')
    allowed = document.get('allowed_project_ids')
    if not isinstance(snapshot, dict):
        return {'ok': False, 'errors': ['snapshot must be an object']}
    if not isinstance(operations, list) or not operations:
        fail('operations', 'nonempty array required')
    if not strings(allowed) or not allowed:
        fail('allowed_project_ids', 'nonempty string array required')
    indexes = {}
    for key in ('projects', 'columns', 'tasks'):
        rows = snapshot.get(key)
        index = {}
        if not isinstance(rows, list):
            fail(f'snapshot.{key}', 'object array required')
            continue
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get('id'), str) or not row['id']:
                fail(f'snapshot.{key}', 'each row needs an id')
                continue
            if row['id'] in index:
                fail(f'snapshot.{key}', 'duplicate id')
            index[row['id']] = row
            if key != 'projects' and (not isinstance(row.get('projectId'), str) or not row['projectId']):
                fail(f'snapshot.{key}', 'projectId required')
        indexes[key] = index
    tags = snapshot.get('tags')
    if 'tags' not in snapshot or (tags is not None and (
        not isinstance(tags, list) or not all(isinstance(t, dict) and isinstance(t.get('name'), str) and t['name'] for t in tags)
    )):
        fail('snapshot.tags', 'tag name objects required, or null when unavailable')
    complete = snapshot.get('subtree_complete_ids', [])
    if not strings(complete):
        fail('snapshot.subtree_complete_ids', 'string array required')
    depth_limit = snapshot.get('max_task_depth')
    if depth_limit is not None and (type(depth_limit) is not int or depth_limit < 1):
        fail('snapshot.max_task_depth', 'positive integer or null required')
    if errors:
        return {'ok': False, 'errors': errors}

    projects, columns, current_tasks = (indexes[k] for k in ('projects', 'columns', 'tasks'))
    tag_names = {t['name'] for t in tags} if tags is not None else set()
    graph = dict(current_tasks)
    affected = set()
    moved = set()
    digests = []
    seen = set()
    for i, op in enumerate(operations):
        path = f'operations[{i}]'
        if not isinstance(op, dict) or op.get('operation') not in ('create', 'update'):
            fail(path, 'only create/update supported')
            continue
        task = op.get('task')
        task_class = op.get('taskClass')
        explicit = op.get('explicit_fields', {})
        if not isinstance(task, dict):
            fail(path, 'task object required')
            continue
        if task_class not in ('action', 'reference'):
            fail(path, 'taskClass must be action/reference')
        if not isinstance(explicit, dict) or any(k not in TASK_FIELDS or not isinstance(v, str) or not v.strip() for k, v in explicit.items()):
            fail(path, 'explicit_fields must map known fields to user instruction evidence')
            explicit = {}
        if set(task) - TASK_FIELDS:
            fail(path, 'unknown task fields; normalize before validation')
        project_id = task.get('projectId')
        if not isinstance(project_id, str) or project_id not in projects or project_id not in allowed:
            fail(path, 'projectId must be live and within scope')
            continue
        project = projects[project_id]
        closed, permission = project.get('closed'), project.get('permission')
        if closed is not None and type(closed) is not bool:
            fail(path, 'closed must be bool or null')
        if closed is True or permission in ('read', 'comment'):
            fail(path, 'project closed or explicitly not writable')
        if permission not in (None, 'read', 'comment', 'write'):
            fail(path, 'unknown project permission')
        action = op['operation']
        current = {}
        node_id = f'@new:{i}'
        if action == 'update':
            node_id = task.get('id')
            if not isinstance(node_id, str) or node_id not in current_tasks:
                fail(path, 'update requires a freshly read task')
                continue
            current = current_tasks[node_id]
            if current.get('projectId') != project_id:
                fail(path, 'cross-project move is a separate operation')
                continue
        else:
            if not isinstance(task.get('title'), str) or not task['title'].strip():
                fail(path, 'create requires nonempty title')
            if type(task.get('status', 0)) is not int or task.get('status', 0) != 0 or nonempty(task.get('completedTime')):
                fail(path, 'create must be incomplete')
        effective = {**current, **task}
        kind = effective.get('kind')
        if kind not in ('TEXT', 'NOTE', 'CHECKLIST'):
            fail(path, 'kind must be TEXT/NOTE/CHECKLIST')
        if (task_class == 'reference' and kind != 'NOTE') or (task_class == 'action' and kind == 'NOTE'):
            fail(path, 'taskClass and kind disagree')
        if 'priority' in task and (type(task['priority']) is not int or task['priority'] not in (0, 1, 3, 5)):
            fail(path, 'priority must be integer 0/1/3/5')
        if 'isAllDay' in task and type(task['isAllDay']) is not bool:
            fail(path, 'isAllDay must be bool')
        if action == 'update':
            for field in ('status', 'completedTime'):
                if field in task and task[field] != current.get(field):
                    fail(path, f'{field} change requires a separate completion workflow')

        if 'columnId' in task:
            column_id = task['columnId']
            if not isinstance(column_id, str) or columns.get(column_id, {}).get('projectId') != project_id:
                fail(path, 'columnId must belong to this project')
        if 'tags' in task:
            selected, existing = task['tags'], current.get('tags') or []
            if not strings(selected) or not strings(existing):
                fail(path, 'tags must be exact-name arrays; omit rather than null')
            else:
                if len(selected) != len(set(selected)):
                    fail(path, 'duplicate tags')
                if set(selected) - tag_names - set(existing):
                    fail(path, 'new tags outside live whitelist')
                if set(existing) - set(selected):
                    fail(path, 'update would remove existing tags')

        if task_class == 'reference':
            if action == 'create' and 'projectId' not in explicit:
                inbox = snapshot.get('inbox_project_id')
                if not isinstance(inbox, str) or inbox not in projects or project_id != inbox:
                    fail(path, 'reference create requires verified inbox or explicit destination')
            for field in NOTE_FIELDS:
                if field in task and nonempty(task[field]) and task[field] != current.get(field) and field not in explicit:
                    fail(path, f'NOTE {field} requires explicit user instruction')

        parsed = {}
        for field in ('startDate', 'dueDate'):
            value = effective.get(field)
            if value == CLEAR_DATE and field in task:
                if action != 'update':
                    fail(path, 'date clearing sentinel is update-only')
                value = None
            if field in task and task[field] is None:
                fail(path, 'omit date to preserve; use documented sentinel to clear')
            if value is not None:
                try:
                    parsed[field] = parse_date(value)
                except (ValueError, TypeError, OverflowError):
                    fail(path, f'{field} must be a valid timezone-aware ISO datetime')
        if parsed and (not isinstance(effective.get('timeZone'), str) or not effective['timeZone'].strip()):
            fail(path, 'dated task needs timeZone')
        if len(parsed) == 2 and parsed['startDate'] > parsed['dueDate']:
            fail(path, 'startDate is later than dueDate after merging update')

        if kind != 'CHECKLIST' and nonempty(effective.get('items')):
            fail(path, 'nonempty items require CHECKLIST after merging update')
        if 'items' in task:
            items = task['items']
            if not isinstance(items, list) or not all(isinstance(x, dict) for x in items):
                fail(path, 'items must be object array')
            elif items and kind != 'CHECKLIST':
                fail(path, 'nonempty items require CHECKLIST')
            else:
                item_ids = [x.get('id') for x in items if x.get('id') is not None]
                if not all(isinstance(x, str) and x for x in item_ids) or len(item_ids) != len(set(x for x in item_ids if isinstance(x, str))):
                    fail(path, 'invalid or duplicate checklist item IDs')
                for item in items:
                    if type(item.get('status', 0)) is not int or item.get('status', 0) not in (0, 1):
                        fail(path, 'checklist item status must be 0/1')
                old_done = {x.get('id') for x in (current.get('items') or []) if isinstance(x, dict) and x.get('status') == 1 and isinstance(x.get('id'), str)}
                new_done = {x.get('id') for x in items if x.get('status') == 1 and isinstance(x.get('id'), str)}
                if old_done - new_done:
                    fail(path, 'update would remove or reset completed checklist items')

        if 'parentId' in task and not isinstance(task['parentId'], str):
            fail(path, 'parentId must be a real ID or empty string to detach')
        if action == 'update' and 'parentId' in task and (task['parentId'] or None) != (current.get('parentId') or None):
            moved.add(node_id)
            if node_id not in complete:
                fail(path, 'reparenting requires a complete descendant snapshot')
        graph[node_id] = effective
        affected.add(node_id)
        digest = fingerprint(task)
        key = (action, node_id if action == 'update' else digest)
        if key in seen:
            fail(path, 'duplicate creation or repeated update in batch')
        seen.add(key)
        digests.append({'index': i, 'payload_sha256': digest})

    # Reparenting can make descendants exceed the limit; include the whole subtree.
    frontier = set(moved)
    visited = set(moved)
    while frontier:
        next_nodes = {key for key, row in graph.items() if isinstance(row.get('parentId'), str) and row['parentId'] in frontier} - visited
        visited.update(next_nodes)
        affected.update(next_nodes)
        frontier = next_nodes
    for node_id in affected:
        trail = set()
        cursor = node_id
        project_id = graph[node_id]['projectId']
        while cursor:
            if cursor in trail:
                fail('parentId', 'cycle detected')
                break
            trail.add(cursor)
            row = graph.get(cursor)
            if row is None:
                fail('parentId', 'missing parent or ancestor in snapshot')
                break
            if row.get('projectId') != project_id:
                fail('parentId', 'ancestor belongs to another project')
                break
            parent = row.get('parentId')
            if parent is not None and not isinstance(parent, str):
                fail('parentId', 'malformed parent ID')
                break
            if parent and depth_limit is None:
                fail('parentId', 'verified max_task_depth required for nesting')
                break
            if depth_limit is not None and len(trail) > depth_limit:
                fail('parentId', 'maximum task depth exceeded')
                break
            cursor = parent
    if errors:
        return {'ok': False, 'errors': errors}
    return {'ok': True, 'operation_count': len(operations), 'validated_payloads': digests}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    try:
        result = validate(json.loads(args.input.read_text(encoding='utf-8-sig')))
    except (OSError, ValueError, TypeError, RecursionError):
        result = {'ok': False, 'errors': ['input could not be read as valid guard JSON']}
    print(json.dumps(result, ensure_ascii=True))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

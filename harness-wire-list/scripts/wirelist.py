"""Evidence-preserving extraction from reviewed CAD table regions. Stdlib only."""
import argparse
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
from pathlib import Path
import sys

REQUIRED = {'wire_id', 'from_id', 'from_pin', 'to_id', 'to_pin'}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)


def entities(data):
    out, seen = [], set()
    for e in data:
        if not e.get('text'):
            continue
        xy = e.get('10', [e.get('x'), e.get('y')])
        space = e.get('space', e.get('block', ''))
        handle = e.get('handle', e.get('5'))
        if not space or not handle or len(xy) < 2 or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in xy[:2]):
            raise ValueError('Text entity missing space, handle or finite coordinates')
        key = (space, handle)
        if key in seen:
            raise ValueError(f'Duplicate entity identity: {key}; use instance paths for blocks')
        seen.add(key)
        if not isinstance(e['text'], str):
            raise ValueError('Entity text must be a string')
        out.append({'space': space, 'handle': str(handle), 'x': xy[0], 'y': xy[1],
                    'text': e['text'], 'raw_text': e.get('raw_text', e.get('1', e['text']))})
    return out


def scan(data):
    text = entities(data)
    return {'entity_count': len(data), 'text_count': len(text),
            'spaces': dict(Counter(e.get('space', e.get('block', '?')) for e in data)),
            'object_types': dict(Counter(e.get('type', e.get('0', '?')) for e in data)),
            'header_candidates': [e for e in text if e['text'].strip().casefold() in
                                  ('wire id', 'wire', '线号', '导线编号')],
            'coverage': 'Inventory only. Inspect tables, blocks, attributes, layouts and xrefs separately.'}


def issue(code, **details):
    return {'code': code, **details}


def extract(data, plan):
    source = plan['source']
    for field in ('id', 'path', 'sha256', 'harness', 'drawing_number', 'revision',
                  'project', 'length_unit', 'size_unit', 'method', 'uncovered'):
        if field not in source:
            raise ValueError(f'Missing source field: {field}')
    if not source['id'] or not source['harness'] or not isinstance(source['uncovered'], list):
        raise ValueError('Invalid source identity or uncovered list')
    if digest(source['path']) != source['sha256']:
        raise ValueError('Source SHA-256 mismatch; do not reuse a stale extraction plan')
    tables = plan['tables']
    if not tables:
        raise ValueError('No reviewed tables')
    text, records, problems, counts, scopes = entities(data), [], [], [], []
    for t in tables:
        tid, space, bounds = t['id'], t['space'], t['bounds']
        left, bottom, right, top = bounds
        ys, tol, cols = t['rows_y'], t['tolerance'], t['columns']
        if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in bounds + ys + [tol]):
            raise ValueError('Non-finite geometry')
        if not left < right or not bottom < top or not ys or tol <= 0:
            raise ValueError(f'Invalid table geometry: {tid}')
        if any(not bottom < y < top for y in ys) or any(abs(a-b) <= 2*tol for i,a in enumerate(ys) for b in ys[i+1:]):
            raise ValueError(f'Ambiguous/outside row bands: {tid}')
        if type(t['expected_records']) is not int or t['expected_records'] < 0:
            raise ValueError('expected_records must be an independently reviewed nonnegative integer')
        fields = [c['field'] for c in cols]
        if len(fields) != len(set(fields)) or not REQUIRED <= set(fields):
            raise ValueError(f'Duplicate or missing required columns: {tid}')
        for i,c in enumerate(cols):
            if not left <= c['left'] < c['right'] <= right:
                raise ValueError(f'Column outside table: {tid}')
            if any(max(c['left'],d['left']) < min(c['right'],d['right']) for d in cols[i+1:]):
                raise ValueError(f'Overlapping columns: {tid}')
        for old in scopes:
            if old['id'] == tid or (space == old['space'] and
                max(left,old['bounds'][0]) < min(right,old['bounds'][2]) and
                max(bottom,old['bounds'][1]) < min(top,old['bounds'][3])):
                raise ValueError(f'Duplicate id or overlapping tables: {tid}')
        scopes.append(t)
        cells = defaultdict(lambda: defaultdict(list))
        for e in text:
            if e['space'] != space or not (left <= e['x'] < right and bottom < e['y'] < top):
                continue
            ri = [i for i,y in enumerate(ys) if abs(e['y']-y) <= tol]
            ci = [c['field'] for c in cols if c['left'] <= e['x'] < c['right']]
            if len(ri) != 1 or len(ci) != 1:
                problems.append(issue('unassigned_text', source_id=source['id'], table=tid, evidence=e))
            else:
                cells[ri[0]][ci[0]].append(e)
        start = len(records)
        for i in sorted(cells):
            row = cells[i]
            rid = f"{source['id']}/{source['harness']}/{tid}/{i+1}"
            values = {field: row[field][0]['text'] if len(row[field]) == 1 else None for field in fields}
            for field in fields:
                if len(row[field]) > 1:
                    problems.append(issue('multiple_cell_values', record_id=rid, field=field, evidence=row[field]))
            for field in sorted(REQUIRED):
                if values[field] in (None, ''):
                    problems.append(issue('missing_required_value', record_id=rid, field=field))
            for field in ('size', 'length'):
                value = values.get(field)
                if value not in (None, '', '-'):
                    try:
                        n = Decimal(value)
                        if not n.is_finite() or n < 0:
                            raise InvalidOperation
                    except InvalidOperation:
                        problems.append(issue('invalid_numeric_text', record_id=rid, field=field, value=value))
            records.append({'record_id':rid, 'source_id':source['id'], 'harness':source['harness'],
                            'table':tid, 'row':i+1, 'values':values, 'evidence':dict(row)})
        actual = len(records)-start
        counts.append({'source_id':source['id'], 'table':tid, 'expected':t['expected_records'], 'actual':actual})
        if actual != t['expected_records']:
            problems.append(issue('row_count_mismatch', **counts[-1]))
    for area in source['uncovered']:
        problems.append(issue('uncovered_source_area', source_id=source['id'], area=area))
    return {'schema':'harness-wire-list/v1', 'sources':[source], 'records':records,
            'tables':counts, 'issues':problems, 'status':'needs_review' if problems else 'extracted_not_crosschecked'}


def equal_value(field, a, b):
    if field == 'size':
        try:
            return Decimal(a) == Decimal(b)
        except InvalidOperation:
            pass
    return a == b


def assemble(batches, pins):
    records, sources, problems, tables, ids = [], {}, [], [], set()
    for batch in batches:
        if batch.get('schema') != 'harness-wire-list/v1':
            raise ValueError('Unsupported extraction schema')
        for source in batch['sources']:
            if source['id'] in sources and sources[source['id']] != source:
                raise ValueError('Source id reused for different source identity')
            sources[source['id']] = source
        for row in batch['records']:
            if row['record_id'] in ids:
                raise ValueError('Repeated input record; do not append the same extraction twice')
            if row['source_id'] not in sources:
                raise ValueError('Record source missing')
            ids.add(row['record_id']); records.append(row)
        problems.extend(batch['issues']); tables.extend(batch['tables'])
    if not records:
        raise ValueError('No extracted records to assemble')
    index = defaultdict(list)
    for p in pins:
        ev = p.get('evidence', {})
        if (not ev.get('handles') or not ev.get('table') or ev.get('source_id') != p['source_id']
            or p['source_id'] not in sources):
            raise ValueError('Pin record needs independent same-source evidence')
        key = tuple(p[k] for k in ('source_id','harness','connector','pin','wire_id'))
        if not all(isinstance(v,str) and v for v in key):
            raise ValueError('Pin identifiers must be nonempty text')
        if not isinstance(p.get('values'), dict) or any(v is not None and not isinstance(v,str) for v in p['values'].values()):
            raise ValueError('Pin values must be original text or null')
        index[key].append(p)
    stats = Counter(total_endpoints=2*len(records), matched_endpoints=0, unmatched_endpoints=0,
                    ambiguous_endpoints=0, compared_fields=0, not_comparable_fields=0, differences=0)
    groups = defaultdict(list)
    for r in records:
        v = r['values']
        groups[(r['source_id'],r['harness'],v['wire_id'])].append(r['record_id'])
        for side,n in [('from',1),('to',2)]:
            key = (r['source_id'],r['harness'],v.get(side+'_id'),v.get(side+'_pin'),v.get('wire_id'))
            matches = index.get(key, [])
            if len(matches) != 1:
                kind = 'ambiguous' if matches else 'unmatched'
                stats[kind+'_endpoints'] += 1
                problems.append(issue(kind+'_endpoint',record_id=r['record_id'],end=side,match_count=len(matches)))
                continue
            stats['matched_endpoints'] += 1
            p = matches[0]
            fields = [(f,f) for f in ['color','size','material','option','multicore']]
            fields += [(f+str(n),f) for f in ['terminal','seal']]
            for field,pfield in fields:
                a,b = v.get(field),p['values'].get(pfield)
                if a in (None,'') or b in (None,''):
                    stats['not_comparable_fields'] += 1
                    continue
                stats['compared_fields'] += 1
                if not equal_value(pfield,a,b):
                    stats['differences'] += 1
                    problems.append(issue('field_difference', record_id=r['record_id'],end=side,field=field,
                                          wire_value=a,pin_value=b,wire_evidence=r['evidence'].get(field),
                                          pin_evidence=p['evidence']))
    duplicates = [dict(source_id=k[0],harness=k[1],wire_id=k[2],records=rs) for k,rs in groups.items() if len(rs)>1]
    problems.extend(issue('duplicate_wire_id',**d) for d in duplicates)
    if sum(stats[k] for k in ('matched_endpoints','unmatched_endpoints','ambiguous_endpoints')) != stats['total_endpoints']:
        raise AssertionError('Endpoint accounting failed')
    # shortcut: per-harness physical segments stay separate; mating requires reviewed interface evidence.
    return {'schema':'harness-wire-list/v1','sources':list(sources.values()),'records':records,
            'tables':tables,'issues':problems,'audit':dict(stats),'duplicate_groups':duplicates,
            'status':'needs_review' if problems else 'checked_within_supplied_scope'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('scan','extract','assemble'):
        p = sub.add_parser(name); p.add_argument('--output',required=True)
        if name != 'assemble': p.add_argument('--entities',required=True)
        if name == 'extract': p.add_argument('--plan',required=True)
        if name == 'assemble':
            p.add_argument('--inputs',nargs='+',required=True); p.add_argument('--pins')
    args = parser.parse_args()
    try:
        if args.command == 'scan': result = scan(read(args.entities))
        elif args.command == 'extract':
            result = extract(read(args.entities),read(args.plan))
            result['sources'][0]['entity_file_sha256'] = digest(args.entities)
        else: result = assemble([read(p) for p in args.inputs],read(args.pins) if args.pins else [])
        write(args.output,result)
        print(json.dumps({'output':args.output,'records':len(result.get('records',[])),
                          'issues':len(result.get('issues',[])),'status':result.get('status','inventory')},ensure_ascii=False))
        return 2 if result.get('issues') else 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(str(exc),file=sys.stderr); return 1


if __name__ == '__main__':
    sys.exit(main())

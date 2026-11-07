#!/usr/bin/env python3
"""Score observed offline scenario outcomes; does not run a model or Dida."""
import argparse
import json
from pathlib import Path

EXPECTATIONS = Path(__file__).resolve().parents[1] / 'evals' / 'expectations.json'


def score(document, expectations):
    errors, reports = [], []
    if not isinstance(document, dict) or document.get('evaluationType') not in ('isolated_model_replay', 'manual_trace_review'):
        return {'ok': False, 'errors': ['evaluationType must describe actual evaluation method']}
    results = document.get('results')
    if not isinstance(results, list):
        return {'ok': False, 'errors': ['results array required']}
    index = {}
    for row in results:
        if not isinstance(row, dict) or not isinstance(row.get('caseId'), str):
            errors.append('invalid result record')
            continue
        key = row['caseId']
        if key in index:
            errors.append(f'{key}: duplicate result')
        index[key] = row
    for key, expected in expectations.items():
        row = index.get(key, {})
        observed = row.get('observed')
        problems = []
        if not isinstance(observed, dict):
            observed = {}
            problems.append('missing observed outcome')
        trace = row.get('traceEvidence')
        if not isinstance(trace, list) or not trace or not all(isinstance(x, str) and x.strip() for x in trace):
            problems.append('missing trace evidence')
        for field, value in expected.items():
            actual = observed.get(field)
            if field not in observed or type(actual) is not type(value) or actual != value:
                problems.append(f'{field}: expected {value!r}, observed {actual!r}')
        reports.append({'caseId': key, 'passed': not problems, 'failures': problems})
    extras = set(index) - set(expectations)
    if extras:
        errors.append('unknown case IDs: ' + ', '.join(sorted(extras)))
    passed = sum(row['passed'] for row in reports)
    return {'ok': not errors and passed == len(expectations), 'passed': passed,
            'total': len(expectations), 'errors': errors, 'cases': reports}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    try:
        result = score(json.loads(args.input.read_text(encoding='utf-8-sig')),
                       json.loads(EXPECTATIONS.read_text(encoding='utf-8')))
    except (OSError, ValueError, TypeError):
        result = {'ok': False, 'errors': ['input or expectations could not be read']}
    print(json.dumps(result, ensure_ascii=True))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

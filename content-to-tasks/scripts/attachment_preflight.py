#!/usr/bin/env python3
"""Check local attachments and adapter evidence. Does not contact Dida or upload."""
import argparse
import hashlib
import json
from pathlib import Path

DEFAULT_MAX_BYTES = 10_000_000  # Conservative skill policy, not an account entitlement.


def preflight(manifest):
    if not isinstance(manifest, dict):
        return {'status': 'blocked', 'can_create_task': False, 'can_upload': False,
                'issues': ['manifest must be an object'], 'files': [], 'unverified': []}
    issues, unverified, files = [], [], []
    body = manifest.get('independent_content') is True
    if type(manifest.get('independent_content')) is not bool:
        issues.append('independent_content must be bool')
        body = False
    if manifest.get('attachment_mode') != 'enabled':
        issues.append('attachment upload is disabled or not configured')
    if manifest.get('session') != 'ready' or manifest.get('account_match') is not True:
        issues.append('same-account authenticated session is not verified')
    if manifest.get('protocol') != 'verified':
        issues.append('private protocol is changed or unverified')
    limits = manifest.get('limits', {})
    if not isinstance(limits, dict):
        issues.append('limits must be an object')
        limits = {}
    account_limit = limits.get('account_max_bytes')
    adapter_limit = limits.get('adapter_max_bytes')
    bounds = []
    for name, value in (('account_max_bytes', account_limit), ('adapter_max_bytes', adapter_limit)):
        if value is not None:
            if type(value) is not int or value < 1:
                issues.append(f'{name} must be a positive integer or null')
            else:
                bounds.append(value)
    if account_limit is None:
        bounds.append(DEFAULT_MAX_BYTES)
        unverified.append('account limit unknown; applied 10,000,000-byte ceiling')
    max_bytes = min(bounds) if bounds else DEFAULT_MAX_BYTES
    attachments = manifest.get('attachments')
    if not isinstance(attachments, list) or not attachments:
        issues.append('nonempty attachments array required')
        attachments = []
    for name in ('remaining_task_slots', 'remaining_daily_slots'):
        value = limits.get(name)
        if value is None:
            unverified.append(f'{name} unknown; server may still reject upload')
        elif type(value) is not int or value < 0:
            issues.append(f'{name} must be a nonnegative integer or null')
        elif value < len(attachments):
            issues.append(f'{name} insufficient')
    for index, item in enumerate(attachments):
        if not isinstance(item, dict) or not isinstance(item.get('path'), str) or not item['path']:
            issues.append(f'attachments[{index}] needs a local path')
            continue
        path = Path(item['path'])
        try:
            if not path.is_file():
                raise OSError('not a file')
            before = path.stat()
            if before.st_size > max_bytes:
                issues.append(f'attachments[{index}] exceeds {max_bytes} bytes')
                continue
            if before.st_size == 0:
                issues.append(f'attachments[{index}] is empty')
                continue
            digest = hashlib.sha256()
            with path.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(chunk)
            after = path.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                issues.append(f'attachments[{index}] changed during preflight')
                continue
            files.append({'index': index, 'name': path.name, 'size': after.st_size,
                          'sha256': digest.hexdigest()})
        except (OSError, ValueError):
            issues.append(f'attachments[{index}] cannot be read')
    status = 'ready' if not issues else ('body_only' if body else 'blocked')
    return {'status': status, 'can_create_task': status != 'blocked',
            'can_upload': status == 'ready', 'max_bytes': max_bytes,
            'issues': issues, 'unverified': unverified, 'files': files}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    try:
        result = preflight(json.loads(args.input.read_text(encoding='utf-8-sig')))
    except (OSError, ValueError, TypeError):
        result = preflight(None)
    print(json.dumps(result, ensure_ascii=True))
    # body_only is a handled degradation, but never a successful attachment check.
    return 0 if result['can_upload'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

"""Offline attachment preflight tests. No account access or test uploads."""
import tempfile
import unittest
from pathlib import Path

from attachment_preflight import DEFAULT_MAX_BYTES, preflight


class AttachmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.file = Path(self.temp.name) / 'image.png'
        self.file.write_bytes(b'known local fixture')
        self.data = {'attachment_mode': 'enabled', 'session': 'ready', 'account_match': True,
                     'protocol': 'verified', 'independent_content': False, 'limits': {},
                     'attachments': [{'path': str(self.file)}]}

    def test_ready_with_hash_and_unknown_quota_notice(self):
        result = preflight(self.data)
        self.assertEqual(result['status'], 'ready')
        self.assertEqual(result['max_bytes'], DEFAULT_MAX_BYTES)
        self.assertEqual(len(result['files'][0]['sha256']), 64)
        self.assertEqual(len(result['unverified']), 3)

    def test_unknown_account_limit_is_decimal_10mb(self):
        with self.file.open('wb') as stream:
            stream.truncate(10_000_001)
        result = preflight(self.data)
        self.assertEqual(result['status'], 'blocked')
        self.assertFalse(result['can_create_task'])

    def test_exact_limit_accepted(self):
        self.data['limits']['account_max_bytes'] = self.file.stat().st_size
        self.assertEqual(preflight(self.data)['status'], 'ready')

    def test_verified_account_and_adapter_take_minimum(self):
        self.data['limits'].update(account_max_bytes=30_000_000, adapter_max_bytes=20_000_000)
        self.assertEqual(preflight(self.data)['max_bytes'], 20_000_000)

    def test_adapter_limit_cannot_raise_unknown_account_limit(self):
        self.data['limits']['adapter_max_bytes'] = 20_971_520
        self.assertEqual(preflight(self.data)['max_bytes'], 10_000_000)

    def test_image_only_disabled_session_or_protocol_blocks_creation(self):
        for field, value in (('attachment_mode', 'disabled'), ('session', 'expired'),
                             ('account_match', False), ('protocol', 'changed'), ('protocol', 'unknown')):
            with self.subTest(field=field, value=value):
                candidate = dict(self.data, **{field: value})
                result = preflight(candidate)
                self.assertFalse(result['can_create_task'])
                self.assertFalse(result['can_upload'])

    def test_independent_body_degrades_without_upload(self):
        self.data.update(protocol='changed', independent_content=True)
        result = preflight(self.data)
        self.assertEqual(result['status'], 'body_only')
        self.assertTrue(result['can_create_task'])
        self.assertFalse(result['can_upload'])

    def test_zero_remaining_quota(self):
        self.data['limits']['remaining_task_slots'] = 0
        self.assertEqual(preflight(self.data)['status'], 'blocked')

    def test_missing_or_empty_file(self):
        self.file.write_bytes(b'')
        self.assertEqual(preflight(self.data)['status'], 'blocked')
        self.file.unlink()
        self.assertEqual(preflight(self.data)['status'], 'blocked')

    def test_malformed_evidence(self):
        for candidate in (None, {}, dict(self.data, limits=[]), dict(self.data, independent_content='true'),
                          dict(self.data, attachments=[]), dict(self.data, limits={'account_max_bytes': True})):
            self.assertFalse(preflight(candidate)['can_upload'])


if __name__ == '__main__':
    unittest.main()

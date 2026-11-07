"""Hub contract validation, using fixtures only."""
import copy
import json
import unittest
from pathlib import Path

from validate_hub_result import SCHEMA, validate


class HubTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((SCHEMA.parent / 'hub-plan.example.json').read_text(encoding='utf-8'))

    @property
    def row(self):
        return self.data['tasks'][0]

    def assert_ok(self):
        result = validate(self.data)
        self.assertTrue(result['ok'], result)

    def assert_bad(self):
        self.assertFalse(validate(self.data)['ok'])

    def executed(self):
        self.data.update(mode='execute', executor='agent', status='executed')
        self.row.update(remoteId='real-task-id', verified=True)
        self.data['verification'].update(readBack=True, verifiedAt='2026-10-08T10:00:00+08:00')
        self.data['attachments'][0].update(state='readable', remoteId='real-attachment-id')

    def test_schema_is_valid_draft_2020_12(self):
        from jsonschema import Draft202012Validator
        Draft202012Validator.check_schema(json.loads(SCHEMA.read_text(encoding='utf-8')))

    def test_complete_plan_example(self):
        self.assert_ok()

    def test_extraction_without_actions_can_return_empty_plan(self):
        self.data.update(tasks=[], attachments=[], reason='仅提取：未发现用户行动')
        self.assert_ok()

    def test_version_and_policy_must_match(self):
        for field in ('contractVersion', 'didaPolicyVersion'):
            candidate = copy.deepcopy(self.data)
            candidate[field] = 'old-version'
            self.assertFalse(validate(candidate)['ok'])

    def test_legacy_overloaded_kind_rejected(self):
        self.row['kind'] = self.row.pop('taskClass')
        self.assert_bad()

    def test_plan_cannot_claim_creation(self):
        self.row['remoteId'] = 'invented'
        self.assert_bad()

    def test_plan_cannot_claim_verified_existing_task(self):
        self.row.update(operation='reuse', remoteId='existing', verified=True)
        self.row['task']['id'] = 'existing'
        self.assert_bad()

    def test_plan_can_reuse_existing_identity(self):
        self.row.update(operation='reuse', remoteId='existing')
        self.row['task']['id'] = 'existing'
        self.assert_ok()

    def test_plan_has_one_host_writer(self):
        self.data['executor'] = 'agent'
        self.assert_bad()

    def test_plan_cannot_report_attachment_success(self):
        self.data['attachments'][0].update(state='uploaded', remoteId='invented')
        self.assert_bad()

    def test_executed_requires_all_readback(self):
        self.executed()
        self.assert_ok()
        self.data['attachments'][0]['state'] = 'linked'
        self.assert_bad()

    def test_executed_needs_task_verification(self):
        self.executed()
        self.row['verified'] = False
        self.assert_bad()

    def test_verification_timestamp_format(self):
        self.executed()
        self.data['verification']['verifiedAt'] = 'yesterday'
        self.assert_bad()

    def test_partial_requires_actual_side_effect(self):
        self.data.update(mode='execute', status='partial', issues=['attachment failed'])
        self.assert_bad()
        self.row['remoteId'] = 'real-task'
        self.assert_ok()

    def test_partial_update_can_have_failed_field_verification(self):
        self.data.update(mode='execute', status='partial', issues=['NOTE type not applied'])
        self.row.update(operation='update', remoteId='existing', writeConfirmed=True)
        self.row['task']['id'] = 'existing'
        self.assert_ok()

    def test_failed_cannot_hide_created_record(self):
        self.data.update(mode='execute', status='failed', issues=['attachment failed'])
        self.row['remoteId'] = 'real-task'
        self.assert_bad()

    def test_needs_connection_cannot_hide_partial_write(self):
        self.data.update(mode='execute', status='needs_connection', issues=['session expired'])
        self.row['remoteId'] = 'real-task'
        self.assert_bad()

    def test_unknown_does_not_require_inventing_remote_id(self):
        self.data.update(mode='execute', status='unknown', issues=['create timed out; unable to read'])
        self.assert_ok()

    def test_unknown_attachment_cannot_be_reported_as_failed(self):
        self.data.update(mode='execute', status='failed', issues=['upload timed out'])
        self.row.update(operation='reuse', remoteId='existing')
        self.row['task']['id'] = 'existing'
        self.data['attachments'][0]['state'] = 'unknown'
        self.assert_bad()
        self.data['status'] = 'unknown'
        self.assert_ok()

    def test_confirmed_write_requires_traceable_id(self):
        self.data.update(mode='execute', status='partial', issues=['field verification failed'])
        self.row['writeConfirmed'] = True
        self.assert_bad()

    def test_missing_inbox_can_return_connection_gap(self):
        self.data.update(status='needs_connection', tasks=[], attachments=[], issues=['inbox identity unavailable'])
        self.data['destination']['allowedProjectIds'] = []
        self.assert_ok()

    def test_mismatching_remote_ids(self):
        self.row.update(operation='update', remoteId='a')
        self.row['task']['id'] = 'b'
        self.assert_bad()

    def test_duplicate_local_identity(self):
        self.data['tasks'].append(copy.deepcopy(self.row))
        self.assert_bad()

    def test_missing_or_cyclic_parent(self):
        self.row['parentLocalId'] = 'missing'
        self.assert_bad()
        self.row['parentLocalId'] = self.row['localId']
        self.assert_bad()

    def test_cross_project_parent(self):
        parent = copy.deepcopy(self.row)
        parent['localId'] = 'parent'
        parent['task']['projectId'] = 'other-project'
        self.data['destination']['allowedProjectIds'].append('other-project')
        self.data['tasks'].append(parent)
        self.row['parentLocalId'] = 'parent'
        self.assert_bad()

    def test_attachment_relation_must_resolve(self):
        self.data['attachments'][0]['localTaskId'] = 'missing'
        self.assert_bad()

    def test_duplicate_attachment_binding(self):
        self.data['attachments'].append(copy.deepcopy(self.data['attachments'][0]))
        self.assert_bad()

    def test_out_of_scope_project(self):
        self.row['task']['projectId'] = 'foreign'
        self.assert_bad()

    def test_source_url_preserved_in_body(self):
        self.data['source']['urls'] = ['https://example.com/article?id=7']
        self.assert_bad()
        self.row['task']['content'] = '原文\n来源：https://example.com/article?id=7'
        self.assert_ok()

    def test_checklist_source_url_uses_desc(self):
        self.data['source']['urls'] = ['https://example.com/tutorial']
        self.row['taskClass'] = 'action'
        self.row['task'].update(kind='CHECKLIST', desc='https://example.com/tutorial')
        self.assert_ok()

    def test_kind_matches_class(self):
        self.row['task']['kind'] = 'TEXT'
        self.assert_bad()

    def test_schema_rejects_wrong_priority(self):
        self.row['task']['priority'] = 2
        self.assert_bad()


if __name__ == '__main__':
    unittest.main()

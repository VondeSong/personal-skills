"""Offline guard regression tests with synthetic live snapshots."""
import copy
import unittest

from validate_dida_payload import CLEAR_DATE, validate


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.data = {
            'snapshot': {
                'projects': [{'id': 'p1', 'permission': None, 'closed': None},
                             {'id': 'p2', 'permission': 'write', 'closed': False}],
                'inbox_project_id': 'p1',
                'tags': [{'name': 'pc', 'label': '电脑'}, {'name': '等待'}],
                'columns': [{'id': 'c1', 'projectId': 'p1'}, {'id': 'c2', 'projectId': 'p2'}],
                'tasks': [{'id': 't1', 'projectId': 'p1', 'kind': 'TEXT', 'tags': ['pc']}],
                'max_task_depth': 3, 'subtree_complete_ids': []},
            'allowed_project_ids': ['p1', 'p2'],
            'operations': [{'operation': 'create', 'taskClass': 'action', 'explicit_fields': {},
                            'task': {'title': '核对报告', 'projectId': 'p1', 'kind': 'TEXT'}}]}

    @property
    def op(self):
        return self.data['operations'][0]

    @property
    def task(self):
        return self.op['task']

    @property
    def current(self):
        return self.data['snapshot']['tasks'][0]

    def assert_ok(self):
        result = validate(self.data)
        self.assertTrue(result['ok'], result)
        return result

    def assert_bad(self, text):
        result = validate(self.data)
        self.assertFalse(result['ok'], result)
        self.assertIn(text, '\n'.join(result['errors']))

    def note(self):
        self.op['taskClass'] = 'reference'
        self.task['kind'] = 'NOTE'

    def update(self):
        self.op['operation'] = 'update'
        self.task['id'] = 't1'

    def node(self, identifier, parent=None, project='p1'):
        self.data['snapshot']['tasks'].append({'id': identifier, 'projectId': project, 'kind': 'TEXT', 'parentId': parent})

    def test_valid_defaults_and_hash(self):
        self.assertEqual(len(self.assert_ok()['validated_payloads'][0]['payload_sha256']), 64)

    def test_exact_tags_only(self):
        self.task['tags'] = ['pc']
        self.assert_ok()
        for invalid in (['电脑'], ['new'], ['pc', 'pc'], None, 'pc'):
            with self.subTest(invalid=invalid):
                self.task['tags'] = invalid
                self.assertFalse(validate(self.data)['ok'])

    def test_tag_read_failure_requires_omission(self):
        self.data['snapshot']['tags'] = None
        self.assert_ok()
        self.task['tags'] = ['pc']
        self.assert_bad('whitelist')

    def test_update_preserves_tags_during_read_failure(self):
        self.update()
        self.data['snapshot']['tags'] = None
        self.assert_ok()
        self.task['tags'] = ['pc']
        self.assert_ok()
        self.task['tags'] = ['pc', '等待']
        self.assert_bad('whitelist')

    def test_update_cannot_remove_existing_tags(self):
        self.update()
        self.task['tags'] = ['等待']
        self.assert_bad('remove existing tags')

    def test_missing_allowed_projects(self):
        del self.data['allowed_project_ids']
        self.assert_bad('allowed_project_ids')

    def test_empty_allowed_projects(self):
        self.data['allowed_project_ids'] = []
        self.assert_bad('allowed_project_ids')

    def test_destination_scope(self):
        self.task['projectId'] = 'missing'
        self.assert_bad('projectId')
        self.task['projectId'] = 'p1'
        self.data['allowed_project_ids'] = ['p2']
        self.assert_bad('projectId')

    def test_null_permission_closed_true(self):
        self.data['snapshot']['projects'][0]['closed'] = True
        self.assert_bad('closed')

    def test_closed_strict_boolean(self):
        for value in (0, 1, 'false'):
            with self.subTest(value=value):
                self.data['snapshot']['projects'][0]['closed'] = value
                self.assert_bad('closed must be bool')

    def test_permissions(self):
        for value in ('read', 'comment', 'owner'):
            with self.subTest(value=value):
                self.data['snapshot']['projects'][0]['permission'] = value
                self.assertFalse(validate(self.data)['ok'])

    def test_column_create_and_update(self):
        for operation in ('create', 'update'):
            with self.subTest(operation=operation):
                if operation == 'update':
                    self.update()
                self.task['columnId'] = 'c1'
                self.assert_ok()
                self.task['columnId'] = 'c2'
                self.assert_bad('columnId')

    def test_kind_enumeration(self):
        for kind in ('reference', 'action', 'text', None, []):
            with self.subTest(kind=kind):
                self.task['kind'] = kind
                self.assert_bad('kind')

    def test_class_kind_consistency(self):
        self.op['taskClass'] = 'reference'
        self.assert_bad('disagree')

    def test_priority(self):
        for value in (0, 1, 3, 5):
            self.task['priority'] = value
            self.assert_ok()
        for value in (2, 4, -1, True, 1.0, '3'):
            self.task['priority'] = value
            self.assert_bad('priority')

    def test_note_defaults(self):
        self.note()
        self.assert_ok()

    def test_note_requires_inbox_identity(self):
        self.note()
        del self.data['snapshot']['inbox_project_id']
        self.assert_bad('verified inbox')

    def test_note_not_routed_by_topic(self):
        self.note()
        self.task['projectId'] = 'p2'
        self.assert_bad('verified inbox')
        self.op['explicit_fields'] = {'projectId': '请放入资料清单'}
        self.assert_ok()

    def test_note_nondefault_fields_need_evidence(self):
        self.note()
        baseline = copy.deepcopy(self.data)
        fields = {'tags': ['pc'], 'columnId': 'c1', 'parentId': 't1', 'priority': 1,
                  'reminders': ['TRIGGER:-PT10M'], 'repeatFlag': 'RRULE:FREQ=DAILY',
                  'repeatFrom': 1, 'assigneeUsername': 'user',
                  'startDate': '2026-10-10T10:00:00+08:00', 'dueDate': '2026-10-10T11:00:00+08:00'}
        for field, value in fields.items():
            with self.subTest(field=field):
                self.data = copy.deepcopy(baseline)
                self.task[field] = value
                self.task['timeZone'] = 'Asia/Shanghai'
                self.assert_bad(f'NOTE {field}')
                self.op['explicit_fields'][field] = '用户明确要求设置该属性'
                self.assert_ok()

    def test_note_items_not_allowed_even_with_evidence(self):
        self.note()
        self.task['items'] = [{'title': 'follow up'}]
        self.op['explicit_fields'] = {'items': '写成清单'}
        self.assert_bad('CHECKLIST')

    def test_note_conversion_cannot_inherit_checklist_items(self):
        self.note()
        self.update()
        self.current['kind'] = 'CHECKLIST'
        self.current['items'] = [{'id': 'i1', 'title': 'old step', 'status': 0}]
        self.assert_bad('after merging update')

    def test_note_update_preserves_user_attributes(self):
        self.note()
        self.update()
        self.current['kind'] = 'NOTE'
        self.current['columnId'] = 'c1'
        self.task.update(tags=['pc'], columnId='c1')
        self.assert_ok()
        self.task['tags'] = ['pc', '等待']
        self.assert_bad('NOTE tags')

    def test_explicit_evidence_does_not_bypass_tag_whitelist(self):
        self.note()
        self.task['tags'] = ['unknown']
        self.op['explicit_fields'] = {'tags': '加此标签'}
        self.assert_bad('whitelist')

    def test_blank_or_unknown_evidence_rejected(self):
        for value in ({'tags': ''}, {'anything': 'user request'}, []):
            self.op['explicit_fields'] = value
            self.assert_bad('explicit_fields')

    def test_parent_exists_and_same_project(self):
        self.task['parentId'] = 'missing'
        self.assert_bad('missing parent')
        self.task['parentId'] = 't1'
        self.assert_ok()
        self.current['projectId'] = 'p2'
        self.assert_bad('another project')

    def test_parent_depth_requires_capability(self):
        self.task['parentId'] = 't1'
        self.data['snapshot']['max_task_depth'] = None
        self.assert_bad('verified max_task_depth')

    def test_parent_depth_boundaries(self):
        self.node('t2', 't1')
        self.task['parentId'] = 't2'
        self.assert_ok()
        self.node('t3', 't2')
        self.task['parentId'] = 't3'
        self.assert_bad('maximum task depth')

    def test_parent_cycle_in_snapshot(self):
        self.current['parentId'] = 't2'
        self.node('t2', 't1')
        self.task['parentId'] = 't1'
        self.assert_bad('cycle')

    def test_reparent_requires_descendant_completeness(self):
        self.update()
        self.node('t2')
        self.task['parentId'] = 't2'
        self.assert_bad('complete descendant')
        self.data['snapshot']['subtree_complete_ids'] = ['t1']
        self.assert_ok()

    def test_reparent_self_cycle(self):
        self.update()
        self.task['parentId'] = 't1'
        self.data['snapshot']['subtree_complete_ids'] = ['t1']
        self.assert_bad('cycle')

    def test_reparent_descendant_depth_even_if_child_also_updated(self):
        self.update()
        self.node('child', 't1')
        self.node('grandchild', 'child')
        self.node('newparent')
        self.task['parentId'] = 'newparent'
        self.data['snapshot']['subtree_complete_ids'] = ['t1']
        self.data['operations'].append({'operation': 'update', 'taskClass': 'action',
                                       'task': {'id': 'child', 'projectId': 'p1', 'title': 'edited'}})
        self.assert_bad('maximum task depth')

    def test_update_date_order_merges_current_values(self):
        self.update()
        self.current.update(startDate='2026-10-10T10:00:00+08:00', timeZone='Asia/Shanghai')
        self.task['dueDate'] = '2026-10-10T01:00:00Z'
        self.assert_bad('later than')
        self.task['dueDate'] = '2026-10-10T02:00:00Z'
        self.assert_ok()

    def test_invalid_and_timezone_less_dates(self):
        self.task['timeZone'] = 'Asia/Shanghai'
        for value in ('tomorrow', '2026-02-30T09:00:00+08:00', '2026-10-10', '2026-10-10T09:00:00', None):
            self.task['dueDate'] = value
            self.assertFalse(validate(self.data)['ok'])

    def test_date_needs_timezone(self):
        self.task['dueDate'] = '2026-10-10T09:00:00+08:00'
        self.assert_bad('needs timeZone')

    def test_update_date_clear(self):
        self.task['dueDate'] = CLEAR_DATE
        self.assert_bad('update-only')
        self.update()
        self.assert_ok()

    def test_complete_status_requires_other_workflow(self):
        self.task['status'] = 2
        self.assert_bad('incomplete')
        self.update()
        self.current['status'] = 0
        self.assert_bad('completion workflow')

    def test_preserve_completed_checklist_items(self):
        self.update()
        self.task['kind'] = self.current['kind'] = 'CHECKLIST'
        self.current['items'] = [{'id': 'i1', 'title': 'done', 'status': 1}]
        self.task['items'] = []
        self.assert_bad('completed checklist')
        self.task['items'] = copy.deepcopy(self.current['items'])
        self.assert_ok()

    def test_invalid_item_ids_and_status(self):
        self.task['kind'] = 'CHECKLIST'
        for items in ([{'id': 'a'}, {'id': 'a'}], [{'id': []}], [{'status': True}], [{'status': 2}]):
            self.task['items'] = items
            self.assertFalse(validate(self.data)['ok'])

    def test_unknown_fields_require_mapping(self):
        self.task['project_id'] = 'p1'
        self.assert_bad('normalize')

    def test_unknown_update_or_move_rejected(self):
        self.update()
        self.task['id'] = 'missing'
        self.assert_bad('freshly read')
        self.task['id'] = 't1'
        self.task['projectId'] = 'p2'
        self.assert_bad('cross-project')

    def test_duplicate_create_or_update(self):
        self.data['operations'].append(copy.deepcopy(self.op))
        self.assert_bad('duplicate')

    def test_payload_digest_changes(self):
        first = self.assert_ok()['validated_payloads'][0]['payload_sha256']
        self.task['title'] = '提交报告'
        self.assertNotEqual(first, self.assert_ok()['validated_payloads'][0]['payload_sha256'])

    def test_tag_management_rejected(self):
        self.op['operation'] = 'create_tag'
        self.assert_bad('create/update')

    def test_malformed_input_rejected(self):
        for value in (None, [], {}, {'snapshot': {}}, {'snapshot': [], 'operations': []}):
            self.assertFalse(validate(value)['ok'])


if __name__ == '__main__':
    unittest.main()

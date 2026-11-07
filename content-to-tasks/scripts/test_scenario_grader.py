"""Test grading failures, not the skill's semantic behavior."""
import copy
import json
import unittest
from score_scenarios import EXPECTATIONS, score


class GraderTests(unittest.TestCase):
    def setUp(self):
        self.expectations = {'unknown-result': {'created': 1, 'replayed': False}}
        self.result = {'evaluationType': 'manual_trace_review', 'results': [
            {'caseId': 'unknown-result', 'observed': {'created': 1, 'replayed': False}, 'traceEvidence': ['trace:1']}]}

    def test_compliant_record_and_replayed_mutation(self):
        self.assertTrue(score(self.result, self.expectations)['ok'])
        self.result['results'][0]['observed']['replayed'] = True
        self.assertFalse(score(self.result, self.expectations)['ok'])

    def test_missing_and_duplicate_cases_fail(self):
        candidate = copy.deepcopy(self.result)
        candidate['results'] = []
        self.assertFalse(score(candidate, self.expectations)['ok'])
        self.result['results'].append(copy.deepcopy(self.result['results'][0]))
        self.assertFalse(score(self.result, self.expectations)['ok'])

    def test_outcome_without_trace_is_not_evidence(self):
        self.result['results'][0]['traceEvidence'] = []
        self.assertFalse(score(self.result, self.expectations)['ok'])

    def test_expected_cases_correspond_to_inputs(self):
        expected = json.loads(EXPECTATIONS.read_text(encoding='utf-8'))
        cases = json.loads((EXPECTATIONS.parent / 'cases.json').read_text(encoding='utf-8'))['evals']
        ids = [case['id'] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), set(expected))


if __name__ == '__main__':
    unittest.main()

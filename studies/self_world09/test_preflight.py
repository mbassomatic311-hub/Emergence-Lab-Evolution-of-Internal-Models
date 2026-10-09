import json
import unittest
from pathlib import Path
from copy import deepcopy
from preflight import (
    ProtocolError, check_draft, confirmatory_blockers,
    require_confirmatory_ready, validate_paired_population_results,
    validate_agent_observation,
)

PLAN = json.loads(Path(__file__).with_name('study_plan.json').read_text())


class ResearchGatesTests(unittest.TestCase):
    def test_proposed_draft_valid(self):
        self.assertEqual(check_draft(PLAN), [])
    def test_confirmatory_is_actually_blocked(self):
        self.assertGreaterEqual(len(confirmatory_blockers(PLAN)), 8)
        with self.assertRaisesRegex(ProtocolError, 'CONFIRMATORY RUN BLOCKED'):
            require_confirmatory_ready(PLAN)
    def test_seed_list_disallowed_in_draft(self):
        altered=deepcopy(PLAN);altered['confirmatory_seed_list']=[88]
        self.assertTrue(check_draft(altered))
    def test_cannot_claim_consciousness(self):
        altered=deepcopy(PLAN);altered['claims_consciousness']=True
        self.assertTrue(check_draft(altered))
    def test_missing_strong_benchmark_rejected(self):
        altered=deepcopy(PLAN);altered['baselines'].remove('bayesian_system_identifier')
        self.assertTrue(any('bayesian_system_identifier' in x for x in check_draft(altered)))
    def test_observation_accepts_agent_available_signals(self):
        validate_agent_observation({'sensor_values':[.1,-.2,4.0], 'last_action':3})
    def test_observation_rejects_privileged_truth(self):
        with self.assertRaises(ProtocolError):
            validate_agent_observation({'sensor_values':[.3], 'last_action':0, 'true_cause':'motor'})
    def test_observation_rejects_nan(self):
        with self.assertRaises(ProtocolError):
            validate_agent_observation({'sensor_values':[float('nan')], 'last_action':1})
    def test_independent_populations_only(self):
        res=validate_paired_population_results([
            {'population_id':'P1','candidate':5,'comparator':4},
            {'population_id':'P2','candidate':2,'comparator':3}])
        self.assertEqual(res,[1,-1])
    def test_rejects_episode_pseudoreplication(self):
        with self.assertRaisesRegex(ProtocolError, 'Pseudoreplication'):
            validate_paired_population_results([
                {'population_id':'P1','candidate':5,'comparator':4},
                {'population_id':'P1','candidate':6,'comparator':4}])
    def test_rejects_oracle_labels_in_scored_rows(self):
        with self.assertRaisesRegex(ProtocolError,'Privileged'):
            validate_paired_population_results([
                {'population_id':'P1','candidate':5,'comparator':4,'true_cause':'motor'},
                {'population_id':'P2','candidate':6,'comparator':4}])
    def test_requires_two_independent_world_families(self):
        altered=deepcopy(PLAN);altered['environments']=altered['environments'][:1]
        self.assertTrue(check_draft(altered))


if __name__=='__main__':
    unittest.main()

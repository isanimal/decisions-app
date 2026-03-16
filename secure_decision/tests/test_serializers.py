import pytest
from datetime import datetime
from unittest.mock import Mock
from app.serializers import serialize_decision, serialize_revision, serialize_threat_lite
from app.models import Decision, DecisionRevision, ThreatLiteAssessment

class TestSerializers:
    """Test cases for data serializers"""

    def test_serialize_revision(self):
        """Test revision serialization"""
        revision = Mock(spec=DecisionRevision)
        revision.id = 1
        revision.decision_id = 100
        revision.created_by = 5
        revision.changed_at = datetime(2024, 1, 1, 12, 0, 0)
        revision.change_summary = "Updated title"
        revision.changed_fields = "title"
        revision.before_snapshot = "old data"
        revision.after_snapshot = "new data"

        result = serialize_revision(revision)

        expected = {
            "revision_id": 1,
            "decision_id": 100,
            "created_by": 5,
            "changed_at": "2024-01-01T12:00:00",
            "change_summary": "Updated title",
            "changed_fields": "title",
            "before_snapshot": "old data",
            "after_snapshot": "new data",
        }

        assert result == expected

    def test_serialize_decision_basic(self):
        """Test basic decision serialization without history"""
        decision = Mock(spec=Decision)
        decision.id = 1
        decision.title = "Test Decision"
        decision.context = "Test context"
        decision.status = "DRAFT"
        decision.superseded_by_id = None
        decision.team_id = 1
        decision.created_by = 2
        decision.updated_by = 3
        decision.archived = False
        decision.technical_goal = "Goal"
        decision.assumptions = "Assumptions"
        decision.conscious_simplifications = "Simplifications"
        decision.non_negotiables = "Non-negotiables"
        decision.accepted_worst_case = "Worst case"
        decision.created_at = datetime(2024, 1, 1, 10, 0, 0)
        decision.updated_at = datetime(2024, 1, 2, 11, 0, 0)
        decision.revisions = []

        result = serialize_decision(decision, include_history=False)

        assert result["decision_id"] == 1
        assert result["title"] == "Test Decision"
        assert result["status"] == "DRAFT"
        assert result["statement"]["technical_goal"] == "Goal"
        assert "history" not in result

    def test_serialize_decision_with_history(self):
        """Test decision serialization with revision history"""
        decision = Mock(spec=Decision)
        decision.id = 1
        decision.title = "Test Decision"
        decision.context = "Test context"
        decision.status = "ACTIVE"
        decision.superseded_by_id = None
        decision.team_id = 1
        decision.created_by = 2
        decision.updated_by = 3
        decision.archived = False
        decision.technical_goal = "Goal"
        decision.assumptions = "Assumptions"
        decision.conscious_simplifications = "Simplifications"
        decision.non_negotiables = "Non-negotiables"
        decision.accepted_worst_case = "Worst case"
        decision.created_at = datetime(2024, 1, 1, 10, 0, 0)
        decision.updated_at = datetime(2024, 1, 2, 11, 0, 0)

        # Mock revisions
        revision1 = Mock(spec=DecisionRevision)
        revision1.id = 1
        revision1.decision_id = 1
        revision1.created_by = 2
        revision1.changed_at = datetime(2024, 1, 1, 11, 0, 0)
        revision1.change_summary = "Initial creation"
        revision1.changed_fields = "all"
        revision1.before_snapshot = ""
        revision1.after_snapshot = "initial data"

        revision2 = Mock(spec=DecisionRevision)
        revision2.id = 2
        revision2.decision_id = 1
        revision2.created_by = 3
        revision2.changed_at = datetime(2024, 1, 2, 11, 0, 0)
        revision2.change_summary = "Updated status"
        revision2.changed_fields = "status"
        revision2.before_snapshot = "DRAFT"
        revision2.after_snapshot = "ACTIVE"

        decision.revisions = [revision2, revision1]  # Newest first

        result = serialize_decision(decision, include_history=True)

        assert result["decision_id"] == 1
        assert result["status"] == "ACTIVE"
        assert len(result["history"]) == 2

        # Check history is in correct order (newest first)
        assert result["history"][0]["revision_id"] == 2
        assert result["history"][0]["change_summary"] == "Updated status"
        assert result["history"][1]["revision_id"] == 1
        assert result["history"][1]["change_summary"] == "Initial creation"

    def test_serialize_threat_lite(self):
        """Test threat lite assessment serialization"""
        threat = Mock(spec=ThreatLiteAssessment)
        threat.id = 1
        threat.decision_id = 1
        threat.created_by = 2
        threat.updated_by = 3
        threat.archived = False
        threat.context_summary = "Context summary"
        threat.assumptions = "Assumptions"
        threat.assumption_stress_test = "Stress test"
        threat.boundaries_trust = "Boundaries"
        threat.threat_scenarios = "Scenarios"
        threat.reflection_outcome = "accept"
        threat.reflection_notes = "Notes"
        threat.reflection_rationale = "Rationale"
        threat.guided_mode = True
        threat.tags = "tag1,tag2"
        threat.created_at = datetime(2024, 1, 1, 10, 0, 0)
        threat.updated_at = datetime(2024, 1, 2, 11, 0, 0)

        result = serialize_threat_lite(threat)

        expected = {
            "id": 1,
            "decision_id": 1,
            "created_by": 2,
            "updated_by": 3,
            "archived": False,
            "context_summary": "Context summary",
            "assumptions": "Assumptions",
            "assumption_stress_test": "Stress test",
            "boundaries_trust": "Boundaries",
            "threat_scenarios": "Scenarios",
            "reflection_outcome": "accept",
            "reflection_notes": "Notes",
            "reflection_rationale": "Rationale",
            "guided_mode": True,
            "tags": "tag1,tag2",
            "created_at": "2024-01-01T10:00:00",
            "updated_at": "2024-01-02T11:00:00"
        }

        assert result == expected
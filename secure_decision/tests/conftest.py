import pytest
from unittest.mock import Mock
from app.models import Decision, User, Team, DecisionRevision, ThreatLiteAssessment
from app.kb_loader import KnowledgeBase

@pytest.fixture
def mock_kb():
    """Mock knowledge base"""
    kb = Mock(spec=KnowledgeBase)
    kb.cards = []
    kb.get_status.return_value = {"cards": 0, "status": "empty"}
    kb.match.return_value = []
    return kb

@pytest.fixture
def mock_user():
    """Mock user object"""
    user = Mock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.password_hash = "hashed_password"
    user.is_active = True
    user.default_team_id = 1
    return user

@pytest.fixture
def mock_team():
    """Mock team object"""
    team = Mock(spec=Team)
    team.id = 1
    team.name = "Test Team"
    return team

@pytest.fixture
def mock_decision(mock_user):
    """Mock decision object"""
    decision = Mock(spec=Decision)
    decision.id = 1
    decision.title = "Test Decision"
    decision.context = "Test context"
    decision.status = "DRAFT"
    decision.team_id = 1
    decision.created_by = mock_user.id
    decision.updated_by = mock_user.id
    decision.archived = False
    decision.technical_goal = "Test goal"
    decision.assumptions = "Test assumptions"
    decision.conscious_simplifications = "Test simplifications"
    decision.non_negotiables = "Test non-negotiables"
    decision.accepted_worst_case = "Test worst case"
    decision.superseded_by_id = None
    decision.created_at = Mock()
    decision.updated_at = Mock()
    decision.revisions = []
    decision.threat_lite_assessments = []
    decision.comments = []
    return decision

@pytest.fixture
def mock_decision_revision(mock_decision, mock_user):
    """Mock decision revision object"""
    revision = Mock(spec=DecisionRevision)
    revision.id = 1
    revision.decision_id = mock_decision.id
    revision.created_by = mock_user.id
    revision.changed_at = Mock()
    revision.change_summary = "Test change"
    revision.changed_fields = "title"
    revision.before_snapshot = "old"
    revision.after_snapshot = "new"
    revision.decision = mock_decision
    return revision

@pytest.fixture
def mock_threat_assessment(mock_decision, mock_user):
    """Mock threat lite assessment object"""
    threat = Mock(spec=ThreatLiteAssessment)
    threat.id = 1
    threat.decision_id = mock_decision.id
    threat.created_by = mock_user.id
    threat.updated_by = mock_user.id
    threat.archived = False
    threat.context_summary = "Test context"
    threat.assumptions = "Test assumptions"
    threat.assumption_stress_test = "Test stress test"
    threat.boundaries_trust = "Test boundaries"
    threat.threat_scenarios = "Test scenarios"
    threat.reflection_outcome = "accept"
    threat.reflection_notes = "Test notes"
    threat.reflection_rationale = "Test rationale"
    threat.guided_mode = True
    threat.tags = "test,tags"
    threat.created_at = Mock()
    threat.updated_at = Mock()
    threat.decision = mock_decision
    return threat
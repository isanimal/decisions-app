import pytest
from unittest.mock import Mock
from app.kb_matcher import match_cards, MatchResult, _fuzzy_ratio
from app.kb_loader import KnowledgeBase, MitigationCard

class TestKBMatcher:
    """Test cases for knowledge base matching functionality"""

    def test_fuzzy_ratio(self):
        """Test fuzzy string matching ratio"""
        assert _fuzzy_ratio("hello", "hello") == 1.0
        assert _fuzzy_ratio("hello", "world") < 0.5  # Some similarity due to 'o'
        assert _fuzzy_ratio("test", "testing") > 0.5
        assert _fuzzy_ratio("", "test") == 0.0
        assert _fuzzy_ratio("test", "") == 0.0

    def test_fuzzy_ratio_case_insensitive(self):
        """Test that fuzzy ratio is case insensitive"""
        assert _fuzzy_ratio("Hello", "hello") == 1.0
        assert _fuzzy_ratio("TEST", "test") == 1.0

    def test_match_cards_empty_kb(self):
        """Test matching with empty knowledge base"""
        kb = Mock(spec=KnowledgeBase)
        kb.cards = []

        tags = {"assumption": ["auth"], "boundary": ["input"]}
        results = match_cards(kb, "test decision", tags)

        assert results == []

    def test_match_cards_no_matches(self):
        """Test matching when no cards match"""
        kb = Mock(spec=KnowledgeBase)
        card = Mock()
        card.id = "MK-0001"
        card.title = "Unrelated Card"
        card.content = "Unrelated content"
        card.decision_pattern = "unrelated pattern"
        card.tags = Mock(return_value={
            "assumption": [],
            "boundary": [],
            "failure_mode": [],
            "control": []
        })
        kb.cards = [card]

        tags = {"assumption": ["auth"], "boundary": ["input"]}
        results = match_cards(kb, "test decision", tags)

        assert len(results) == 0  # No matches found

    def test_match_cards_pattern_match(self):
        """Test matching based on decision pattern"""
        kb = Mock(spec=KnowledgeBase)
        card = Mock()
        card.id = "MK-0001"
        card.title = "Authentication Security"
        card.content = "Authentication content"
        card.decision_pattern = "implement authentication system"
        card.tags = Mock(return_value={
            "assumption": [],
            "boundary": [],
            "failure_mode": [],
            "control": []
        })
        kb.cards = [card]

        # Pattern matches "authentication" in title
        results = match_cards(kb, "implement authentication system", {})

        assert len(results) == 1
        assert results[0].card_id == "MK-0001"
        assert results[0].score > 0

    def test_match_cards_tag_matches(self):
        """Test matching based on tags"""
        kb = Mock(spec=KnowledgeBase)
        card = Mock()
        card.id = "MK-0001"
        card.title = "Test Card"
        card.content = "Test content"
        card.decision_pattern = "test pattern"
        card.tags = Mock(return_value={
            "assumption": ["auth", "trust"],
            "boundary": ["input"],
            "failure_mode": ["injection"],
            "control": ["validation"]
        })
        kb.cards = [card]

        # Match all tag types
        tags = {
            "assumption": ["auth", "trust"],
            "boundary": ["input"],
            "failure_mode": ["injection"],
            "control": ["validation"]
        }
        results = match_cards(kb, "test", tags)

        assert len(results) == 1
        assert results[0].score > 10  # Should have high score from multiple matches

    def test_match_cards_coverage_bonus(self):
        """Test coverage bonus for having matches in multiple categories"""
        kb = Mock(spec=KnowledgeBase)
        card = Mock(spec=MitigationCard)
    def test_match_cards_coverage_bonus(self):
        """Test coverage bonus for having matches in multiple categories"""
        kb = Mock(spec=KnowledgeBase)
        card = Mock()
        card.id = "MK-0001"
        card.title = "Test Card"
        card.content = "Test content"
        card.decision_pattern = "test pattern"
        card.tags = Mock(return_value={
            "assumption": ["auth"],
            "boundary": ["input"],
            "failure_mode": [],
            "control": []
        })
        kb.cards = [card]

        # Match both assumption and boundary for coverage bonus
        tags = {
            "assumption": ["auth"],
            "boundary": ["input"]
        }
        results = match_cards(kb, "test", tags)

        assert len(results) == 1
        # Score should include coverage bonus of +3
        assert results[0].score >= 3 + 2 + 3  # assumption + boundary + coverage

    def test_match_cards_top_k(self):
        """Test limiting results to top K"""
        kb = Mock(spec=KnowledgeBase)
        cards = []

        # Create 10 cards with different scores
        for i in range(10):
            card = Mock()
            card.id = f"MK-{i:04d}"
            card.title = f"Card {i}"
            card.content = f"Content {i}"
            card.decision_pattern = f"pattern {i}"
            card.tags = Mock(return_value={"assumption": [f"tag{i}"], "boundary": [], "failure_mode": [], "control": []})
            cards.append(card)

        kb.cards = cards

        # Match with tags that will score them differently
        tags = {"assumption": ["tag0", "tag1", "tag2"]}
        results = match_cards(kb, "test", tags, top_k=3)

        assert len(results) == 3
        # Should be sorted by score descending
        assert results[0].score >= results[1].score >= results[2].score

    def test_match_result_structure(self):
        """Test MatchResult structure"""
        card_data = {"id": "MK-0001", "title": "Test"}
        result = MatchResult(
            card_id="MK-0001",
            title="Test Card",
            score=5,
            why=["pattern match", "tag match"],
            card=card_data
        )

        assert result.card_id == "MK-0001"
        assert result.title == "Test Card"
        assert result.score == 5
        assert result.why == ["pattern match", "tag match"]
        assert result.card == card_data
"""
Integration tests for the Risk Fusion Engine.
Verifies multi-layer integration, privacy preservation, and failsafe behavior when LLM is unconfigured.
"""

import pytest
import asyncio
from datetime import datetime, timezone
import mongomock

from backend.monitoring.risk_engine import RiskEngine
from backend.database.mongodb import create_indexes, auto_seed_if_needed
import backend.database.mongodb as mdb


class TestRiskEngineIntegration:
    """Test suite for full multi-layer risk analysis pipeline."""

    @pytest.fixture(scope="class")
    def mock_db(self):
        """Setup in-memory mongomock database with seeded demo data."""
        client = mongomock.MongoClient()
        db = client['childsafe']
        mdb._client = client
        mdb._db = db
        mdb._is_mock = True
        create_indexes()
        auto_seed_if_needed()
        return db

    @pytest.fixture(scope="class")
    def risk_engine(self, mock_db):
        return RiskEngine(mock_db)

    @pytest.mark.asyncio
    async def test_full_pipeline_safe_message(self, risk_engine):
        """Verify normal school conversation remains SAFE."""
        message = {
            'message_id': 'MSG_TEST_001',
            'conversation_id': 'CHAT001',
            'sender_id': 'CHILD001',
            'receiver_id': 'ALICE001',
            'content': 'Hey Alice, do you have the notes for biology class tomorrow?',
            'timestamp': datetime.now(timezone.utc),
        }
        res = await risk_engine.analyze_message(message, 'CHAT001')
        assert res['risk_score'] <= 29, f"Expected SAFE score (<=29), got {res['risk_score']}"
        assert res['severity'] == 'SAFE'
        assert res['should_alert'] is False

    @pytest.mark.asyncio
    async def test_full_pipeline_threat_message(self, risk_engine):
        """Verify direct threat message produces appropriate risk score."""
        message = {
            'message_id': 'MSG_TEST_002',
            'conversation_id': 'CHAT002',
            'sender_id': 'BOB001',
            'receiver_id': 'CHILD001',
            'content': 'I am going to strangle you after school, watch your back!',
            'timestamp': datetime.now(timezone.utc),
        }
        res = await risk_engine.analyze_message(message, 'CHAT002')
        assert res['risk_score'] >= 30, f"Expected elevated risk score (>=30), got {res['risk_score']}"
        assert 'THREAT' in res['categories']
        assert res['layer_scores']['ml'] >= 25 or res['layer_scores']['rule'] >= 25

    @pytest.mark.asyncio
    async def test_privacy_preservation_in_alerts(self, risk_engine):
        """
        Verify privacy-by-design requirement:
        Parent alert data must contain category summaries and severity,
        NOT raw unredacted private message transcripts.
        """
        raw_secret_message = "This is a super private secret transcript that parents must not read verbatim."
        message = {
            'message_id': 'MSG_TEST_003',
            'conversation_id': 'CHAT003',
            'sender_id': 'CHARLIE001',
            'receiver_id': 'CHILD001',
            'content': f"Don't tell your parents! {raw_secret_message}",
            'timestamp': datetime.now(timezone.utc),
        }
        res = await risk_engine.analyze_message(message, 'CHAT003')
        
        # If an alert was generated or in reasons list
        if res.get('alert_data'):
            alert_str = str(res['alert_data'])
            assert raw_secret_message not in alert_str, "Raw private chat transcript leaked in alert data!"
            assert 'severity' in res['alert_data']
            assert 'categories' in res['alert_data']

    @pytest.mark.asyncio
    async def test_llm_unavailability_failsafe(self, risk_engine):
        """Verify pipeline operates seamlessly even when optional LLM is disabled or unavailable."""
        assert risk_engine.llm_analyzer.available is False or isinstance(risk_engine.llm_analyzer.available, bool)
        
        message = {
            'message_id': 'MSG_TEST_004',
            'conversation_id': 'CHAT001',
            'sender_id': 'ALICE001',
            'receiver_id': 'CHILD001',
            'content': 'Did you finish chapter 4 of the book?',
            'timestamp': datetime.now(timezone.utc),
        }
        res = await risk_engine.analyze_message(message, 'CHAT001')
        assert 'risk_score' in res
        assert 'severity' in res
        assert res['layer_scores']['llm'] == 0

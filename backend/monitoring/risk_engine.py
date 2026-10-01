"""
Risk Fusion Engine — Main Orchestrator for Child Safety Monitoring.

Combines all 5 analysis layers (Rule, ML, Context, Behaviour, LLM)
into a unified risk assessment with intelligent alert decisions.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

from backend.monitoring.preprocessing import clean_text, get_conversation_text
from backend.monitoring.rules import RuleEngine
from backend.monitoring.ml_model import MLClassifier
from backend.monitoring.context import ContextAnalyzer
from backend.monitoring.behaviour import BehaviourAnalyzer
from backend.monitoring.llm_analyzer import LLMAnalyzer

try:
    from backend.config.settings import Settings
    settings = Settings()
except ImportError:
    # Fallback settings if config not available yet
    class Settings:
        RISK_WEIGHTS = {'rule': 0.20, 'ml': 0.25, 'context': 0.25, 'behaviour': 0.20, 'llm': 0.10}
        RISK_THRESHOLDS = {'safe': 29, 'moderate': 59, 'high': 79, 'critical': 100}
        ALERT_COOLDOWN_MINUTES = 30
        LLM_API_KEY = ''
        LLM_MODEL = 'gpt-4'
    settings = Settings()

try:
    from backend.utils.helpers import generate_uuid, get_severity, format_timestamp
except ImportError:
    import uuid as _uuid
    def generate_uuid() -> str:
        return str(_uuid.uuid4())
    def get_severity(score: int) -> str:
        if score <= 29: return 'SAFE'
        elif score <= 59: return 'MODERATE'
        elif score <= 79: return 'HIGH'
        else: return 'CRITICAL'
    def format_timestamp(dt) -> str:
        if isinstance(dt, datetime):
            return dt.isoformat()
        return str(dt)

logger = logging.getLogger(__name__)


class RiskEngine:
    """Main orchestrator that fuses all analysis layers."""

    def __init__(self, db):
        """
        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.rule_engine = RuleEngine()
        self.ml_classifier = MLClassifier()
        self.context_analyzer = ContextAnalyzer()
        self.behaviour_analyzer = BehaviourAnalyzer(db)
        self.llm_analyzer = LLMAnalyzer(
            api_key=getattr(settings, 'LLM_API_KEY', ''),
            model=getattr(settings, 'LLM_MODEL', 'gpt-4'),
        )

    async def analyze_message(self, message: dict,
                               conversation_id: str) -> dict:
        """
        Full multi-layer analysis pipeline.

        Args:
            message: {message_id, conversation_id, sender_id, receiver_id, content, timestamp}
            conversation_id: ID of the conversation

        Returns:
            dict with risk_score, severity, categories, reasons, should_alert,
            layer_scores, alert_data
        """
        content = message.get('content', '')
        if not content or not content.strip():
            return self._empty_result()

        # Step 1: Get conversation history from DB
        conversation_history = self._get_conversation_history(conversation_id)

        # Step 2: Get participant info
        participants = self._get_participants(conversation_id)
        child_id = participants.get('child_id')
        contact_id = participants.get('contact_id')
        contact_name = participants.get('contact_name', 'Unknown')

        # Step 3: Clean text
        cleaned_content = clean_text(content)

        # ===== LAYER 1: Rule Engine =====
        rule_result = self.rule_engine.analyze(content, conversation_history)
        rule_score = rule_result.get('score', 0)

        # ===== LAYER 2: ML Classification =====
        ml_result = self.ml_classifier.predict(cleaned_content)
        ml_score = ml_result.get('score', 0)

        # ===== LAYER 3: Context Analysis =====
        context_result = self.context_analyzer.analyze(
            message, conversation_history, participants
        )
        context_score = context_result.get('score', 0)

        # Preliminary score (without behaviour and LLM)
        preliminary_score = (
            rule_score * 0.30 + ml_score * 0.35 + context_score * 0.35
        )

        # ===== LAYER 4: Behaviour Analysis =====
        # Merge categories from rule engine and ML
        merged_categories = dict(rule_result.get('categories', {}))
        if ml_result.get('category', 'SAFE') != 'SAFE':
            ml_cat = ml_result['category']
            ml_conf = ml_result.get('confidence', 0.5)
            merged_categories[ml_cat] = max(
                merged_categories.get(ml_cat, 0), ml_conf
            )

        behaviour_result = self.behaviour_analyzer.analyze(
            conversation_id, preliminary_score, merged_categories
        )
        behaviour_score = behaviour_result.get('score', 0)

        # ===== LAYER 5: LLM Analysis (conditional) =====
        llm_score = 0
        llm_result = {'score': 0, 'available': False, 'categories': [], 'reason': ''}
        llm_used = False

        if preliminary_score >= 30 and self.llm_analyzer.available:
            context_text = get_conversation_text(conversation_history, window=15)
            context_text += f"\n[Latest]: {content}"
            llm_result = await self.llm_analyzer.analyze(
                context_text, preliminary_score
            )
            llm_score = llm_result.get('score', 0)
            llm_used = llm_result.get('available', False)

        # ===== RISK FUSION =====
        layer_scores = {
            'rule': rule_score,
            'ml': ml_score,
            'context': context_score,
            'behaviour': behaviour_score,
            'llm': llm_score,
        }

        final_score = self._fuse_scores(layer_scores, llm_used)
        severity = get_severity(int(final_score))

        # Collect all reasons
        reasons = []
        reasons.extend(rule_result.get('signals', []))
        if ml_result.get('category', 'SAFE') != 'SAFE':
            reasons.append(
                f"ML classified as {ml_result['category']} "
                f"(confidence: {ml_result.get('confidence', 0):.0%})"
            )
        reasons.extend(context_result.get('signals', []))
        reasons.extend(behaviour_result.get('signals', []))
        if llm_used and llm_result.get('reason'):
            reasons.append(f"LLM: {llm_result['reason']}")

        # Merge all categories
        all_categories = dict(merged_categories)
        if context_result.get('context_type') == 'suspicious':
            all_categories['SUSPICIOUS_CONTEXT'] = 0.5
        for cat in llm_result.get('categories', []):
            all_categories[cat] = max(all_categories.get(cat, 0), 0.5)

        # Save risk score to DB
        risk_record = {
            'risk_id': generate_uuid(),
            'conversation_id': conversation_id,
            'message_id': message.get('message_id'),
            'risk_score': int(final_score),
            'severity': severity,
            'categories': all_categories,
            'rule_score': rule_score,
            'ml_score': ml_score,
            'context_score': context_score,
            'behaviour_score': behaviour_score,
            'llm_score': llm_score,
            'timestamp': datetime.now(timezone.utc),
            'reasons': reasons[:10],  # Top 10 reasons
        }
        self._save_risk_score(risk_record)

        # ===== ALERT DECISION =====
        should_alert, alert_data = self._make_alert_decision(
            final_score=int(final_score),
            severity=severity,
            layer_scores=layer_scores,
            behaviour_result=behaviour_result,
            conversation_id=conversation_id,
            child_id=child_id,
            contact_id=contact_id,
            contact_name=contact_name,
            categories=all_categories,
            reasons=reasons,
        )

        return {
            'risk_score': int(final_score),
            'severity': severity,
            'categories': all_categories,
            'reasons': reasons[:10],
            'should_alert': should_alert,
            'layer_scores': layer_scores,
            'alert_data': alert_data,
        }

    def _fuse_scores(self, layer_scores: dict, llm_used: bool) -> float:
        """Fuse layer scores using configured weights."""
        weights = dict(getattr(settings, 'RISK_WEIGHTS', {
            'rule': 0.20, 'ml': 0.25, 'context': 0.25,
            'behaviour': 0.20, 'llm': 0.10,
        }))

        if not llm_used:
            # Redistribute LLM weight proportionally
            llm_weight = weights.pop('llm', 0.10)
            remaining_total = sum(weights.values())
            if remaining_total > 0:
                for key in weights:
                    weights[key] += llm_weight * (weights[key] / remaining_total)
        
        final_score = sum(
            layer_scores.get(layer, 0) * weight
            for layer, weight in weights.items()
        )

        return max(0, min(100, final_score))

    def _make_alert_decision(
        self,
        final_score: int,
        severity: str,
        layer_scores: dict,
        behaviour_result: dict,
        conversation_id: str,
        child_id: str,
        contact_id: str,
        contact_name: str,
        categories: dict,
        reasons: list,
    ) -> Tuple[bool, Optional[dict]]:
        """Decide whether to generate an alert."""
        should_alert = False

        # CRITICAL: always alert
        if final_score >= 80:
            should_alert = True
            logger.info("CRITICAL alert triggered for conversation %s (score=%d)",
                       conversation_id, final_score)

        # HIGH: alert if multi-layer confirmation
        elif final_score >= 60:
            layers_above_40 = sum(
                1 for layer, score in layer_scores.items()
                if score > 40 and layer != 'llm'
            )
            if layers_above_40 >= 2:
                should_alert = True
                logger.info(
                    "HIGH alert triggered for conversation %s (score=%d, %d layers above 40)",
                    conversation_id, final_score, layers_above_40
                )

        # Behaviour trend increasing with moderate+ score
        if not should_alert and behaviour_result.get('trend') == 'increasing' and final_score > 50:
            should_alert = True
            logger.info(
                "Alert triggered due to increasing behaviour trend (conversation=%s, score=%d)",
                conversation_id, final_score
            )

        if not should_alert:
            return False, None

        # Check cooldown
        if self._is_cooldown_active(conversation_id):
            # But DO alert if risk jumped significantly or new CRITICAL category
            recent_alert = self._get_last_alert(conversation_id)
            if recent_alert:
                previous_score = recent_alert.get('risk_score', 0)
                score_jump = final_score - previous_score

                # New critical category check
                prev_cats = set(recent_alert.get('categories', {}).keys())
                curr_critical_cats = {c for c, s in categories.items() if s > 0.7}
                new_critical = curr_critical_cats - prev_cats

                if score_jump >= 25:
                    logger.info(
                        "Overriding cooldown: score jumped by %d points",
                        score_jump
                    )
                elif new_critical:
                    logger.info(
                        "Overriding cooldown: new critical categories: %s",
                        new_critical
                    )
                else:
                    logger.debug(
                        "Alert suppressed by cooldown for conversation %s",
                        conversation_id
                    )
                    return False, None

        # Prepare alert data
        # Get top categories (score > 0.3)
        top_categories = [
            cat for cat, score in sorted(
                categories.items(), key=lambda x: x[1], reverse=True
            )
            if score > 0.3
        ][:5]

        top_reasons = reasons[:5]

        alert_data = {
            'alert_id': generate_uuid(),
            'child_id': child_id,
            'conversation_id': conversation_id,
            'contact_id': contact_id,
            'contact_name': contact_name,
            'severity': severity,
            'risk_score': final_score,
            'categories': top_categories,
            'reasons': top_reasons,
            'created_at': datetime.now(timezone.utc),
            'status': 'NEW',
        }

        # Save alert to DB
        self._save_alert(alert_data)

        return True, alert_data

    def _is_cooldown_active(self, conversation_id: str) -> bool:
        """Check if an alert was recently sent for this conversation."""
        try:
            if self.db is None:
                return False
            cooldown_minutes = getattr(
                settings, 'ALERT_COOLDOWN_MINUTES', 30
            )
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=cooldown_minutes)
            recent = self.db.alerts.find_one({
                'conversation_id': conversation_id,
                'created_at': {'$gte': cutoff},
            })
            return recent is not None
        except Exception as e:
            logger.error("Cooldown check failed: %s", str(e))
            return False

    def _get_last_alert(self, conversation_id: str) -> Optional[dict]:
        """Get the most recent alert for a conversation."""
        try:
            if self.db is None:
                return None
            return self.db.alerts.find_one(
                {'conversation_id': conversation_id},
                sort=[('created_at', -1)],
            )
        except Exception:
            return None

    def _get_conversation_history(self, conversation_id: str) -> list:
        """Fetch last 20 messages for the conversation from DB."""
        try:
            if self.db is None:
                return []
            messages = list(
                self.db.messages.find(
                    {'conversation_id': conversation_id},
                    {'_id': 0, 'sender_id': 1, 'receiver_id': 1,
                     'content': 1, 'timestamp': 1},
                )
                .sort('timestamp', -1)
                .limit(20)
            )
            messages.reverse()  # Chronological order
            return messages
        except Exception as e:
            logger.error(
                "Failed to fetch conversation history: %s", str(e)
            )
            return []

    def _get_participants(self, conversation_id: str) -> dict:
        """Get participant info and identify child vs contact."""
        result = {'child_id': None, 'contact_id': None, 'contact_name': 'Unknown'}
        try:
            if self.db is None:
                return result

            conversation = self.db.conversations.find_one(
                {'conversation_id': conversation_id}
            )
            if not conversation:
                return result

            participant_ids = conversation.get('participants', [])

            for pid in participant_ids:
                user = self.db.users.find_one({'_id': pid})
                if not user:
                    continue
                role = user.get('role', '')
                if role == 'CHILD':
                    result['child_id'] = pid
                elif role == 'CONTACT':
                    result['contact_id'] = pid
                    result['contact_name'] = user.get('name', 'Unknown')

            # If roles aren't set, use first two participants
            if not result['child_id'] and len(participant_ids) >= 1:
                result['child_id'] = participant_ids[0]
            if not result['contact_id'] and len(participant_ids) >= 2:
                result['contact_id'] = participant_ids[1]

        except Exception as e:
            logger.error("Failed to get participants: %s", str(e))

        return result

    def _save_risk_score(self, risk_record: dict):
        """Save risk score record to database."""
        try:
            if self.db is not None:
                self.db.risk_scores.insert_one(risk_record)
        except Exception as e:
            logger.error("Failed to save risk score: %s", str(e))

    def _save_alert(self, alert_data: dict):
        """Save alert to database."""
        try:
            if self.db is not None:
                self.db.alerts.insert_one(alert_data)
                logger.info(
                    "Alert saved: %s (severity=%s, score=%d)",
                    alert_data['alert_id'],
                    alert_data['severity'],
                    alert_data['risk_score'],
                )
        except Exception as e:
            logger.error("Failed to save alert: %s", str(e))

    def _empty_result(self) -> dict:
        """Return empty/safe result for empty messages."""
        return {
            'risk_score': 0,
            'severity': 'SAFE',
            'categories': {},
            'reasons': [],
            'should_alert': False,
            'layer_scores': {
                'rule': 0, 'ml': 0, 'context': 0,
                'behaviour': 0, 'llm': 0,
            },
            'alert_data': None,
        }

"""
Layer 4: Behavioural Analysis for Child Safety Monitoring.

Tracks and analyzes behavioural trends over time for each
conversation, detecting patterns and escalation.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class BehaviourAnalyzer:
    """Tracks and analyzes behavioural trends over time."""

    MAX_HISTORY_LENGTH = 100

    def __init__(self, db):
        """
        Args:
            db: MongoDB database instance
        """
        self.db = db

    def analyze(self, conversation_id: str, current_risk: float,
                categories: dict) -> dict:
        """
        Track and analyze behavioural trends.

        Args:
            conversation_id: ID of the conversation
            current_risk: Current risk score from other layers (0-100)
            categories: Current detected categories {cat: score}

        Returns:
            dict with score, trend, average_risk, risk_history,
            category_frequency, signals
        """
        # Load or create behaviour profile
        profile = self._load_profile(conversation_id)
        is_new = profile is None

        if is_new:
            profile = {
                'conversation_id': conversation_id,
                'child_id': None,
                'contact_id': None,
                'risk_history': [],
                'average_risk': 0.0,
                'trend': 'new',
                'category_frequency': {},
                'last_updated': datetime.now(timezone.utc),
            }

        # Update risk history
        risk_history = profile.get('risk_history', [])
        risk_history.append({
            'score': current_risk,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        })
        # Keep only last MAX_HISTORY_LENGTH entries
        if len(risk_history) > self.MAX_HISTORY_LENGTH:
            risk_history = risk_history[-self.MAX_HISTORY_LENGTH:]
        profile['risk_history'] = risk_history

        # Update category frequency
        cat_freq = profile.get('category_frequency', {})
        for cat, score in categories.items():
            if score > 0.2:  # Only count meaningful detections
                cat_freq[cat] = cat_freq.get(cat, 0) + 1
        profile['category_frequency'] = cat_freq

        # Calculate trend
        trend = self._calculate_trend(risk_history)
        profile['trend'] = trend

        # Calculate average risk
        scores = [entry['score'] for entry in risk_history]
        average_risk = sum(scores) / len(scores) if scores else 0.0
        profile['average_risk'] = average_risk

        # Calculate behaviour score
        signals = []
        score = self._calculate_behaviour_score(
            risk_history, trend, cat_freq, current_risk, average_risk, signals
        )

        # Update profile timestamp
        profile['last_updated'] = datetime.now(timezone.utc)

        # Save profile to DB
        self._save_profile(conversation_id, profile)

        return {
            'score': min(100, max(0, int(score))),
            'trend': trend,
            'average_risk': round(average_risk, 2),
            'risk_history': risk_history[-20:],  # Return last 20 for API response
            'category_frequency': cat_freq,
            'signals': signals,
        }

    def _load_profile(self, conversation_id: str) -> Optional[dict]:
        """Load behaviour profile from database."""
        try:
            if self.db is None:
                return None
            profile = self.db.behaviour_profiles.find_one(
                {'conversation_id': conversation_id}
            )
            return profile
        except Exception as e:
            logger.error("Failed to load behaviour profile: %s", str(e))
            return None

    def _save_profile(self, conversation_id: str, profile: dict):
        """Save behaviour profile to database."""
        try:
            if self.db is None:
                return
            self.db.behaviour_profiles.update_one(
                {'conversation_id': conversation_id},
                {'$set': profile},
                upsert=True
            )
            from backend.database.mongodb import save_mock_db
            save_mock_db()
        except Exception as e:
            logger.error("Failed to save behaviour profile: %s", str(e))

    def _calculate_trend(self, risk_history: list) -> str:
        """Calculate risk trend from history."""
        if len(risk_history) < 5:
            return 'new'

        scores = [entry['score'] for entry in risk_history]

        # Compare average of last 5 vs previous 5
        recent_5 = scores[-5:]
        previous_5 = scores[-10:-5] if len(scores) >= 10 else scores[:max(1, len(scores)-5)]

        recent_avg = sum(recent_5) / len(recent_5)
        previous_avg = sum(previous_5) / len(previous_5) if previous_5 else 0

        if previous_avg == 0:
            if recent_avg > 20:
                return 'increasing'
            return 'stable'

        change_pct = ((recent_avg - previous_avg) / max(previous_avg, 1)) * 100

        if change_pct > 20:
            return 'increasing'
        elif change_pct < -20:
            return 'decreasing'
        else:
            return 'stable'

    def _calculate_behaviour_score(self, risk_history: list, trend: str,
                                    cat_freq: dict, current_risk: float,
                                    average_risk: float, signals: list) -> float:
        """Calculate the overall behaviour score."""
        num_entries = len(risk_history)

        # New conversation (< 5 messages)
        if num_entries < 5:
            signals.append('New conversation - limited behavioural data')
            return current_risk * 0.5

        # Base score from average risk
        scores = [entry['score'] for entry in risk_history]
        recent_avg = sum(scores[-5:]) / min(5, len(scores))

        # Stable low risk
        if trend == 'stable' and average_risk < 20:
            signals.append('Stable low risk pattern')
            return min(15, average_risk * 0.5)

        # Stable moderate risk
        if trend == 'stable' and average_risk < 40:
            signals.append('Stable moderate risk - monitoring')
            return average_risk * 0.6

        # Decreasing trend
        if trend == 'decreasing':
            signals.append('Risk trend is decreasing')
            return max(5, recent_avg * 0.4)

        # Calculate base from recent average
        base = recent_avg * 0.7

        # Increasing trend bonus
        if trend == 'increasing':
            trend_bonus = 20
            signals.append('Risk trend is INCREASING - elevated concern')
            base += trend_bonus

        # Category frequency analysis
        repeated_cats = {cat: count for cat, count in cat_freq.items() if count >= 3}
        if repeated_cats:
            signals.append(f'Repeated risk categories detected: {", ".join(repeated_cats.keys())}')
            # Multiplier for persistent categories
            cat_multiplier = 1.0 + (len(repeated_cats) * 0.15)
            base *= cat_multiplier

        # Sustained high risk
        high_risk_count = sum(1 for s in scores[-10:] if s > 50)
        if high_risk_count >= 5:
            signals.append('Sustained high risk across multiple messages')
            base = max(base, 70)
        elif high_risk_count >= 3:
            signals.append('Recurring high risk episodes')
            base = max(base, 50)

        # Stable at high level
        if trend == 'stable' and average_risk >= 50:
            signals.append('Risk stable at HIGH level - persistent concern')
            base = max(base, 55)

        return min(100, max(0, base))

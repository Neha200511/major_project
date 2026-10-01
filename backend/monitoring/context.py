"""
Layer 3: Context Analysis for Child Safety Monitoring.

Analyzes the FULL conversation context including topic detection,
progression analysis, power dynamics, and both-sides analysis.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class ContextAnalyzer:
    """Analyzes full conversation context for risk assessment."""

    ENTERTAINMENT_KEYWORDS = {
        'movie', 'film', 'show', 'series', 'episode', 'netflix', 'youtube',
        'game', 'gaming', 'minecraft', 'fortnite', 'roblox', 'valorant',
        'song', 'music', 'album', 'band', 'concert', 'tiktok', 'video',
        'book', 'novel', 'story', 'character', 'anime', 'manga', 'comic',
    }
    ACADEMIC_KEYWORDS = {
        'homework', 'exam', 'test', 'assignment', 'project', 'teacher',
        'school', 'class', 'study', 'grade', 'math', 'science', 'english',
        'history', 'biology', 'physics', 'chemistry', 'lecture', 'essay',
    }
    SPORTS_KEYWORDS = {
        'sport', 'football', 'soccer', 'basketball', 'baseball', 'cricket',
        'tennis', 'swimming', 'running', 'match', 'team', 'score', 'goal',
        'win', 'lost', 'tournament', 'competition', 'practice', 'coach',
    }
    PERSONAL_KEYWORDS = {
        'feel', 'feeling', 'sad', 'happy', 'angry', 'scared', 'worried',
        'love', 'hate', 'miss', 'lonely', 'depressed', 'anxious', 'afraid',
        'parents', 'family', 'relationship', 'breakup', 'crush', 'secret',
    }
    SUSPICIOUS_KEYWORDS = {
        'secret', 'private', 'alone', 'hidden', 'delete', 'nobody knows',
        'just between us', 'meet up', 'in person', 'come over', 'address',
        'photo', 'pic', 'selfie', 'camera', 'video call',
    }

    SECRECY_PATTERNS = [
        re.compile(r"don[\u2019't]*\s*tell", re.I),
        re.compile(r"(our|keep.*?)\s*secret", re.I),
        re.compile(r"(just\s+)?between\s+(you and me|us)", re.I),
        re.compile(r"delete\s+(this|the|these|our)\s*(message|chat|conversation|text)", re.I),
        re.compile(r"don[\u2019't]*\s*let\s+anyone", re.I),
    ]

    REQUEST_PATTERNS = [
        re.compile(r"send\s+(me\s+)?(a\s+)?(pic|photo|picture|selfie|video)", re.I),
        re.compile(r"(what|where|tell me)\s+.*(address|school|phone|number)", re.I),
        re.compile(r"(meet|see)\s+(me\s+)?(in\s+)?person", re.I),
        re.compile(r"turn\s+on\s+(your\s+)?cam", re.I),
    ]

    DISCOMFORT_PATTERNS = [
        re.compile(r"(i\s+)?(don[\u2019't]*|do not)\s+(want|like|feel comfortable)", re.I),
        re.compile(r"(stop|please stop|leave me alone|go away)", re.I),
        re.compile(r"(that[\u2019']?s|this is)\s+(weird|creepy|uncomfortable|scary|strange)", re.I),
        re.compile(r"i[\u2019']?m\s+(not sure|uncomfortable|scared|afraid|worried)", re.I),
    ]

    PROBING_PATTERNS = [
        re.compile(r"(how old|what.*age|where.*live|what school|do you have a)", re.I),
        re.compile(r"(are you|you are)\s+(home\s+)?alone", re.I),
        re.compile(r"(when|what time).*parents\s+(come|get|are)\s+(home|back)", re.I),
    ]

    def analyze(self, current_message: dict, conversation_history: list,
                participants: dict) -> dict:
        """
        Analyze the full conversation context.

        Args:
            current_message: {sender_id, receiver_id, content, timestamp}
            conversation_history: last 20 messages [{sender_id, content, timestamp}, ...]
            participants: {child_id: '...', contact_id: '...'}

        Returns:
            dict with score, signals, progression, context_type
        """
        if not current_message or not current_message.get('content'):
            return {
                'score': 0,
                'signals': [],
                'progression': 'normal',
                'context_type': 'casual',
            }

        signals = []

        # 1. Topic Detection
        context_type = self._detect_topic(current_message, conversation_history)

        # 2. Progression Analysis
        progression, prog_signals = self._analyze_progression(conversation_history)
        signals.extend(prog_signals)

        # 3. Power Dynamics
        power_signals = self._analyze_power_dynamics(
            conversation_history, participants
        )
        signals.extend(power_signals)

        # 4. Both Sides Analysis
        sides_signals = self._analyze_both_sides(
            current_message, conversation_history, participants
        )
        signals.extend(sides_signals)

        # 5. Conversation Velocity
        velocity_signals = self._analyze_velocity(conversation_history)
        signals.extend(velocity_signals)

        # 6. Secrecy Accumulation
        secrecy_signals = self._count_secrecy(conversation_history)
        signals.extend(secrecy_signals)

        # Calculate score
        score = self._calculate_score(context_type, progression, signals)

        return {
            'score': min(100, max(0, int(score))),
            'signals': signals,
            'progression': progression,
            'context_type': context_type,
        }

    def _detect_topic(self, current_message: dict, history: list) -> str:
        """Detect the primary topic of the conversation."""
        all_texts = [m.get('content', '') for m in (history or [])[-10:]]
        all_texts.append(current_message.get('content', ''))
        combined = ' '.join(all_texts).lower()
        words = set(combined.split())

        scores = {
            'entertainment': len(words & self.ENTERTAINMENT_KEYWORDS),
            'academic': len(words & self.ACADEMIC_KEYWORDS),
            'sports': len(words & self.SPORTS_KEYWORDS),
            'personal': len(words & self.PERSONAL_KEYWORDS),
            'suspicious': len(words & self.SUSPICIOUS_KEYWORDS),
        }

        max_topic = max(scores, key=scores.get)
        max_score = scores[max_topic]

        if max_score == 0:
            return 'casual'

        topic_map = {
            'entertainment': 'entertainment',
            'academic': 'academic',
            'sports': 'entertainment',
            'personal': 'personal',
            'suspicious': 'suspicious',
        }
        return topic_map.get(max_topic, 'casual')

    def _analyze_progression(self, history: list) -> tuple:
        """Analyze how the conversation has progressed over time."""
        if not history or len(history) < 3:
            return 'normal', []

        signals = []
        messages = history[-20:]
        total = len(messages)
        if total < 3:
            return 'normal', []

        # Split conversation into thirds
        third = max(1, total // 3)
        early = messages[:third]
        middle = messages[third:2*third]
        late = messages[2*third:]

        def count_risk_indicators(msgs):
            count = 0
            for m in msgs:
                text = m.get('content', '').lower()
                for pattern in self.REQUEST_PATTERNS + self.SECRECY_PATTERNS + self.PROBING_PATTERNS:
                    if pattern.search(text):
                        count += 1
            return count

        early_risk = count_risk_indicators(early)
        middle_risk = count_risk_indicators(middle)
        late_risk = count_risk_indicators(late)

        # Detect escalation
        if late_risk > middle_risk > early_risk and late_risk >= 2:
            signals.append('Escalating pattern: risk indicators increasing over conversation')
            return 'escalating', signals
        elif late_risk >= 3 and late_risk > early_risk:
            signals.append('Dangerous progression: high concentration of risk indicators in recent messages')
            return 'dangerous', signals
        elif late_risk >= 2 or middle_risk >= 2:
            signals.append('Concerning pattern: multiple risk indicators detected in conversation')
            return 'concerning', signals

        # Check for sudden topic shift
        early_topics = ' '.join(m.get('content', '') for m in early).lower()
        late_topics = ' '.join(m.get('content', '') for m in late).lower()

        early_is_casual = any(w in early_topics for w in self.ENTERTAINMENT_KEYWORDS | self.ACADEMIC_KEYWORDS)
        late_has_risk = any(w in late_topics for w in self.SUSPICIOUS_KEYWORDS)

        if early_is_casual and late_has_risk:
            signals.append('Topic shift: conversation moved from casual to suspicious topics')
            return 'concerning', signals

        return 'normal', signals

    def _analyze_power_dynamics(self, history: list, participants: dict) -> list:
        """Analyze power dynamics between conversation participants."""
        signals = []
        if not history or len(history) < 4:
            return signals

        child_id = participants.get('child_id')
        contact_id = participants.get('contact_id')
        if not child_id or not contact_id:
            return signals

        contact_questions = 0
        contact_requests = 0
        contact_flattery = 0
        child_answers = 0

        for msg in history[-15:]:
            sender = msg.get('sender_id', '')
            text = msg.get('content', '').lower()

            if sender == contact_id:
                if '?' in text:
                    contact_questions += 1
                for p in self.REQUEST_PATTERNS:
                    if p.search(text):
                        contact_requests += 1
                if any(w in text for w in ['special', 'mature', 'beautiful', 'pretty', 'handsome', 'smart', 'unique']):
                    contact_flattery += 1
            elif sender == child_id:
                # Short responses to questions suggest answering
                if len(text.split()) < 15 and contact_questions > 0:
                    child_answers += 1

        # Probing: contact asks many questions
        if contact_questions >= 4:
            signals.append('Power dynamic: contact is consistently probing with questions')

        # Controlling: contact making repeated requests/demands
        if contact_requests >= 2:
            signals.append('Power dynamic: contact making repeated requests or demands')

        # Grooming flattery pattern
        if contact_flattery >= 2 and contact_questions >= 2:
            signals.append('Power dynamic: contact combining flattery with personal questions (grooming pattern)')

        return signals

    def _analyze_both_sides(self, current_message: dict, history: list,
                            participants: dict) -> list:
        """Analyze messages from both child and contact sides."""
        signals = []
        child_id = participants.get('child_id')
        contact_id = participants.get('contact_id')
        if not child_id or not contact_id:
            return signals

        contact_msgs = []
        child_msgs = []

        all_msgs = list(history or []) + [current_message]
        for msg in all_msgs:
            sender = msg.get('sender_id', '')
            if sender == contact_id:
                contact_msgs.append(msg.get('content', ''))
            elif sender == child_id:
                child_msgs.append(msg.get('content', ''))

        # Check if dangerous signals come from the contact
        contact_text = ' '.join(contact_msgs).lower()
        contact_risk = 0
        for pattern in self.REQUEST_PATTERNS + self.SECRECY_PATTERNS + self.PROBING_PATTERNS:
            if pattern.search(contact_text):
                contact_risk += 1

        if contact_risk >= 2:
            signals.append('Risk signals originating from contact side (higher concern)')

        # Check if child is expressing discomfort
        child_text = ' '.join(child_msgs).lower()
        child_discomfort = 0
        for pattern in self.DISCOMFORT_PATTERNS:
            if pattern.search(child_text):
                child_discomfort += 1

        if child_discomfort >= 1 and contact_risk >= 1:
            signals.append('Child expressing discomfort while contact shows risk signals (amplified risk)')

        # Check if child is going along with suspicious requests
        if contact_risk >= 2 and child_discomfort == 0 and len(child_msgs) >= 3:
            child_compliant = any(w in child_text for w in ['ok', 'okay', 'sure', 'fine', 'alright', 'yes'])
            if child_compliant:
                signals.append('Child appears to be complying with suspicious requests (concerning)')

        return signals

    def _analyze_velocity(self, history: list) -> list:
        """Analyze conversation velocity (rapid exchanges on sensitive topics)."""
        signals = []
        if not history or len(history) < 5:
            return signals

        recent = history[-10:]
        timestamps = []
        for msg in recent:
            ts = msg.get('timestamp')
            if ts:
                if isinstance(ts, str):
                    try:
                        ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    except (ValueError, TypeError):
                        continue
                if isinstance(ts, datetime):
                    timestamps.append(ts)

        if len(timestamps) < 3:
            return signals

        # Calculate average time between messages
        intervals = []
        for i in range(1, len(timestamps)):
            delta = (timestamps[i] - timestamps[i-1]).total_seconds()
            if delta >= 0:
                intervals.append(delta)

        if not intervals:
            return signals

        avg_interval = sum(intervals) / len(intervals)

        # Check if rapid AND has risky content
        combined = ' '.join(m.get('content', '') for m in recent).lower()
        has_risk_content = any(w in combined for w in self.SUSPICIOUS_KEYWORDS)

        if avg_interval < 30 and has_risk_content:  # Less than 30 seconds average
            signals.append('Rapid message exchange on sensitive topics')
        elif avg_interval < 15 and len(recent) >= 8:
            signals.append('Very rapid message exchange detected')

        return signals

    def _count_secrecy(self, history: list) -> list:
        """Count secrecy-related messages across the conversation."""
        signals = []
        if not history:
            return signals

        secrecy_count = 0
        for msg in history:
            text = msg.get('content', '')
            for pattern in self.SECRECY_PATTERNS:
                if pattern.search(text):
                    secrecy_count += 1
                    break

        if secrecy_count >= 3:
            signals.append(f'High secrecy accumulation: {secrecy_count} secrecy-related messages in conversation')
        elif secrecy_count >= 2:
            signals.append(f'Moderate secrecy: {secrecy_count} secrecy-related messages detected')

        return signals

    def _calculate_score(self, context_type: str, progression: str,
                         signals: list) -> float:
        """Calculate the final context score."""
        # Base from progression
        progression_scores = {
            'normal': 5,
            'concerning': 35,
            'escalating': 60,
            'dangerous': 85,
        }
        base = progression_scores.get(progression, 5)

        # Add signal contributions
        signal_bonus = len(signals) * 8

        score = base + signal_bonus

        # Context type caps
        if context_type == 'entertainment':
            score = min(score, 15)
        elif context_type == 'academic':
            score = min(score, 20)
        elif context_type == 'casual' and progression == 'normal':
            score = min(score, 15)
        elif context_type == 'suspicious':
            score = max(score, 25)  # Minimum for suspicious context

        # Signal count ranges
        if not signals:
            score = min(score, 15)
        elif len(signals) == 1:
            score = max(score, 15)
            score = min(score, 35)
        elif len(signals) >= 2 and len(signals) <= 3:
            score = max(score, 30)
        elif len(signals) >= 4:
            score = max(score, 55)

        return min(100, max(0, score))

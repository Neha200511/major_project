"""
Layer 5: Optional LLM-based Analysis for Child Safety Monitoring.

Only invoked when other layers indicate moderate+ risk AND an API key is configured.
Uses an OpenAI-compatible API for deeper semantic analysis.
"""

import json
import logging
from typing import Dict, Optional

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

logger = logging.getLogger(__name__)


class LLMAnalyzer:
    """Optional LLM-based deep analysis for ambiguous cases."""

    SYSTEM_PROMPT = """You are a child safety analysis expert. Analyze the following conversation 
for potential risks to a child participant. Consider the FULL context, not just individual words.

IMPORTANT:
- Movie/game/sports discussions with violence words are SAFE
- Joking between friends (with emojis like 😂) is usually SAFE
- Look for PATTERNS of grooming, manipulation, threats, not isolated words
- Consider power dynamics between participants
- Secrecy + personal requests + escalation = HIGH RISK

Respond with a JSON object ONLY (no markdown, no extra text):
{
    "risk_level": "SAFE" | "MODERATE" | "HIGH" | "CRITICAL",
    "score": 0-100,
    "categories": ["GROOMING", "CYBERBULLYING", "THREAT", ...],
    "confidence": 0.0-1.0,
    "reason": "Brief explanation of assessment"
}"""

    def __init__(self, api_key: str = None, model: str = 'gpt-4'):
        self.api_key = api_key
        self.model = model
        self.available = (
            bool(api_key) 
            and not api_key.lower().startswith(('optional', 'your-', 'test', 'demo', 'none', 'change'))
            and HTTPX_AVAILABLE
        )

    async def analyze(self, conversation_context: str,
                      current_risk: float) -> dict:
        """
        Perform LLM analysis on conversation context.

        Only called when:
        1. API key is configured
        2. Current risk from other layers >= 30

        Args:
            conversation_context: Formatted conversation text
            current_risk: Preliminary risk score from other layers

        Returns:
            dict with score, risk_level, categories, confidence, reason, available
        """
        unavailable_response = {
            'score': 0,
            'risk_level': 'SAFE',
            'categories': [],
            'confidence': 0.0,
            'reason': 'LLM analysis not available',
            'available': False,
        }

        # Check if LLM should be used
        if not self.available:
            logger.debug("LLM analyzer not available (no API key or httpx)")
            return unavailable_response

        if current_risk < 30:
            return {
                'score': 0,
                'risk_level': 'SAFE',
                'categories': [],
                'confidence': 0.0,
                'reason': 'Risk too low for LLM analysis',
                'available': True,
            }

        try:
            result = await self._call_api(conversation_context)
            return result
        except Exception as e:
            logger.error("LLM analysis failed: %s", str(e))
            return unavailable_response

    async def _call_api(self, conversation_context: str) -> dict:
        """Call OpenAI-compatible API for analysis."""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

        payload = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': self.SYSTEM_PROMPT},
                {
                    'role': 'user',
                    'content': f"Analyze this conversation for child safety risks:\n\n{conversation_context}"
                },
            ],
            'temperature': 0.1,
            'max_tokens': 500,
            'response_format': {'type': 'json_object'},
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

        data = response.json()
        content = data['choices'][0]['message']['content']

        return self._parse_response(content)

    def _parse_response(self, content: str) -> dict:
        """Parse and validate LLM JSON response."""
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            logger.warning("LLM returned invalid JSON: %s", content[:200])
            return {
                'score': 0,
                'risk_level': 'SAFE',
                'categories': [],
                'confidence': 0.0,
                'reason': 'Failed to parse LLM response',
                'available': True,
            }

        # Validate and normalize fields
        valid_levels = {'SAFE', 'MODERATE', 'HIGH', 'CRITICAL'}
        risk_level = result.get('risk_level', 'SAFE').upper()
        if risk_level not in valid_levels:
            risk_level = 'SAFE'

        score = result.get('score', 0)
        try:
            score = int(score)
            score = max(0, min(100, score))
        except (TypeError, ValueError):
            score = 0

        confidence = result.get('confidence', 0.5)
        try:
            confidence = float(confidence)
            confidence = max(0.0, min(1.0, confidence))
        except (TypeError, ValueError):
            confidence = 0.5

        categories = result.get('categories', [])
        if not isinstance(categories, list):
            categories = []

        reason = result.get('reason', 'No reason provided')
        if not isinstance(reason, str):
            reason = str(reason)

        return {
            'score': score,
            'risk_level': risk_level,
            'categories': categories,
            'confidence': round(confidence, 3),
            'reason': reason,
            'available': True,
        }

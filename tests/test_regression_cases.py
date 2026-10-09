"""
Regression and coverage tests for SafeChat Guardian detection engine.
Evaluates handling of slang, misspellings, harmless contexts, indirect threats, and negations.
"""

import pytest
from backend.monitoring.ml_model import MLClassifier
from backend.monitoring.rules import RuleEngine


class TestDetectionCoverage:
    """Evaluates detection performance on varied language patterns."""

    @pytest.fixture(scope="class")
    def classifier(self):
        return MLClassifier()

    @pytest.fixture(scope="class")
    def rule_engine(self):
        return RuleEngine()

    # 1. Casing variants
    @pytest.mark.parametrize("phrase", [
        "i will strangle you",
        "I WILL STRANGLE YOU",
        "I WiLl StRaNgLe YoU",
    ])
    def test_casing_insensitivity(self, classifier, phrase):
        """Verify model prediction is robust across casing."""
        res = classifier.predict(phrase)
        assert res['category'] == 'THREAT'
        assert res['score'] >= 25

    # 2. Repeated characters & misspellings
    @pytest.mark.parametrize("phrase, expected_cat", [
        ("i will kiiiill you", "THREAT"),
        ("you are sooooo ugly and pathetic", "BULLYING"),
        ("u r such a loserrrrr", "BULLYING"),
        ("stoppppp touching me", "SAFE"),  # child discomfort / protest or safe
    ])
    def test_repeated_characters_and_elongation(self, classifier, phrase, expected_cat):
        """Verify detection handles character elongation."""
        res = classifier.predict(phrase)
        # Should detect the category or flag risk
        assert res['category'] == expected_cat or res['score'] >= 20

    # 3. Slang and abbreviations
    @pytest.mark.parametrize("phrase, expected_risk", [
        ("kys nobody likes u", True),
        ("im gonna k1ll u rn", True),
        ("wanna sneak out w/ me 2night?", True),
        ("send spicy pic on snap rn", True),
        ("tell me ur home address rn", True),
    ])
    def test_slang_and_abbreviations(self, classifier, phrase, expected_risk):
        """Verify that common risky slang triggers appropriate risk classification."""
        res = classifier.predict(phrase)
        is_risk = (res['category'] != 'SAFE') or (res['score'] >= 25)
        assert is_risk == expected_risk, f"Failed for phrase: '{phrase}', got {res}"

    # 4. Harmless contexts containing alarming words (false-positive prevention)
    @pytest.mark.parametrize("phrase", [
        "I killed you in Fortnite haha 😂",
        "We killed them in that football match",
        "The villain was killed at the end of the movie",
        "That comedy video had me dying of laughter 🤣",
        "My legs are dead after the marathon",
        "That test was absolute murder lol",
    ])
    def test_harmless_slang_and_pop_culture(self, classifier, rule_engine, phrase):
        """Verify false-positive suppression on gaming, sports, movies, and humor."""
        ml_res = classifier.predict(phrase)
        rule_res = rule_engine.analyze(phrase, [])
        
        # Rule engine should apply context modifiers (entertainment / sports / joke emoji)
        # Or ML classifier should recognize SAFE context
        is_safe_ml = (ml_res['category'] == 'SAFE') or (ml_res['score'] <= 35)
        is_safe_rule = rule_res.get('score', 0) <= 25
        assert is_safe_ml or is_safe_rule, f"False positive triggered on harmless phrase: '{phrase}'"

    # 5. Direct and indirect threats
    @pytest.mark.parametrize("phrase", [
        "I will strangle you",
        "I'm going to bash your face in",
        "I will stab you with a knife",
        "I'll jump you with my gang after school",
        "You might want to look over your shoulder today",
        "Certain people know how to make kids like you disappear",
    ])
    def test_direct_and_indirect_threats(self, classifier, rule_engine, phrase):
        """Verify threats are flagged by ML or Rule Engine."""
        ml_res = classifier.predict(phrase)
        rule_res = rule_engine.analyze(phrase, [])
        
        threat_detected = (ml_res['category'] == 'THREAT') or (rule_res.get('category') == 'THREAT') or (ml_res['score'] >= 30)
        assert threat_detected, f"Threat missed: '{phrase}', ML: {ml_res}, Rule: {rule_res}"

    # 6. Negations
    @pytest.mark.parametrize("phrase", [
        "I would never hurt you or anyone else",
        "I am definitely not going to fight anyone",
        "I do not hate you at all, you are my best friend",
        "Please do not kill yourself, you have so much to live for",
    ])
    def test_negation_awareness(self, classifier, phrase):
        """Verify negations don't blindly classify as high risk."""
        res = classifier.predict(phrase)
        assert res['category'] == 'SAFE' or res['score'] <= 35, f"Negation misclassified: '{phrase}' got {res}"

import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)


class OmegaJudge:
    """Layer 3: Judge System — evaluates and improves the fused response."""

    def evaluate(self, fused: dict[str, Any], original_query: str, analysis: Optional[dict] = None) -> dict[str, Any]:
        """Evaluate fused response with 3 judges."""
        text = fused.get("text", "")
        if not text:
            return {**fused, "judge_score": 0.0, "issues": ["empty_response"]}

        accuracy_score = self._judge_accuracy(text, original_query, analysis)
        completeness_score = self._judge_completeness(text, original_query, analysis)
        user_fit_score = self._judge_user_fit(text, original_query, analysis)

        overall = (accuracy_score * 0.4) + (completeness_score * 0.35) + (user_fit_score * 0.25)
        issues = []

        if accuracy_score < 0.5:
            issues.append("low_accuracy")
        if completeness_score < 0.5:
            issues.append("incomplete")
        if user_fit_score < 0.5:
            issues.append("poor_user_fit")

        result = {
            **fused,
            "judge_score": round(overall, 3),
            "accuracy_score": round(accuracy_score, 3),
            "completeness_score": round(completeness_score, 3),
            "user_fit_score": round(user_fit_score, 3),
            "issues": issues,
        }

        if overall < 0.4:
            result["text"] = self._add_disclaimer(text, issues)

        logger.debug(f"Judge scores: accuracy={accuracy_score:.2f}, complete={completeness_score:.2f}, fit={user_fit_score:.2f}, overall={overall:.2f}")
        return result

    def _judge_accuracy(self, text: str, query: str, analysis: Optional[dict]) -> float:
        """Judge 1: Accuracy — does the response answer the question?"""
        score = 0.5

        query_words = set(query.lower().split())
        text_lower = text.lower()
        matched = sum(1 for w in query_words if w in text_lower and len(w) > 3)
        relevance = min(matched / max(len(query_words), 1), 1.0)
        score += relevance * 0.3

        hedging = len(re.findall(r"\b(maybe|perhaps|might|possibly|ربما|قد|يمكن)\b", text_lower))
        if hedging > 3:
            score -= 0.1

        if re.search(r"\b(error|mistake|incorrect|خطأ)\b", text_lower):
            score -= 0.15

        has_numbers = bool(re.search(r"\b\d+\.?\d*\b", text))
        if analysis and analysis.get("task_type") in ("math", "factual") and has_numbers:
            score += 0.1

        return max(0.0, min(score, 1.0))

    def _judge_completeness(self, text: str, query: str, analysis: Optional[dict]) -> float:
        """Judge 2: Completeness — is the response thorough enough?"""
        score = 0.3

        word_count = len(text.split())
        complexity = (analysis or {}).get("complexity", "medium")

        if complexity == "high":
            target = 200
        elif complexity == "low":
            target = 30
        else:
            target = 80

        length_ratio = min(word_count / target, 1.5)
        score += min(length_ratio * 0.3, 0.4)

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if len(paragraphs) >= 2:
            score += 0.1

        if any(marker in text for marker in ["1.", "2.", "•", "-", "①", "②"]):
            score += 0.1

        has_intro = len(paragraphs) > 0 and len(paragraphs[0].split()) >= 10
        has_conclusion = len(paragraphs) > 1 and len(paragraphs[-1].split()) >= 5
        if has_intro:
            score += 0.05
        if has_conclusion:
            score += 0.05

        return max(0.0, min(score, 1.0))

    def _judge_user_fit(self, text: str, query: str, analysis: Optional[dict]) -> float:
        """Judge 3: User Fit — is the response appropriate for the user?"""
        score = 0.5

        query_lang = (analysis or {}).get("language", "en")
        if query_lang == "ar":
            arabic_ratio = len(re.findall(r"[\u0600-\u06FF]+", text)) / max(len(text.split()), 1)
            if arabic_ratio > 0.3:
                score += 0.3
            else:
                score -= 0.2
        elif query_lang == "en":
            english_ratio = len(re.findall(r"[a-zA-Z]+", text)) / max(len(text.split()), 1)
            if english_ratio > 0.5:
                score += 0.2

        if "?" in query or "؟" in query:
            if text.strip().startswith(("Yes", "No", "نعم", "لا", "The", "It", "هو", "هي")):
                score += 0.1

        return max(0.0, min(score, 1.0))

    def _add_disclaimer(self, text: str, issues: list[str]) -> str:
        """Add disclaimer for low-quality responses."""
        disclaimer = "\n\n⚠️ *Note: This response may not be fully accurate. Please verify important information.*"
        return text + disclaimer


omega_judge = OmegaJudge()

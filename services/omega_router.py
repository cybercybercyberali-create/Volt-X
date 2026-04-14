import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

TASK_PATTERNS = {
    "code": [r"\bcode\b", r"\bprogram\b", r"\bscript\b", r"\bfunction\b", r"\bclass\b", r"\bapi\b", r"\bdebug\b", r"\bكود\b", r"\bبرمج\b"],
    "math": [r"\bcalculate\b", r"\bsolve\b", r"\bequation\b", r"\bmath\b", r"\bاحسب\b", r"\bحل\b", r"\bمعادلة\b"],
    "creative": [r"\bwrite\b.*\b(story|poem|essay)\b", r"\bcreative\b", r"\bimagine\b", r"\bاكتب\b", r"\bقصة\b", r"\bقصيدة\b"],
    "analysis": [r"\banalyze\b", r"\bcompare\b", r"\bevaluate\b", r"\bحلل\b", r"\bقارن\b"],
    "translation": [r"\btranslat\b", r"\bترجم\b"],
    "factual": [r"\bwhat is\b", r"\bwho is\b", r"\bwhen did\b", r"\bما هو\b", r"\bمن هو\b", r"\bمتى\b"],
    "chat": [r"\bhello\b", r"\bhi\b", r"\bhey\b", r"\bmerhaba\b", r"\bمرحبا\b", r"\bأهلا\b", r"\bسلام\b"],
    "summarize": [r"\bsummar\b", r"\btl;?dr\b", r"\bلخص\b", r"\bملخص\b"],
    "explain": [r"\bexplain\b", r"\bteach\b", r"\bhow does\b", r"\bاشرح\b", r"\bكيف\b"],
}

COMPLEXITY_INDICATORS = {
    "high": [r"\bdetail\b", r"\bcomplex\b", r"\badvanced\b", r"\bin-depth\b", r"\bتفصيل\b", r"\bمعقد\b", r"\bمتقدم\b"],
    "low": [r"\bsimple\b", r"\bquick\b", r"\bbrief\b", r"\bبسيط\b", r"\bسريع\b", r"\bمختصر\b"],
}

LANGUAGE_PATTERNS = {
    "ar": r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+",
    "fa": r"[\u0600-\u06FF]+",
    "he": r"[\u0590-\u05FF]+",
    "zh": r"[\u4E00-\u9FFF]+",
    "ja": r"[\u3040-\u309F\u30A0-\u30FF]+",
    "ko": r"[\uAC00-\uD7AF]+",
    "ru": r"[\u0400-\u04FF]+",
    "hi": r"[\u0900-\u097F]+",
    "th": r"[\u0E00-\u0E7F]+",
}


class OmegaRouter:
    """Layer 0: Extracts 'DNA' of a question — task type, complexity, urgency, language."""

    def analyze(self, text: str) -> dict[str, Any]:
        """Analyze a user query and return its DNA."""
        text_lower = text.lower().strip()

        result = {
            "task_type": self._detect_task_type(text_lower),
            "complexity": self._detect_complexity(text_lower),
            "language": self._detect_language(text),
            "urgency": self._detect_urgency(text_lower),
            "word_count": len(text.split()),
            "has_question_mark": "?" in text or "؟" in text,
            "recommended_models": [],
            "recommended_timeout": 4,
            "needs_reasoning": False,
        }

        result["needs_reasoning"] = result["task_type"] in ("code", "math", "analysis")
        result["recommended_timeout"] = self._recommend_timeout(result)
        result["recommended_models"] = self._recommend_models(result)

        logger.debug(f"Router analysis: task={result['task_type']}, complexity={result['complexity']}, lang={result['language']}")
        return result

    def _detect_task_type(self, text: str) -> str:
        """Detect the primary task type."""
        scores: dict[str, int] = {}
        for task, patterns in TASK_PATTERNS.items():
            score = sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))
            if score > 0:
                scores[task] = score

        if not scores:
            return "general"
        return max(scores, key=scores.get)

    def _detect_complexity(self, text: str) -> str:
        """Detect query complexity: low, medium, high."""
        for level, patterns in COMPLEXITY_INDICATORS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return level

        word_count = len(text.split())
        if word_count > 50:
            return "high"
        elif word_count > 15:
            return "medium"
        return "low"

    def _detect_language(self, text: str) -> str:
        """Detect the primary language of the text."""
        for lang, pattern in LANGUAGE_PATTERNS.items():
            matches = re.findall(pattern, text)
            if len(matches) >= 2 or (len(matches) == 1 and len(matches[0]) > 3):
                return lang
        return "en"

    def _detect_urgency(self, text: str) -> str:
        """Detect urgency level."""
        urgent_words = [r"\burgent\b", r"\basap\b", r"\bnow\b", r"\bquick\b", r"\bعاجل\b", r"\bفوراً\b", r"\bسريع\b"]
        for pattern in urgent_words:
            if re.search(pattern, text, re.IGNORECASE):
                return "high"
        return "normal"

    def _recommend_timeout(self, analysis: dict[str, Any]) -> int:
        """Recommend total timeout based on analysis."""
        base = 4
        if analysis["complexity"] == "high":
            base = 8
        elif analysis["complexity"] == "low":
            base = 2
        if analysis["urgency"] == "high":
            base = max(2, base - 2)
        if analysis["needs_reasoning"]:
            base += 2
        return min(base, 12)

    def _recommend_models(self, analysis: dict[str, Any]) -> list[str]:
        """Recommend model IDs based on analysis."""
        from config import AI_MODELS

        task = analysis["task_type"]
        complexity = analysis["complexity"]

        if complexity == "low" or analysis["urgency"] == "high":
            return [m["id"] for m in AI_MODELS if m["tier"] <= 2]

        if task in ("code", "math"):
            preferred = ["deepseek", "gemini", "groq"]
            recommended = [m["id"] for m in AI_MODELS if m["provider"] in preferred]
            others = [m["id"] for m in AI_MODELS if m["provider"] not in preferred]
            return recommended + others

        if task == "creative":
            preferred = ["cohere", "openrouter", "gemini"]
            recommended = [m["id"] for m in AI_MODELS if m["provider"] in preferred]
            others = [m["id"] for m in AI_MODELS if m["provider"] not in preferred]
            return recommended + others

        return [m["id"] for m in AI_MODELS]


omega_router = OmegaRouter()

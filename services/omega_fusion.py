import logging
import re
from collections import Counter
from typing import Any, Optional

logger = logging.getLogger(__name__)


class OmegaFusion:
    """Layer 2: Fusion Engine — merges multiple AI responses into one optimal answer."""

    TIER_WEIGHTS = {1: 1.0, 2: 0.9, 3: 0.8, 4: 0.6}

    def fuse(self, responses: list[dict[str, Any]], analysis: Optional[dict] = None) -> dict[str, Any]:
        """Fuse multiple AI responses into the best answer."""
        if not responses:
            return {"text": "", "confidence": 0.0, "models_used": [], "method": "none"}

        if len(responses) == 1:
            return {
                "text": responses[0]["text"],
                "confidence": 0.7,
                "models_used": [responses[0]["model_id"]],
                "method": "single",
            }

        task_type = (analysis or {}).get("task_type", "general")

        if task_type in ("code", "math"):
            return self._fuse_precision(responses)
        elif task_type == "creative":
            return self._fuse_creative(responses)
        elif task_type == "factual":
            return self._fuse_factual(responses)
        else:
            return self._fuse_general(responses)

    def _fuse_general(self, responses: list[dict[str, Any]]) -> dict[str, Any]:
        """General fusion: weighted scoring."""
        scored = []
        for resp in responses:
            weight = self.TIER_WEIGHTS.get(resp.get("tier", 4), 0.6)
            text = resp["text"]
            length_score = min(len(text) / 500, 1.0)
            structure_score = self._score_structure(text)
            speed_bonus = 0.1 if resp.get("elapsed_ms", 5000) < 2000 else 0.0

            total_score = (weight * 0.4) + (length_score * 0.2) + (structure_score * 0.3) + speed_bonus
            scored.append((resp, total_score))

        scored.sort(key=lambda x: x[1], reverse=True)
        best = scored[0][0]

        return {
            "text": best["text"],
            "confidence": min(scored[0][1], 1.0),
            "models_used": [r["model_id"] for r, _ in scored[:3]],
            "method": "weighted_general",
        }

    def _fuse_precision(self, responses: list[dict[str, Any]]) -> dict[str, Any]:
        """Precision fusion for code/math: prefer responses with code blocks."""
        code_responses = []
        for resp in responses:
            text = resp["text"]
            has_code = bool(re.search(r"```[\s\S]+?```", text))
            weight = self.TIER_WEIGHTS.get(resp.get("tier", 4), 0.6)
            score = weight + (0.3 if has_code else 0.0)
            code_responses.append((resp, score))

        code_responses.sort(key=lambda x: x[1], reverse=True)
        best = code_responses[0][0]

        return {
            "text": best["text"],
            "confidence": min(code_responses[0][1], 1.0),
            "models_used": [r["model_id"] for r, _ in code_responses[:3]],
            "method": "precision",
        }

    def _fuse_creative(self, responses: list[dict[str, Any]]) -> dict[str, Any]:
        """Creative fusion: pick the longest, most expressive response."""
        creative_scored = []
        for resp in responses:
            text = resp["text"]
            uniqueness = len(set(text.split())) / max(len(text.split()), 1)
            length_score = min(len(text) / 1000, 1.0)
            score = (uniqueness * 0.5) + (length_score * 0.5)
            creative_scored.append((resp, score))

        creative_scored.sort(key=lambda x: x[1], reverse=True)
        best = creative_scored[0][0]

        return {
            "text": best["text"],
            "confidence": min(creative_scored[0][1], 1.0),
            "models_used": [r["model_id"] for r, _ in creative_scored[:3]],
            "method": "creative",
        }

    def _fuse_factual(self, responses: list[dict[str, Any]]) -> dict[str, Any]:
        """Factual fusion: voting + consensus."""
        texts = [r["text"] for r in responses]
        key_facts = []
        for text in texts:
            numbers = re.findall(r"\b\d[\d,.]+\b", text)
            key_facts.extend(numbers)

        fact_counts = Counter(key_facts)
        consensus_facts = {fact for fact, count in fact_counts.items() if count >= 2}

        best_resp = None
        best_score = -1
        for resp in responses:
            text = resp["text"]
            match_count = sum(1 for fact in consensus_facts if fact in text)
            weight = self.TIER_WEIGHTS.get(resp.get("tier", 4), 0.6)
            score = (match_count * 0.5) + (weight * 0.3) + (self._score_structure(text) * 0.2)
            if score > best_score:
                best_score = score
                best_resp = resp

        if best_resp is None:
            best_resp = responses[0]

        return {
            "text": best_resp["text"],
            "confidence": min(best_score, 1.0) if best_score > 0 else 0.5,
            "models_used": [r["model_id"] for r in responses[:3]],
            "method": "factual_consensus",
        }

    def _score_structure(self, text: str) -> float:
        """Score text structure quality."""
        score = 0.0
        if len(text) > 100:
            score += 0.2
        if "\n" in text:
            score += 0.2
        if any(marker in text for marker in ["1.", "•", "-", "*", "①"]):
            score += 0.2
        if re.search(r"```[\s\S]+?```", text):
            score += 0.2
        if text.strip().endswith((".", "!", "؟", "?")):
            score += 0.2
        return min(score, 1.0)


omega_fusion = OmegaFusion()

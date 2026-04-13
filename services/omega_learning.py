import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class OmegaLearning:
    """Layer 5: Real-time Data Fusion — replaces AI-generated data with real API data."""

    def inject_real_data(self, ai_text: str, real_data: Optional[dict[str, Any]] = None) -> str:
        """Replace any AI-generated numbers/data with real API data."""
        if not real_data:
            return ai_text

        result = ai_text

        for key, value in real_data.items():
            if isinstance(value, (int, float)):
                placeholder_patterns = [
                    f"{{{key}}}",
                    f"[{key}]",
                ]
                for pattern in placeholder_patterns:
                    result = result.replace(pattern, str(value))

        return result

    def build_fact_prompt(self, real_data: dict[str, Any]) -> str:
        """Build a fact-injection prompt section with real data."""
        if not real_data:
            return ""

        lines = ["IMPORTANT: Use these EXACT real-time values in your response:"]
        for key, value in real_data.items():
            lines.append(f"  - {key}: {value}")
        lines.append("Do NOT make up any numbers. Only use the values above.")

        return "\n".join(lines)

    def validate_response_data(self, text: str, real_data: dict[str, Any], tolerance: float = 0.02) -> dict[str, Any]:
        """Validate that the AI response uses correct real data."""
        import re

        issues = []
        valid = True

        for key, expected in real_data.items():
            if not isinstance(expected, (int, float)):
                continue

            numbers_in_text = re.findall(r"[\d,]+\.?\d*", text)
            found = False
            for num_str in numbers_in_text:
                try:
                    num = float(num_str.replace(",", ""))
                    if abs(num - expected) / max(abs(expected), 0.01) <= tolerance:
                        found = True
                        break
                except ValueError:
                    continue

            if not found:
                issues.append(f"Missing or incorrect value for {key}: expected {expected}")
                valid = False

        return {"valid": valid, "issues": issues}


omega_learning = OmegaLearning()

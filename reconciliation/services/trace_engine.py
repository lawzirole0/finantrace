from decimal import Decimal
from typing import Dict, List, Optional

class TraceResult:
    def __init__(self, opening: Decimal, deposits: Decimal, withdrawals: Decimal, closing: Decimal):
        self.opening = opening
        self.deposits = deposits
        self.withdrawals = withdrawals
        self.closing = closing
        self.expected_closing = opening + deposits - withdrawals
        self.difference = closing - self.expected_closing
        self.is_balanced = (self.difference == 0)

    def get_suggestions(self) -> List[Dict[str, str]]:
        if self.is_balanced:
            return []
        suggestions = []
        diff = abs(self.difference)

        if self.difference < 0:
            suggestions.append({
                "icon": "payments",
                "title": "Missing deposit",
                "description": f"A ${diff} deposit may not have been recorded. Check if a transaction was missed."
            })
            suggestions.append({
                "icon": "repeat",
                "title": "Duplicate withdrawal",
                "description": f"A ${diff} withdrawal might be logged twice. Review your recent withdrawals."
            })
        else:
            suggestions.append({
                "icon": "payments",
                "title": "Missing withdrawal",
                "description": f"A ${diff} withdrawal may not have been recorded. Check for unlogged expenses."
            })
            suggestions.append({
                "icon": "repeat",
                "title": "Duplicate deposit",
                "description": f"A ${diff} deposit might be logged twice. Review your recent deposits."
            })

        suggestions.append({
            "icon": "edit_note",
            "title": "Data entry error",
            "description": "One of the numbers may have been typed incorrectly. Double-check each entry."
        })
        return suggestions

    def to_context(self) -> Dict:
        return {
            "balanced": self.is_balanced,
            "opening": self.opening,
            "deposits": self.deposits,
            "withdrawals": self.withdrawals,
            "closing": self.closing,
            "expected_closing": self.expected_closing,
            "difference": self.difference,
            "suggestions": self.get_suggestions(),
        }

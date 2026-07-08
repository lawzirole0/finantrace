from decimal import Decimal
from typing import List, Dict
from ..models import Transaction

def get_cash_flow_summary(transactions: List[Transaction]) -> Dict:
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    net = total_income - total_expenses

    matched = sum(1 for t in transactions if t.status == 'matched')
    discrepancies = sum(1 for t in transactions if t.status == 'discrepancy')
    total = len(transactions)
    accuracy = (matched / total * 100) if total > 0 else 100

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_profit": net,
        "matched_count": matched,
        "discrepancy_count": discrepancies,
        "accuracy": round(accuracy, 1),
    }

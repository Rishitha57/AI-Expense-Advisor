from typing import List


class AIExpenseService:
    def __init__(self):
        self.category_map = {
            "restaurant": "food",
            "coffee": "food",
            "grocery": "food",
            "gas": "transport",
            "uber": "transport",
            "rent": "housing",
            "mortgage": "housing",
            "pharmacy": "health",
            "hospital": "health",
            "netflix": "entertainment",
            "spotify": "entertainment",
            "electric": "utilities",
            "water": "utilities",
        }

    def classify_transaction(self, merchant: str, description: str = "") -> tuple[str, float]:
        text = f"{merchant} {description}".lower()
        for keyword, category in self.category_map.items():
            if keyword in text:
                return category, 0.9
        return "uncategorized", 0.4

    def generate_advice(self, question: str, context: str, documents: List[str]) -> dict:
        evidence = documents[:3] if documents else ["No supporting finance guidance found."]
        answer = (
            f"Based on your spending context, here's a practical response to '{question}': "
            f"{context}. Focus on reducing discretionary spending and prioritizing recurring essentials."
        )
        return {
            "question": question,
            "answer": answer,
            "evidence": evidence,
            "context_summary": context,
        }

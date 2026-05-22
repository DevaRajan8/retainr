import time
import math

def decay_score(base_score: float, timestamp: float, decay_days: int) -> float:
    """
    decay_days=0  → no decay (memory stays at full score forever)
    decay_days=30 → score halves every 30 days
    Formula: score * e^(-lambda * age_in_days), lambda = ln(2)/half_life
    """
    if decay_days == 0:
        return base_score
    age_days = (time.time() - timestamp) / 86400
    decay_lambda = math.log(2) / decay_days
    return base_score * math.exp(-decay_lambda * age_days)

def composite_score(similarity: float, importance: float,
                    timestamp: float, decay_days: int) -> float:

    decayed_importance = decay_score(importance, timestamp, decay_days)
    return similarity * (0.7 + 0.3 * decayed_importance)
from typing import Dict, Any
from .diagnostic_model import Question, Domain


def score_question(question: Question, answer: Any) -> float:
    """Score entre 0 et 100 pour une question."""
    if question.type == "stars":
        if answer is None:
            return 0.0
        try:
            v = int(answer)
        except (TypeError, ValueError):
            return 0.0
        v = max(0, min(5, v))
        return (v / 5.0) * 100.0

    if question.type == "boolean":
        if isinstance(answer, str):
            val = answer.strip().lower() in ("oui", "yes", "true", "1")
        else:
            val = bool(answer)
        return 100.0 if val else 0.0

    raise ValueError(f"Type de question inconnu: {question.type}")


def score_domain(domain: Domain, answers: Dict[str, Any]) -> float:
    """
    Score d'un domaine (0 à 100).
    answers : dict {question_id (str): réponse}
    """
    total_weight = 0.0
    total_score = 0.0

    for q in domain.questions:
        ans = answers.get(q.id)         # q.id est maintenant un str
        qs = score_question(q, ans)
        total_score += qs * q.weight
        total_weight += q.weight

    if total_weight == 0:
        return 0.0

    return total_score / total_weight


def score_global(domains: Dict[str, Domain],
                 all_answers: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
    """
    Retourne :
      - score par domaine
      - score global dans '__global__'
    """
    domain_scores: Dict[str, float] = {}
    sum_scores = 0.0
    count = 0

    for domain_id, domain in domains.items():
        d_answers = all_answers.get(domain_id, {})
        s = score_domain(domain, d_answers)
        domain_scores[domain_id] = s
        if d_answers:
            sum_scores += s
            count += 1

    global_score = sum_scores / count if count > 0 else 0.0
    domain_scores["__global__"] = global_score
    return domain_scores

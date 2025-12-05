import random

import json
from pathlib import Path

from typing import Dict, Dict as DictType, Any
from .diagnostic_model import Domain
from .scoring import score_domain

STRONG_THRESHOLD = 75.0     # >= 75  -> point fort
IMPROVE_THRESHOLD = 40.0    # 40-75  -> à améliorer


def generate_sample_answers(domains: Dict[str, Domain]) -> Dict[str, Dict[str, Any]]:
    """
    Génère des réponses d'exemples plausibles pour chaque qiestion :
         - questions 'stars' -> une note entre 1 et 5
         - questions 'boolean' -> True / False aléatoire
    Retourne un dict : {domain_id: {question_id: answer}}
    """

    sample: Dict[str, Dict[str, Any]] = {}

    for domain_id, domain in domains.items():
        d_answers: Dict[str, Any] = {}
        for q in domain.questions:
            if q.type == "stars":
                d_answers[q.id] = random.randint(1, 5)
            else:   # "boolean"
                d_answers[q.id]= random.choice([True, False])

        sample[domain_id] = d_answers

    return sample




def classify_domain(score: float) -> str:
    """Retourne 'fort', 'améliorer' ou 'critique'."""
    if score >= STRONG_THRESHOLD:
        return "fort"
    if score >= IMPROVE_THRESHOLD:
        return "améliorer"
    return "critique"


def extract_weak_points(
    domains: Dict[str, Domain],
    all_answers: Dict[str, DictType[str, Any]],
) -> Dict[str, float]:
    """Domaines à améliorer ou critiques (triés du plus faible au plus fort)."""
    scores: Dict[str, float] = {}

    for did, domain in domains.items():
        d_ans = all_answers.get(did, {})
        if not d_ans:
            continue
        s = score_domain(domain, d_ans)
        if classify_domain(s) != "fort":
            scores[did] = s

    return dict(sorted(scores.items(), key=lambda kv: kv[1]))


def extract_strong_points(
    domains: Dict[str, Domain],
    all_answers: Dict[str, DictType[str, Any]],
) -> Dict[str, float]:
    """Domaines forts (triés du meilleur au moins bon)."""
    scores: Dict[str, float] = {}

    for did, domain in domains.items():
        d_ans = all_answers.get(did, {})
        if not d_ans:
            continue
        s = score_domain(domain, d_ans)
        if classify_domain(s) == "fort":
            scores[did] = s

    return dict(sorted(scores.items(), key=lambda kv: kv[1], reverse=True))



def generate_empty_answers(domains: Dict[str, Domain]) -> Dict[str, Dict[str, Any]]:
    """
    Génère un formulaire de réponses vide à partir des domaines.

    Structure retournée :
    {
        "finance": {
            "finance_1": None,
            "finance_2": None,
            ...
        },
        "rh": {
            "rh_1": None,
            ...
        },
        ...
    }

    On met None pour indiquer "pas encore répondu".
    """

    result: Dict[str, Dict[str, Any]] = {}

    for domain_id, domain in domains.items():
        domain_answers: Dict[str, Any] = {}
        for q in domain.questions:
            # q.id vient du JSON ("finance_1", "rh_3", etc.)
            domain_answers[q.id] = None
        result[domain_id] = domain_answers

    return result


def load_answers_from_file(path: str) -> Dict[str, Dict[str, Any]] :
    """
    Charge un fichier JSON de réponses et le retourne sous forme de dictionnaire Python

    Le fichier doit avoir la structure :
    {
        "finance" : {
            "finance_1" : 4,
            "finance_2" : true,
            ...
            },
        "rh" : {
            "rh_1" : false,
            ...
            }
    }
    """

    file_path = Path(path)
    if not file_path.exists() :
        raise FileNotFoundError(f"Fichier de réponse introuvable : {file_path}")
    
    with file_path.open("r", encoding="utf-8") as f:
        data: Dict[str, Dict[str, Any]] = json.load(f)

    return data 




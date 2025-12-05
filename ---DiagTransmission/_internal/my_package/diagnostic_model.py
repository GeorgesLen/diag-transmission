# diagnostic_model.py
"""
Modèle de diagnostic de transmission d'entreprise.

Les questions et domaines sont stockés dans des fichiers JSON
(par exemple : config/questions_fr.json) pour faciliter :
- la modification des textes
- la gestion de plusieurs langues

Ce module :
- définit les dataclasses (Question, Domain, SectorProfile)
- charge les données depuis le JSON (load_questions)
- expose DOMAINS_COMMON et SECTORS
- fournit build_domains_for_sector(sector_id)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional
from pathlib import Path
import json
import copy

# ---------------------------------------------------------------------------
# Types de base
# ---------------------------------------------------------------------------

QuestionType = Literal["stars", "boolean"]


@dataclass
class Question:
    id: str                 # ex: "finance_1"
    type: QuestionType      # "stars" ou "boolean"
    text: str
    weight: float = 1.0     # pondération éventuelle


@dataclass
class Domain:
    id: str                 # ex: "finance"
    label: str              # ex: "Finance"
    description: str
    questions: List[Question]


@dataclass
class SectorProfile:
    id: str                 # ex: "tech"
    label: str              # ex: "Tech / numérique / start-up"
    # questions additionnelles par domaine : {domain_id: [Question, ...]}
    extra_questions: Dict[str, List[Question]]


# ---------------------------------------------------------------------------
# Chargement des questions depuis un fichier JSON
# ---------------------------------------------------------------------------

# Répertoire racine du projet (TRANSMISSION/)
BASE_DIR = Path(__file__).resolve().parent.parent
# Dossier où se trouvent les fichiers questions_<langue>.json
CONFIG_DIR = BASE_DIR / "config"


def load_questions(language: str = "fr") -> tuple[Dict[str, Domain], Dict[str, SectorProfile]]:
    """
    Charge les domaines et secteurs à partir d'un fichier JSON :
      config/questions_<langue>.json

    Structure attendue du JSON :

    {
      "domains": [
        {
          "id": "finance",
          "label": "Finance",
          "description": "...",
          "questions": [
             {"id": "finance_1", "type": "stars", "text": "...", "weight": 1.0},
             ...
          ]
        },
        ...
      ],
      "sectors": [
        {
          "id": "tech",
          "label": "Tech / numérique / start-up",
          "extra_questions": {
            "finance": [
              {"id": "finance_tech_1", "type": "stars", "text": "..."}
            ],
            "rh": [
              {"id": "rh_tech_1", "type": "stars", "text": "..."}
            ]
          }
        },
        ...
      ]
    }
    """
    path = CONFIG_DIR / f"questions_{language}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Fichier de questions introuvable : {path}.\n"
            f"Crée par exemple 'config/questions_{language}.json'."
        )

    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    # --- Domains ---
    domains: Dict[str, Domain] = {}
    for d in data["domains"]:
        questions = [
            Question(
                id=q["id"],
                type=q["type"],
                text=q["text"],
                weight=q.get("weight", 1.0),
            )
            for q in d["questions"]
        ]
        domains[d["id"]] = Domain(
            id=d["id"],
            label=d["label"],
            description=d.get("description", ""),
            questions=questions,
        )

    # --- Sectors ---
    sectors: Dict[str, SectorProfile] = {}
    for s in data.get("sectors", []):
        extra: Dict[str, List[Question]] = {}

        for domain_id, q_list in s.get("extra_questions", {}).items():
            extra[domain_id] = [
                Question(
                    id=q["id"],
                    type=q["type"],
                    text=q["text"],
                    weight=q.get("weight", 1.0),
                )
                for q in q_list
            ]

        sectors[s["id"]] = SectorProfile(
            id=s["id"],
            label=s["label"],
            extra_questions=extra,
        )

    return domains, sectors


# ---------------------------------------------------------------------------
# Référentiels métier : domaines + secteurs
# ---------------------------------------------------------------------------

# Tu peux changer "fr" en "en", "de", etc. quand tu auras d'autres fichiers.
DOMAINS_COMMON: Dict[str, Domain]
SECTORS: Dict[str, SectorProfile]

DOMAINS_COMMON, SECTORS = load_questions(language="fr")


# ---------------------------------------------------------------------------
# Construction d'un questionnaire pour un SECTEUR donné
# ---------------------------------------------------------------------------

def build_domains_for_sector(sector_id: Optional[str]) -> Dict[str, Domain]:
    """
    Retourne une copie des domaines du tronc commun,
    enrichis avec les questions spécifiques au secteur si sector_id est fourni.

    - sector_id = None  -> seulement le tronc commun
    - sector_id inconnu -> ValueError
    """
    # copie profonde pour ne pas modifier le référentiel de base
    domains = {k: copy.deepcopy(v) for k, v in DOMAINS_COMMON.items()}

    if sector_id is None:
        return domains

    sector = SECTORS.get(sector_id)
    if sector is None:
        raise ValueError(f"Secteur inconnu: {sector_id}")

    for domain_id, extra_qs in sector.extra_questions.items():
        if domain_id not in domains:
            # domaine non défini dans le tronc commun -> on ignore
            continue
        domains[domain_id].questions.extend(copy.deepcopy(extra_qs))

    return domains

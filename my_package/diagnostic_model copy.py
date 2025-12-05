# diagnostic_model.py
"""
Modèle de diagnostic de transmission d'entreprise (version simplifiée pour tests).

- 2 domaines tronc commun : Finance, Ressources Humaines
- 10 secteurs avec quelques questions additionnelles

Tu pourras ensuite ré-étendre à 8 domaines comme dans ta version complète.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional
import copy

QuestionType = Literal["stars", "boolean"]


# ---------------------------------------------------------------------------
# Modèle de base
# ---------------------------------------------------------------------------

@dataclass
class Question:
    id: str                     # ex : "finance_1"
    type: QuestionType          # "stars" ou "boolean"
    text: str
    weight: float = 1.0          # pondération éventuelle


@dataclass
class Domain:
    id: str                   # ex: "finance"
    label: str                # ex: "Finance"
    description: str
    questions: List[Question]


@dataclass
class SectorProfile:
    id: str                   # ex: "industrie"
    label: str                # ex: "Industrie & fabrication"
    extra_questions: Dict[str, List[Question]]   # clé = domain.id


# ---------------------------------------------------------------------------
# TRONC COMMUN (simplifié pour tests) : 2 domaines
# ---------------------------------------------------------------------------

DOMAINS_COMMON: Dict[str, Domain] = {}

# 1) FINANCE
DOMAINS_COMMON["finance"] = Domain(
    id="finance",
    label="Finance",
    description="Santé financière, rentabilité, trésorerie et valorisation",
    questions=[
        Question("finance_1", "stars",
                 "La rentabilité de l'entreprise est-elle stable sur les 3 dernières années ?"),
        Question("finance_2", "boolean",
                 "La trésorerie permet-elle de couvrir 3 mois de charges fixes ?"),
        Question("finance_3", "boolean",
                 "Les comptes sont-ils certifiés par un expert-comptable ?"),
        Question("finance_4", "stars",
                 "Le niveau d'endettement est-il maîtrisé (ratio < 3) ?"),
        Question("finance_5", "boolean",
                 "Existe-t-il un tableau de bord financier régulièrement mis à jour ?"),
        Question("finance_6", "stars",
                 "La marge brute est-elle conforme au secteur d'activité ?"),
    ],
)

# 2) RESSOURCES HUMAINES
DOMAINS_COMMON["rh"] = Domain(
    id="rh",
    label="Ressources Humaines",
    description="Équipe, compétences, culture et organisation RH",
    questions=[
        Question("rh_1", "boolean",
                 "Le taux de turnover est-il inférieur à 15 % ?"),
        Question("rh_2", "stars",
                 "Les compétences clés sont-elles documentées et transférables ?"),
        Question("rh_3", "boolean",
                 "Existe-t-il un plan de formation structuré ?"),
        Question("rh_4", "stars",
                 "Le climat social est-il favorable ?"),
        Question("rh_5", "boolean",
                 "Les contrats de travail sont-ils conformes et à jour ?"),
        Question("rh_6", "stars",
                 "Y a-t-il des personnes clés indispensables au fonctionnement ?"),
    ],
)

# 3) COMMERCIAL & MARKETING
DOMAINS_COMMON["commercial"] = Domain(
    id="commercial",
    label="Commercial & Marketing",
    description="Clients, marché, ventes et stratégie commerciale",
    questions=[
        Question("commercial_1", "boolean",
                 "Le portefeuille clients est-il diversifié (pas de dépendance > 30 %) ?"),
        Question("commercial_2", "stars",
                 "Le taux de fidélisation client est-il satisfaisant ?"),
        Question("commercial_3", "boolean",
                 "La stratégie commerciale est-elle formalisée ?"),
        Question("commercial_4", "stars",
                 "Le positionnement prix est-il compétitif ?"),
        Question("commercial_5", "stars",
                 "Les contrats clients sont-ils sécurisés et récurrents ?"),
        Question("commercial_6", "stars",
                 "La notoriété de la marque est-elle établie ?"),
    ],
)

# 4) PRODUCTION & OPÉRATIONS
DOMAINS_COMMON["production"] = Domain(
    id="production",
    label="Production & Opérations",
    description="Processus, qualité, capacités et efficacité opérationnelle",
    questions=[
        Question("production_1", "boolean",
                 "Les processus de production sont-ils documentés ?"),
        Question("production_2", "stars",
                 "Le taux de qualité/conformité est-il supérieur à 95 % ?"),
        Question("production_3", "stars",
                 "Les équipements sont-ils en bon état et entretenus ?"),
        Question("production_4", "boolean",
                 "La capacité de production peut-elle être augmentée ?"),
        Question("production_5", "stars",
                 "Les fournisseurs clés sont-ils fiables et diversifiés ?"),
        Question("production_6", "boolean",
                 "Existe-t-il des certifications qualité (ISO, etc.) ?"),
    ],
)

# 5) JURIDIQUE & CONFORMITÉ
DOMAINS_COMMON["juridique"] = Domain(
    id="juridique",
    label="Juridique & Conformité",
    description="Contrats, propriété intellectuelle et conformité réglementaire",
    questions=[
        Question("juridique_1", "boolean",
                 "Les statuts et documents sociaux sont-ils à jour ?"),
        Question("juridique_2", "boolean",
                 "Y a-t-il des litiges en cours ou potentiels ?"),
        Question("juridique_3", "stars",
                 "La propriété intellectuelle est-elle protégée ?"),
        Question("juridique_4", "stars",
                 "Les baux et contrats importants sont-ils sécurisés ?"),
        Question("juridique_5", "boolean",
                 "L'entreprise est-elle conforme au RGPD ?"),
        Question("juridique_6", "boolean",
                 "Les assurances sont-elles adaptées et à jour ?"),
    ],
)

# 6) SYSTÈMES D'INFORMATION
DOMAINS_COMMON["si"] = Domain(
    id="si",
    label="Systèmes d'Information",
    description="Infrastructure IT, données et sécurité informatique",
    questions=[
        Question("si_1", "stars",
                 "L'infrastructure IT est-elle documentée et maintenue ?"),
        Question("si_2", "boolean",
                 "Les données sont-elles sauvegardées régulièrement ?"),
        Question("si_3", "stars",
                 "La cybersécurité est-elle au niveau requis ?"),
        Question("si_4", "stars",
                 "Les logiciels métier sont-ils standards ou propriétaires ?"),
        Question("si_5", "boolean",
                 "Un plan de continuité d'activité existe-t-il ?"),
        Question("si_6", "boolean",
                 "Les accès et mots de passe sont-ils gérés de manière sécurisée ?"),
    ],
)

# 7) STRATÉGIE & GOUVERNANCE
DOMAINS_COMMON["strategie"] = Domain(
    id="strategie",
    label="Stratégie & Gouvernance",
    description="Vision, positionnement et prise de décision",
    questions=[
        Question("strategie_1", "stars",
                 "La vision et la stratégie sont-elles clairement définies ?"),
        Question("strategie_2", "stars",
                 "Le marché cible présente-t-il un potentiel de croissance ?"),
        Question("strategie_3", "stars",
                 "Les avantages concurrentiels sont-ils identifiés et durables ?"),
        Question("strategie_4", "boolean",
                 "La gouvernance est-elle structurée (comité, réunions) ?"),
        Question("strategie_5", "boolean",
                 "Un business plan à 3 ans existe-t-il ?"),
        Question("strategie_6", "stars",
                 "Les décisions sont-elles prises de manière collégiale ?"),
    ],
)

# 8) ORGANISATION & PROCESSUS
DOMAINS_COMMON["organisation"] = Domain(
    id="organisation",
    label="Organisation & Processus",
    description="Structure, workflows et documentation interne",
    questions=[
        Question("organisation_1", "boolean",
                 "L'organigramme est-il clair et à jour ?"),
        Question("organisation_2", "stars",
                 "Les processus métier sont-ils documentés ?"),
        Question("organisation_3", "stars",
                 "La délégation des responsabilités est-elle effective ?"),
        Question("organisation_4", "stars",
                 "Les réunions sont-elles efficaces et structurées ?"),
        Question("organisation_5", "stars",
                 "La communication interne est-elle fluide ?"),
        Question("organisation_6", "stars",
                 "L'entreprise peut-elle fonctionner sans le dirigeant ?"),
    ],
)


# ---------------------------------------------------------------------------
# SECTEURS (10) – ils pourront ajouter des questions sur ces domaines
# ---------------------------------------------------------------------------

SECTORS: Dict[str, SectorProfile] = {}

SECTORS["industrie"] = SectorProfile(
    id="industrie",
    label="Industrie & fabrication",
    extra_questions={
        "finance": [
            Question(
                id=101,
                type="stars",
                text="Les coûts de production sont-ils bien maîtrisés et suivis ?",
            ),
        ],
    },
)

SECTORS["construction"] = SectorProfile(
    id="construction",
    label="Construction / BTP",
    extra_questions={
        "finance": [
            Question(
                id=201,
                type="boolean",
                text="Les marges par chantier sont-elles suivies individuellement ?",
            ),
        ],
    },
)

SECTORS["retail"] = SectorProfile(
    id="retail",
    label="Commerce de détail & distribution",
    extra_questions={
        "finance": [
            Question(
                id=301,
                type="stars",
                text="La rotation des stocks a-t-elle un impact maîtrisé sur la trésorerie ?",
            ),
        ],
    },
)

SECTORS["hotellerie"] = SectorProfile(
    id="hotellerie",
    label="Hôtellerie, restauration & tourisme",
    extra_questions={
        "rh": [
            Question(
                id=401,
                type="stars",
                text="La saisonnalité est-elle anticipée dans la gestion des équipes ?",
            ),
        ],
    },
)

SECTORS["services_pro"] = SectorProfile(
    id="services_pro",
    label="Services professionnels",
    extra_questions={
        "rh": [
            Question(
                id=501,
                type="stars",
                text="Les profils clés sont-ils fidélisés (plan de carrière, intéressement, etc.) ?",
            ),
        ],
    },
)

SECTORS["sante"] = SectorProfile(
    id="sante",
    label="Santé & médico-social",
    extra_questions={
        "rh": [
            Question(
                id=601,
                type="boolean",
                text="Les effectifs sont-ils adaptés aux exigences réglementaires (ratios, qualifications) ?",
            ),
        ],
    },
)

SECTORS["tech"] = SectorProfile(
    id="tech",
    label="Tech / numérique / start-up",
    extra_questions={
        "rh": [
            Question(
                id=701,
                type="stars",
                text="Les compétences techniques clés sont-elles sécurisées (peu de dépendance à une seule personne) ?",
            ),
        ],
    },
)

SECTORS["logistique"] = SectorProfile(
    id="logistique",
    label="Transport & logistique",
    extra_questions={
        "finance": [
            Question(
                id=801,
                type="stars",
                text="Les coûts de carburant et de transport sont-ils suivis et optimisés ?",
            ),
        ],
    },
)

SECTORS["agro"] = SectorProfile(
    id="agro",
    label="Agriculture & agroalimentaire",
    extra_questions={
        "finance": [
            Question(
                id=901,
                type="boolean",
                text="Les aides/subventions sont-elles intégrées et suivies dans la gestion financière ?",
            ),
        ],
    },
)

SECTORS["asso"] = SectorProfile(
    id="asso",
    label="Associations & organisations non lucratives",
    extra_questions={
        "finance": [
            Question(
                id=1001,
                type="stars",
                text="La dépendance à un financeur unique est-elle limitée ?",
            ),
        ],
    },
)

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
            continue
        domains[domain_id].questions.extend(copy.deepcopy(extra_qs))

    return domains

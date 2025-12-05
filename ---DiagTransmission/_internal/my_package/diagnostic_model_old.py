# diagnostic_model_old.py
"""
Modèle de diagnostic de transmission d'entreprise.

- 8 domaines
- 48 questions "tronc commun"
- 10 secteurs d'activité avec questions additionnelles

Types de question :
- "stars"   : note de 1 à 5
- "boolean" : Oui/Non

Les fonctions principales :
- build_domains_for_sector(sector_id)
- compute_domain_score(domain_id, answers)
- compute_global_score(domain_scores)
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
    id: int
    type: QuestionType        # "stars" ou "boolean"
    text: str
    weight: float = 1.0       # pondération éventuelle


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
    # questions supplémentaires par domaine (clé = domain.id)
    extra_questions: Dict[str, List[Question]]


# ---------------------------------------------------------------------------
# Définition du TRONC COMMUN : 8 domaines, 48 questions
# ---------------------------------------------------------------------------

DOMAINS_COMMON: Dict[str, Domain] = {}

# 1) FINANCE
DOMAINS_COMMON["finance"] = Domain(
    id="finance",
    label="Finance",
    description="Santé financière, rentabilité, trésorerie et valorisation",
    questions=[
        Question(
            id=1,
            type="stars",
            text="La rentabilité de l'entreprise est-elle stable sur les 3 dernières années ?",
        ),
        Question(
            id=2,
            type="boolean",
            text="La trésorerie permet-elle de couvrir 3 mois de charges fixes ?",
        ),
        Question(
            id=3,
            type="boolean",
            text="Les comptes sont-ils certifiés par un expert-comptable ?",
        ),
        Question(
            id=4,
            type="stars",
            text="Le niveau d'endettement est-il maîtrisé (ratio < 3) ?",
        ),
        Question(
            id=5,
            type="boolean",
            text="Existe-t-il un tableau de bord financier régulièrement mis à jour ?",
        ),
        Question(
            id=6,
            type="stars",
            text="La marge brute est-elle conforme au secteur d'activité ?",
        ),
    ],
)

# 2) RESSOURCES HUMAINES
DOMAINS_COMMON["rh"] = Domain(
    id="rh",
    label="Ressources Humaines",
    description="Équipe, compétences, culture et organisation RH",
    questions=[
        Question(
            id=1,
            type="boolean",
            text="Le taux de turnover est-il inférieur à 15 % ?",
        ),
        Question(
            id=2,
            type="stars",
            text="Les compétences clés sont-elles documentées et transférables ?",
        ),
        Question(
            id=3,
            type="boolean",
            text="Existe-t-il un plan de formation structuré ?",
        ),
        Question(
            id=4,
            type="stars",
            text="Le climat social est-il favorable ?",
        ),
        Question(
            id=5,
            type="boolean",
            text="Les contrats de travail sont-ils conformes et à jour ?",
        ),
        Question(
            id=6,
            type="stars",
            text="Y a-t-il des personnes clés indispensables au fonctionnement ?",
        ),
    ],
)

# 3) COMMERCIAL & MARKETING
DOMAINS_COMMON["commercial"] = Domain(
    id="commercial",
    label="Commercial & Marketing",
    description="Clients, marché, ventes et stratégie commerciale",
    questions=[
        Question(
            id=1,
            type="boolean",
            text="Le portefeuille clients est-il diversifié (pas de dépendance > 30 %) ?",
        ),
        Question(
            id=2,
            type="stars",
            text="Le taux de fidélisation client est-il satisfaisant ?",
        ),
        Question(
            id=3,
            type="boolean",
            text="La stratégie commerciale est-elle formalisée ?",
        ),
        Question(
            id=4,
            type="stars",
            text="Le positionnement prix est-il compétitif ?",
        ),
        Question(
            id=5,
            type="stars",
            text="Les contrats clients sont-ils sécurisés et récurrents ?",
        ),
        Question(
            id=6,
            type="stars",
            text="La notoriété de la marque est-elle établie ?",
        ),
    ],
)

# 4) PRODUCTION & OPÉRATIONS
DOMAINS_COMMON["production"] = Domain(
    id="production",
    label="Production & Opérations",
    description="Processus, qualité, capacités et efficacité opérationnelle",
    questions=[
        Question(
            id=1,
            type="boolean",
            text="Les processus de production sont-ils documentés ?",
        ),
        Question(
            id=2,
            type="stars",
            text="Le taux de qualité/conformité est-il supérieur à 95 % ?",
        ),
        Question(
            id=3,
            type="stars",
            text="Les équipements sont-ils en bon état et entretenus ?",
        ),
        Question(
            id=4,
            type="boolean",
            text="La capacité de production peut-elle être augmentée ?",
        ),
        Question(
            id=5,
            type="stars",
            text="Les fournisseurs clés sont-ils fiables et diversifiés ?",
        ),
        Question(
            id=6,
            type="boolean",
            text="Existe-t-il des certifications qualité (ISO, etc.) ?",
        ),
    ],
)

# 5) JURIDIQUE & CONFORMITÉ
DOMAINS_COMMON["juridique"] = Domain(
    id="juridique",
    label="Juridique & Conformité",
    description="Contrats, propriété intellectuelle et conformité réglementaire",
    questions=[
        Question(
            id=1,
            type="boolean",
            text="Les statuts et documents sociaux sont-ils à jour ?",
        ),
        Question(
            id=2,
            type="boolean",
            text="Y a-t-il des litiges en cours ou potentiels ?",
        ),
        Question(
            id=3,
            type="stars",
            text="La propriété intellectuelle est-elle protégée ?",
        ),
        Question(
            id=4,
            type="stars",
            text="Les baux et contrats importants sont-ils sécurisés ?",
        ),
        Question(
            id=5,
            type="boolean",
            text="L'entreprise est-elle conforme au RGPD ?",
        ),
        Question(
            id=6,
            type="boolean",
            text="Les assurances sont-elles adaptées et à jour ?",
        ),
    ],
)

# 6) SYSTÈMES D'INFORMATION
DOMAINS_COMMON["si"] = Domain(
    id="si",
    label="Systèmes d'Information",
    description="Infrastructure IT, données et sécurité informatique",
    questions=[
        Question(
            id=1,
            type="stars",
            text="L'infrastructure IT est-elle documentée et maintenue ?",
        ),
        Question(
            id=2,
            type="boolean",
            text="Les données sont-elles sauvegardées régulièrement ?",
        ),
        Question(
            id=3,
            type="stars",
            text="La cybersécurité est-elle au niveau requis ?",
        ),
        Question(
            id=4,
            type="stars",
            text="Les logiciels métier sont-ils adaptés (standards ou maîtrisés en interne) ?",
        ),
        Question(
            id=5,
            type="boolean",
            text="Un plan de continuité d'activité existe-t-il ?",
        ),
        Question(
            id=6,
            type="boolean",
            text="Les accès et mots de passe sont-ils gérés de manière sécurisée ?",
        ),
    ],
)

# 7) STRATÉGIE & GOUVERNANCE
DOMAINS_COMMON["strategie"] = Domain(
    id="strategie",
    label="Stratégie & Gouvernance",
    description="Vision, positionnement et prise de décision",
    questions=[
        Question(
            id=1,
            type="stars",
            text="La vision et la stratégie sont-elles clairement définies ?",
        ),
        Question(
            id=2,
            type="stars",
            text="Le marché cible présente-t-il un potentiel de croissance ?",
        ),
        Question(
            id=3,
            type="stars",
            text="Les avantages concurrentiels sont-ils identifiés et durables ?",
        ),
        Question(
            id=4,
            type="boolean",
            text="La gouvernance est-elle structurée (comité, réunions) ?",
        ),
        Question(
            id=5,
            type="boolean",
            text="Un business plan à 3 ans existe-t-il ?",
        ),
        Question(
            id=6,
            type="stars",
            text="Les décisions sont-elles prises de manière collégiale ?",
        ),
    ],
)

# 8) ORGANISATION & PROCESSUS
DOMAINS_COMMON["organisation"] = Domain(
    id="organisation",
    label="Organisation & Processus",
    description="Structure, workflows et documentation interne",
    questions=[
        Question(
            id=1,
            type="boolean",
            text="L'organigramme est-il clair et à jour ?",
        ),
        Question(
            id=2,
            type="stars",
            text="Les processus métier sont-ils documentés ?",
        ),
        Question(
            id=3,
            type="stars",
            text="La délégation des responsabilités est-elle effective ?",
        ),
        Question(
            id=4,
            type="stars",
            text="Les réunions sont-elles efficaces et structurées ?",
        ),
        Question(
            id=5,
            type="stars",
            text="La communication interne est-elle fluide ?",
        ),
        Question(
            id=6,
            type="stars",
            text="L'entreprise peut-elle fonctionner sans le dirigeant ?",
        ),
    ],
)

# ---------------------------------------------------------------------------
# Définition des 10 SECTEURS avec questions additionnelles
# (pour l'instant seulement quelques questions par secteur ; à compléter)
# ---------------------------------------------------------------------------

SECTORS: Dict[str, SectorProfile] = {}

SECTORS["industrie"] = SectorProfile(
    id="industrie",
    label="Industrie & fabrication",
    extra_questions={
        "production": [
            Question(
                id=101,
                type="stars",
                text="Le taux d'utilisation des capacités de production est-il optimisé ?",
            ),
            Question(
                id=102,
                type="boolean",
                text="Un plan de maintenance préventive est-il formalisé et suivi ?",
            ),
        ],
        "organisation": [
            Question(
                id=103,
                type="stars",
                text="Les procédures de sécurité au travail sont-elles appliquées et contrôlées ?",
            ),
        ],
    },
)

SECTORS["construction"] = SectorProfile(
    id="construction",
    label="Construction / BTP",
    extra_questions={
        "production": [
            Question(
                id=201,
                type="stars",
                text="La planification des chantiers permet-elle de limiter les retards ?",
            ),
            Question(
                id=202,
                type="boolean",
                text="Les coûts de chantier sont-ils suivis en temps réel ?",
            ),
        ],
        "juridique": [
            Question(
                id=203,
                type="boolean",
                text="Les contrats de sous-traitance sont-ils sécurisés et standardisés ?",
            ),
        ],
    },
)

SECTORS["retail"] = SectorProfile(
    id="retail",
    label="Commerce de détail & distribution",
    extra_questions={
        "commercial": [
            Question(
                id=301,
                type="stars",
                text="La rotation des stocks est-elle maîtrisée ?",
            ),
            Question(
                id=302,
                type="boolean",
                text="Les ruptures de stock sont-elles rares ?",
            ),
        ],
        "organisation": [
            Question(
                id=303,
                type="stars",
                text="Les procédures d'encaissement et de gestion de caisse sont-elles sécurisées ?",
            ),
        ],
    },
)

SECTORS["hotellerie"] = SectorProfile(
    id="hotellerie",
    label="Hôtellerie, restauration & tourisme",
    extra_questions={
        "commercial": [
            Question(
                id=401,
                type="stars",
                text="La satisfaction client est-elle régulièrement mesurée (avis, enquêtes) ?",
            ),
            Question(
                id=402,
                type="boolean",
                text="Les avis en ligne sont-ils suivis et traités ?",
            ),
        ],
        "production": [
            Question(
                id=403,
                type="stars",
                text="Les standards de qualité de service sont-ils définis et respectés ?",
            ),
        ],
    },
)

SECTORS["services_pro"] = SectorProfile(
    id="services_pro",
    label="Services professionnels (fiduciaire, conseil, ingénierie, etc.)",
    extra_questions={
        "rh": [
            Question(
                id=501,
                type="stars",
                text="Le niveau de compétence des équipes est-il aligné sur les attentes des clients ?",
            ),
        ],
        "strategie": [
            Question(
                id=502,
                type="stars",
                text="Le positionnement de l'offre se distingue-t-il clairement de la concurrence ?",
            ),
        ],
    },
)

SECTORS["sante"] = SectorProfile(
    id="sante",
    label="Santé & médico-social",
    extra_questions={
        "juridique": [
            Question(
                id=601,
                type="boolean",
                text="Les exigences réglementaires spécifiques au secteur de la santé sont-elles respectées ?",
            ),
        ],
        "production": [
            Question(
                id=602,
                type="stars",
                text="Les protocoles de prise en charge sont-ils formalisés et appliqués ?",
            ),
        ],
    },
)

SECTORS["tech"] = SectorProfile(
    id="tech",
    label="Tech / numérique / start-up",
    extra_questions={
        "si": [
            Question(
                id=701,
                type="stars",
                text="La propriété du code et des données (IP) est-elle clairement définie et sécurisée ?",
            ),
            Question(
                id=702,
                type="boolean",
                text="Les environnements de développement, test et production sont-ils séparés ?",
            ),
        ],
        "strategie": [
            Question(
                id=703,
                type="stars",
                text="La roadmap produit est-elle structurée et partagée avec les équipes ?",
            ),
        ],
    },
)

SECTORS["logistique"] = SectorProfile(
    id="logistique",
    label="Transport & logistique",
    extra_questions={
        "production": [
            Question(
                id=801,
                type="stars",
                text="Les indicateurs de ponctualité et de fiabilité des livraisons sont-ils satisfaisants ?",
            ),
        ],
        "si": [
            Question(
                id=802,
                type="stars",
                text="Les systèmes de suivi (tracking) des flux sont-ils fiables et intégrés ?",
            ),
        ],
    },
)

SECTORS["agro"] = SectorProfile(
    id="agro",
    label="Agriculture & agroalimentaire",
    extra_questions={
        "production": [
            Question(
                id=901,
                type="stars",
                text="La traçabilité des produits est-elle assurée tout au long de la chaîne ?",
            ),
        ],
        "juridique": [
            Question(
                id=902,
                type="boolean",
                text="Les normes sanitaires et environnementales sont-elles respectées ?",
            ),
        ],
    },
)

SECTORS["asso"] = SectorProfile(
    id="asso",
    label="Associations & organisations non lucratives",
    extra_questions={
        "strategie": [
            Question(
                id=1001,
                type="stars",
                text="La mission et les objectifs de l'organisation sont-ils clairement formalisés ?",
            ),
        ],
        "finance": [
            Question(
                id=1002,
                type="stars",
                text="La diversification des sources de financement est-elle suffisante ?",
            ),
        ],
    },
)

# ---------------------------------------------------------------------------
# Construction d'un questionnaire pour un SECTEUR donné
# ---------------------------------------------------------------------------

def build_domains_for_sector(sector_id: Optional[str]) -> Dict[str, Domain]:
    """
    Retourne une copie des domaines, enrichis avec les questions
    spécifiques au secteur si sector_id est fourni.

    - sector_id = None  -> seulement le tronc commun
    - sector_id inconnu -> ValueError
    """
    # copie profonde pour ne pas modifier le référentiel
    domains = {k: copy.deepcopy(v) for k, v in DOMAINS_COMMON.items()}

    if sector_id is None:
        return domains

    sector = SECTORS.get(sector_id)
    if sector is None:
        raise ValueError(f"Secteur inconnu: {sector_id}")

    for domain_id, extra_qs in sector.extra_questions.items():
        if domain_id not in domains:
            # domaine non défini dans le tronc commun
            continue
        domains[domain_id].questions.extend(copy.deepcopy(extra_qs))

    return domains

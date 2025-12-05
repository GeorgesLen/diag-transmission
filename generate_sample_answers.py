import json
from pathlib import Path

from my_package.diagnostic_model import build_domains_for_sector, SECTORS

# Génère des réponses aléatoires plausibles
def generate_sample_answers(domains):
    answers = {}

    for domain_id, domain in domains.items():
        answers[domain_id] = {}

        for q in domain.questions:
            if q.type == "stars":          # note sur 5
                answers[domain_id][q.id] = 1 + (hash(q.id) % 5)
            elif q.type == "boolean":      # oui / non
                answers[domain_id][q.id] = bool(hash(q.id) % 2)
            else:
                answers[domain_id][q.id] = None

    return answers


def main():
    # Choisir un secteur (par défaut "tech")
    sector_id = "tech"  
    domains = build_domains_for_sector(sector_id)

    sample_answers = generate_sample_answers(domains)

    # Sauvegarde dans data/
    out_path = Path("data/reponses_exemple.json")
    out_path.parent.mkdir(exist_ok=True)

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(sample_answers, f, ensure_ascii=False, indent=2)

    print(f"✔ Fichier de réponses d'exemple généré : {out_path}")


if __name__ == "__main__":
    main()


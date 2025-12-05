from my_package.diagnostic_model import build_domains_for_sector, SECTORS
from my_package.scoring import score_global
from my_package.questionnaire import (
    extract_weak_points, 
    extract_strong_points, 
    generate_empty_answers,
    load_answers_from_file,
)

import json
from pathlib import Path


def main() -> None:

    # Afficher les secteurs disponibles
    print("Secteurs disponibles :", list(SECTORS.keys()))

    # Choix du secteur à tester
    sector_id = "industrie"  # ou "tech", "commerce", "sante", "btp", "agro", None...
    domains = build_domains_for_sector(sector_id)


    # ---------------------------------------------------------------
    # MODE 1 : générer un modèle de réponses (à lancer une fois)
    # ---------------------------------------------------------------
    generate_template = False       # passer à True pour générer le fichier

    if generate_template:
        empty_answers = generate_empty_answers(domains)
        Path("data").mkdir(exist_ok=True)
        template_path=Path("data/reponses_template.json")

        with template_path.open("w", encoding="utf-8") as f:
            json.dump(empty_answers, f, ensure_ascii=False, indent=2)

        print(f"Modèle de réponses généré dans : {template_path}")

        return      # on arrête là dans ce mode
    

    # ---------------------------------------------------------------
    # MODE 2 : kire un fichier de réponses rempli
    # ---------------------------------------------------------------
    answers_path = "data/reponses_template.json"    # à remplir à la main
    all_answers = load_answers_from_file(answers_path)

    # Afficher un petit résimé
    print("\nNombre de questions par domaine :")
    for did, domain in domains.items():
        print(f"- {did} : {len(domain.questions)} question(s)")

    # Calcul des scores
    scores = score_global(domains, all_answers)
    print("\nScore global :", round(scores["__global__"], 1))
    print("Points faibles :", extract_weak_points(domains, all_answers))
    print("Points forts   :", extract_strong_points(domains, all_answers))
    print("Domaines disponibles :", list(domains.keys()))


if __name__ == "__main__":
    main()

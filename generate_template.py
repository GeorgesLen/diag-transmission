from pathlib import Path
import json

from my_package.diagnostic_model import build_domains_for_sector
from my_package.questionnaire import generate_empty_answers


def main() -> None:
    # Choisis un secteur pour le modèle (ou None pour tronc commun)
    sector_id = "industrie"   # tu peux mettre "tech", "commerce", etc. ou None
    domains = build_domains_for_sector(sector_id)

    # On génère le formulaire vide
    empty_answers = generate_empty_answers(domains)

    # Dossier data/
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    template_path = data_dir / "reponses_template.json"
    with template_path.open("w", encoding="utf-8") as f:
        json.dump(empty_answers, f, ensure_ascii=False, indent=2)

    print(f"Modèle de réponses généré dans : {template_path}")


if __name__ == "__main__":
    main()

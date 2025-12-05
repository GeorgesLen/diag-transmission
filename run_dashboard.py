# run_dashboard.py
from pathlib import Path
import os
import sys
import subprocess


def main() -> None:
    """
    Lance Streamlit comme si on faisait :

        streamlit run dashboard.py --server.port 8501

    dans le bon dossier de projet.
    """

    # 1) Dossier du projet = dossier où se trouve cet EXE / script
    project_dir = Path(__file__).resolve().parent
    os.chdir(project_dir)  # très important

    # 2) Chemin vers le dashboard
    dashboard_path = project_dir / "dashboard.py"

    # 3) Commande à exécuter : python -m streamlit run dashboard.py ...
    cmd = [
        sys.executable,   # l'interpréteur Python embarqué dans l'EXE
        "-m",
        "streamlit",
        "run",
        str(dashboard_path),
        "--server.port",
        "8501",
    ]

    # 4) Lancer Streamlit (on laisse la console ouverte)
    subprocess.run(cmd)


if __name__ == "__main__":
    main()


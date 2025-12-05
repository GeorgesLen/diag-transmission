from .diagnostic_model import (
    Question,
    Domain,
    SectorProfile,
    DOMAINS_COMMON,
    SECTORS,
    build_domains_for_sector,
)

from .scoring import (
    score_question,
    score_domain,
    score_global,
)

from .questionnaire import (
    classify_domain,
    extract_weak_points,
    extract_strong_points,
    generate_empty_answers,
    load_answers_from_file,
    generate_sample_answers,
)

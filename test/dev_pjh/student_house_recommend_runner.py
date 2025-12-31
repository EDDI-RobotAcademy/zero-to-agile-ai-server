"""finder_request 기반 추천 러너."""
from __future__ import annotations

import argparse
import json
import os
import sys

from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from infrastructure.db.postgres import get_db_session
from infrastructure.external.embedding_agent import OpenAIEmbeddingAgent
from modules.finder_request.adapter.output.repository.finder_request_repository import (
    FinderRequestRepository,
)
from modules.finder_request.infrastructure.repository.finder_request_embedding_repository import (
    FinderRequestEmbeddingRepository,
)
from modules.student_house.application.usecase.recommend_student_house_for_finder_request import (
    RecommendStudentHouseUseCase,
)
from modules.student_house.infrastructure.repository.student_house_embedding_search_repository import (
    StudentHouseEmbeddingSearchRepository,
)
from modules.student_house.infrastructure.repository.student_house_search_repository import (
    StudentHouseSearchRepository,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--finder-request-id", type=int, required=True)
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    db_gen = get_db_session()
    db = next(db_gen)
    try:
        finder_request_repo = FinderRequestRepository(db)
        embedding_repo = FinderRequestEmbeddingRepository()
        search_repo = StudentHouseSearchRepository()
        vector_repo = StudentHouseEmbeddingSearchRepository()
        embedder = OpenAIEmbeddingAgent()

        usecase = RecommendStudentHouseUseCase(
            finder_request_repo,
            embedding_repo,
            search_repo,
            vector_repo,
            embedder,
        )

        result = usecase.execute(args.finder_request_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        db_gen.close()


if __name__ == "__main__":
    main()

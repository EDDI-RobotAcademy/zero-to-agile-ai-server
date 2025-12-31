"""student_house 추천 API 테스트 러너."""
from __future__ import annotations

import argparse
import json
import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from modules.student_house.adapter.input.web.router.student_house_router import (
    router as student_house_router,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--finder-request-id", type=int, required=True)
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    app = FastAPI()
    app.include_router(student_house_router, prefix="/api")
    client = TestClient(app)

    response = client.post(
        "/api/student_house/recommend",
        json={"finder_request_id": args.finder_request_id},
    )
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

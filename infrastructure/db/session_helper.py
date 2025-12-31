from __future__ import annotations

from typing import Generator

from sqlalchemy.orm import Session


def open_session(session_factory) -> tuple[Session, Generator | None]:
    """세션을 열고 종료용 제너레이터를 반환한다."""
    if callable(session_factory):
        candidate = session_factory()
    else:
        candidate = session_factory

    if hasattr(candidate, "__next__"):
        generator = candidate
        session = next(generator)
        return session, generator

    return candidate, None

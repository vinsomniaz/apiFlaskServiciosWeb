from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, RowMapping
from sqlalchemy.exc import SQLAlchemyError

from config import settings

engine: Engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True,
)

@contextmanager
def get_conn():
    conn = engine.connect()
    trans = conn.begin()
    try:
        yield conn
        trans.commit()
    except Exception:
        trans.rollback()
        raise
    finally:
        conn.close()

def fetch_one(sql: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        result = conn.execute(text(sql), params or {})
        row: Optional[RowMapping] = result.mappings().first()
        return dict(row) if row else None

def fetch_all(sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        result = conn.execute(text(sql), params or {})
        rows = result.mappings().all()
        return [dict(r) for r in rows]

def execute(sql: str, params: Optional[Dict[str, Any]] = None) -> int:
    with get_conn() as conn:
        res = conn.execute(text(sql), params or {})
        return int(res.rowcount or 0)

def execute_returning_id(sql: str, params: Optional[Dict[str, Any]] = None) -> int:
    with get_conn() as conn:
        res = conn.execute(text(sql), params or {})
        last_id = getattr(res, "lastrowid", None)
        if last_id is None:
            row = conn.execute(text("SELECT LAST_INSERT_ID() AS id")).mappings().first()
            return int(row["id"])
        return int(last_id)

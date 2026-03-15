from typing import Any

import psycopg2
import psycopg2.extras


class DbClient:
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self._conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=database,
            user=user,
            password=password,
        )
        self._conn.autocommit = True

    def close(self) -> None:
        self._conn.close()

    def execute_query(self, query: str, params: tuple[Any, ...] | None = None) -> None:
        with self._conn.cursor() as cur:
            cur.execute(query, params)

    def fetch_one(self, query: str, params: tuple[Any, ...] | None = None) -> dict[str, Any] | None:
        with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            row = cur.fetchone()
            return dict(row) if row else None

    def fetch_all(self, query: str, params: tuple[Any, ...] | None = None) -> list[dict[str, Any]]:
        with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            return [dict(r) for r in rows]

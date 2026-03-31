from __future__ import annotations

from collections import Counter
from decimal import Decimal

import psycopg2
from psycopg2.extras import RealDictCursor


DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "dbname": "qa_test",
    "user": "qa_user",
    "password": "qa_password",
}


class DbClient:
    def __init__(self, **connection_kwargs) -> None:
        self.connection = psycopg2.connect(cursor_factory=RealDictCursor, **connection_kwargs)
        self.connection.autocommit = True

    def close(self) -> None:
        self.connection.close()

    def fetch_one(self, query: str, params: tuple | None = None) -> dict | None:
        with self.connection.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()

    def fetch_all(self, query: str, params: tuple | None = None) -> list[dict]:
        with self.connection.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()

    def execute(self, query: str, params: tuple | None = None) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(query, params or ())

    def get_finding_by_id(self, finding_id: int) -> dict | None:
        return self.fetch_one(
            """
            SELECT id, asset_id, vulnerability_id, status, detected_at, resolved_at, scanner, notes, is_dismissed
            FROM findings
            WHERE id = %s
            """,
            (finding_id,),
        )

    def get_finding_detail_by_id(self, finding_id: int) -> dict | None:
        return self.fetch_one(
            """
            SELECT
                f.id,
                f.asset_id,
                f.vulnerability_id,
                f.status,
                f.detected_at,
                f.resolved_at,
                f.scanner,
                f.notes,
                f.is_dismissed,
                a.hostname AS asset_hostname,
                v.id AS vuln_id,
                v.cve_id,
                v.title,
                v.description,
                v.severity,
                v.cvss_score,
                v.published_date,
                v.created_at
            FROM findings f
            LEFT JOIN assets a ON f.asset_id = a.id
            LEFT JOIN vulnerabilities v ON f.vulnerability_id = v.id
            WHERE f.id = %s
            """,
            (finding_id,),
        )

    def get_asset_by_id(self, asset_id: int) -> dict | None:
        return self.fetch_one(
            """
            SELECT id, hostname, ip_address, asset_type, environment, os, is_active, created_at
            FROM assets
            WHERE id = %s
            """,
            (asset_id,),
        )

    def get_vulnerability_by_id(self, vulnerability_id: int) -> dict | None:
        return self.fetch_one(
            """
            SELECT id, cve_id, title, description, severity, cvss_score, published_date, created_at
            FROM vulnerabilities
            WHERE id = %s
            """,
            (vulnerability_id,),
        )

    def get_scan_by_id(self, scan_id: int) -> dict | None:
        return self.fetch_one(
            """
            SELECT id, asset_id, scanner_name, status, started_at, completed_at, findings_count
            FROM scans
            WHERE id = %s
            """,
            (scan_id,),
        )

    def get_findings_page(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        status: str | None = None,
        severity: str | None = None,
        asset_id: int | None = None,
    ) -> dict:
        where_clauses = ["f.is_dismissed = FALSE"]
        params: list = []

        if status:
            where_clauses.append("f.status = %s")
            params.append(status)
        if asset_id:
            where_clauses.append("f.asset_id = %s")
            params.append(asset_id)
        if severity:
            where_clauses.append("v.severity = %s")
            params.append(severity)

        where_sql = " AND ".join(where_clauses)

        total = self.fetch_one(
            f"""
            SELECT COUNT(*) AS count
            FROM findings f
            LEFT JOIN vulnerabilities v ON f.vulnerability_id = v.id
            WHERE {where_sql}
            """,
            tuple(params),
        )["count"]

        items = self.fetch_all(
            f"""
            SELECT f.id, f.asset_id, f.vulnerability_id, f.status, f.detected_at, f.resolved_at, f.scanner, f.notes, f.is_dismissed
            FROM findings f
            LEFT JOIN vulnerabilities v ON f.vulnerability_id = v.id
            WHERE {where_sql}
            ORDER BY f.id DESC
            OFFSET %s LIMIT %s
            """,
            tuple(params + [(page - 1) * per_page, per_page]),
        )

        return {"items": items, "total": total, "page": page, "per_page": per_page}

    def search_findings_from_db(self, query: str) -> list[dict]:
        if not query:
            return []
        return self.fetch_all(
            """
            SELECT
                f.id AS finding_id,
                f.status,
                f.scanner,
                v.cve_id,
                v.severity,
                a.hostname
            FROM findings f
            JOIN vulnerabilities v ON f.vulnerability_id = v.id
            JOIN assets a ON f.asset_id = a.id
            WHERE v.cve_id LIKE %s
               OR a.hostname LIKE %s
               OR f.notes LIKE %s
            """,
            (f"%{query}%", f"%{query}%", f"%{query}%"),
        )

    def list_vulnerabilities_from_db(self, severity: str | None = None) -> list[dict]:
        if severity:
            return self.fetch_all(
                """
                SELECT id, cve_id, title, description, severity, cvss_score, published_date, created_at
                FROM vulnerabilities
                WHERE severity = %s
                ORDER BY cvss_score DESC
                """,
                (severity,),
            )
        return self.fetch_all(
            """
            SELECT id, cve_id, title, description, severity, cvss_score, published_date, created_at
            FROM vulnerabilities
            ORDER BY cvss_score DESC
            """
        )

    def list_assets_from_db(
        self,
        *,
        page: int = 1,
        per_page: int = 10,
        environment: str | None = None,
        asset_type: str | None = None,
    ) -> dict:
        where_clauses = ["is_active = TRUE"]
        params: list = []
        if environment:
            where_clauses.append("environment = %s")
            params.append(environment)
        if asset_type:
            where_clauses.append("asset_type = %s")
            params.append(asset_type)
        where_sql = " AND ".join(where_clauses)

        total = self.fetch_one(
            f"SELECT COUNT(*) AS count FROM assets WHERE {where_sql}",
            tuple(params),
        )["count"]
        items = self.fetch_all(
            f"""
            SELECT id, hostname, ip_address, asset_type, environment, os, is_active, created_at
            FROM assets
            WHERE {where_sql}
            ORDER BY id
            OFFSET %s LIMIT %s
            """,
            tuple(params + [(page - 1) * per_page, per_page]),
        )
        pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        return {"items": items, "total": total, "page": page, "per_page": per_page, "pages": pages}

    def list_scans_from_db(
        self,
        *,
        page: int = 1,
        per_page: int = 10,
        asset_id: int | None = None,
    ) -> dict:
        params: list = []
        where_sql = ""
        if asset_id:
            where_sql = "WHERE asset_id = %s"
            params.append(asset_id)

        total = self.fetch_one(
            f"SELECT COUNT(*) AS count FROM scans {where_sql}",
            tuple(params),
        )["count"]
        items = self.fetch_all(
            f"""
            SELECT id, asset_id, scanner_name, status, started_at, completed_at, findings_count
            FROM scans
            {where_sql}
            ORDER BY id DESC
            OFFSET %s LIMIT %s
            """,
            tuple(params + [(page - 1) * per_page, per_page]),
        )
        return {"items": items, "total": total, "page": page, "per_page": per_page}

    def count_findings_for_asset_and_vulnerabilities(self, asset_id: int, vulnerability_ids: list[int]) -> int:
        return self.fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM findings
            WHERE asset_id = %s
              AND vulnerability_id = ANY(%s)
            """,
            (asset_id, vulnerability_ids),
        )["count"]

    def get_findings_for_asset_and_vulnerabilities(self, asset_id: int, vulnerability_ids: list[int]) -> list[dict]:
        return self.fetch_all(
            """
            SELECT id, asset_id, vulnerability_id, status, scanner, is_dismissed
            FROM findings
            WHERE asset_id = %s
              AND vulnerability_id = ANY(%s)
            ORDER BY id DESC
            """,
            (asset_id, vulnerability_ids),
        )

    def get_summary_from_db(self) -> dict:
        findings = self.fetch_all(
            """
            SELECT status
            FROM findings
            WHERE is_dismissed = FALSE
            """
        )

        status_counter = Counter(row["status"] for row in findings)

        severity_rows = self.fetch_all(
            """
            SELECT v.severity, COUNT(f.id) AS count
            FROM findings f
            JOIN vulnerabilities v ON f.vulnerability_id = v.id
            WHERE f.is_dismissed = FALSE
              AND f.status NOT IN ('resolved', 'false_positive')
            GROUP BY v.severity
            """
        )

        environment_rows = self.fetch_all(
            """
            SELECT a.environment, COUNT(f.id) AS count
            FROM findings f
            JOIN assets a ON f.asset_id = a.id
            WHERE f.is_dismissed = FALSE
              AND f.status NOT IN ('resolved', 'false_positive')
            GROUP BY a.environment
            """
        )

        return {
            "total_findings": len(findings),
            "open_findings": status_counter.get("open", 0),
            "confirmed_findings": status_counter.get("confirmed", 0),
            "in_progress_findings": status_counter.get("in_progress", 0),
            "resolved_findings": status_counter.get("resolved", 0),
            "false_positive_findings": status_counter.get("false_positive", 0),
            "by_severity": {row["severity"]: row["count"] for row in severity_rows},
            "by_environment": {row["environment"]: row["count"] for row in environment_rows},
        }

    def get_risk_score_from_db(self) -> dict:
        rows = self.fetch_all(
            """
            SELECT v.severity, v.cvss_score
            FROM findings f
            JOIN vulnerabilities v ON f.vulnerability_id = v.id
            WHERE f.is_dismissed = FALSE
              AND f.status NOT IN ('resolved', 'false_positive')
            """
        )

        if not rows:
            return {
                "risk_score": Decimal("0.0"),
                "total_findings": 0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "average_cvss": Decimal("0.0"),
            }

        critical = high = medium = low = 0
        total_cvss = Decimal("0.0")

        for row in rows:
            cvss = row["cvss_score"]
            if cvss is not None:
                total_cvss += Decimal(str(cvss))

            if row["severity"] == "critical":
                critical += 1
            elif row["severity"] == "high":
                high += 1
            elif row["severity"] == "medium":
                medium += 1
            elif row["severity"] == "low":
                low += 1

        total = len(rows)
        average_cvss = total_cvss / Decimal(str(total))
        weighted = (
            Decimal(str(critical)) * Decimal("4.0")
            + Decimal(str(high)) * Decimal("3.0")
            + Decimal(str(medium)) * Decimal("2.0")
            + Decimal(str(low)) * Decimal("1.0")
        )
        max_possible = Decimal(str(total)) * Decimal("4.0")
        risk_score = (weighted / max_possible) * Decimal("10.0") * (average_cvss / Decimal("10.0"))

        return {
            "risk_score": risk_score,
            "total_findings": total,
            "critical_count": critical,
            "high_count": high,
            "medium_count": medium,
            "low_count": low,
            "average_cvss": average_cvss,
        }

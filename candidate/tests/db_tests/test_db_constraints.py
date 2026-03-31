import pytest
import psycopg2

from tests.db_tests.base_db_test import BaseDbTest


class TestDbConstraints(BaseDbTest):
    def test_required_columns_are_not_nullable(self):
        rows = self.db_client.fetch_all(
            """
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND (
                    (table_name = 'findings' AND column_name IN ('asset_id', 'vulnerability_id', 'status')) OR
                    (table_name = 'vulnerabilities' AND column_name IN ('cve_id', 'title', 'severity')) OR
                    (table_name = 'assets' AND column_name IN ('hostname', 'asset_type', 'environment')) OR
                    (table_name = 'scans' AND column_name IN ('asset_id', 'scanner_name', 'status'))
                  )
              AND is_nullable = 'NO'
            ORDER BY table_name, column_name
            """
        )

        actual = {(row["table_name"], row["column_name"]) for row in rows}
        expected = {
            ("findings", "asset_id"),
            ("findings", "vulnerability_id"),
            ("findings", "status"),
            ("vulnerabilities", "cve_id"),
            ("vulnerabilities", "title"),
            ("vulnerabilities", "severity"),
            ("assets", "hostname"),
            ("assets", "asset_type"),
            ("assets", "environment"),
            ("scans", "asset_id"),
            ("scans", "scanner_name"),
            ("scans", "status"),
        }

        assert actual == expected

    def test_vulnerabilities_cve_id_has_unique_constraint(self):
        rows = self.db_client.fetch_all(
            """
            SELECT c.conname, pg_get_constraintdef(c.oid) AS definition
            FROM pg_constraint c
            JOIN pg_class t ON c.conrelid = t.oid
            WHERE t.relname = 'vulnerabilities'
              AND c.contype IN ('u', 'p')
            """
        )

        definitions = " ".join(row["definition"] for row in rows)

        assert "UNIQUE (cve_id)" in definitions or "PRIMARY KEY (id)" in definitions
        assert "UNIQUE (cve_id)" in definitions

    def test_findings_and_scans_have_foreign_key_constraints(self):
        rows = self.db_client.fetch_all(
            """
            SELECT t.relname AS table_name, pg_get_constraintdef(c.oid) AS definition
            FROM pg_constraint c
            JOIN pg_class t ON c.conrelid = t.oid
            WHERE t.relname IN ('findings', 'scans')
              AND c.contype = 'f'
            ORDER BY t.relname
            """
        )

        definitions = {(row["table_name"], row["definition"]) for row in rows}

        assert any(
            table_name == "findings" and "FOREIGN KEY (asset_id) REFERENCES assets(id)" in definition
            for table_name, definition in definitions
        )
        assert any(
            table_name == "findings" and "FOREIGN KEY (vulnerability_id) REFERENCES vulnerabilities(id)" in definition
            for table_name, definition in definitions
        )
        assert any(
            table_name == "scans" and "FOREIGN KEY (asset_id) REFERENCES assets(id)" in definition
            for table_name, definition in definitions
        )

    def test_inserting_vulnerability_without_required_fields_is_rejected(self):
        with pytest.raises(psycopg2.Error):
            self.db_client.execute(
                """
                INSERT INTO vulnerabilities (description, cvss_score)
                VALUES (%s, %s)
                """,
                ("missing required fields", 5.0),
            )

    def test_inserting_vulnerability_with_invalid_cvss_score_is_rejected(self,unique_suffix):
        with pytest.raises(psycopg2.Error):
            self.db_client.execute(
                """
                INSERT INTO vulnerabilities (cve_id, title, severity, cvss_score)
                VALUES (%s, %s, %s, %s)
                """,
                (f"CVE-2999-{unique_suffix[:4]}","Invalid CVSS test","high",11.5),
            )
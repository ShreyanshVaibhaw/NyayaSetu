"""Seed SQLite database from synthetic and reference datasets."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd


DB_PATH = Path("data/nyayasetu.db")


def create_tables(conn: sqlite3.Connection) -> None:
    """Create minimal relational tables used in demo/integration."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS disputes (
            case_id TEXT PRIMARY KEY,
            state TEXT,
            buyer_type TEXT,
            sector TEXT,
            dispute_amount REAL,
            recovery_percentage REAL,
            stage TEXT,
            resolution_days INTEGER
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS case_outcomes (
            case_id TEXT PRIMARY KEY,
            settlement_probability REAL,
            recovery_percentage REAL,
            resolution_days REAL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS buyer_profiles (
            buyer_gstin TEXT PRIMARY KEY,
            buyer_name TEXT,
            buyer_type TEXT,
            risk_score REAL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reference_data (
            key TEXT PRIMARY KEY,
            payload TEXT
        )
        """
    )
    conn.commit()


def seed_csv_tables(conn: sqlite3.Connection) -> None:
    """Load synthetic CSVs into relational tables."""
    disputes = pd.read_csv("data/synthetic/disputes.csv")
    disputes[
        ["case_id", "state", "buyer_type", "sector", "dispute_amount", "recovery_percentage", "stage", "resolution_days"]
    ].to_sql("disputes", conn, if_exists="replace", index=False)

    outcomes = pd.read_csv("data/synthetic/case_outcomes.csv")
    outcomes[["case_id", "settlement_probability", "recovery_percentage", "resolution_days"]].to_sql(
        "case_outcomes", conn, if_exists="replace", index=False
    )

    buyers = pd.read_csv("data/synthetic/buyer_profiles.csv")
    buyers[["buyer_gstin", "buyer_name", "buyer_type", "risk_score"]].to_sql(
        "buyer_profiles", conn, if_exists="replace", index=False
    )


def seed_reference_data(conn: sqlite3.Connection) -> None:
    """Store key JSON references in a simple key-value table."""
    refs = {
        "msmed_act_sections": "data/legal/msmed_act_sections.json",
        "rbi_bank_rates": "data/legal/rbi_bank_rates.json",
        "msefc_directory": "data/legal/msefc_directory.json",
    }
    conn.execute("DELETE FROM reference_data")
    for key, path in refs.items():
        payload = Path(path).read_text(encoding="utf-8")
        conn.execute("INSERT INTO reference_data(key, payload) VALUES (?, ?)", (key, payload))
    conn.commit()


def main() -> None:
    """Create DB and seed all available datasets."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        create_tables(conn)
        seed_csv_tables(conn)
        seed_reference_data(conn)
        dispute_count = conn.execute("SELECT COUNT(*) FROM disputes").fetchone()[0]
        print(f"Database seeded at {DB_PATH} with {dispute_count} disputes.")


if __name__ == "__main__":
    main()

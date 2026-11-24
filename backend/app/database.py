"""Store inspection history and job progress in a small SQLite database.
Each operation gets its own connection, which keeps background jobs simple.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from .config import DATA


def now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def connection():
    db = sqlite3.connect(DATA / "imarah.db", timeout=15)
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    finally:
        db.close()


def initialize():
    with connection() as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute(
            "CREATE TABLE IF NOT EXISTS inspections (id TEXT PRIMARY KEY, created_at TEXT NOT NULL, payload TEXT NOT NULL)"
        )
        db.execute(
            "CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, kind TEXT NOT NULL, status TEXT NOT NULL, message TEXT NOT NULL, created_at TEXT NOT NULL)"
        )
        db.execute(
            "UPDATE jobs SET status='failed', message='Server restarted. Please run this task again.' WHERE status IN ('queued','running')"
        )
        for row in db.execute("SELECT id, payload FROM inspections").fetchall():
            item = json.loads(row["payload"])
            if item["status"] in ("queued", "running"):
                item.update(
                    status="failed",
                    error="Server restarted before this inspection finished.",
                )
                db.execute(
                    "UPDATE inspections SET payload=? WHERE id=?",
                    (json.dumps(item), row["id"]),
                )


def save_inspection(item):
    with connection() as db:
        db.execute(
            "INSERT INTO inspections VALUES (?,?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload",
            (item["id"], item["created_at"], json.dumps(item)),
        )


def get_inspection(item_id):
    with connection() as db:
        row = db.execute("SELECT payload FROM inspections WHERE id=?", (item_id,)).fetchone()
        return json.loads(row["payload"]) if row else None


def list_inspections():
    with connection() as db:
        return [
            json.loads(row["payload"])
            for row in db.execute(
                "SELECT payload FROM inspections ORDER BY created_at DESC LIMIT 200"
            )
        ]


def create_job(job_id, kind):
    with connection() as db:
        db.execute(
            "INSERT INTO jobs VALUES (?,?,?,?,?)",
            (job_id, kind, "queued", "Waiting for the local model runner", now()),
        )


def update_job(job_id, status, message):
    with connection() as db:
        db.execute("UPDATE jobs SET status=?, message=? WHERE id=?", (status, message, job_id))


def get_job(job_id):
    with connection() as db:
        row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        return dict(row) if row else None


def pending_count():
    with connection() as db:
        return db.execute(
            "SELECT count(*) FROM jobs WHERE status IN ('queued','running')"
        ).fetchone()[0]

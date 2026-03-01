"""Database utility with PostgreSQL URI support and SQLite fallback."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy import Column, DateTime, String, Text, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

import config

Base = declarative_base()


class DisputeRecord(Base):
    """Persisted dispute case row."""

    __tablename__ = "disputes"

    case_id = Column(String(64), primary_key=True)
    mse_name = Column(String(256), nullable=False)
    buyer_name = Column(String(256), nullable=False)
    state = Column(String(64), nullable=False)
    stage = Column(String(64), nullable=False, default="Filed")
    total_principal = Column(String(32), nullable=False)
    total_claim = Column(String(32), nullable=False)
    payload_json = Column(Text, nullable=False)
    prediction_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


@dataclass
class DatabaseManager:
    """Create SQLAlchemy engines for primary or fallback storage."""

    uri: str = config.POSTGRES_URI
    sqlite_path: str = "data/nyayasetu.db"
    _engine: Optional[Engine] = None
    _session_factory: Optional[sessionmaker] = None

    def get_engine(self) -> Engine:
        """Return live engine, falling back to SQLite if primary unavailable."""
        if self._engine is not None:
            return self._engine

        if self.uri and not self.uri.startswith("sqlite"):
            try:
                engine = create_engine(self.uri, pool_pre_ping=True)
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                self._engine = engine
                Base.metadata.create_all(engine)
                return engine
            except Exception:
                pass

        Path(self.sqlite_path).parent.mkdir(parents=True, exist_ok=True)
        engine = create_engine(f"sqlite:///{self.sqlite_path}", future=True)
        Base.metadata.create_all(engine)
        self._engine = engine
        return engine

    def _get_session(self) -> Session:
        """Get a new database session."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(bind=self.get_engine())
        return self._session_factory()

    def save_dispute(self, dispute, prediction=None) -> None:
        """Persist a DisputeCase (and optional prediction) to the database."""
        session = self._get_session()
        try:
            payload = json.loads(dispute.model_dump_json())
            pred_json = json.loads(prediction.model_dump_json()) if prediction else None

            existing = session.query(DisputeRecord).filter_by(case_id=dispute.case_id).first()
            if existing:
                existing.stage = dispute.current_stage
                existing.total_principal = str(dispute.total_principal)
                existing.total_claim = str(dispute.total_claim)
                existing.payload_json = json.dumps(payload, default=str)
                existing.prediction_json = json.dumps(pred_json, default=str) if pred_json else existing.prediction_json
                existing.updated_at = datetime.utcnow()
            else:
                record = DisputeRecord(
                    case_id=dispute.case_id,
                    mse_name=dispute.mse.enterprise_name,
                    buyer_name=dispute.buyer.buyer_name,
                    state=dispute.msefc_state,
                    stage=dispute.current_stage,
                    total_principal=str(dispute.total_principal),
                    total_claim=str(dispute.total_claim),
                    payload_json=json.dumps(payload, default=str),
                    prediction_json=json.dumps(pred_json, default=str) if pred_json else None,
                )
                session.add(record)
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()

    def load_dispute(self, case_id: str) -> Optional[Dict]:
        """Load a dispute by case_id. Returns dict with 'dispute' and 'prediction' keys."""
        session = self._get_session()
        try:
            record = session.query(DisputeRecord).filter_by(case_id=case_id).first()
            if not record:
                return None
            result = {
                "dispute": json.loads(record.payload_json),
                "prediction": json.loads(record.prediction_json) if record.prediction_json else None,
            }
            return result
        except Exception:
            return None
        finally:
            session.close()

    def list_disputes(self) -> List[Dict]:
        """Return summary list of all saved disputes."""
        session = self._get_session()
        try:
            records = session.query(DisputeRecord).order_by(DisputeRecord.created_at.desc()).all()
            return [
                {
                    "case_id": r.case_id,
                    "mse_name": r.mse_name,
                    "buyer_name": r.buyer_name,
                    "state": r.state,
                    "stage": r.stage,
                    "total_claim": r.total_claim,
                    "created_at": r.created_at.isoformat() if r.created_at else "",
                }
                for r in records
            ]
        except Exception:
            return []
        finally:
            session.close()

    def delete_dispute(self, case_id: str) -> bool:
        """Remove a dispute from the database."""
        session = self._get_session()
        try:
            deleted = session.query(DisputeRecord).filter_by(case_id=case_id).delete()
            session.commit()
            return deleted > 0
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()

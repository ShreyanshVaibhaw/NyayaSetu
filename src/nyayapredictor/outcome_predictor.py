"""Outcome prediction engine for NyayaPredictor."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from src.common.models import CaseOutcomePrediction, DisputeCase
from src.nyayapredictor.feature_engineering import FeatureEngineer

try:
    from catboost import CatBoostRegressor  # type: ignore

    CATBOOST_AVAILABLE = True
except Exception:
    CatBoostRegressor = None
    CATBOOST_AVAILABLE = False


_BUNDLE_CACHE: Dict[str, Dict] = {}


@dataclass
class OutcomePredictor:
    """Predict settlement probability, recovery, timeline, and feature impacts."""

    model_path: Optional[str] = None
    data_path: str = "data/synthetic/case_outcomes.csv"
    feature_engineer: FeatureEngineer = field(default_factory=FeatureEngineer)
    ensemble_size: int = 5

    def __post_init__(self) -> None:
        cache_key = self.model_path or "__default__"
        if cache_key in _BUNDLE_CACHE:
            self.bundle = _BUNDLE_CACHE[cache_key]
        else:
            self.bundle = self._load_or_train_model(self.model_path)
            _BUNDLE_CACHE[cache_key] = self.bundle

    def _generate_fallback_training(self, n: int = 2000) -> pd.DataFrame:
        """Generate fallback training data when CSV is missing or empty."""
        rng = np.random.default_rng(42)
        buyer_types = np.array(["Private Ltd", "Proprietorship", "PSU", "State Govt", "Central Govt", "LLP"])
        sectors = np.array(["Manufacturing", "Services"])
        states = np.array(["Maharashtra", "Gujarat", "Tamil Nadu", "Uttar Pradesh", "Delhi", "Rajasthan", "Karnataka"])

        records = []
        for _ in range(n):
            amount = float(rng.uniform(25000, 5000000))
            overdue = int(rng.integers(25, 730))
            buyer = str(rng.choice(buyer_types))
            sector = str(rng.choice(sectors))
            state = str(rng.choice(states))
            has_agreement = bool(rng.random() < 0.62)
            cross_state = bool(rng.random() < 0.35)

            base_settlement = 0.64
            if buyer in {"PSU", "State Govt", "Central Govt"}:
                base_settlement += 0.12
            if buyer == "Proprietorship":
                base_settlement -= 0.14
            if amount > 1000000:
                base_settlement -= 0.07
            if has_agreement:
                base_settlement += 0.09
            if state == "Maharashtra":
                base_settlement += 0.03
            settlement_prob = float(np.clip(base_settlement + rng.normal(0, 0.07), 0.12, 0.98))

            recovery_pct = float(np.clip(48 + settlement_prob * 48 + rng.normal(0, 6), 15, 100))
            resolution_days = float(
                np.clip(
                    62
                    + (20 if cross_state else 0)
                    + (35 if buyer in {"PSU", "Central Govt", "State Govt"} else 0)
                    + (22 if state == "Uttar Pradesh" else 0)
                    + (-12 if state == "Maharashtra" else 0)
                    + rng.normal(0, 14),
                    28,
                    320,
                )
            )

            records.append(
                {
                    "dispute_amount": amount,
                    "days_overdue": overdue,
                    "invoice_count": int(rng.integers(1, 8)),
                    "has_agreement": has_agreement,
                    "agreed_credit_days": 45 if has_agreement else 0,
                    "interest_amount": amount * 0.08,
                    "buyer_type": buyer,
                    "sector": sector,
                    "state": state,
                    "buyer_gst_compliant": bool(rng.random() < 0.82),
                    "cross_state": cross_state,
                    "settlement_probability": settlement_prob,
                    "recovery_percentage": recovery_pct,
                    "resolution_days": resolution_days,
                }
            )
        return pd.DataFrame(records)

    def _train_single_model(self, X: pd.DataFrame, y: pd.Series, random_seed: int, categorical_cols: List[str]):
        if CATBOOST_AVAILABLE:
            model = CatBoostRegressor(
                iterations=500,
                learning_rate=0.05,
                depth=6,
                verbose=False,
                random_seed=random_seed,
            )
            cat_features = [X.columns.get_loc(c) for c in categorical_cols if c in X.columns]
            model.fit(X, y, cat_features=cat_features)
            return model
        model = RandomForestRegressor(n_estimators=300, random_state=random_seed)
        model.fit(pd.get_dummies(X, drop_first=False), y)
        return model

    def _predict_model(self, model, X: pd.DataFrame, feature_columns: List[str]):
        if CATBOOST_AVAILABLE and model.__class__.__name__.lower().startswith("catboost"):
            return float(model.predict(X)[0])
        x_enc = pd.get_dummies(X, drop_first=False)
        for col in feature_columns:
            if col not in x_enc.columns:
                x_enc[col] = 0
        x_enc = x_enc[feature_columns]
        return float(model.predict(x_enc)[0])

    def _load_or_train_model(self, model_path: Optional[str]):
        """Load trained bundle or train regressors from synthetic case data."""
        if model_path and Path(model_path).exists():
            return joblib.load(model_path)

        source_path = Path(self.data_path)
        if source_path.exists():
            data = pd.read_csv(source_path)
            if data.empty or len(data.columns) <= 2:
                data = self._generate_fallback_training()
        else:
            data = self._generate_fallback_training()
        if len(data) < 2000:
            extra = self._generate_fallback_training(n=2000 - len(data))
            data = pd.concat([data, extra], ignore_index=True)

        feature_df = self.feature_engineer.prepare_training_data(data.to_dict(orient="records"))
        target_cols = ["settlement_probability", "recovery_percentage", "resolution_days"]
        X = feature_df.drop(columns=target_cols)
        y = feature_df[target_cols]
        categorical_cols = [col for col in X.columns if str(X[col].dtype) in {"object", "category"}]

        settlement_models = [
            self._train_single_model(X, y["settlement_probability"], random_seed=42 + i, categorical_cols=categorical_cols)
            for i in range(self.ensemble_size)
        ]
        recovery_model = self._train_single_model(X, y["recovery_percentage"], random_seed=67, categorical_cols=categorical_cols)
        timeline_model = self._train_single_model(X, y["resolution_days"], random_seed=91, categorical_cols=categorical_cols)

        rf_feature_columns = list(pd.get_dummies(X, drop_first=False).columns)
        bundle = {
            "models": {
                "settlement_ensemble": settlement_models,
                "recovery": recovery_model,
                "timeline": timeline_model,
            },
            "feature_columns": list(X.columns),
            "categorical_columns": categorical_cols,
            "rf_feature_columns": rf_feature_columns,
        }

        if model_path:
            Path(model_path).parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(bundle, model_path)
        return bundle

    def _prepare_input(self, dispute: DisputeCase) -> pd.DataFrame:
        features = self.feature_engineer.extract_features(dispute)
        X = pd.DataFrame([features])
        for col in self.bundle["feature_columns"]:
            if col not in X.columns:
                X[col] = 0
        return X[self.bundle["feature_columns"]]

    def _feature_contributions(self, X: pd.DataFrame) -> List[Dict]:
        """Compute top feature contributions using SHAP when available."""
        model = self.bundle["models"]["settlement_ensemble"][0]
        try:
            import shap  # type: ignore

            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X)
            values = shap_values[0] if isinstance(shap_values, (list, np.ndarray)) else shap_values
            names = list(X.columns)
            pairs = [{"feature": names[i], "impact": float(values[i])} for i in range(len(names))]
            pairs.sort(key=lambda row: abs(row["impact"]), reverse=True)
            return pairs[:5]
        except Exception:
            # Fallback pseudo-contribution using feature importance and normalized feature value.
            if hasattr(model, "feature_importances_"):
                importances = np.asarray(model.feature_importances_, dtype=float)
                names = list(X.columns)
                scores = []
                row = X.iloc[0].to_dict()
                for idx, name in enumerate(names):
                    value = row.get(name, 0)
                    numeric = float(value) if isinstance(value, (int, float, np.integer, np.floating, bool)) else 0.5
                    centered = numeric - 0.5
                    scores.append({"feature": name, "impact": float(importances[idx] * centered)})
                scores.sort(key=lambda row: abs(row["impact"]), reverse=True)
                return scores[:5]
        return []

    def predict(self, dispute: DisputeCase, similar_cases: Optional[List[Dict]] = None) -> CaseOutcomePrediction:
        """Predict outcome for a new dispute."""
        X = self._prepare_input(dispute)
        settlement_preds = [
            self._predict_model(model, X, self.bundle["rf_feature_columns"]) for model in self.bundle["models"]["settlement_ensemble"]
        ]
        settlement_probability = float(np.mean(settlement_preds))
        settlement_std = float(np.std(settlement_preds))

        recovery_percentage = self._predict_model(self.bundle["models"]["recovery"], X, self.bundle["rf_feature_columns"])
        timeline_days = self._predict_model(self.bundle["models"]["timeline"], X, self.bundle["rf_feature_columns"])

        settlement_probability = float(np.clip(settlement_probability, 0.01, 0.99))
        recovery_percentage = float(np.clip(recovery_percentage, 5, 100))
        estimated_days = int(np.clip(timeline_days, 20, 365))

        if dispute.total_claim > 1000000:
            settlement_probability -= 0.04
            estimated_days += 18
        if dispute.has_written_agreement:
            settlement_probability += 0.05
            recovery_percentage += 3
        if dispute.buyer.buyer_type in {"PSU", "Central Govt", "State Govt"}:
            settlement_probability += 0.04
            estimated_days += 12
        if dispute.buyer.state != dispute.mse.state:
            estimated_days += 10

        similar_case_summary = None
        if similar_cases:
            avg_sim_recovery = float(np.mean([float(c.get("recovery_percentage", 0)) for c in similar_cases]))
            avg_sim_days = float(np.mean([float(c.get("resolution_days", estimated_days)) for c in similar_cases]))
            similar_case_summary = (
                f"In {len(similar_cases)} similar cases, average recovery was {avg_sim_recovery:.1f}% "
                f"with {avg_sim_days:.0f} days resolution."
            )
            if abs(avg_sim_recovery - recovery_percentage) > 12:
                if avg_sim_recovery < recovery_percentage:
                    recovery_percentage -= 5
                else:
                    recovery_percentage += 4

        settlement_probability = float(np.clip(settlement_probability, 0.01, 0.99))
        recovery_percentage = float(np.clip(recovery_percentage, 5, 100))
        estimated_days = int(np.clip(estimated_days, 20, 365))
        predicted_amount = round(dispute.total_claim * (recovery_percentage / 100.0), 2)

        if settlement_probability >= 0.8:
            strategy = "negotiate"
        elif settlement_probability >= 0.5:
            strategy = "escalate_msefc"
        else:
            strategy = "arbitration"

        contributions = self._feature_contributions(X)
        favorable = [f"{c['feature']} supports settlement (+{abs(c['impact']):.3f})" for c in contributions if c["impact"] > 0][:3]
        risks = [f"{c['feature']} increases friction ({c['impact']:.3f})" for c in contributions if c["impact"] < 0][:3]
        if not favorable and dispute.has_written_agreement:
            favorable.append("Written agreement improves enforceability.")
        if not risks and dispute.total_claim > 1000000:
            risks.append("High claim amount can increase negotiation timeline.")

        confidence = float(np.clip(1.0 - (settlement_std * 3.5), 0.45, 0.98))
        if similar_cases and similar_case_summary and abs(np.mean([c.get("recovery_percentage", 0) for c in similar_cases]) - recovery_percentage) > 12:
            risks.append(
                f"Model vs similar-case divergence detected. {similar_case_summary} Review documentation strength."
            )

        return CaseOutcomePrediction(
            case_id=dispute.case_id,
            settlement_probability=round(settlement_probability, 4),
            predicted_recovery_percentage=round(recovery_percentage, 2),
            predicted_recovery_amount=predicted_amount,
            estimated_days_to_resolution=estimated_days,
            recommended_strategy=strategy,
            confidence=round(confidence, 4),
            similar_cases=similar_cases or [],
            risk_factors=risks or ["General litigation timeline uncertainty."],
            favorable_factors=favorable or ["Statutory MSMED framework supports delayed payment claims."],
            feature_contributions=contributions,
            similar_case_summary=similar_case_summary,
        )

    def get_confidence_interval(self, prediction: CaseOutcomePrediction) -> Dict:
        """Return optimistic/expected/pessimistic projection ranges."""
        expected = prediction.predicted_recovery_amount
        spread = max(0.08, min(0.25, 1 - prediction.confidence))
        return {
            "optimistic": round(expected * (1 + spread), 2),
            "expected": round(expected, 2),
            "pessimistic": round(expected * (1 - spread), 2),
            "days_range": {
                "optimistic": max(15, int(prediction.estimated_days_to_resolution * 0.8)),
                "expected": int(prediction.estimated_days_to_resolution),
                "pessimistic": int(prediction.estimated_days_to_resolution * 1.35),
            },
        }

    def explain_prediction(self, dispute: DisputeCase, prediction: CaseOutcomePrediction) -> str:
        """Provide human-readable rationale for model output."""
        top_pos = [c for c in prediction.feature_contributions if c.get("impact", 0) > 0][:2]
        top_neg = [c for c in prediction.feature_contributions if c.get("impact", 0) < 0][:2]
        pos_text = ", ".join(row["feature"] for row in top_pos) if top_pos else "written agreement support"
        neg_text = ", ".join(row["feature"] for row in top_neg) if top_neg else "claim size and delay profile"
        return (
            f"Predicted settlement probability is {prediction.settlement_probability * 100:.1f}% for case {dispute.case_id}. "
            f"Positive drivers: {pos_text}. Risk drivers: {neg_text}. "
            f"Expected recovery is approximately Rs {prediction.predicted_recovery_amount:,.2f} "
            f"within about {prediction.estimated_days_to_resolution} days."
        )


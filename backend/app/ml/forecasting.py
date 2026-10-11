"""
Revenue & Order-Count Forecasting
===================================
Uses statsmodels SimpleExpSmoothing on monthly aggregates.
Train on 80%, evaluate on remaining 20%, forecast 3 months ahead.

Results are cached in-process for 1 hour.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

try:
    from statsmodels.tsa.holtwinters import SimpleExpSmoothing
    _STATSMODELS_OK = True
except ImportError:
    _STATSMODELS_OK = False

# ---------------------------------------------------------------------------
# In-memory cache
# ---------------------------------------------------------------------------
_CACHE: Dict[str, Dict[str, Any]] = {}
_CACHE_TTL = 3600


def _get_cached(key: str) -> Optional[Any]:
    entry = _CACHE.get(key)
    if entry and (time.time() - entry["timestamp"]) < _CACHE_TTL:
        return entry["data"]
    return None


def _set_cached(key: str, data: Any) -> None:
    _CACHE[key] = {"timestamp": time.time(), "data": data}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_revenue_forecast(db: Session) -> Dict[str, Any]:
    cached = _get_cached("forecast_revenue")
    if cached is not None:
        return cached
    result = _compute_forecast(db, metric="revenue")
    if result.get("status") == "ok":
        _set_cached("forecast_revenue", result)
    return result


def compute_orders_forecast(db: Session) -> Dict[str, Any]:
    cached = _get_cached("forecast_orders")
    if cached is not None:
        return cached
    result = _compute_forecast(db, metric="orders")
    if result.get("status") == "ok":
        _set_cached("forecast_orders", result)
    return result


# ---------------------------------------------------------------------------
# Core computation
# ---------------------------------------------------------------------------

def _compute_forecast(db: Session, metric: str) -> Dict[str, Any]:
    if not _STATSMODELS_OK:
        return {
            "status": "error",
            "message": "statsmodels not available.",
            "forecast": [],
            "historical": [],
        }

    sql = text(
        """
        SELECT
            to_char(o.order_purchase_timestamp, 'YYYY-MM') AS year_month,
            SUM(op.payment_value) AS total_revenue,
            COUNT(DISTINCT o.order_id) AS order_count
        FROM orders o
        JOIN order_payments op ON o.order_id = op.order_id
        WHERE o.order_status NOT IN ('canceled', 'unavailable')
        GROUP BY to_char(o.order_purchase_timestamp, 'YYYY-MM')
        ORDER BY year_month
        """
    )
    rows = db.execute(sql).fetchall()

    if not rows:
        return {
            "status": "no_data",
            "message": "Dataset not loaded.",
            "forecast": [],
            "historical": [],
        }

    df = pd.DataFrame(rows, columns=["year_month", "total_revenue", "order_count"])
    df["total_revenue"] = pd.to_numeric(df["total_revenue"], errors="coerce").fillna(0.0)
    df["order_count"] = pd.to_numeric(df["order_count"], errors="coerce").fillna(0).astype(int)

    if len(df) < 12:
        return {
            "status": "insufficient_data",
            "message": f"Need at least 12 months of data. Found {len(df)}.",
            "forecast": [],
            "historical": [],
        }

    series = df["total_revenue"].values if metric == "revenue" else df["order_count"].values.astype(float)
    months = df["year_month"].tolist()

    # Train/test split (80/20)
    split_idx = max(int(len(series) * 0.8), 1)
    train = series[:split_idx]
    test = series[split_idx:]

    # Fit on train
    model = SimpleExpSmoothing(train, initialization_method="estimated")
    fit = model.fit(optimized=True)

    # Forecast over test period + 3 extra months
    n_forecast = len(test) + 3
    forecast_all = fit.forecast(n_forecast)

    test_pred = forecast_all[: len(test)]
    future_pred = forecast_all[len(test):]

    # Metrics on test set
    if len(test) > 0:
        residuals = test - test_pred
        mae = float(np.mean(np.abs(residuals)))
        rmse = float(np.sqrt(np.mean(residuals ** 2)))
        nonzero = test != 0
        mape = float(np.mean(np.abs(residuals[nonzero] / test[nonzero])) * 100) if nonzero.any() else None
    else:
        mae = rmse = mape = None

    # Confidence bounds: mean ± 1.5 * std of residuals (or ±10% if insufficient data)
    if len(test) > 1:
        residual_std = float(np.std(residuals))
    else:
        residual_std = float(np.mean(np.abs(series))) * 0.1

    # Build future month labels
    last_month_dt = pd.to_datetime(months[-1] + "-01")
    future_months = [
        (last_month_dt + pd.DateOffset(months=i + 1)).strftime("%Y-%m")
        for i in range(3)
    ]

    forecast_points = []
    for i, (month, val) in enumerate(zip(future_months, future_pred)):
        forecast_points.append(
            {
                "period": month,
                "forecast": round(float(val), 2),
                "lower_bound": round(float(max(0.0, val - 1.5 * residual_std)), 2),
                "upper_bound": round(float(val + 1.5 * residual_std), 2),
            }
        )

    historical = [
        {"period": m, "value": round(float(v), 2)}
        for m, v in zip(months, series)
    ]

    return {
        "status": "ok",
        "message": "",
        "metric": metric,
        "mae": round(mae, 2) if mae is not None else None,
        "rmse": round(rmse, 2) if rmse is not None else None,
        "mape": round(mape, 2) if mape is not None else None,
        "forecast": forecast_points,
        "historical": historical,
    }

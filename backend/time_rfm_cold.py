"""Temporary script: measure cold-start RFM timing. Delete after use."""
import sys, time
sys.path.insert(0, '/app')

from app.analytics import rfm as rfm_mod
from app.db.session import SessionLocal

# Clear the cache
rfm_mod._CACHE.clear()
print("Cache cleared")

db = SessionLocal()
try:
    t0 = time.time()
    result = rfm_mod.compute_rfm(db)
    elapsed = round((time.time() - t0) * 1000)
    status = result.get("status")
    total = result.get("total_customers")
    segs = len(result.get("segments", result.get("data", [])))
    print(f"Cold-start RFM: {elapsed}ms | status={status} | customers={total} | segments={segs}")

    # Warm cache hit
    t1 = time.time()
    result2 = rfm_mod.compute_rfm(db)
    elapsed2 = round((time.time() - t1) * 1000)
    print(f"Warm-cache RFM: {elapsed2}ms")
finally:
    db.close()

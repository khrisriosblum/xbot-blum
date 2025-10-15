
from fastapi import APIRouter
from datetime import datetime, timedelta, date, time as dtime
from typing import List
import pytz, random, traceback
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from .settings import settings
from .excel_loader import load_candidates
from .queue_manager import select_candidate_for_slot, compose_text
from .poster import post_to_x
from .storage import storage

router = APIRouter()
scheduler = BackgroundScheduler(timezone=settings.TIMEZONE)

POST_SLOTS = [s.strip() for s in settings.POST_TIMES.split(",") if s.strip()]

def _today_local() -> date:
    tz = pytz.timezone(settings.TIMEZONE)
    return datetime.now(tz).date()

def _localize(dt: datetime) -> datetime:
    tz = pytz.timezone(settings.TIMEZONE)
    return tz.localize(dt) if dt.tzinfo is None else dt.astimezone(tz)

def _randomized_time(base_time_str: str, day: date) -> datetime:
    hh, mm = map(int, base_time_str.split(":"))
    base = datetime(day.year, day.month, day.day, hh, mm, 0)
    # +/- jitter minutes
    jitter = settings.JITTER_MINUTES
    delta = random.randint(-jitter, jitter)
    dt = base + timedelta(minutes=delta)
    return _localize(dt)

def plan_today_jobs():
    today = _today_local()
    # Load candidates every day to reflect growth in the Excel
    try:
        cands_sheet1, cands_sc, cands_st = load_candidates()
    except Exception as e:
        print("ERROR loading Excel:", e)
        cands_sheet1, cands_sc, cands_st = [], [], []

    for slot in POST_SLOTS:
        run_at = _randomized_time(slot, today)
        # Skip slots already in the past (avoid backfilling on resume)
        now_local = _localize(datetime.now())
        if run_at <= now_local:
            print(f"Skipping {slot} for {today} because run time {run_at.isoformat()} is in the past")
            continue
        run_id = storage.add_run(run_date=str(today), slot_label=slot, scheduled_at=run_at.isoformat())
        scheduler.add_job(execute_slot, trigger=DateTrigger(run_date=run_at),
                          args=[run_id, slot, today, cands_sheet1, cands_sc, cands_st],
                          name=f"post_{slot}_{today.isoformat()}")
        print(f"Planned {slot} at {run_at.isoformat()} (run_id={run_id})")

def execute_slot(run_id: int, slot_label: str, today: date, cands_sheet1, cands_sc, cands_st):
    try:
        # Select candidate according to rules
        cand = select_candidate_for_slot(slot_label, cands_sheet1, cands_sc, cands_st, today)
        if not cand:
            storage.update_run(run_id, status="skipped", executed_at=datetime.utcnow().isoformat(), error="No hay candidatos disponibles (tras dedup/filtrado)")
            print("No candidate available for", slot_label)
            return

        text = compose_text(cand)
        # Post with pre-wait handled inside poster
        result = post_to_x(text)
        if result.get("status") in ("ok", "dry_run"):
            storage.record_post(url=cand.url, sheet=cand.sheet, col=cand.col, row=cand.row, title=getattr(cand, "title", "") or (getattr(cand, "track_title","") or ""))
            storage.update_run(run_id, status="success", executed_at=datetime.utcnow().isoformat(), selected_url=cand.url)
            print(f"Posted ({result.get('status')}): {cand.url}")
        else:
            storage.update_run(run_id, status="error", executed_at=datetime.utcnow().isoformat(), selected_url=cand.url, error=result.get("error","unknown"))
            print("Post error:", result.get("error"))
    except Exception as e:
        storage.update_run(run_id, status="error", executed_at=datetime.utcnow().isoformat(), error=str(e))
        traceback.print_exc()

@router.get("/queue")
def get_queue_preview():
    """Quick view of recently planned runs."""
    return {"runs": storage.list_runs(100)}

@router.get("/history")
def get_history():
    return {"posts": storage.list_recent_posts(200)}

def start_scheduler():
    if not scheduler.running:
        scheduler.start()
    # Plan today's posts shortly after boot
    plan_today_jobs()
    # Re-plan every midnight
    tz = pytz.timezone(settings.TIMEZONE)
    # Plan tomorrow at 00:01 local
    tomorrow = _today_local() + timedelta(days=1)
    at = tz.localize(datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 1))
    scheduler.add_job(plan_today_jobs, trigger=DateTrigger(run_date=at), name="plan_tomorrow")

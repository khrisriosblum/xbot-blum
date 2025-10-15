
from datetime import datetime, timedelta, date
from typing import List, Optional, Tuple
import random
from .models import Candidate
from .settings import settings
from .storage import storage
from .hashtags import SHEET1_HASHTAGS, SOUNDCLOUD_HASHTAGS, SPOTIFYTOPS_HASHTAGS, RECENT_TAGS

def _is_recent(iso_date: Optional[str]) -> bool:
    if not iso_date:
        return False
    try:
        d = datetime.strptime(iso_date, "%Y-%m-%d").date()
        return (date.today() - d).days <= settings.RECENT_DAYS
    except Exception:
        return False

def _dedup_ok(url: str) -> bool:
    return not storage.was_posted_within_days(url, settings.DEDUP_DAYS)

def pick_for_special(sheet_type: str, cands_sc: List[Candidate], cands_st: List[Candidate]) -> Optional[Candidate]:
    pool = cands_sc if sheet_type == "soundcloud" else cands_st
    pool = [c for c in pool if _dedup_ok(c.url)]
    if not pool:
        return None
    recents = [c for c in pool if _is_recent(c.release_date)]
    return random.choice(recents) if recents else random.choice(pool)

def pick_for_sheet1(cands_sheet1: List[Candidate]) -> Optional[Candidate]:
    pool = [c for c in cands_sheet1 if _dedup_ok(c.url)]
    if not pool:
        return None
    recents = [c for c in pool if _is_recent(c.release_date)]
    return random.choice(recents) if recents else random.choice(pool)

def day_index(today: date) -> int:
    base = datetime.strptime(settings.START_DATE, "%Y-%m-%d").date()
    return (today - base).days + 1

def compose_text(cand: Candidate) -> str:
    # Prefix hashtags if recent
    recent_prefix = []
    if cand.source.startswith("sheet1"):
        if _is_recent(cand.release_date):
            recent_prefix = RECENT_TAGS["sheet1"]
        if cand.source == "sheet1_youtube":
            # "Techouse on Youtube For You!" + 3 Sheet1Hashtags + C Artist + D TrackTitle + E Mix + URL
            hash3 = " ".join(random.sample(SHEET1_HASHTAGS, 3))
            parts = ["Techouse on Youtube For You!", hash3]
        elif cand.source == "sheet1_apple":
            # "Music ON Apple" + 3 SoundcloudHashtags + fields + URL (per spec literal)
            hash3 = " ".join(random.sample(SOUNDCLOUD_HASHTAGS, 3))
            parts = ["Music ON Apple", hash3]
        else: # sheet1_spotify
            # "Listening Techouse On Spotify" + 3 SpotifyTopsHashtags + fields + URL
            hash3 = " ".join(random.sample(SPOTIFYTOPS_HASHTAGS, 3))
            parts = ["Listening Techouse On Spotify", hash3]
        tail = " ".join(filter(None, [cand.artist, cand.track_title, cand.mix, cand.url]))
        full = " ".join(recent_prefix + parts + [tail])
        return full.strip()

    if cand.source == "soundcloud":
        # recent tags for soundcloud
        if _is_recent(cand.release_date):
            recent_prefix = RECENT_TAGS["soundcloud"]
        parts = ["Long Sets On My Souncloud", cand.url]
        return " ".join(recent_prefix + parts).strip()

    if cand.source == "spotifytops":
        # recent tags for spotifytops
        if _is_recent(cand.release_date):
            recent_prefix = RECENT_TAGS["spotifytops"]
        parts = ["Khris Rios Tops 10", cand.url]
        return " ".join(recent_prefix + parts).strip()

    return cand.url

def select_candidate_for_slot(slot_label: str, cands_sheet1: List[Candidate], cands_sc: List[Candidate], cands_st: List[Candidate], today: date) -> Optional[Candidate]:
    """ slot_label is '12:00' etc. 21:00 has special rules. """
    if slot_label == "21:00":
        di = day_index(today)
        # SpotifyTops priority if both match the same day, as it's rarer
        if settings.SPOTIFY_TOPS_EVERY_N_DAYS and di % settings.SPOTIFY_TOPS_EVERY_N_DAYS == 0:
            cand = pick_for_special("spotifytops", cands_sc, cands_st)
            if cand: return cand
        if settings.SOUND_CLOUD_EVERY_N_DAYS and di % settings.SOUND_CLOUD_EVERY_N_DAYS == 0:
            cand = pick_for_special("soundcloud", cands_sc, cands_st)
            if cand: return cand
        # fallback to sheet1
        return pick_for_sheet1(cands_sheet1)

    # Other hours -> random from Sheet1 with recent priority
    return pick_for_sheet1(cands_sheet1)

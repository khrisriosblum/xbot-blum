
from dataclasses import dataclass
from typing import Optional, Literal, List, Dict

SourceType = Literal["sheet1_youtube", "sheet1_apple", "sheet1_spotify", "soundcloud", "spotifytops"]

@dataclass
class Candidate:
    source: SourceType
    sheet: str
    row: int
    col: str
    url: str
    artist: Optional[str] = None
    track_title: Optional[str] = None
    mix: Optional[str] = None
    release_date: Optional[str] = None  # ISO YYYY-MM-DD
    # extra fields per sheet
    title: Optional[str] = None  # soundcloud title

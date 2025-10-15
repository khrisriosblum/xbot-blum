
import pandas as pd
from typing import List, Tuple
from .models import Candidate
from .settings import settings
import re

def _norm_header(h: str) -> str:
    return re.sub(r'\s+', '', h.strip().lower())

def load_candidates() -> Tuple[List[Candidate], List[Candidate], List[Candidate]]:
    """
    Returns (sheet1_candidates, soundcloud_candidates, spotifytops_candidates)
    Each list contains Candidate objects with proper source + url + metadata.
    """
    path = settings.EXCEL_PATH
    xls = pd.ExcelFile(path, engine="openpyxl")

    sheet1_name = None
    sc_name = None
    st_name = None
    for n in xls.sheet_names:
        ln = n.lower()
        if ln == "sheet1":
            sheet1_name = n
        elif ln == "soundcloud":
            sc_name = n
        elif ln == "spotifytops":
            st_name = n
    if not sheet1_name:
        raise RuntimeError("No se encontró la hoja 'Sheet1' en el Excel.")

    # Sheet1
    df1 = pd.read_excel(xls, sheet1_name)
    # Normalize column indexes by header names
    headers = {_norm_header(c): c for c in df1.columns}
    col_artist = headers.get("artist", "C")
    col_track = headers.get("tracktitle", "D")
    col_mix = headers.get("mix", "E")
    col_youtube = headers.get("youtubeurl", "F")
    col_apple = headers.get("applemusicurl", "G")
    col_spotify = headers.get("spotifyurl", "H")
    col_release = headers.get("releasedate", "K")

    cands_sheet1 = []
    def add_row(row, col_name, source_tag, col_letter):
        url = str(row.get(col_name, "")).strip()
        if url and url.lower().startswith(("http://","https://")):
            cand = Candidate(
                source=source_tag,
                sheet=sheet1_name,
                row=int(row.name)+2,  # assume header row then starts at row 2 like spec
                col=col_letter,
                url=url,
                artist=str(row.get(col_artist,"")).strip(),
                track_title=str(row.get(col_track,"")).strip(),
                mix=str(row.get(col_mix,"")).strip(),
                release_date=str(row.get(col_release,"")).split(" ")[0] if str(row.get(col_release,"")).strip() else None
            )
            cands_sheet1.append(cand)

    for idx, row in df1.iterrows():
        add_row(row, col_youtube, "sheet1_youtube", "F")
        add_row(row, col_apple, "sheet1_apple", "G")
        add_row(row, col_spotify, "sheet1_spotify", "H")

    # Soundcloud
    cands_sc = []
    if sc_name:
        dfsc = pd.read_excel(xls, sc_name)
        sc_headers = {_norm_header(c): c for c in dfsc.columns}
        col_sctitle = sc_headers.get("title", "A")
        col_scurl = sc_headers.get("soundcloudurl", "B")
        col_screl = sc_headers.get("releasedate", "C")
        for idx, row in dfsc.iterrows():
            url = str(row.get(col_scurl,"")).strip()
            if url and url.lower().startswith(("http://","https://")):
                cands_sc.append(Candidate(
                    source="soundcloud",
                    sheet=sc_name,
                    row=int(row.name)+2,
                    col="B",
                    url=url,
                    title=str(row.get(col_sctitle,"")).strip(),
                    release_date=str(row.get(col_screl,"")).split(" ")[0] if str(row.get(col_screl,"")).strip() else None
                ))

    # SpotifyTops
    cands_st = []
    if st_name:
        dfst = pd.read_excel(xls, st_name)
        st_headers = {_norm_header(c): c for c in dfst.columns}
        # Spec conflict: B or C for URL? We'll detect by header name
        col_sturl = st_headers.get("spotifytopsurl", None)
        if col_sturl is None:
            # fallback to column B by position
            col_sturl = dfst.columns[1] if len(dfst.columns) > 1 else dfst.columns[0]
        col_strel = st_headers.get("releasedate", None)
        if col_strel is None:
            # fallback to column C by position if exists
            col_strel = dfst.columns[2] if len(dfst.columns) > 2 else None

        for idx, row in dfst.iterrows():
            url = str(row.get(col_sturl,"")).strip()
            if url and url.lower().startswith(("http://","https://")):
                cands_st.append(Candidate(
                    source="spotifytops",
                    sheet=st_name,
                    row=int(row.name)+2,
                    col="B",
                    url=url,
                    release_date=str(row.get(col_strel,"")).split(" ")[0] if (col_strel and str(row.get(col_strel,"")).strip()) else None
                ))

    return cands_sheet1, cands_sc, cands_st

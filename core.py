# core.py
import os
import math
import unicodedata
from pathlib import Path
from typing import Optional, Literal, Tuple
import pandas as pd

# ----------------------------
# Robust data directory resolver
# ----------------------------
def resolve_data_dir() -> Path:
    env = os.environ.get("KC_DATA_DIR")
    if env:
        p = Path(os.path.expanduser(env))
        if p.exists():
            return p if p.is_dir() else p.parent
    try:
        base = Path(__file__).resolve().parent
    except NameError:
        base = Path(os.getcwd())
    candidates = [
        base / "backend" / "data",
        base / "data",
        Path.cwd() / "backend" / "data",
        Path(r"C:\Users\krupa\Desktop\Bootcamp\project_keiz_connect\kiez_connect\backend\data"),
    ]
    for c in candidates:
        if c.exists():
            return c
    return base / "backend" / "data"

DATA_DIR = resolve_data_dir()

# ----------------------------
# Berlin district centroids
# ----------------------------
DISTRICT_CENTROIDS = {
    "mitte": (52.5200, 13.4050),
    "kreuzberg": (52.4986, 13.4030),
    "neukölln": (52.4751, 13.4386),
    "friedrichshain": (52.5156, 13.4549),
    "charlottenburg": (52.5070, 13.3040),
    "wilmersdorf": (52.4895, 13.3157),
    "schöneberg": (52.4832, 13.3477),
    "tempelhof": (52.4675, 13.4036),
    "pankow": (52.5693, 13.4010),
    "prenzlauer berg": (52.5380, 13.4247),
    "spandau": (52.5511, 13.1999),
    "steglitz": (52.4560, 13.3220),
    "treptow": (52.4816, 13.4764),
    "köpenick": (52.4429, 13.5756),
    "marzahn": (52.5450, 13.5690),
    "hellersdorf": (52.5345, 13.6132),
    "reinickendorf": (52.5870, 13.3260),
    "moabit": (52.5303, 13.3390),
    "wedding": (52.5496, 13.3551),
    "berlin": (52.5200, 13.4050),
}

def _normalize_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    for ch in "-_\\/.,":
        s = s.replace(ch, " ")
    s = "".join(ch for ch in s if ch.isalnum() or ch.isspace())
    return " ".join(part for part in s.split() if part)

_NORMALIZED_DISTRICT_MAP = {_normalize_text(k): k for k in DISTRICT_CENTROIDS.keys()}
DISTRICT_KEYS = sorted(_NORMALIZED_DISTRICT_MAP.keys(), key=len, reverse=True)

def detect_district(text: str) -> Optional[str]:
    if not isinstance(text, str):
        return None
    norm = _normalize_text(text)
    for nd in DISTRICT_KEYS:
        if nd and nd in norm:
            return _NORMALIZED_DISTRICT_MAP.get(nd)
    if "berlin" in norm:
        return "berlin"
    return None

def bake_coords(df_in: pd.DataFrame) -> pd.DataFrame:
    df = df_in.copy()
    if "latitude" not in df.columns:
        df["latitude"] = pd.NA
    if "longitude" not in df.columns:
        df["longitude"] = pd.NA
    if "district" not in df.columns:
        df["district"] = pd.NA

    for i in df.index:
        if pd.isna(df.at[i, "latitude"]) or pd.isna(df.at[i, "longitude"]):
            d = (
                detect_district(str(df.at[i, "district"]))
                or detect_district(str(df.at[i, "location"]))
                or "berlin"
            )
            lat, lon = DISTRICT_CENTROIDS.get(d, DISTRICT_CENTROIDS["berlin"])
            df.at[i, "latitude"] = lat
            df.at[i, "longitude"] = lon
            if pd.isna(df.at[i, "district"]) or not str(df.at[i, "district"]).strip():
                df.at[i, "district"] = d.title()
    return df

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    try:
        r = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c
    except Exception:
        return float("inf")

def _smart_read(path: Path) -> pd.DataFrame:
    for enc in ("utf-8", "latin-1"):
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception:
            pass
    return pd.read_csv(path)

def load_data(data_dir: Path | None = None) -> pd.DataFrame:
    data_dir = Path(data_dir) if data_dir else DATA_DIR

    ev_base = data_dir / "berlin_tech_events.csv"
    ev_geo  = data_dir / (ev_base.stem + "_geo.csv")
    events  = _smart_read(ev_geo if ev_geo.exists() else ev_base)

    jb_base = data_dir / "berlin_tech_jobs.csv"
    jb_geo  = data_dir / (jb_base.stem + "_geo.csv")
    jobs    = _smart_read(jb_geo if jb_geo.exists() else jb_base)

    courses = _smart_read(data_dir / "german_courses_berlin.csv")

    for df, t in [(jobs, "job"), (events, "event"), (courses, "course")]:
        df.columns = [c.strip().lower() for c in df.columns]
        df["type"] = t

    merged = pd.concat([jobs, events, courses], ignore_index=True)
    merged = bake_coords(merged)
    return merged

def search(
    df: pd.DataFrame,
    query: Optional[str] = None,
    topic: Optional[Literal["job","event","course"]] = None,
    district: Optional[str] = None,
    scope: Optional[Literal["all","only","nearby"]] = "all",
    radius_km: float = 3.0,
    use_my_location: bool = False,
    origin_lat: Optional[float] = None,
    origin_lon: Optional[float] = None,
    keyword: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_dir: Optional[Literal["asc","desc"]] = "asc",
) -> pd.DataFrame:
    """
    Server-side version of your Streamlit filtering, including:
    - topic filter
    - district detection + scope ("all", "only", "nearby")
    - nearby radius with optional user coordinates
    - keyword filter
    - optional sort
    """
    subset = df.copy()

    # infer district from query if not provided
    if (not district) and query:
        district = detect_district(query)

    # topic
    if topic and "type" in subset.columns:
        subset = subset[subset["type"].astype(str).str.lower() == topic]

    # keyword detection (fallback to your keyword list if not given)
    if (not keyword) and query:
        keys = ["developer","engineer","data","design","marketing","teacher","python","manager"]
        ql = query.lower()
        keyword = next((k for k in keys if k in ql), None)

    # district + scope
    if district:
        dkey = district.lower()
        if scope == "only":
            subset = subset[
                subset["district"].fillna("").str.lower().str.contains(dkey)
                | subset["location"].fillna("").str.lower().str.contains(dkey)
            ]
        elif scope == "nearby":
            # get origin: either user-provided or district centroid
            if use_my_location and origin_lat is not None and origin_lon is not None:
                lat0, lon0 = float(origin_lat), float(origin_lon)
            else:
                lat0, lon0 = DISTRICT_CENTROIDS.get(dkey, DISTRICT_CENTROIDS["berlin"])
            subset = bake_coords(subset)
            mask = []
            for _, r in subset.iterrows():
                try:
                    lat = float(r.get("latitude", lat0))
                    lon = float(r.get("longitude", lon0))
                    dkm = _haversine_km(lat0, lon0, lat, lon)
                    mask.append(dkm <= float(radius_km))
                except Exception:
                    mask.append(False)
            subset = subset.loc[mask]
        else:
            # 'all' → no filtering by district
            pass

    # explicit keyword filter
    if keyword:
        cols = [c for c in ["title","company","provider","course_name"] if c in subset.columns]
        if cols:
            k = keyword.lower()
            subset = subset[subset[cols].apply(lambda x: x.astype(str).str.lower().str.contains(k).any(), axis=1)]

    # free-text query fallback across many columns
    if query:
        q = query.lower()
        cols = [c for c in ["title","course_name","provider","company","district","location","address"] if c in subset.columns]
        if cols:
            m = subset[cols].apply(lambda x: x.astype(str).str.lower().str.contains(q).any(), axis=1)
            subset = subset[m]

    # ensure coords for clients that map
    subset = bake_coords(subset)

    # optional sorting
    if sort_by and sort_by in subset.columns:
        subset = subset.sort_values(sort_by, ascending=(sort_dir != "desc"))

    return subset

# utils.py
import math, re, unicodedata
import pandas as pd

def to_datetime_safe(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, errors="coerce")

def to_number_safe(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.replace(r"[^0-9\.-]", "", regex=True), errors="coerce")

def format_currency(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "-"
    return f"₩{int(round(float(v))):,}"

def pct(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "-"
    return f"{float(v)*100:.1f}%"

def df_to_html_table(d: pd.DataFrame | None, max_rows: int = 15) -> str:
    if d is None or d.empty:
        return "<p>데이터 없음</p>"
    return d.head(max_rows).to_html(index=False, border=1, justify="center")

def sanitize_filename(s: str) -> str:
    return (
        s.replace("/", "_").replace("\\", "_").replace(" ", "_")
         .replace(":", "_").replace("*", "_").replace("?", "_")
         .replace('"', "_").replace("<", "_").replace(">", "_").replace("|", "_")
    )

# ── 가명키 생성 유틸 ─────────────────────────────────────────────
_KOREAN_ADMIN_RE = re.compile(r"(?:[가-힣A-Za-z]+(?:시|군|구)\s*)?([가-힣A-Za-z0-9]+(?:동|읍|면|리))")

def _norm_txt(s: str) -> str:
    # 공백/구두점 제거 + NFKC 정규화 + 소문자
    s = unicodedata.normalize("NFKC", str(s)).strip()
    s = re.sub(r"[\s\p{P}]+", "", s, flags=re.UNICODE)
    return s.lower()

def _digits_tail4(s: str) -> str | None:
    digits = re.sub(r"\D", "", str(s))
    return digits[-4:] if len(digits) >= 4 else None

def _addr_token(addr: str) -> str | None:
    if not addr or str(addr).strip() == "":
        return None
    m = _KOREAN_ADMIN_RE.search(str(addr))
    if m:
        return m.group(1)  # ex) 역삼동, 중구 등
    # 대체: 공백 기준 마지막 두 토큰
    toks = str(addr).split()
    if len(toks) >= 2:
        return "".join(toks[-2:])
    return toks[-1] if toks else None

def build_pseudokey_row(
    name: str | None,
    phone: str | None = None,
    postcode: str | None = None,
    address: str | None = None,
) -> str | None:
    """
    가명키 = <이름정규화>[-전화뒤4][-우편번호][-주소토큰]
    입력 값이 없으면 해당 파트는 생략.
    모든 파트가 비면 None 반환.
    """
    parts = []
    if name and str(name).strip():
        parts.append(_norm_txt(name))
    if phone:
        tail = _digits_tail4(phone)
        if tail:
            parts.append(tail)
    if postcode:
        pc = re.sub(r"\D", "", str(postcode))
        if pc:
            parts.append(pc)
    if address:
        tok = _addr_token(address)
        if tok:
            parts.append(_norm_txt(tok))
    if not parts:
        return None
    return "-".join(parts)

# index_html.py
from typing import List, Tuple

def build_index_html(title: str, items: List[Tuple[str, str]]) -> str:
    # items: [(표시명, 파일명), ...]
    links = "\n".join([f'<li><a href="{fname}" target="_blank">{name}</a></li>' for name, fname in items])
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8"/>
  <title>{title}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic', Arial, sans-serif; padding: 24px; }}
    h1 {{ margin-top: 0; }}
    ul {{ line-height: 1.8; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <ul>
    {links}
  </ul>
</body>
</html>
"""

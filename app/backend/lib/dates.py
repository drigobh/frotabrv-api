"""Server-side date helpers. The pod clock is UTC — anchor "today" here, never in the browser."""

import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def today_iso(tz: str | None = None) -> str:
    """Today's date as YYYY-MM-DD in `tz` (default: APP_TZ env, else UTC)."""
    zone = tz or os.environ.get("APP_TZ", "UTC")
    return datetime.now(ZoneInfo(zone)).strftime("%Y-%m-%d")


def now_iso() -> str:
    """Current instant as an aware UTC ISO string (stored as string to avoid naive-datetime traps)."""
    return datetime.now(timezone.utc).isoformat()


def last_months(n: int = 6) -> list[str]:
    """The last `n` months as YYYY-MM, oldest first, ending in the current month."""
    today = today_iso()
    y, m = int(today[:4]), int(today[5:7])
    out: list[str] = []
    for i in range(n - 1, -1, -1):
        mm, yy = m - i, y
        while mm <= 0:
            mm += 12
            yy -= 1
        out.append(f"{yy:04d}-{mm:02d}")
    return out

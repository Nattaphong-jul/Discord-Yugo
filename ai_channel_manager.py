import csv
from pathlib import Path
import pandas as pd

CSV_PATH = Path("AI_Channel.csv")
CSV_HEADERS = ["channel_name", "channel_id"]

def ensure_csv_exists() -> None:
    """Create the CSV with headers if it doesn't exist."""
    if not CSV_PATH.exists():
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)

def read_rows() -> list[dict]:
    """Read all rows as dicts, skipping malformed/blank lines."""
    ensure_csv_exists()
    rows = []
    with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return rows
        for r in reader:
            if not r or not r.get("channel_id"):
                continue
            rows.append({"channel_name": r["channel_name"], "channel_id": str(r["channel_id"])})
    return rows

def write_rows(rows: list[dict]) -> None:
    """Rewrite CSV cleanly with headers (prevents blanks)."""
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for r in rows:
            writer.writerow({
                "channel_name": r["channel_name"],
                "channel_id": str(r["channel_id"])
            })

def toggle_channel(channel_name: str, channel_id: str) -> str:
    """
    Toggle AI mode for a given channel.
    Returns: "enabled" or "disabled"
    """
    rows = read_rows()
    already = any(r["channel_id"] == channel_id for r in rows)

    if already:
        new_rows = [r for r in rows if r["channel_id"] != channel_id]
        write_rows(new_rows)
        return "disabled"
    else:
        rows.append({"channel_name": channel_name, "channel_id": channel_id})
        # Deduplicate in case of manual edits
        seen = set()
        clean = []
        for r in reversed(rows):
            if r["channel_id"] not in seen:
                seen.add(r["channel_id"])
                clean.append(r)
        clean.reverse()
        write_rows(clean)
        return "enabled"
    
def is_ai_channel(channel_id: str) -> bool:
    """Return True if the channel_id exists in AI_Channel.csv."""
    try:
        df = pd.read_csv("AI_Channel.csv")
        # Check if file has expected column and is not empty
        if "channel_id" not in df.columns:
            return False
        return str(channel_id) in df["channel_id"].astype(str).values
    except FileNotFoundError:
        return False

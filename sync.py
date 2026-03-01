import json
import os
import sys
import requests
import feedparser

RSS_URL = os.environ.get("RSS_URL")
WEBHOOK = os.environ.get("DISCORD_WEBHOOK")
STATE_FILE = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_id": None}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def post_to_discord(content: str):
    r = requests.post(WEBHOOK, json={"content": content}, timeout=20)
    if r.status_code >= 300:
        raise RuntimeError(f"Discord webhook failed: {r.status_code} {r.text}")

def main():
    if not RSS_URL or not WEBHOOK:
        print("Missing RSS_URL or DISCORD_WEBHOOK", file=sys.stderr)
        sys.exit(1)

    state = load_state()

    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        print("No RSS entries. RSSHub may be temporarily blocked or empty.")
        sys.exit(0)

    newest = feed.entries[0]
    tweet_id = getattr(newest, "id", None) or getattr(newest, "guid", None) or newest.link

    if state["last_id"] == tweet_id:
        print("No new tweet.")
        sys.exit(0)

    title = getattr(newest, "title", "").strip()
    link = getattr(newest, "link", "").strip()

    msg = f"🃏 {title}\n{link}".strip()
    post_to_discord(msg)

    state["last_id"] = tweet_id
    save_state(state)
    print("Posted new tweet!")

if __name__ == "__main__":
    main()

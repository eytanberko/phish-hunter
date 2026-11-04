"""Downloads the OpenPhish feed and records when each URL first appeared.
NOTE: the first run marks everything as 'new' -> treat it as a baseline in the analysis."""
import csv, datetime, os, urllib.request
from urllib.parse import urlparse

FEEDS = {"openphish": "https://openphish.com/feed.txt"}
OUT = "data/feed_sightings.csv"
FIELDS = ["first_seen", "source", "url", "domain"]

def main():
    os.makedirs("data", exist_ok=True)
    seen = set()
    if os.path.exists(OUT):
        with open(OUT, newline="", encoding="utf-8") as f:
            seen = {(r["source"], r["url"]) for r in csv.DictReader(f)}

    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    new_rows = []
    for source, feed_url in FEEDS.items():
        req = urllib.request.Request(feed_url, headers={"User-Agent": "phish-hunter-research"})
        with urllib.request.urlopen(req, timeout=60) as r:
            lines = r.read().decode("utf-8", "ignore").splitlines()
        for url in (l.strip() for l in lines):
            if url and (source, url) not in seen:
                seen.add((source, url))
                new_rows.append({"first_seen": now, "source": source, "url": url,
                                 "domain": urlparse(url).hostname or ""})

    new_file = not os.path.exists(OUT)
    with open(OUT, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        w.writerows(new_rows)
    print(f"{now}: {len(new_rows)} new URLs")

if __name__ == "__main__":
    main()

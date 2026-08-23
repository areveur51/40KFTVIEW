"""Parse an official X/Twitter account archive into post records."""

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from ingest.detect import score_decode

JS_PREFIXES = ("window.YTD.", "window.YTD")


def _parse_js_array(text):
    start = text.find("[")
    if start < 0:
        raise ValueError("Archive file does not contain a JSON array")
    return json.loads(text[start:])


def _coerce_tweet(entry):
    if isinstance(entry, dict) and "tweet" in entry:
        return entry["tweet"]
    return entry


def _parse_created_at(raw):
    if not raw:
        return ""
    if isinstance(raw, str) and raw.endswith("Z") and "T" in raw:
        return raw
    try:
        parsed = datetime.strptime(raw, "%a %b %d %H:%M:%S %z %Y")
        return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except ValueError:
        return raw


def _media_from_tweet(tweet):
    entities = tweet.get("extended_entities") or tweet.get("entities") or {}
    items = []
    for media in entities.get("media") or []:
        url = media.get("media_url_https") or media.get("media_url") or ""
        if url:
            items.append({
                "url": url,
                "type": media.get("type") or "photo",
            })
    return items


def tweet_to_record(tweet, source="archive"):
    """Normalize a raw archive/API tweet object into an inbox record."""
    tweet_id = str(tweet.get("id_str") or tweet.get("id") or "")
    username = (
        (tweet.get("user") or {}).get("screen_name")
        or tweet.get("username")
        or "areveur51"
    )
    text = tweet.get("full_text") or tweet.get("text") or ""
    media = tweet.get("media") or _media_from_tweet(tweet)
    graphic = ""
    if media:
        graphic = media[0].get("url") or ""
    is_retweet = bool(
        tweet.get("retweeted_status")
        or tweet.get("retweeted")
        or text.startswith("RT @")
    )
    is_reply = bool(tweet.get("in_reply_to_status_id_str") or tweet.get("in_reply_to_user_id_str"))
    record = {
        "tweet_id": tweet_id,
        "created_at": _parse_created_at(tweet.get("created_at")),
        "text": text,
        "xPostURL": f"https://x.com/{username}/status/{tweet_id}" if tweet_id else "",
        "xGraphicURL": graphic,
        "media": media,
        "is_reply": is_reply,
        "is_retweet": is_retweet,
        "source": source,
    }
    verdict = score_decode(record)
    record["score"] = verdict["score"]
    record["is_decode"] = verdict["is_decode"]
    record["reasons"] = verdict["reasons"]
    record["keywords"] = verdict["keywords"]
    record["status"] = "candidate" if verdict["is_decode"] else "rejected"
    return record


def _iter_js_files(root):
    root = Path(root)
    candidates = []
    search_roots = [root]
    if (root / "data").is_dir():
        search_roots.append(root / "data")
    for folder in search_roots:
        for pattern in ("tweets.js", "tweet.js", "tweets*.js", "tweet-part*.js", "tweets-part*.js"):
            candidates.extend(sorted(folder.glob(pattern)))
    # Preserve order while dropping duplicates
    seen = set()
    for path in candidates:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            yield path


def load_archive_posts(path):
    """
    Load posts from an official archive zip, extracted folder, or tweets.js file.

    Returns a list of normalized records, newest first.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Archive path not found: {path}")

    posts = []
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            names = [
                name for name in archive.namelist()
                if name.lower().endswith(".js")
                and ("/tweet" in name.lower() or name.lower().endswith("tweets.js") or name.lower().endswith("tweet.js"))
            ]
            if not names:
                raise ValueError("Zip archive does not contain tweets.js")
            for name in sorted(names):
                text = archive.read(name).decode("utf-8")
                for entry in _parse_js_array(text):
                    posts.append(tweet_to_record(_coerce_tweet(entry), source="archive"))
    elif path.is_file():
        text = path.read_text(encoding="utf-8")
        for entry in _parse_js_array(text):
            posts.append(tweet_to_record(_coerce_tweet(entry), source="archive"))
    else:
        files = list(_iter_js_files(path))
        if not files:
            raise ValueError(f"No tweets.js files found under {path}")
        for js_file in files:
            text = js_file.read_text(encoding="utf-8")
            for entry in _parse_js_array(text):
                posts.append(tweet_to_record(_coerce_tweet(entry), source="archive"))

    posts.sort(key=lambda item: item.get("created_at") or "", reverse=True)
    return posts

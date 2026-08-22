"""Fetch and cache full X post text for catalog decodes."""

import json
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ingest.catalog import NODES_FILE, load_json, load_post_texts, save_json, POST_TEXTS_FILE
from ingest.snowflake import tweet_id_from_url

FX_URL = "https://api.fxtwitter.com/status/{tweet_id}"


def save_post_texts(payload):
    save_json(POST_TEXTS_FILE, payload)
    return payload


def _fetch_one(tweet_id, timeout=20):
    req = urllib.request.Request(
        FX_URL.format(tweet_id=tweet_id),
        headers={"User-Agent": "40kft-decode-explorer/1.0"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as handle:
        payload = json.load(handle)
    tweet = payload.get("tweet") or {}
    text = (tweet.get("text") or tweet.get("raw_text") or "").strip()
    if not text:
        raise ValueError(f"empty text for {tweet_id}")
    return text


def fetch_post_text(tweet_id, retries=2):
    last_error = None
    for attempt in range(retries + 1):
        try:
            return _fetch_one(tweet_id)
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            last_error = exc
            time.sleep(0.4 * (attempt + 1))
    raise RuntimeError(f"could not fetch {tweet_id}: {last_error}")


def tweet_ids_from_nodes(nodes=None):
    nodes = nodes if nodes is not None else load_json(NODES_FILE, default=[]) or []
    ids = []
    for node in nodes:
        tweet_id = tweet_id_from_url(node.get("xPostURL") or "")
        if tweet_id:
            ids.append(tweet_id)
    return ids


def refresh_post_texts(force=False, workers=6):
    """Fill data/post_texts.json from public tweet lookups. Idempotent unless force."""
    cached = load_post_texts()
    wanted = tweet_ids_from_nodes()
    todo = [tweet_id for tweet_id in wanted if force or not (cached.get(tweet_id) or "").strip()]
    errors = []

    def work(tweet_id):
        return tweet_id, fetch_post_text(tweet_id)

    if todo:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(work, tweet_id) for tweet_id in todo]
            for future in as_completed(futures):
                try:
                    tweet_id, text = future.result()
                    cached[tweet_id] = text
                except Exception as exc:  # noqa: BLE001 - keep going; report at end
                    errors.append(str(exc))
        save_post_texts(cached)

    return {
        "wanted": len(wanted),
        "cached": sum(1 for tweet_id in wanted if (cached.get(tweet_id) or "").strip()),
        "fetched": len(todo) - len(errors),
        "errors": errors,
        "changed": bool(todo) and len(errors) < len(todo),
    }

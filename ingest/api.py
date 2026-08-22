"""X API v2 client for incremental and optional full-archive sync."""

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from ingest.detect import score_decode

DEFAULT_USERNAME = "areveur51"
API_BASE = "https://api.x.com/2"


class XApiError(RuntimeError):
    """Raised when the X API cannot complete a request."""


def _bearer_token():
    return (
        os.environ.get("X_BEARER_TOKEN")
        or os.environ.get("TWITTER_BEARER_TOKEN")
        or ""
    ).strip()


def api_available():
    return bool(_bearer_token())


def _request(path, params=None):
    token = _bearer_token()
    if not token:
        raise XApiError(
            "Missing X_BEARER_TOKEN. Add a developer bearer token to sync from the X API."
        )
    query = urllib.parse.urlencode(params or {}, doseq=True)
    url = f"{API_BASE}{path}"
    if query:
        url = f"{url}?{query}"
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": "40kftview-decode-ingest",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise XApiError(f"X API {exc.code} on {path}: {detail[:400]}") from exc
    except urllib.error.URLError as exc:
        raise XApiError(f"X API network error: {exc.reason}") from exc
    return json.loads(payload)


def lookup_user(username=DEFAULT_USERNAME):
    data = _request(f"/users/by/username/{urllib.parse.quote(username)}")
    user = data.get("data") or {}
    if not user.get("id"):
        raise XApiError(f"X user not found: {username}")
    return user


def _iso_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _media_index(payload):
    includes = payload.get("includes") or {}
    return {item.get("media_key"): item for item in includes.get("media") or []}


def _records_from_payload(payload, username, source):
    media_by_key = _media_index(payload)
    records = []
    for tweet in payload.get("data") or []:
        media = []
        for key in (tweet.get("attachments") or {}).get("media_keys") or []:
            item = media_by_key.get(key) or {}
            url = item.get("url") or item.get("preview_image_url") or ""
            if url:
                media.append({"url": url, "type": item.get("type") or "photo"})
        created = tweet.get("created_at") or _iso_now()
        record = {
            "tweet_id": str(tweet.get("id") or ""),
            "created_at": created,
            "text": tweet.get("text") or "",
            "xPostURL": f"https://x.com/{username}/status/{tweet.get('id')}",
            "xGraphicURL": media[0]["url"] if media else "",
            "media": media,
            "is_reply": tweet.get("in_reply_to_user_id") is not None,
            "is_retweet": (tweet.get("text") or "").startswith("RT @"),
            "source": source,
        }
        verdict = score_decode(record)
        record["score"] = verdict["score"]
        record["is_decode"] = verdict["is_decode"]
        record["reasons"] = verdict["reasons"]
        record["keywords"] = verdict["keywords"]
        record["status"] = "candidate" if verdict["is_decode"] else "rejected"
        records.append(record)
    return records


def _paginate(path, params, username, source, max_pages=40):
    page = 0
    next_token = None
    collected = []
    while page < max_pages:
        page_params = dict(params)
        if next_token:
            page_params["pagination_token"] = next_token
            page_params["next_token"] = next_token
        payload = _request(path, page_params)
        collected.extend(_records_from_payload(payload, username, source))
        meta = payload.get("meta") or {}
        next_token = meta.get("next_token")
        if not next_token:
            break
        page += 1
    return collected


def fetch_user_timeline(username=DEFAULT_USERNAME, since_id=None, start_time=None):
    """
    Fetch recent original posts from the user timeline.

    Lower X API tiers typically cap this around the newest 3,200 posts.
    Use the official account archive for history from account creation.
    """
    user = lookup_user(username)
    params = {
        "max_results": 100,
        "tweet.fields": "created_at,entities,attachments,in_reply_to_user_id",
        "expansions": "attachments.media_keys",
        "media.fields": "url,preview_image_url,type",
        "exclude": "retweets",
    }
    if since_id:
        params["since_id"] = since_id
    if start_time:
        params["start_time"] = start_time
    return _paginate(f"/users/{user['id']}/tweets", params, username, source="api_timeline")


def fetch_full_archive(username=DEFAULT_USERNAME, start_time=None, end_time=None):
    """
    Search every public post from the account via full-archive search.

    Requires paid X API full-archive access. Prefer the official archive zip
    when that access is not available.
    """
    query = f"from:{username} -is:retweet"
    params = {
        "query": query,
        "max_results": 100,
        "tweet.fields": "created_at,entities,attachments,in_reply_to_user_id",
        "expansions": "attachments.media_keys",
        "media.fields": "url,preview_image_url,type",
    }
    if start_time:
        params["start_time"] = start_time
    if end_time:
        params["end_time"] = end_time
    return _paginate("/tweets/search/all", params, username, source="api_full_archive")

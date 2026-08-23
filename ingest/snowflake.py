"""Twitter/X snowflake helpers."""

from datetime import datetime, timezone

TWITTER_EPOCH_MS = 1288834974657


def tweet_id_from_url(url):
    """Extract a numeric tweet id from an x.com/twitter.com status URL."""
    if not url:
        return ""
    marker = "/status/"
    if marker not in url:
        return ""
    raw = url.split(marker, 1)[1].split("?", 1)[0].split("/", 1)[0]
    return raw if raw.isdigit() else ""


def datetime_from_snowflake(tweet_id):
    """Return UTC datetime encoded in a tweet snowflake id, or None."""
    try:
        snowflake = int(tweet_id)
    except (TypeError, ValueError):
        return None
    timestamp_ms = (snowflake >> 22) + TWITTER_EPOCH_MS
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)


def isoformat_utc(value):
    """Serialize a datetime as an ISO-8601 UTC string."""
    if value is None:
        return ""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

"""CLI: python -m ingest archive|sync|rebuild."""

import argparse
import sys
from datetime import datetime, timezone

from ingest import api
from ingest.archive import load_archive_posts
from ingest.catalog import build_catalog, load_state, merge_inbox, save_state


def _now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _update_state(source, records, extra=None):
    state = load_state()
    tweet_ids = [item.get("tweet_id") for item in records if item.get("tweet_id")]
    newest = max(tweet_ids, key=lambda value: int(value)) if tweet_ids else state.get("newest_tweet_id")
    state.update({
        "last_sync_at": _now(),
        "last_source": source,
        "newest_tweet_id": newest or "",
        "api_available": api.api_available(),
    })
    if extra:
        state.update(extra)
    save_state(state)
    return state


def cmd_archive(args):
    posts = load_archive_posts(args.path)
    decodes = [item for item in posts if item.get("is_decode")]
    if args.all_posts:
        selected = posts
    else:
        selected = decodes
    stats = merge_inbox(selected)
    _update_state("archive", posts, extra={"archive_posts": len(posts), "archive_decodes": len(decodes)})
    print(f"Archive posts: {len(posts)}")
    print(f"Detected decodes: {len(decodes)}")
    print(f"Inbox added: {stats['added']}  updated: {stats['updated']}  size: {stats['inbox_size']}")
    return 0


def cmd_sync(args):
    if not api.api_available():
        print(
            "X_BEARER_TOKEN is not set. For complete history, download your official "
            "X archive and run: python -m ingest archive /path/to/twitter-archive.zip"
        )
        return 2
    state = load_state()
    username = args.username
    if args.full:
        records = api.fetch_full_archive(username=username, start_time=args.start_time)
        source = "api_full_archive"
    else:
        since_id = None if args.backfill else state.get("newest_tweet_id")
        records = api.fetch_user_timeline(
            username=username,
            since_id=since_id or None,
            start_time=args.start_time,
        )
        source = "api_timeline"
    decodes = [item for item in records if item.get("is_decode")]
    selected = records if args.all_posts else decodes
    stats = merge_inbox(selected)
    _update_state(source, records)
    print(f"Fetched posts: {len(records)}")
    print(f"Detected decodes: {len(decodes)}")
    print(f"Inbox added: {stats['added']}  updated: {stats['updated']}  size: {stats['inbox_size']}")
    return 0


def cmd_rebuild(args):
    catalog = build_catalog()
    counts = catalog["counts"]
    print(
        f"Catalog ready: {counts['confirmed']} confirmed, "
        f"{counts['candidates']} candidates, {counts['keywords']} keywords"
    )
    if args.json:
        import json
        print(json.dumps(catalog["range"]))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        description="Detect and ingest @areveur51 decodes from an X archive or the X API."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    archive = sub.add_parser("archive", help="Import an official X archive zip or tweets.js")
    archive.add_argument("path", help="Path to twitter-*.zip, extracted folder, or tweets.js")
    archive.add_argument("--all-posts", action="store_true", help="Keep non-decode posts in the inbox")
    archive.set_defaults(func=cmd_archive)

    sync = sub.add_parser("sync", help="Pull new posts from the X API")
    sync.add_argument("--username", default="areveur51")
    sync.add_argument("--full", action="store_true", help="Use full-archive search (paid API access)")
    sync.add_argument("--backfill", action="store_true", help="Ignore since_id and walk the timeline")
    sync.add_argument("--start-time", help="RFC3339 start time")
    sync.add_argument("--all-posts", action="store_true")
    sync.set_defaults(func=cmd_sync)

    rebuild = sub.add_parser("rebuild", help="Print catalog counts from current files")
    rebuild.add_argument("--json", action="store_true")
    rebuild.set_defaults(func=cmd_rebuild)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

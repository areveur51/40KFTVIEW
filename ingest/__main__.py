"""CLI: python -m ingest archive|sync|rebuild."""

import argparse
import sys

from ingest import api
from ingest.archive import load_archive_posts
from ingest.catalog import build_catalog, load_state, merge_inbox, record_import_state, sha256_file
from ingest.texts import refresh_post_texts


def cmd_archive(args):
    digest = sha256_file(args.path)
    posts = load_archive_posts(args.path)
    decodes = [item for item in posts if item.get("is_decode")]
    selected = posts if args.all_posts else decodes
    stats = merge_inbox(selected)
    record_import_state("archive", posts, stats, extra={
        "archive_posts": len(posts),
        "archive_decodes": len(decodes),
        "last_archive_sha256": digest,
        "fetched": len(posts),
        "api_available": api.api_available(),
    })
    print(f"Archive posts: {len(posts)}")
    print(f"Detected decodes: {len(decodes)}")
    print(
        f"Inbox added: {stats['added']}  updated: {stats['updated']}  "
        f"unchanged: {stats['unchanged']}  skipped: {stats['skipped']}  size: {stats['inbox_size']}"
    )
    if not stats["changed"]:
        print("Idempotent: archive already applied, inbox left unchanged.")
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
    record_import_state(source, records, stats, extra={
        "fetched": len(records),
        "api_available": api.api_available(),
    })
    print(f"Fetched posts: {len(records)}")
    print(f"Detected decodes: {len(decodes)}")
    print(
        f"Inbox added: {stats['added']}  updated: {stats['updated']}  "
        f"unchanged: {stats['unchanged']}  skipped: {stats['skipped']}  size: {stats['inbox_size']}"
    )
    return 0


def cmd_texts(args):
    stats = refresh_post_texts(force=args.force)
    print(
        f"Post texts: {stats['cached']}/{stats['wanted']} cached, "
        f"{stats['fetched']} fetched"
    )
    if stats["errors"]:
        print(f"Errors: {len(stats['errors'])}")
        for item in stats["errors"][:8]:
            print(f"  {item}")
        return 1
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

    texts = sub.add_parser("texts", help="Fetch and cache full X post text for catalog decodes")
    texts.add_argument("--force", action="store_true", help="Refetch texts that are already cached")
    texts.set_defaults(func=cmd_texts)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

"""Assemble a time-aware decode catalog from nodes, edges, and inbox."""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from ingest.detect import matched_keywords, score_decode
from ingest.snowflake import datetime_from_snowflake, isoformat_utc, tweet_id_from_url

DATA_DIR = Path("data")
NODES_FILE = DATA_DIR / "nodes.json"
EDGES_FILE = DATA_DIR / "edges.json"
INBOX_FILE = DATA_DIR / "inbox.json"
STATE_FILE = DATA_DIR / "ingest_state.json"
POST_TEXTS_FILE = DATA_DIR / "post_texts.json"
ACCOUNT = "areveur51"
PROTECTED_STATUSES = frozenset({"confirmed", "rejected"})
RECORD_FIELDS = (
    "tweet_id",
    "created_at",
    "text",
    "xPostURL",
    "xGraphicURL",
    "media",
    "is_reply",
    "is_retweet",
    "source",
    "score",
    "is_decode",
    "reasons",
    "keywords",
    "status",
    "imported_at",
)


def load_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path, payload):
    """Atomically write JSON so a crashed import cannot leave a half file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    os.replace(tmp, path)


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonicalize_record(record):
    """Keep inbox rows in a stable field order for identical re-imports."""
    return {key: record[key] for key in RECORD_FIELDS if key in record}


def record_fingerprint(record):
    media = record.get("media") or []
    media_urls = ",".join(item.get("url") or "" for item in media if isinstance(item, dict))
    return "|".join((
        str(record.get("tweet_id") or ""),
        str(record.get("created_at") or ""),
        str(record.get("text") or ""),
        str(record.get("xGraphicURL") or ""),
        media_urls,
        "1" if record.get("is_decode") else "0",
        str(record.get("score") or ""),
    ))


def load_inbox():
    return load_json(INBOX_FILE, default=[]) or []


def load_post_texts():
    payload = load_json(POST_TEXTS_FILE, default={}) or {}
    return payload if isinstance(payload, dict) else {}


def fold_styled_text(value):
    """Map mathematical/styled Unicode letters back to ASCII for search."""
    out = []
    for char in str(value or ""):
        code = ord(char)
        mapped = None
        ranges = (
            (0x1D400, 0x1D419, 65),
            (0x1D41A, 0x1D433, 97),
            (0x1D434, 0x1D44D, 65),
            (0x1D44E, 0x1D467, 97),
            (0x1D468, 0x1D481, 65),
            (0x1D482, 0x1D49B, 97),
            (0x1D4D0, 0x1D4E9, 65),
            (0x1D4EA, 0x1D503, 97),
            (0x1D5D4, 0x1D5ED, 65),
            (0x1D5EE, 0x1D607, 97),
            (0x1D63C, 0x1D655, 65),
            (0x1D656, 0x1D66F, 97),
            (0x1D670, 0x1D689, 65),
            (0x1D68A, 0x1D6A3, 97),
            (0xFF21, 0xFF3A, 65),
            (0xFF41, 0xFF5A, 97),
        )
        for start, end, base in ranges:
            if start <= code <= end:
                mapped = chr(base + (code - start))
                break
        out.append(mapped if mapped else char)
    return "".join(out)


def save_inbox(records):
    save_json(INBOX_FILE, records)
    return records


def load_state():
    return load_json(STATE_FILE, default={}) or {}


def save_state(state):
    save_json(STATE_FILE, state)
    return state


def _keyword_id(term):
    compact = "".join(ch for ch in term if ch.isalnum())
    return f"kw-{compact}" if compact else ""


def _existing_tweet_ids(nodes):
    ids = set()
    for node in nodes:
        tweet_id = tweet_id_from_url(node.get("xPostURL", ""))
        if tweet_id:
            ids.add(tweet_id)
    return ids


def merge_inbox(new_records, existing_nodes=None):
    """
    Merge records into inbox.json by tweet id.

    Re-running the same archive is a no-op: identical rows stay byte-stable,
    protected statuses (confirmed/rejected) are never overwritten, and the
    file is rewritten only when something actually changed.
    """
    nodes = existing_nodes if existing_nodes is not None else load_json(NODES_FILE, default=[])
    known = _existing_tweet_ids(nodes)
    inbox = load_inbox()
    by_id = {}
    for item in inbox:
        tweet_id = item.get("tweet_id")
        if tweet_id and tweet_id not in by_id:
            by_id[tweet_id] = item

    added = 0
    updated = 0
    unchanged = 0
    skipped = 0
    seen_input = set()

    for record in new_records:
        tweet_id = record.get("tweet_id")
        if not tweet_id or tweet_id in seen_input:
            skipped += 1
            continue
        seen_input.add(tweet_id)
        if tweet_id in known:
            skipped += 1
            continue

        incoming = canonicalize_record(record)
        existing = by_id.get(tweet_id)
        if existing is None:
            incoming["imported_at"] = incoming.get("imported_at") or isoformat_utc(datetime.now(timezone.utc))
            by_id[tweet_id] = canonicalize_record(incoming)
            added += 1
            continue

        merged_row = dict(existing)
        incoming_status = incoming.get("status")
        existing_status = existing.get("status")
        for key, value in incoming.items():
            if key in {"status", "imported_at"}:
                continue
            merged_row[key] = value
        if existing_status in PROTECTED_STATUSES:
            merged_row["status"] = existing_status
        elif incoming_status:
            merged_row["status"] = incoming_status
        if existing.get("imported_at"):
            merged_row["imported_at"] = existing["imported_at"]
        merged_row = canonicalize_record(merged_row)

        if record_fingerprint(existing) == record_fingerprint(merged_row) and existing.get("status") == merged_row.get("status"):
            unchanged += 1
            continue
        by_id[tweet_id] = merged_row
        updated += 1

    merged = [canonicalize_record(item) for item in by_id.values()]
    merged.sort(key=lambda item: (item.get("created_at") or "", item.get("tweet_id") or ""), reverse=True)
    previous = [canonicalize_record(item) for item in inbox]
    previous.sort(key=lambda item: (item.get("created_at") or "", item.get("tweet_id") or ""), reverse=True)
    changed = added > 0 or updated > 0 or previous != merged
    if previous != merged:
        save_inbox(merged)
    return {
        "added": added,
        "updated": updated,
        "unchanged": unchanged,
        "skipped": skipped,
        "inbox_size": len(merged),
        "changed": changed,
    }


def append_event(event):
    state = load_state()
    events = list(state.get("events") or [])
    events.append(event)
    state["events"] = events[-40:]
    save_state(state)
    return state


def record_import_state(source, records, stats, extra=None):
    """Update ingest state without rewriting it on a no-op re-import."""
    state = load_state()
    now = isoformat_utc(datetime.now(timezone.utc))
    tweet_ids = [item.get("tweet_id") for item in records if item.get("tweet_id")]
    newest = max(tweet_ids, key=lambda value: int(value)) if tweet_ids else state.get("newest_tweet_id")
    state["last_checked_at"] = now
    state["last_source"] = source
    state["newest_tweet_id"] = newest or state.get("newest_tweet_id") or ""
    if extra:
        state.update(extra)
    if stats.get("changed"):
        state["last_sync_at"] = now
    events = list(state.get("events") or [])
    events.append({
        "at": now,
        "source": source,
        "added": stats.get("added", 0),
        "updated": stats.get("updated", 0),
        "unchanged": stats.get("unchanged", 0),
        "skipped": stats.get("skipped", 0),
        "fetched": extra.get("fetched") if extra else len(records),
    })
    state["events"] = events[-40:]
    save_state(state)
    return state


def _node_created_at(node):
    tweet_id = tweet_id_from_url(node.get("xPostURL", ""))
    return isoformat_utc(datetime_from_snowflake(tweet_id))


def _adjacency(edges):
    neighbors = {}
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if not source or not target:
            continue
        neighbors.setdefault(source, []).append({
            "id": target,
            "label": edge.get("label") or "",
        })
        neighbors.setdefault(target, []).append({
            "id": source,
            "label": edge.get("label") or "",
        })
    return neighbors


def build_catalog():
    """Build the explorer catalog from confirmed nodes plus inbox candidates."""
    nodes = load_json(NODES_FILE, default=[]) or []
    edges = load_json(EDGES_FILE, default=[]) or []
    inbox = load_inbox()
    state = load_state()
    neighbors = _adjacency(edges)
    post_texts = load_post_texts()

    keywords = []
    decodes = []
    keyword_ids = set()

    for node in nodes:
        name = node.get("graphicName") or ""
        label = node.get("graphicLabel") or name
        if name.startswith("kw-"):
            keywords.append({
                "id": name,
                "label": label,
                "type": "keyword",
            })
            keyword_ids.add(name)
            continue

        tweet_id = tweet_id_from_url(node.get("xPostURL", ""))
        created_at = _node_created_at(node)
        connected = neighbors.get(name, [])
        linked_keywords = [item["id"] for item in connected if item["id"] in keyword_ids or item["id"].startswith("kw-")]
        body = (node.get("text") or post_texts.get(tweet_id) or "").strip() or label
        # Keywords are appended after this loop in source order; resolve on a second pass.
        decodes.append({
            "id": name,
            "tweet_id": tweet_id,
            "label": label,
            "created_at": created_at,
            "text": body,
            "xPostURL": node.get("xPostURL") or "",
            "xGraphicURL": node.get("xGraphicURL") or "",
            "media": (
                [{"url": node.get("xGraphicURL"), "type": "photo"}]
                if node.get("xGraphicURL") else []
            ),
            "keywords": linked_keywords,
            "connections": [item["id"] for item in connected if not item["id"].startswith("kw-")],
            "edge_labels": [item["label"] for item in connected if item["label"]],
            "status": "confirmed",
            "score": 1.0,
            "source": "catalog",
            "reasons": ["manual_catalog"],
        })

    keyword_ids = {item["id"] for item in keywords}
    keyword_labels = {item["id"]: item["label"] for item in keywords}
    for decode in decodes:
        decode["keywords"] = [
            item for item in neighbors.get(decode["id"], [])
            if item["id"] in keyword_ids
        ]
        decode["keyword_ids"] = [item["id"] for item in decode["keywords"]]
        decode["keyword_labels"] = [keyword_labels[item["id"]] for item in decode["keywords"]]
        # Keep a flat list for search
        text_hints = " ".join([
            decode["label"],
            decode.get("text") or "",
            fold_styled_text(decode.get("text") or ""),
            *decode["keyword_labels"],
            *decode["edge_labels"],
        ])
        decode["search_text"] = text_hints.lower()
        extra = matched_keywords(text_hints)
        decode["detected_keywords"] = extra

    known_ids = {item["tweet_id"] for item in decodes if item.get("tweet_id")}
    for record in inbox:
        tweet_id = record.get("tweet_id")
        if not tweet_id or tweet_id in known_ids:
            continue
        if record.get("status") == "rejected" and not record.get("is_decode"):
            # Keep rejected posts out of the default visual; they stay in inbox.
            continue
        slug = f"tw-{tweet_id}"
        label = (record.get("text") or slug).strip().split("\n", 1)[0][:80]
        verdict = score_decode(record) if "score" not in record else None
        score = record.get("score")
        if verdict:
            score = verdict["score"]
        detected = record.get("keywords") or []
        matched_ids = []
        for term in detected:
            kid = _keyword_id(term)
            if kid in keyword_ids:
                matched_ids.append(kid)
        decodes.append({
            "id": slug,
            "tweet_id": tweet_id,
            "label": label,
            "created_at": record.get("created_at") or "",
            "text": record.get("text") or "",
            "xPostURL": record.get("xPostURL") or "",
            "xGraphicURL": record.get("xGraphicURL") or "",
            "media": record.get("media") or (
                [{"url": record.get("xGraphicURL"), "type": "photo"}]
                if record.get("xGraphicURL") else []
            ),
            "keywords": [{"id": kid, "label": keyword_labels.get(kid, kid)} for kid in matched_ids],
            "keyword_ids": matched_ids,
            "keyword_labels": [keyword_labels.get(kid, kid) for kid in matched_ids],
            "connections": [],
            "edge_labels": [],
            "status": record.get("status") or "candidate",
            "score": score if score is not None else 0.0,
            "source": record.get("source") or "inbox",
            "reasons": record.get("reasons") or [],
            "search_text": " ".join([
                label,
                record.get("text") or "",
                fold_styled_text(record.get("text") or ""),
                *detected,
            ]).lower(),
            "detected_keywords": detected,
        })

    dated = [item["created_at"] for item in decodes if item.get("created_at")]
    dated.sort()
    now = datetime.now(timezone.utc)

    return {
        "account": ACCOUNT,
        "generated_at": isoformat_utc(now),
        "range": {
            "min": dated[0] if dated else "",
            "max": dated[-1] if dated else "",
        },
        "counts": {
            "keywords": len(keywords),
            "confirmed": sum(1 for item in decodes if item["status"] == "confirmed"),
            "candidates": sum(1 for item in decodes if item["status"] == "candidate"),
            "edges": len(edges),
            "inbox": len(inbox),
        },
        "ingest": {
            "last_sync_at": state.get("last_sync_at") or "",
            "last_checked_at": state.get("last_checked_at") or "",
            "last_source": state.get("last_source") or "",
            "newest_tweet_id": state.get("newest_tweet_id") or "",
            "api_available": bool(state.get("api_available")),
            "last_archive_sha256": state.get("last_archive_sha256") or "",
            "events": state.get("events") or [],
        },
        "keywords": keywords,
        "decodes": decodes,
        "edges": edges,
    }

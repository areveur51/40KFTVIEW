"""Assemble a time-aware decode catalog from nodes, edges, and inbox."""

import json
from datetime import datetime, timezone
from pathlib import Path

from ingest.detect import matched_keywords, score_decode
from ingest.snowflake import datetime_from_snowflake, isoformat_utc, tweet_id_from_url

DATA_DIR = Path("data")
NODES_FILE = DATA_DIR / "nodes.json"
EDGES_FILE = DATA_DIR / "edges.json"
INBOX_FILE = DATA_DIR / "inbox.json"
STATE_FILE = DATA_DIR / "ingest_state.json"
ACCOUNT = "areveur51"


def load_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def load_inbox():
    return load_json(INBOX_FILE, default=[]) or []


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
    """Insert unseen records into inbox.json, keyed by tweet id."""
    nodes = existing_nodes if existing_nodes is not None else load_json(NODES_FILE, default=[])
    known = _existing_tweet_ids(nodes)
    inbox = load_inbox()
    by_id = {item.get("tweet_id"): item for item in inbox if item.get("tweet_id")}
    added = 0
    updated = 0
    for record in new_records:
        tweet_id = record.get("tweet_id")
        if not tweet_id or tweet_id in known:
            continue
        if tweet_id in by_id:
            by_id[tweet_id].update(record)
            updated += 1
        else:
            by_id[tweet_id] = record
            added += 1
    merged = list(by_id.values())
    merged.sort(key=lambda item: item.get("created_at") or "", reverse=True)
    save_inbox(merged)
    return {"added": added, "updated": updated, "inbox_size": len(merged)}


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
        # Keywords are appended after this loop in source order; resolve on a second pass.
        decodes.append({
            "id": name,
            "tweet_id": tweet_id,
            "label": label,
            "created_at": created_at,
            "text": label,
            "xPostURL": node.get("xPostURL") or "",
            "xGraphicURL": node.get("xGraphicURL") or "",
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
        text_hints = " ".join([decode["label"], *decode["keyword_labels"], *decode["edge_labels"]])
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
            "keywords": [{"id": kid, "label": keyword_labels.get(kid, kid)} for kid in matched_ids],
            "keyword_ids": matched_ids,
            "keyword_labels": [keyword_labels.get(kid, kid) for kid in matched_ids],
            "connections": [],
            "edge_labels": [],
            "status": record.get("status") or "candidate",
            "score": score if score is not None else 0.0,
            "source": record.get("source") or "inbox",
            "reasons": record.get("reasons") or [],
            "search_text": " ".join([label, record.get("text") or "", *detected]).lower(),
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
            "last_source": state.get("last_source") or "",
            "newest_tweet_id": state.get("newest_tweet_id") or "",
            "api_available": bool(state.get("api_available")),
        },
        "keywords": keywords,
        "decodes": decodes,
        "edges": edges,
    }

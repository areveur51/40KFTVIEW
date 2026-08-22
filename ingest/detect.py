"""Score X posts as likely visual decodes."""

import re

# Themes already used as outer-ring keyword nodes, plus common decode markers.
KEYWORD_LEXICON = (
    "NCSWIC",
    "COVID",
    "DECLAS",
    "NewsUnlocksMap",
    "NOSUCHAGENCY",
    "PanicInDC",
    "LogicalThinking",
    "MathematicallyImpossible",
    "PATRIOTS",
    "QANON",
    "FISA",
    "SESSIONS",
    "SNOWDEN",
    "TheGreatAwakening",
    "GREAT AWAKENING",
    "USMIL",
    "VirusOrElection",
    "WWG1WGA",
    "RussiaHoax",
    "Q+",
    "Q CLEARANCE",
    "DIGITAL SOLDIERS",
    "WHERE WE GO ONE",
    "DARK TO LIGHT",
    "THE PLAN",
    "ENJOY THE SHOW",
    "TRUST THE PLAN",
)

BRACKET_LETTER = re.compile(r"\[[A-Za-z0-9]\]")
FILENAME_HINT = re.compile(r"\b[\w.-]+\.(?:jpg|jpeg|png|webp)\b", re.IGNORECASE)
TITLE_CAPS = re.compile(r"\b[A-Z0-9][A-Z0-9 _&'./-]{2,}\b")
Q_MARK = re.compile(r"(?<![A-Za-z])Q(?:ANON|\+| CLEARANCE)?(?![A-Za-z])", re.IGNORECASE)

DEFAULT_THRESHOLD = 0.55


def _text_blob(post):
    parts = [
        post.get("text") or "",
        post.get("graphicLabel") or "",
        post.get("label") or "",
    ]
    return " ".join(parts)


def _has_media(post):
    if post.get("xGraphicURL") or post.get("media_url"):
        return True
    media = post.get("media") or []
    return any(item.get("url") or item.get("type") == "photo" for item in media)


def matched_keywords(text):
    """Return lexicon terms found in text (case-insensitive)."""
    upper = text.upper()
    hits = []
    for term in KEYWORD_LEXICON:
        if term.upper() in upper and term not in hits:
            hits.append(term)
    return hits


def score_decode(post, threshold=DEFAULT_THRESHOLD):
    """
    Return a decode classification dict.

    A decode in this catalog is almost always an original image post with
    title-case/ALL-CAPS framing, bracketed letters, or known theme keywords.
    """
    text = _text_blob(post)
    reasons = []
    score = 0.0

    if post.get("is_retweet"):
        return {
            "score": 0.0,
            "is_decode": False,
            "reasons": ["retweet"],
            "keywords": [],
        }

    if _has_media(post):
        score += 0.40
        reasons.append("has_media")

    if BRACKET_LETTER.search(text):
        score += 0.22
        reasons.append("bracket_letters")

    keywords = matched_keywords(text)
    if keywords:
        score += min(0.24, 0.12 + 0.04 * len(keywords))
        reasons.append("keywords:" + ",".join(keywords[:4]))

    if Q_MARK.search(text):
        score += 0.12
        reasons.append("q_marker")

    if FILENAME_HINT.search(text):
        score += 0.08
        reasons.append("filename_hint")

    compact = re.sub(r"\s+", " ", text).strip()
    if compact and TITLE_CAPS.search(compact) and len(compact) <= 80:
        score += 0.10
        reasons.append("title_caps")

    if post.get("is_reply") and not _has_media(post):
        score -= 0.25
        reasons.append("text_reply")

    score = max(0.0, min(1.0, score))
    return {
        "score": round(score, 3),
        "is_decode": score >= threshold,
        "reasons": reasons,
        "keywords": keywords,
    }

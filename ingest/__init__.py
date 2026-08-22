"""X decode ingest: archive import, API sync, and catalog assembly."""

from ingest.catalog import build_catalog, load_inbox, save_inbox
from ingest.detect import score_decode

__all__ = ["build_catalog", "load_inbox", "save_inbox", "score_decode"]

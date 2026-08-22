"""X decode ingest: archive import, API sync, and catalog assembly."""

from ingest.catalog import (
    build_catalog,
    load_inbox,
    merge_inbox,
    record_import_state,
    save_inbox,
    sha256_file,
)
from ingest.detect import score_decode

__all__ = [
    "build_catalog",
    "load_inbox",
    "merge_inbox",
    "record_import_state",
    "save_inbox",
    "score_decode",
    "sha256_file",
]

# See pipeline order: Ingest → Normalize → Classify → Validate GTIN → Dedupe & Unify → Publish.

- Debug traceability: launchers accept `--debug-on` to stream every action to `logs/app_full_logs.txt` (stdout, stderr, pipeline events, uncaught exceptions).

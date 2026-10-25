# TRUTHLENS Data Directory

This directory stores reference corpus documents, demonstration image samples, uploaded images, and the SQLite database.

## Directory Structure
- `reference_documents/corpus.json`: Curated ground-truth news records, fact-checks, and official bulletins.
- `samples/`: Benchmark demonstration images (floods, protests, relief, synthetic storms).
- `uploads/`: User-submitted investigation targets.
- `uploads/sanitized/`: Privacy-scrubbed copies generated on demand.
- `truthlens.db`: SQLite local database created automatically on backend startup.

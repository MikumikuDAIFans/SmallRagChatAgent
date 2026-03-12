# Lightweight Python RAG Agent

A lightweight Python RAG service for ArtiMaker product documentation.

## Repository Layout

```text
.
|-- server.py
|-- requirements.txt
|-- Dockerfile
|-- .env.example
|-- System_prompt.txt
|-- data/
|   |-- knowledge.md
|   `-- knowledge.pkl         # generated, ignored by git
|-- doc/                      # source markdown knowledge files
|-- tool/                     # ingestion and test scripts
|-- docs/                     # project and migration docs
`-- deploy_package/           # runtime-only deployment package
```

## Quick Start

1. Copy `.env.example` to `.env` and fill in real values.
2. Install dependencies with `pip install -r requirements.txt`.
3. Start the service with `python server.py`.
4. Test locally with `python tool/interactive_client.py`.

## Notes

- Do not commit `.env` or generated vector files.
- Update and commit `.env.example` instead of any real secret.
- Java migration notes are in `docs/java-migration-api.md`.

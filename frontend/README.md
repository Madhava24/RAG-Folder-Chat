# FolderChat Frontend (Demo)

Simple React + Vite UI for the FolderChat backend.

## Features

- Path-based folder ingestion (enter a server-accessible directory path)
- Chat interface (retrieval augmented) with clear chat
- Shows source file names for each assistant response

## Prerequisites

Backend running at `http://localhost:8000` (start with `uvicorn server:app --host localhost`). The path you enter must exist on the BACKEND host file system.

## Install & Run

```bash
npm install
npm run dev
```
Open http://localhost:5173.

## Ingest a Folder
Enter a path such as `./data` or an absolute path like `C:/Users/you/Documents/my_docs`. The backend will run its ingestion pipeline and enable chat once complete.

## Adjust Backend URL
Edit `src/api.js` if backend runs on a different host/port.

## Build
```bash
npm run build
```
Outputs static assets in `dist/`.

## Notes
- Minimal demo; no streaming tokens, no persistent sessions.
- For security, only enter paths you trust; backend reads files directly.
- Sources list shown below each assistant message if available.

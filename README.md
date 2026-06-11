# EMBL-EBI SearchBot Prototype

A unified biological data search platform demonstrating Natural Language Query (NLQ), BLAST integration, MCP server, and Elasticsearch.

## Quickstart

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in necessary values.
3. (Optional) Run Elasticsearch via Docker:
   ```bash
   docker-compose up -d
   ```
4. Run the FastAPI Web Server:
   ```bash
   python run.py
   ```
5. Open `http://localhost:8000` in your browser.

## Running the MCP Server
To expose the EMBL-EBI tools to AI agents using FastMCP, run:
```bash
python app/mcp_server.py
```

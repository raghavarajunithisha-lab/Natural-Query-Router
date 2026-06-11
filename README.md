# EMBL-EBI SearchBot

A prototype that lets users query biological databases using plain English instead of memorising API-specific syntax. It connects to four core EMBL-EBI services (UniProt, Europe PMC, Ensembl, and BLAST) through a single search box, and also exposes every search capability as a set of MCP tools so that AI agents can call the same endpoints programmatically.

## What this project does

Traditional bioinformatics search requires you to know which database to go to and how to format the query for that specific API. This prototype removes that friction:

1. A user types a question like *"find human kinases involved in cancer"*.
2. The backend parses the sentence, figures out the user is looking for **proteins** in **humans** linked to **cancer**, and routes the query to the **UniProt** REST API with the correct structured parameters.
3. Results come back as clickable cards in the browser, each linking to the original database entry.

The same logic is wrapped in an MCP server, meaning an AI agent (Claude Desktop, Cursor, or any MCP-compatible client) can call `search_proteins`, `search_genes`, or `search_publications` directly without a browser.

## Architecture overview

```
User (browser)                    AI Agent (Claude, Cursor, etc.)
      |                                      |
      v                                      v
 FastAPI Server (app/main.py)         MCP Server (app/mcp_server.py)
      |                                      |
      v                                      v
 NLQ Parser (app/nlq/)               Same API clients, called directly
      |                               by the AI with correct parameters
      v
 Elasticsearch Cache (optional)
      |
      v
 API Clients (app/clients/)
      |
      +---> UniProt REST API        (proteins)
      +---> Europe PMC API          (publications)
      +---> Ensembl REST API        (genes)
      +---> EBI Job Dispatcher      (BLAST alignments)
      +---> EBI Search API          (cross-database fallback)
```

### How a query flows through the Web UI

1. The browser sends a POST request to `/api/search` with the raw text.
2. `app/routers/search.py` hands the text to the **NLQ Parser**.
3. The parser has two stages:
   - **Intent Classifier** (`app/nlq/intent.py`) reads the sentence and decides which database is the best match (protein, literature, gene, sequence, or general).
   - **Entity Extractor** (`app/nlq/entities.py`) pulls out structured fields like organism names, disease keywords, gene symbols, and UniProt accession IDs.
4. The parser builds the exact query string the target API expects and returns a structured payload.
5. `app/search/elasticsearch_service.py` checks Elasticsearch (or an in-memory dict if ES is not running) for a cached response. On a cache miss it calls the appropriate API client, stores the result, and returns it.
6. The frontend renders each result as a card with a direct link to the source database entry.

### How the MCP Server works

The MCP server (`app/mcp_server.py`) uses the `FastMCP` library to register the same API clients as callable tools. When an AI agent connects to the server, it sees a list of available tools:

| MCP Tool | What it does | Underlying client |
|---|---|---|
| `search_proteins(query, size)` | Search UniProt for proteins by keyword, gene name, or organism | `app/clients/uniprot.py` |
| `search_publications(query, size)` | Search Europe PMC for papers and preprints | `app/clients/europe_pmc.py` |
| `search_genes(species, symbol)` | Look up a specific gene by symbol via Ensembl | `app/clients/ensembl.py` |
| `search_ebi(query, domain)` | Run a cross-database search through the EBI Search API | `app/clients/ebi_search.py` |
| `run_blast(sequence, program)` | Submit a BLAST alignment job | `app/clients/blast.py` |
| `get_blast_results(job_id)` | Retrieve results for a completed BLAST job | `app/clients/blast.py` |
| `natural_language_search(query)` | Pass free text through the NLQ parser and return results | Uses the full NLQ pipeline |

The AI agent picks which tool to call based on the user's question. For example, if a user asks Claude *"What does the human BRCA1 gene do?"*, Claude would call `search_genes(species="human", symbol="BRCA1")` directly, bypassing the keyword-matching parser entirely. This is a major advantage over the rule-based UI approach because the AI understands biological context without needing hardcoded keyword lists.

The server also exposes two MCP resources (`embl://databases` and `embl://search-help`) and a prompt template (`biological_query`) that agents can use for context.

## Project structure

```
MCPforEMBL/
├── run.py                        # Entry point, starts the FastAPI dev server
├── requirements.txt              # Python dependencies
├── docker-compose.yml            # Optional Elasticsearch container
├── .env.example                  # Template for environment variables
│
├── app/
│   ├── main.py                   # FastAPI app setup, routes, and startup
│   ├── config.py                 # Centralised settings loaded from .env
│   ├── mcp_server.py             # MCP server exposing tools to AI agents
│   │
│   ├── nlq/                      # Natural Language Query parsing pipeline
│   │   ├── intent.py             # Classifies query intent (protein/gene/paper/etc.)
│   │   ├── entities.py           # Extracts organisms, diseases, gene symbols
│   │   └── parser.py             # Combines intent + entities into an API-ready payload
│   │
│   ├── clients/                  # Thin wrappers around each EMBL-EBI REST API
│   │   ├── uniprot.py            # UniProt protein search
│   │   ├── europe_pmc.py         # Europe PMC literature search
│   │   ├── ensembl.py            # Ensembl gene lookup by symbol
│   │   ├── ebi_search.py         # EBI Search cross-database queries
│   │   └── blast.py              # BLAST job submission, polling, and results
│   │
│   ├── routers/                  # FastAPI route handlers
│   │   ├── search.py             # POST /api/search (NLQ endpoint)
│   │   └── blast.py              # POST /api/blast/submit, GET status & results
│   │
│   └── search/
│       └── elasticsearch_service.py  # Caching layer (ES or in-memory fallback)
│
└── frontend/
    ├── index.html                # Single-page UI with three tabs
    ├── css/styles.css            # Dark-themed glassmorphism stylesheet
    └── js/app.js                 # Handles search, BLAST polling, and result rendering
```

## Setup

### Prerequisites

- Python 3.10 or later
- pip

### Install and run

```bash
# Clone the repository
git clone https://github.com/your-username/MCPforEMBL.git
cd Natural-Query-Router

# Install Python dependencies
pip install -r requirements.txt

# Start the server
python run.py
```
Open http://localhost:8000 in your browser.

### Optional: Elasticsearch caching

If you have Docker installed, you can spin up Elasticsearch for persistent caching. Without it, the app uses a simple in-memory dictionary cache that resets on restart.

```bash
docker-compose up -d
```

### Running the MCP Server for AI agents

To let an AI agent connect to your tools:

```bash
python app/mcp_server.py
```

This starts a stdio-based MCP server. To use it with Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "embl-searchbot": {
      "command": "python",
      "args": ["app/mcp_server.py"],
      "cwd": "/path/to/MCPforEMBL"
    }
  }
}
```

## Example queries to test

### Protein search (routed to UniProt)

- `find human kinases involved in cancer`
- `search for mouse kinase proteins`
- `show me enzymes related to diabetes in humans`

### Literature search (routed to Europe PMC)

- `find recent publications about mRNA vaccines`
- `show me papers on the gut microbiome`
- `search for research articles about CRISPR off-target effects`
- `recent publications about the Ebola virus`

### Gene search (routed to Ensembl)

- `search for the TP53 gene`
- `find the mouse APOE gene`
- `show me the human EGFR gene`

### General fallback (routed to Europe PMC literature)

If the query doesn't contain specific biological keywords, it defaults to a literature search:

- `Malaria`
- `COVID-19 variants`
- `Aspirin side effects`

## External APIs used

| Service | Documentation |
|---|---|
| UniProt REST API | https://www.uniprot.org/help/api |
| Europe PMC API | https://europepmc.org/RestfulWebService |
| Ensembl REST API | https://rest.ensembl.org |
| EBI Search | https://www.ebi.ac.uk/ebisearch |
| EBI Job Dispatcher (BLAST) | https://www.ebi.ac.uk/jdispatcher |

## License

This project is a prototype built for demonstration purposes.

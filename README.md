# GraphCoBots‑NKLW‑KGbot

**GraphCoBots‑NKLW‑KGbot** is a Knowledge Graph–driven conversational AI chatbot that provides structured, research‑oriented information about the **life and works of Nikos Kazantzakis**. The system is part of the broader **GraphCoBots** research framework, which investigates distributed, collaborative, and Knowledge Graph‑based multi‑chatbot systems for museums and cultural heritage organizations.

The chatbot is designed to support human‑centered access to cultural knowledge through natural language interaction, leveraging semantic representations and modular deployment practices.

---

## Research Context

This repository represents an experimental and applied research artifact focusing on:

* Knowledge Graphs as a backbone for conversational AI
* Semantic modeling of literary and biographical cultural heritage data
* Conversational interfaces for museums and cultural organizations
* Distributed and collaborative chatbot architectures

The system has been developed and evaluated in the context of peer‑reviewed academic research within the digital cultural heritage and human–computer interaction domains.

---

## Repository Structure

```
.
├── actions/                # GitHub Actions workflows
├── data/                   # Knowledge Graph data and structured exports
├── scripts/                # Utility and helper scripts
├── config.yml              # Chatbot configuration
├── domain.yml              # Conversational domain (intents, entities, responses)
├── endpoints.yml           # External service endpoints
├── credentials.yml         # Credentials file (user‑provided, not committed)
├── docker-compose.yml      # Docker Compose deployment
├── Dockerfile              # Docker image definition
├── index.html              # Web interface or embedded UI
├── server.sh               # Startup script
├── LICENSE                 # Apache License 2.0 (source code)
├── LICENSE-DATA            # CC BY 4.0 (data & Knowledge Graphs)
└── README.md               # Project documentation
```

---

## Prerequisites

To run the chatbot, you will need:

* Docker and Docker Compose (**recommended for reproducibility**), or
* Python 3.x for local execution
* Proper credentials for any external services (defined in `credentials.yml`)

---

## Configuration

### `config.yml`

Defines general runtime parameters such as service ports, logging, and operational settings.

### `domain.yml`

Specifies the chatbot’s conversational domain, including intents, entities, and response templates related to Nikos Kazantzakis’ life and works.

### `endpoints.yml`

Configures connections to external APIs or services used by the chatbot.

### `credentials.yml`

Contains sensitive credentials (API keys, tokens). This file **must not be committed** to the repository.

---

## Running the Chatbot

### Option 1: Docker (Recommended)

```bash
docker compose up --build
```

This command builds and launches the chatbot in a containerized environment, ensuring reproducible deployment.

---

### Option 2: Local Execution

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the chatbot service:

```bash
./server.sh
```

---

## Knowledge Graph Usage

The chatbot relies on a **Knowledge Graph** describing the biography, literary works, and related entities of Nikos Kazantzakis. To ensure transparency and reproducibility, Knowledge Graph content is provided in declarative formats such as:

* Cypher scripts (`.cypher` files)
* CSV datasets suitable for Neo4j import

Database binaries are intentionally excluded from the repository.

---

## Licensing

This repository follows a **dual‑license model**:

* **Source code**: Apache License 2.0 (see `LICENSE`)
* **Data, Knowledge Graphs, and metadata**: Creative Commons Attribution 4.0 International (CC BY 4.0) (see `LICENSE-DATA`)

Users are responsible for complying with the appropriate license depending on the material used.

---

## Citation

If you use this software or its associated data in academic research, please cite the relevant **GraphCoBots** publications. A `CITATION.cff` file may be added to support automated citation workflows.

---

## Notes for Researchers and Developers

* Do not commit credentials or secrets
* Use Docker for reproducible experiments
* Version Knowledge Graph changes using `.cypher` or CSV files
* Avoid committing large binaries or database directories

---

## Contact

For research inquiries, collaboration opportunities, or technical questions, please contact the repository owner via GitHub.

---

## Acknowledgements

This work contributes to ongoing research on conversational AI and Knowledge Graphs for cultural heritage applications, with a focus on museum and literary heritage contexts.

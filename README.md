# AI PoCs Workspace

Personal workspace for AI/LLM experiments and proof-of-concepts by [@eordaxd](https://github.com/eordaxd).

## Structure

```
ai-pocs/
├── experiments/     # Quick, throw-away experiments (hours to days)
├── pocs/            # Structured PoCs, candidates for their own repo
├── shared/          # Reusable clients, utils, and prompt templates
├── scripts/         # Dev tooling (scaffold, etc.)
└── docs/            # Notes, conventions, and guides
```

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/eordaxd/ai-pocs.git
cd ai-pocs

# 2. Copy env template and fill in your keys
cp .env.example .env

# 3. Start a new experiment
./scripts/new-poc.sh experiments my-experiment

# 4. Start a new PoC
./scripts/new-poc.sh pocs my-poc
```

## Experiments vs PoCs

| | Experiments | PoCs |
|---|---|---|
| **Purpose** | Quick idea validation | Structured, shareable proof-of-concept |
| **Scope** | Hours to days | Days to weeks |
| **Tests** | Optional | Encouraged |
| **Docs** | Minimal README | Full README + docs |
| **Next step** | Discard or promote | Promote to its own repo |

## Docs

- [Getting Started](docs/getting-started.md)
- [Conventions](docs/conventions.md)

# PoCs

Structured proof-of-concepts. Each PoC has proper docs, tests, and is a candidate for promotion to its own GitHub repo.

## Active PoCs

| Folder | Description | Status |
|--------|-------------|--------|
| _template | Template — copy this to start | — |

## Starting a New PoC

```bash
./scripts/new-poc.sh pocs <name>
```

## Promoting to Its Own Repo

```bash
cd pocs/<name>
git init
gh repo create eordaxd/<name> --public --source=. --push
```

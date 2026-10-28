# RF Change Validation MCP

A small Python MCP server that lets an AI agent check proposed cellular RF changes against explicit engineering rules before anyone touches the network. Anything the rules don't cover fails closed instead of being guessed.

## Why I built it

A recruiter described an operator team that wanted RF change requests (the data behind an RF data sheet, or RFDS) validated automatically, with AI tools that could not make things up. I built this prototype to show how that could work: domain rules a network engineer would recognise, wrapped in typed MCP tools an agent can call safely.

This is a prototype built on synthetic data. It is not any operator's implementation, a production rules engine, or a full 3GPP validator.

## What it does

| Tool | Checks |
| --- | --- |
| `validate_nr_add` | Duplicate NR-ARFCN on the sector, band and bandwidth limits for n5, n71, n41 and n77, pre-change KPI evidence |
| `validate_carrier_change` | ARFCN actually changes, no simultaneous bandwidth change, spectrum authorisation, neighbour-relation review, pre-change KPIs, rollback plan |
| `server_status` | Reports scope and fail-closed mode |

Every result is structured: `PASS` or `FAIL`, machine-readable reason codes (for example `DUPLICATE_NR_ARFCN`, `ROLLBACK_PLAN_MISSING`) and plain-language messages.

## How it's built

```
MCP client / MCP Inspector
        |  stdio (MCP)
        v
FastMCP server (src/server.py)
        +-- Pydantic request models (typed, validated input)
        +-- deterministic RF rule functions (no model in the loop)
        +-- structured PASS / FAIL results
        +-- pytest regression suite
```

The rule functions are separate from the MCP wrapper, so the engineering logic is tested on its own. Both tools were discovered and called through MCP Inspector with structured inputs and outputs.

## Why it matters

Bad RF changes cost operators outages, drive tests and engineer hours. Letting AI agents help with change review is only useful if they cannot approve something the rules don't support. This pattern (typed inputs, deterministic rules, reason codes, fail-closed) is how you let automation near a live network without letting it guess.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -v            # 16 passed
python -m src.server           # start the MCP server over stdio
```

Tests cover parameterised synthetic scenarios (valid and invalid NR adds, duplicate carriers, unsupported bandwidths, missing KPI evidence, carrier changes, spectrum, neighbour and rollback checks), input validation, and golden-result regression.

Built by [Jeff Taylor](https://jefferyataylor.com).

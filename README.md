\# RFDS MCP Validation Prototype



Small Python prototype demonstrating how an MCP server can expose bounded,

deterministic RF modification validation tools.



This is a learning/prototyping project. It is not a Verizon RFDS implementation,

production rules engine, or complete 3GPP validation system.



\## Purpose



The prototype combines cellular RF domain rules with structured MCP tooling and

fail-closed validation.



Implemented MCP tools:



\- `server\_status`

\- `validate\_nr\_add`

\- `validate\_carrier\_change`



\## Architecture



MCP client / MCP Inspector

&#x20;       |

&#x20;       | stdio / MCP

&#x20;       v

Python FastMCP server

&#x20;       |

&#x20;       +-- Pydantic structured request models

&#x20;       |

&#x20;       +-- deterministic RF validation functions

&#x20;       |

&#x20;       +-- structured PASS / FAIL responses

&#x20;       |

&#x20;       +-- pytest regression suite



RF validation logic is kept separate from the MCP wrapper so the domain rules

can be tested deterministically.



\## RF Scenarios



\### validate\_nr\_add



Bounded NR carrier-add validation including:



\- duplicate NR-ARFCN detection

\- prototype band/bandwidth boundaries

\- pre-change KPI evidence requirement

\- structured PASS/FAIL reason codes



\### validate\_carrier\_change



Bounded LTE/NR carrier-change validation including:



\- ARFCN modification validation

\- rejection of simultaneous bandwidth changes as out of scope

\- spectrum authorization evidence

\- neighbor-relation impact review

\- pre-change KPI evidence

\- rollback-plan requirement



Unsupported or invalid conditions fail closed rather than being inferred.



\## Testing



The project uses `pytest` with:



\- fixtures

\- parameterized synthetic RF scenarios

\- structured-input validation tests

\- golden-scenario regression testing



Current result:



`16 passed`



Synthetic cases include valid and invalid NR adds, duplicate carriers, unsupported

bandwidth combinations, missing KPI evidence, carrier changes, spectrum checks,

neighbor-review checks, and rollback-plan checks.



\## MCP Validation



The server was exercised using MCP Inspector.



Both `validate\_nr\_add` and the subsequently added `validate\_carrier\_change` tool

were discovered and successfully invoked through MCP using structured inputs and

outputs.



\## Run Tests



```powershell

python -m pytest -v


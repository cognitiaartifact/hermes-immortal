# Hermes — Immortal Agent Stack

A self-replicating, memory-persistent AI agent framework.
Holographic memory across 3 layers: vector, graph, hybrid.

## Stack
- **Orchestrator:** DeepSeek API (via Hermes)
- **Memory:** ChromaDB (vector) + NetworkX (graph) + JSON (structured)
- **Tools:** Claude Code skeleton (43 tool schemas)
- **Skills:** Plan → Work → Review → Ship methodology

## Repo Structure
```
hermes-immortal/
├── core/          # Identity, rules, agent config
├── memory/        # Holographic memory layer
├── tools/         # Tool schemas + bridge implementations  
├── skills/        # Reusable skill definitions
├── knowledge/     # Disk-backed knowledge base
├── config/        # Environment + tool configs
└── scripts/       # Automation scripts
```

#!/usr/bin/env python3
"""
Holomorphic memory load — call this at the start of each session
to load relevant context from holographic memory into the agent's working memory.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from holo import HolographicMemory

def load_context(tags=None, days=7, limit=5):
    """Load relevant context from holographic memory."""
    hm = HolographicMemory()
    
    context = hm.recall(query_tags=tags, limit=limit, days=days)
    
    memories = context["vector_memories"]
    if not memories:
        return "No recent memories found."
    
    output = []
    output.append(f"## 🧠 Holographic Context ({len(memories)} memories)")
    output.append("")
    
    for m in memories:
        tags_str = ", ".join(m.get("tags", []))
        ts = m["timestamp"][:19] if "timestamp" in m else "unknown"
        output.append(f"**{m.get('source', 'agent')}** [{ts}]")
        if tags_str:
            output.append(f"*Tags: {tags_str}*")
        output.append(f">{m['text']}")
        output.append("")
    
    return "\n".join(output)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--tags", help="Comma-separated tags to filter by")
    parser.add_argument("--days", type=int, default=7, help="Days of history")
    parser.add_argument("--limit", type=int, default=5, help="Max memories")
    parser.add_argument("--save", help="Save output to file path")
    
    args = parser.parse_args()
    tags = args.tags.split(",") if args.tags else None
    
    output = load_context(tags=tags, days=args.days, limit=args.limit)
    
    if args.save:
        with open(args.save, "w") as f:
            f.write(output)
        print(f"Context saved to {args.save}")
    else:
        print(output)

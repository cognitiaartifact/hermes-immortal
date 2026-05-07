#!/usr/bin/env python3
"""
Seed holographic memory from current session state.
Run periodically to keep memory fresh.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from holo import HolographicMemory

SESSION_LOG = Path.home() / "hermes-knowledge" / "logs" / "current-session.md"

def seed_from_session():
    hm = HolographicMemory()
    
    if not SESSION_LOG.exists():
        print("No session log found")
        return
    
    content = SESSION_LOG.read_text()
    if not content.strip():
        return
    
    # Extract key sections and store as memories with relevant tags
    lines = content.split("\n")
    
    # Look for key markers
    current_section = None
    current_text = []
    tags = []
    
    sections = {
        "Gateway": ["system", "gateway"],
        "Active": ["system", "active"],
        "Cron": ["system", "cron"],
        "Memory": ["system", "memory"],
        "Project": ["project"],
        "Skillucate": ["skillucate"],
        "MoverOS": ["moveros"],
        "Mesh": ["mesh", "agent"],
        "Frank": ["frank", "agent"],
        "Rachel": ["rachel", "agent"],
        "Lucifer": ["lucifer", "agent"],
    }
    
    for line in lines:
        # Check for section headers
        for key, section_tags in sections.items():
            if key.lower() in line.lower() and ("**" in line or "#" in line or ":" in line[:20]):
                # Save previous section
                if current_text and tags:
                    text = "\n".join(current_text).strip()
                    if len(text) > 20:  # Don't store tiny fragments
                        # Check if it's already stored (rough dedup)
                        existing = hm.recall(query_tags=tags, limit=3)
                        stored_already = any(text[:50] in m["text"] for m in existing["vector_memories"])
                        if not stored_already:
                            hm.remember(text[:500], tags=tags, source="session-state")
                
                current_section = key
                tags = section_tags
                current_text = [line]
                break
        else:
            if current_text:
                current_text.append(line)
    
    print(f"Seeded holographic memory from session state")

if __name__ == "__main__":
    seed_from_session()

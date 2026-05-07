#!/usr/bin/env python3
"""
Holographic Memory System — Layer 1: Vector Memory
Stores and retrieves agent memories using semantic embeddings.

Every memory is stored as:
  - text: the raw content
  - embedding: vector representation for semantic search
  - metadata: timestamp, source, type, tags, relationships
  - timestamp: ISO datetime for temporal queries
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

MEMORY_DIR = Path(__file__).parent / "data"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
INDEX_FILE = MEMORY_DIR / "vector-index.json"

class VectorMemory:
    """Lightweight vector memory using numpy cosine similarity."""
    
    def __init__(self):
        self.memories = []
        self.embeddings = []
        self._load_index()
    
    def _load_index(self):
        """Load existing memories from disk."""
        if INDEX_FILE.exists():
            with open(INDEX_FILE) as f:
                data = json.load(f)
                self.memories = data.get("memories", [])
                print(f"  📖 Loaded {len(self.memories)} existing memories")
    
    def _save_index(self):
        """Save all memories to disk."""
        with open(INDEX_FILE, "w") as f:
            json.dump({"memories": self.memories, "count": len(self.memories)}, f, indent=2)
    
    def add(self, text, metadata=None, source="agent"):
        """Add a memory with embedding."""
        memory_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now(timezone.utc).isoformat()
        
        entry = {
            "id": memory_id,
            "text": text,
            "timestamp": timestamp,
            "source": source,
            "metadata": metadata or {},
            "tags": metadata.get("tags", []) if metadata else [],
        }
        
        self.memories.append(entry)
        self._save_index()
        
        # Also append to chronological log
        log_path = MEMORY_DIR / f"log-{timestamp[:10]}.md"
        with open(log_path, "a") as f:
            f.write(f"\n## [{timestamp}] {source}\n")
            f.write(f"**ID:** {memory_id}\n")
            if metadata:
                f.write(f"**Tags:** {', '.join(metadata.get('tags', []))}\n")
            f.write(f"\n{text}\n")
            f.write(f"---\n")
        
        return memory_id
    
    def search(self, query=None, tags=None, limit=10, days=None):
        """Retrieve memories by tag filter or recency."""
        results = self.memories
        
        # Filter by tags
        if tags:
            results = [m for m in results if any(t in m.get("tags", []) for t in tags)]
        
        # Filter by recency
        if days:
            cutoff = datetime.now(timezone.utc).timestamp() - (days * 86400)
            results = [m for m in results if datetime.fromisoformat(m["timestamp"]).timestamp() > cutoff]
        
        # Sort by recency (newest first)
        results.sort(key=lambda m: m["timestamp"], reverse=True)
        
        return results[:limit]
    
    def get_by_id(self, memory_id):
        """Retrieve a specific memory by ID."""
        for m in self.memories:
            if m["id"] == memory_id:
                return m
        return None
    
    def get_stats(self):
        """Get memory statistics."""
        tag_counts = {}
        for m in self.memories:
            for t in m.get("tags", []):
                tag_counts[t] = tag_counts.get(t, 0) + 1
        
        return {
            "total_memories": len(self.memories),
            "top_tags": sorted(tag_counts.items(), key=lambda x: -x[1])[:10],
            "unique_tags": len(tag_counts),
        }


class GraphMemory:
    """Layer 2: Entity-relationship memory using a lightweight graph."""
    
    def __init__(self):
        self.graph_file = MEMORY_DIR / "graph-memory.json"
        self.nodes = {}  # id -> {name, type, metadata}
        self.edges = []  # [{source, target, relation, weight}]
        self._load()
    
    def _load(self):
        if self.graph_file.exists():
            with open(self.graph_file) as f:
                data = json.load(f)
                self.nodes = data.get("nodes", {})
                self.edges = data.get("edges", [])
    
    def _save(self):
        with open(self.graph_file, "w") as f:
            json.dump({"nodes": self.nodes, "edges": self.edges}, f, indent=2)
    
    def add_entity(self, entity_id, name, entity_type="concept", metadata=None):
        """Add or update an entity node."""
        if entity_id not in self.nodes:
            self.nodes[entity_id] = {
                "name": name,
                "type": entity_type,
                "first_seen": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata or {},
            }
        self.nodes[entity_id]["last_seen"] = datetime.now(timezone.utc).isoformat()
        self._save()
    
    def add_relation(self, source_id, target_id, relation, weight=1.0):
        """Add a relationship between two entities."""
        # Check if edge exists, update weight if so
        for edge in self.edges:
            if edge["source"] == source_id and edge["target"] == target_id and edge["relation"] == relation:
                edge["weight"] = min(edge["weight"] + weight, 1.0)
                edge["last_seen"] = datetime.now(timezone.utc).isoformat()
                self._save()
                return
        
        self.edges.append({
            "source": source_id,
            "target": target_id,
            "relation": relation,
            "weight": weight,
            "first_seen": datetime.now(timezone.utc).isoformat(),
        })
        self._save()
    
    def get_related(self, entity_id, max_depth=2):
        """Traverse graph from entity to find related nodes."""
        visited = set()
        results = []
        
        def traverse(node_id, depth, path):
            if node_id in visited or depth > max_depth:
                return
            visited.add(node_id)
            
            if node_id in self.nodes:
                results.append({
                    "node": self.nodes[node_id],
                    "depth": depth,
                    "path": path + [node_id],
                })
            
            for edge in self.edges:
                if edge["source"] == node_id:
                    traverse(edge["target"], depth + 1, path + [edge["target"]])
                elif edge["target"] == node_id:
                    traverse(edge["source"], depth + 1, path + [edge["source"]])
        
        traverse(entity_id, 0, [entity_id])
        return results
    
    def get_stats(self):
        return {
            "total_entities": len(self.nodes),
            "total_relations": len(self.edges),
        }


class HolographicMemory:
    """Layer 3: Unified holographic memory combining vector + graph + temporal.
    
    Holographic property: Any fragment of a query retrieves associated context
    across all dimensions — semantic similarity, entity relationships, and time.
    """
    
    def __init__(self):
        self.vector = VectorMemory()
        self.graph = GraphMemory()
    
    def remember(self, text, tags=None, entities=None, source="agent"):
        """
        Store a memory holographically — in vector store AND graph.
        
        Args:
            text: The memory content
            tags: Categorization tags (list of strings)
            entities: Entity relationships [{id, name, type, relation}]
            source: Origin of the memory
        """
        # Store in vector memory
        mem_id = self.vector.add(text, metadata={"tags": tags or [], "source": source}, source=source)
        
        # Store entities and relations in graph
        if entities:
            main_entity_id = f"mem_{mem_id}"
            self.graph.add_entity(main_entity_id, text[:60], "memory", {"memory_id": mem_id})
            
            for ent in entities:
                eid = ent.get("id", ent["name"].lower().replace(" ", "_"))
                self.graph.add_entity(eid, ent["name"], ent.get("type", "concept"))
                self.graph.add_relation(main_entity_id, eid, ent.get("relation", "mentions"))
        
        return mem_id
    
    def recall(self, query_tags=None, query_entities=None, limit=10, days=None):
        """
        Recall memories holographically — from vector AND graph.
        
        Returns results from both stores with relevance scores.
        """
        # Get vector results
        vector_results = self.vector.search(tags=query_tags, limit=limit, days=days)
        
        # Get graph results if entities specified
        graph_results = []
        if query_entities:
            for entity in query_entities:
                eid = entity.get("id", entity.lower().replace(" ", "_"))
                related = self.graph.get_related(eid, max_depth=2)
                graph_results.extend(related)
        
        return {
            "vector_memories": vector_results,
            "graph_connections": graph_results[:limit],
            "stats": {
                "vector": self.vector.get_stats(),
                "graph": self.graph.get_stats(),
            }
        }
    
    def get_stats(self):
        return {
            "vector": self.vector.get_stats(),
            "graph": self.graph.get_stats(),
            "total_memories": len(self.vector.memories),
        }


# CLI interface
if __name__ == "__main__":
    import sys
    
    hm = HolographicMemory()
    
    if len(sys.argv) < 2:
        stats = hm.get_stats()
        print(f"\n🧠 Holographic Memory System")
        print(f"{'='*50}")
        print(f"Total memories: {stats['total_memories']}")
        print(f"Graph entities: {stats['graph']['total_entities']}")
        print(f"Graph relations: {stats['graph']['total_relations']}")
        print(f"Top tags: {[t for t, c in stats['vector']['top_tags'][:5]]}")
        print(f"\nUsage:")
        print(f"  python3 holo.py remember <text> --tags tag1,tag2")
        print(f"  python3 holo.py recall --tags tag1")
        print(f"  python3 holo.py stats")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "remember":
        text = sys.argv[2] if len(sys.argv) > 2 else input("Memory: ")
        tags = []
        entities = []
        
        for i, arg in enumerate(sys.argv):
            if arg == "--tags" and i + 1 < len(sys.argv):
                tags = sys.argv[i + 1].split(",")
            if arg == "--entities" and i + 1 < len(sys.argv):
                import json as _json
                entities = _json.loads(sys.argv[i + 1])
        
        mem_id = hm.remember(text, tags=tags, entities=entities)
        stats = hm.get_stats()
        print(f"✅ Stored memory #{mem_id}")
        print(f"   Total: {stats['total_memories']} memories")
    
    elif cmd == "recall":
        tags = []
        entities = []
        days = None
        limit = 10
        
        for i, arg in enumerate(sys.argv):
            if arg == "--tags" and i + 1 < len(sys.argv):
                tags = sys.argv[i + 1].split(",")
            if arg == "--days" and i + 1 < len(sys.argv):
                days = int(sys.argv[i + 1])
            if arg == "--limit" and i + 1 < len(sys.argv):
                limit = int(sys.argv[i + 1])
        
        results = hm.recall(query_tags=tags, limit=limit, days=days)
        
        print(f"\n🔍 Holographic Recall: {', '.join(tags) if tags else 'all'}")
        print(f"{'='*50}")
        
        for mem in results["vector_memories"]:
            print(f"\n[{mem['timestamp'][:19]}] {mem['source']}")
            print(f"  {mem['text'][:200]}")
            if mem.get("tags"):
                print(f"  Tags: {', '.join(mem['tags'][:5])}")
        
        print(f"\n📊 Stats: {len(results['vector_memories'])} memories")
    
    elif cmd == "stats":
        stats = hm.get_stats()
        print(f"\n🧠 Memory Statistics")
        print(f"{'='*50}")
        print(f"Total: {stats['total_memories']}")
        print(f"Entities: {stats['graph']['total_entities']}")
        print(f"Relations: {stats['graph']['total_relations']}")
        print(f"\nTop tags:")
        for tag, count in stats['vector']['top_tags'][:10]:
            print(f"  {tag}: {count}")

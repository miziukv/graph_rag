from typing import List, Dict


def rerank(results: List[Dict], top_k: int = 10) -> List[Dict]:
    """
    Rerank search results by relevance.
    
    Simple scoring based on:
    - Vector similarity score (from initial search)
    - Number of entity connections (graph richness)
    - Boost for results with more context
    
    Args:
        results: List of search results from Neo4j
        top_k: Number of top results to return
        
    Returns:
        Reranked results sorted by combined score
    """
    scored_results = []
    
    for result in results:
        score = calculate_score(result)
        scored_results.append({
            **result,
            "rerank_score": score
        })
    
    # Sort by score descending
    scored_results.sort(key=lambda x: x["rerank_score"], reverse=True)
    
    return scored_results[:top_k]


def calculate_score(result: Dict) -> float:
    """
    Calculate relevance score for a single result.
    
    Scoring factors:
    - Base similarity score (0-1) - weight: 0.6
    - Entity count (normalized) - weight: 0.2
    - Relationship count (normalized) - weight: 0.2
    
    Args:
        result: Single search result
        
    Returns:
        Combined relevance score (0-1)
    """
    # Get base similarity score (from vector search)
    similarity_score = result.get("score", 0.5)
    
    # Count entities mentioned in this chunk
    entity_count = len(result.get("entities", []))
    
    # Count relationships connected to these entities
    relationship_count = len(result.get("relationships", []))
    
    # Normalize entity and relationship counts (sigmoid-like)
    # More entities/relationships = richer context
    entity_score = min(entity_count / 10, 1.0)  # Cap at 10 entities
    relationship_score = min(relationship_count / 15, 1.0)  # Cap at 15 relationships
    
    # Weighted combination
    combined_score = (
        0.6 * similarity_score +
        0.2 * entity_score +
        0.2 * relationship_score
    )
    
    return combined_score


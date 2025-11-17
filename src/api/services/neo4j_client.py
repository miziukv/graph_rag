from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
from typing import List, Dict, Any

load_dotenv()

URI = os.getenv('NEO4J_URI')
AUTH = (os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))


class Neo4jClient:
    """
    A reusable Neo4j client that manages connection lifecycle.
    Create once, use throughout the app.
    """
    
    def __init__(self):
        self.driver = None
        
    def connect(self):
        """Initialize the connection to Neo4j"""
        if not self.driver:
            self.driver = GraphDatabase.driver(URI, auth=AUTH)
            self.driver.verify_connectivity()
            print("Connected to Neo4j")
    
    def close(self):
        """Close the connection when app shuts down"""
        if self.driver:
            self.driver.close()
            print("Disconnected from Neo4j")
    
    def query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict]:
        """
        Execute a Cypher query and return results.
        
        Args:
            query: Cypher query string
            parameters: Query parameters (optional)
            
        Returns:
            List of records as dictionaries
        """
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def write(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict]:
        """
        Execute a write query (CREATE, MERGE, etc.)
        
        Args:
            query: Cypher query string
            parameters: Query parameters (optional)
            
        Returns:
            List of records as dictionaries
        """
        with self.driver.session() as session:
            result = session.execute_write(
                lambda tx: tx.run(query, parameters or {}).data()
            )
            return result
    
    def read(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict]:
        """
        Execute a read query (MATCH, etc.) with read transaction
        
        Args:
            query: Cypher query string
            parameters: Query parameters (optional)
            
        Returns:
            List of records as dictionaries
        """
        with self.driver.session() as session:
            result = session.execute_read(
                lambda tx: tx.run(query, parameters or {}).data()
            )
            return result
    
    def create_vector_index(self, index_name: str, label: str, property_name: str, dimensions: int = 1536):
        """
        Create a vector index for similarity search.
        
        Args:
            index_name: Name of the index
            label: Node label to index
            property_name: Property containing embeddings
            dimensions: Embedding dimensions (1536 for text-embedding-3-small)
        """
        query = f"""
        CREATE VECTOR INDEX {index_name} IF NOT EXISTS
        FOR (n:{label})
        ON n.{property_name}
        OPTIONS {{
            indexConfig: {{
                `vector.dimensions`: {dimensions},
                `vector.similarity_function`: 'cosine'
            }}
        }}
        """
        self.query(query)
        print(f"Created vector index: {index_name}")
    
    def vector_search(self, index_name: str, query_vector: List[float], limit: int = 10) -> List[Dict]:
        """
        Perform vector similarity search.
        
        Args:
            index_name: Name of the vector index
            query_vector: Embedding vector to search with
            limit: Number of results to return
            
        Returns:
            List of similar nodes with scores
        """
        query = """
        CALL db.index.vector.queryNodes($index_name, $limit, $query_vector)
        YIELD node, score
        RETURN node, score
        ORDER BY score DESC
        """
        return self.read(query, {
            'index_name': index_name,
            'query_vector': query_vector,
            'limit': limit
        })


# Create a singleton instance that can be imported everywhere
neo4j_client = Neo4jClient()
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List

client = OpenAI()


class Entity(BaseModel):
    """An entity extracted from text."""
    name: str = Field(description="Entity name")
    type: str = Field(description="Entity type (Person, Organization, Location, Concept, etc.)")


class Relationship(BaseModel):
    """A relationship between two entities."""
    source: str = Field(description="Source entity name")
    target: str = Field(description="Target entity name")
    type: str = Field(description="Relationship type (uppercase verb, e.g., WORKS_FOR, INVENTED)")


class ExtractionResult(BaseModel):
    """Result of entity and relationship extraction."""
    entities: List[Entity] = Field(description="List of extracted entities")
    relationships: List[Relationship] = Field(description="List of relationships between entities")


def extract(text: str, model: str = "gpt-4o-mini") -> ExtractionResult:
    """
    Extract entities and relationships from text using structured outputs.
    
    Args:
        text: Text to extract from
        model: OpenAI model to use
        
    Returns:
        ExtractionResult with validated entities and relationships
    """
    prompt = f"""Extract all entities and relationships from the text below.

Rules:
- Extract meaningful entities (people, places, organizations, concepts, events)
- Create relationships that show how entities connect
- Use clear, consistent naming
- Relationship types should be verbs in uppercase (WORKS_FOR, INVENTED, LOCATED_IN, etc.)

Text:
{text}
"""
    
    response = client.beta.chat.completions.parse(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format=ExtractionResult
    )
    
    return response.choices[0].message.parsed


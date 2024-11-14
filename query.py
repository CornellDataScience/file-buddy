import os
from pinecone import Pinecone
from openai import OpenAI
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

LOGGER = logging.getLogger(__name__)
app = FastAPI()

class SearchResult(BaseModel):
    filename: str
    path: str
    score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]

class SearchQuery(BaseModel):
    query: str

def search_files(query_text: str, client: OpenAI, index) -> Optional[List[SearchResult]]:
    """Execute semantic search against the vector database."""
    try:
        # Get embedding for query
        query_embedding = client.embeddings.create(
            input=query_text,
            model="text-embedding-3-small"
        ).data[0].embedding
        
        # Search with user_id filter
        results = index.query(
            vector=query_embedding,
            filter={
                "user_id": os.getenv('USER_ID')
            },
            top_k=5,
            include_metadata=True
        )
        
        if not results or not results.matches:
            return []
            
        return [
            SearchResult(
                filename=match.metadata['filename'],
                path=match.metadata['path'],
                score=match.score
            )
            for match in results.matches
        ]
    except Exception as e:
        LOGGER.error(f"Error during search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Initialize clients
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('PINECONE_INDEX_NAME'))
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app.post("/search", response_model=SearchResponse)
async def search_endpoint(query: SearchQuery):
    """API endpoint for semantic search"""
    results = search_files(query.query, client, index)
    return SearchResponse(results=results)
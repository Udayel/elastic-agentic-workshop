#!/usr/bin/env python3
"""
Elastic MCP Server - FastMCP implementation
Exposes Elasticsearch capabilities as MCP tools for agent consumption
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from elasticsearch import Elasticsearch, AsyncElasticsearch
from elastic_apm import Client as APMClient
import structlog

# Initialize structured logging
logger = structlog.get_logger(__name__)

# FastAPI app
app = FastAPI(
    title="Elastic MCP Server",
    description="Model Context Protocol server for Elasticsearch",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Elasticsearch client (initialized on startup)
es_client: Optional[Elasticsearch] = None
es_async_client: Optional[AsyncElasticsearch] = None
apm_client: Optional[APMClient] = None


class ToolRequest(BaseModel):
    """MCP tool call request"""
    name: str = Field(..., description="Tool name to execute")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")


class ToolResponse(BaseModel):
    """MCP tool call response"""
    content: List[Dict[str, Any]] = Field(..., description="Response content")
    isError: bool = Field(default=False, description="Whether an error occurred")


class ToolDefinition(BaseModel):
    """MCP tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


class ListToolsResponse(BaseModel):
    """MCP tools/list response"""
    tools: List[ToolDefinition]


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Verify OAuth2 Bearer token
    In production, this validates against Cognito
    """
    token = credentials.credentials

    # TODO: Implement Cognito token validation
    # For now, accept any bearer token (development only)
    # In production: verify JWT signature, expiry, audience

    if not token:
        raise HTTPException(status_code=401, detail="Invalid token")

    return token


@app.on_event("startup")
async def startup_event():
    """Initialize Elasticsearch clients on startup"""
    global es_client, es_async_client, apm_client

    es_url = os.getenv("ES_URL")
    es_api_key = os.getenv("ES_API_KEY")

    if not es_url or not es_api_key:
        raise RuntimeError("ES_URL and ES_API_KEY must be set")

    # Initialize sync client
    es_client = Elasticsearch(
        es_url,
        api_key=es_api_key,
        verify_certs=True,
        request_timeout=30
    )

    # Initialize async client
    es_async_client = AsyncElasticsearch(
        es_url,
        api_key=es_api_key,
        verify_certs=True,
        request_timeout=30
    )

    # Initialize APM client
    apm_client = APMClient(
        service_name="elastic-mcp-server",
        server_url=es_url.replace(":443", ":8200"),  # APM typically on port 8200
        environment=os.getenv("ENVIRONMENT", "development")
    )

    # Test connection
    try:
        info = es_client.info()
        logger.info("elasticsearch_connected", cluster_name=info["cluster_name"])
    except Exception as e:
        logger.error("elasticsearch_connection_failed", error=str(e))
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global es_client, es_async_client

    if es_client:
        es_client.close()
    if es_async_client:
        await es_async_client.close()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        es_client.cluster.health()
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Unhealthy: {str(e)}")


@app.get("/mcp/tools/list")
async def list_tools(token: str = Depends(verify_token)) -> ListToolsResponse:
    """
    MCP endpoint: List available tools
    Per MCP spec: GET /tools/list
    """
    tools = [
        ToolDefinition(
            name="elasticsearch_search",
            description="Search Elasticsearch using query DSL. Supports full-text, semantic (ELSER), and KNN vector search.",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "string",
                        "description": "Index name to search"
                    },
                    "query": {
                        "type": "object",
                        "description": "Elasticsearch Query DSL"
                    },
                    "size": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 10
                    }
                },
                "required": ["index", "query"]
            }
        ),
        ToolDefinition(
            name="elasticsearch_elser_search",
            description="Semantic search using ELSER v2. Zero-shot, cross-lingual semantic search without training.",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "string",
                        "description": "Index name with ELSER embeddings"
                    },
                    "query_text": {
                        "type": "string",
                        "description": "Natural language query"
                    },
                    "embedding_field": {
                        "type": "string",
                        "description": "Field containing ELSER embeddings",
                        "default": "text_embedding"
                    },
                    "size": {
                        "type": "integer",
                        "description": "Number of results",
                        "default": 5
                    }
                },
                "required": ["index", "query_text"]
            }
        ),
        ToolDefinition(
            name="elasticsearch_knn_search",
            description="K-nearest neighbors vector search. Find similar documents using vector embeddings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "string",
                        "description": "Index name with vector embeddings"
                    },
                    "field": {
                        "type": "string",
                        "description": "Vector field name"
                    },
                    "query_vector": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Query vector"
                    },
                    "k": {
                        "type": "integer",
                        "description": "Number of neighbors",
                        "default": 10
                    },
                    "num_candidates": {
                        "type": "integer",
                        "description": "Candidate pool size",
                        "default": 100
                    }
                },
                "required": ["index", "field", "query_vector"]
            }
        ),
        ToolDefinition(
            name="elasticsearch_index_document",
            description="Index a document into Elasticsearch",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "string",
                        "description": "Index name"
                    },
                    "document": {
                        "type": "object",
                        "description": "Document to index"
                    },
                    "id": {
                        "type": "string",
                        "description": "Document ID (optional)"
                    }
                },
                "required": ["index", "document"]
            }
        ),
        ToolDefinition(
            name="elasticsearch_get_document",
            description="Retrieve a document by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "string",
                        "description": "Index name"
                    },
                    "id": {
                        "type": "string",
                        "description": "Document ID"
                    }
                },
                "required": ["index", "id"]
            }
        ),
        ToolDefinition(
            name="elasticsearch_aggregation",
            description="Run aggregations for analytics and statistics",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "string",
                        "description": "Index name"
                    },
                    "aggregations": {
                        "type": "object",
                        "description": "Aggregation DSL"
                    },
                    "query": {
                        "type": "object",
                        "description": "Optional query to filter data"
                    }
                },
                "required": ["index", "aggregations"]
            }
        ),
        ToolDefinition(
            name="elasticsearch_create_index",
            description="Create a new index with mappings",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "string",
                        "description": "Index name"
                    },
                    "mappings": {
                        "type": "object",
                        "description": "Index mappings"
                    },
                    "settings": {
                        "type": "object",
                        "description": "Index settings"
                    }
                },
                "required": ["index"]
            }
        ),
        ToolDefinition(
            name="apm_capture_transaction",
            description="Capture APM transaction for monitoring",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Transaction name"
                    },
                    "transaction_type": {
                        "type": "string",
                        "description": "Transaction type"
                    },
                    "duration": {
                        "type": "number",
                        "description": "Duration in milliseconds"
                    },
                    "result": {
                        "type": "string",
                        "description": "Transaction result"
                    }
                },
                "required": ["name", "transaction_type"]
            }
        )
    ]

    return ListToolsResponse(tools=tools)


@app.post("/mcp/tools/call")
async def call_tool(
    request: ToolRequest,
    token: str = Depends(verify_token)
) -> ToolResponse:
    """
    MCP endpoint: Execute a tool
    Per MCP spec: POST /tools/call
    """
    tool_name = request.name
    args = request.arguments

    logger.info("tool_call", tool=tool_name, arguments=args)

    try:
        if tool_name == "elasticsearch_search":
            result = await _elasticsearch_search(args)
        elif tool_name == "elasticsearch_elser_search":
            result = await _elasticsearch_elser_search(args)
        elif tool_name == "elasticsearch_knn_search":
            result = await _elasticsearch_knn_search(args)
        elif tool_name == "elasticsearch_index_document":
            result = await _elasticsearch_index_document(args)
        elif tool_name == "elasticsearch_get_document":
            result = await _elasticsearch_get_document(args)
        elif tool_name == "elasticsearch_aggregation":
            result = await _elasticsearch_aggregation(args)
        elif tool_name == "elasticsearch_create_index":
            result = await _elasticsearch_create_index(args)
        elif tool_name == "apm_capture_transaction":
            result = await _apm_capture_transaction(args)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

        return ToolResponse(
            content=[{
                "type": "text",
                "text": str(result)
            }],
            isError=False
        )

    except Exception as e:
        logger.error("tool_call_failed", tool=tool_name, error=str(e))
        return ToolResponse(
            content=[{
                "type": "text",
                "text": f"Error: {str(e)}"
            }],
            isError=True
        )


async def _elasticsearch_search(args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Elasticsearch search"""
    index = args["index"]
    query = args["query"]
    size = args.get("size", 10)

    result = es_client.search(
        index=index,
        body={"query": query, "size": size}
    )

    return {
        "total": result["hits"]["total"]["value"],
        "hits": [
            {
                "id": hit["_id"],
                "score": hit["_score"],
                "source": hit["_source"]
            }
            for hit in result["hits"]["hits"]
        ]
    }


async def _elasticsearch_elser_search(args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute ELSER semantic search"""
    index = args["index"]
    query_text = args["query_text"]
    embedding_field = args.get("embedding_field", "text_embedding")
    size = args.get("size", 5)

    result = es_client.search(
        index=index,
        body={
            "query": {
                "text_expansion": {
                    embedding_field: {
                        "model_id": ".elser_model_2",
                        "model_text": query_text
                    }
                }
            },
            "size": size
        }
    )

    return {
        "total": result["hits"]["total"]["value"],
        "hits": [
            {
                "id": hit["_id"],
                "score": hit["_score"],
                "source": hit["_source"]
            }
            for hit in result["hits"]["hits"]
        ]
    }


async def _elasticsearch_knn_search(args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute KNN vector search"""
    index = args["index"]
    field = args["field"]
    query_vector = args["query_vector"]
    k = args.get("k", 10)
    num_candidates = args.get("num_candidates", 100)

    result = es_client.search(
        index=index,
        body={
            "knn": {
                "field": field,
                "query_vector": query_vector,
                "k": k,
                "num_candidates": num_candidates
            }
        }
    )

    return {
        "total": result["hits"]["total"]["value"],
        "hits": [
            {
                "id": hit["_id"],
                "score": hit["_score"],
                "source": hit["_source"]
            }
            for hit in result["hits"]["hits"]
        ]
    }


async def _elasticsearch_index_document(args: Dict[str, Any]) -> Dict[str, Any]:
    """Index a document"""
    index = args["index"]
    document = args["document"]
    doc_id = args.get("id")

    if doc_id:
        result = es_client.index(index=index, id=doc_id, document=document)
    else:
        result = es_client.index(index=index, document=document)

    return {
        "result": result["result"],
        "id": result["_id"],
        "index": result["_index"]
    }


async def _elasticsearch_get_document(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get a document by ID"""
    index = args["index"]
    doc_id = args["id"]

    result = es_client.get(index=index, id=doc_id)

    return {
        "found": result["found"],
        "source": result.get("_source", {})
    }


async def _elasticsearch_aggregation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute aggregation"""
    index = args["index"]
    aggregations = args["aggregations"]
    query = args.get("query", {"match_all": {}})

    result = es_client.search(
        index=index,
        body={
            "query": query,
            "aggs": aggregations,
            "size": 0
        }
    )

    return {
        "aggregations": result.get("aggregations", {})
    }


async def _elasticsearch_create_index(args: Dict[str, Any]) -> Dict[str, Any]:
    """Create an index"""
    index = args["index"]
    mappings = args.get("mappings", {})
    settings = args.get("settings", {})

    body = {}
    if mappings:
        body["mappings"] = mappings
    if settings:
        body["settings"] = settings

    result = es_client.indices.create(index=index, body=body)

    return {
        "acknowledged": result["acknowledged"],
        "index": result["index"]
    }


async def _apm_capture_transaction(args: Dict[str, Any]) -> Dict[str, Any]:
    """Capture APM transaction"""
    name = args["name"]
    transaction_type = args["transaction_type"]
    duration = args.get("duration")
    result = args.get("result", "success")

    # In production, use apm_client.begin_transaction() / end_transaction()
    # For now, log the transaction

    logger.info(
        "apm_transaction",
        name=name,
        type=transaction_type,
        duration=duration,
        result=result
    )

    return {
        "captured": True,
        "name": name,
        "type": transaction_type
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("MCP_SERVER_PORT", 8000))
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

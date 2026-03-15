# MCP (Incubation) vs OpenAI Agents SDK (Production) - Comparison

**Document Purpose:** Detail the key differences between incubation-phase MCP tools and production-phase OpenAI Agents SDK tools.

---

## Overview Table

| Aspect | MCP (Incubation) | OpenAI Agents SDK (Production) |
|--------|------------------|-------------------------------|
| **Framework** | Model Context Protocol | OpenAI Agents SDK |
| **Location** | `src/mcp_server.py` | `production/agent/tools.py` |
| **Decorator** | `@server.call_tool()` | `@function_tool()` |
| **Input Validation** | Manual dict parsing | Pydantic BaseModel |
| **Error Handling** | Basic try/except | Comprehensive with graceful fallbacks |
| **Storage** | In-memory dict | PostgreSQL (asyncpg) |
| **Search** | Keyword string matching | pgvector similarity search |
| **Logging** | Print statements | Structured logging (logger.error) |
| **Documentation** | Minimal docstrings | Detailed LLM usage guides |

---

## 1. Input Validation

### MCP (Incubation)
```python
# Manual dict parsing with no validation
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name == "create_ticket":
        customer_id = arguments.get("customer_id", "")  # No validation
        issue = arguments.get("issue", "")  # No length check
        priority = arguments.get("priority", "medium")  # No enum check
        channel_str = arguments.get("channel", "email")  # String, not enum
```

**Problems:**
- No type validation (string could be int, None, etc.)
- No length constraints (issue could be 100KB)
- No enum enforcement (priority could be "urgent!!")
- Silent defaults mask missing required fields

### OpenAI Agents SDK (Production)
```python
# Pydantic BaseModel with comprehensive validation
class TicketInput(BaseModel):
    customer_id: str = Field(..., min_length=1, max_length=255)
    issue: str = Field(..., min_length=10, max_length=5000)
    priority: str = Field(default="medium")
    channel: Channel = Field(...)  # Enum validation
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if v.lower() not in valid_priorities:
            raise ValueError(f'Priority must be one of: {valid_priorities}')
        return v.lower()

# Tool receives validated model
async def create_ticket(input: TicketInput) -> str:
    # input.customer_id is guaranteed to be valid string
    # input.issue is guaranteed to be 10-5000 chars
    # input.priority is guaranteed to be valid enum value
```

**Benefits:**
- Automatic type validation
- Length constraints enforced
- Enum values validated
- Custom validators for business rules
- Clear error messages for invalid input

---

## 2. Error Handling

### MCP (Incubation)
```python
# Basic error handling
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "search_knowledge_base":
        query = arguments.get("query", "")
        results = search_docs(query)
        if not results:
            return [TextContent(type="text", text="No results found.")]
        # No try/except - crashes on file not found
```

**Problems:**
- No exception handling
- Crashes on missing files
- No graceful degradation
- User sees stack traces

### OpenAI Agents SDK (Production)
```python
# Comprehensive error handling with graceful fallbacks
@function_tool(name="search_knowledge_base", description="...")
async def search_knowledge_base(input: KnowledgeSearchInput) -> str:
    try:
        logger.info(f"Searching knowledge base: query='{input.query[:50]}...'")
        
        results = await vector_search_knowledge_base(
            query=input.query,
            max_results=input.max_results,
            category=input.category
        )
        
        if not results:
            # Graceful fallback message
            return "No relevant documentation found for your query. Let me connect you with a team member who can provide more detailed assistance."
        
        return f"Based on our documentation:\n\n{formatted_results}"
        
    except Exception as e:
        # Log error for debugging
        logger.error(f"Knowledge base search failed: {e}")
        # Return helpful fallback instead of crashing
        return "I'm having trouble accessing our documentation right now. Let me help you based on my training, or I can connect you with a team member for detailed assistance."
```

**Benefits:**
- Never crashes - always returns helpful message
- Errors logged for debugging
- User gets actionable fallback
- System remains stable under errors

---

## 3. Database/Storage

### MCP (Incubation)
```python
# In-memory dict storage
tickets: dict[str, dict[str, Any]] = {}
customer_history: dict[str, list[dict[str, Any]]] = {}
escalations: dict[str, dict[str, Any]] = {}

async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "create_ticket":
        ticket_id = str(uuid.uuid4())
        ticket = {
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "issue": issue,
            # ... stored in memory only
        }
        tickets[ticket_id] = ticket  # Lost on restart
```

**Problems:**
- Data lost on process restart
- No persistence across deployments
- No concurrent access handling
- No query capabilities
- No backup/recovery

### OpenAI Agents SDK (Production)
```python
# PostgreSQL with asyncpg connection pool
async def get_db_pool():
    global _db_pool
    if _db_pool is None:
        _db_pool = await asyncpg.create_pool(
            dsn=os.getenv("DATABASE_URL"),
            min_size=2,
            max_size=10
        )
    return _db_pool

async def create_ticket(input: TicketInput) -> str:
    pool = await get_db_pool()
    
    # Calculate SLA deadline
    sla_deadline = datetime.utcnow() + timedelta(
        hours=sla_hours.get(input.priority, 24)
    )
    
    ticket_id = f"tkt_{uuid.uuid4().hex[:12]}"
    
    if pool:
        # PostgreSQL insert with transaction
        await pool.execute("""
            INSERT INTO tickets (
                ticket_id, customer_id, issue, priority, 
                channel, status, sla_deadline
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, ticket_id, input.customer_id, input.issue, 
            input.priority, input.channel.value, "open", sla_deadline)
```

**Benefits:**
- Persistent storage
- Survives restarts/deployments
- Concurrent access safe
- Complex queries supported
- Backup/recovery available
- SLA tracking enabled

---

## 4. Search Method

### MCP (Incubation)
```python
# Simple keyword string matching
def search_docs(query: str, top_k: int = 3) -> list:
    content = load_product_docs()  # Load entire file
    sections = parse_sections(content)
    
    query_terms = query.lower().split()
    results = []
    
    for section, content in sections.items():
        content_lower = content.lower()
        # Exact keyword match only
        score = sum(1 for term in query_terms if term in content_lower)
        
        if score > 0:
            results.append((section, excerpt, score))
    
    return sorted(results, key=lambda x: x[2], reverse=True)[:top_k]
```

**Problems:**
- Exact keyword match only
- No semantic understanding
- "reset password" ≠ "forgot password"
- No typo tolerance
- No relevance ranking beyond keyword count

### OpenAI Agents SDK (Production)
```python
# pgvector cosine similarity search
async def vector_search_knowledge_base(query: str, max_results: int = 5) -> List[Dict]:
    pool = await get_db_pool()
    
    if pool is None:
        return _keyword_search_fallback(query, max_results)
    
    # Generate embedding for query
    embedding = await _generate_embedding(query)
    
    # Cosine similarity search
    results = await pool.fetch("""
        SELECT section, content,
               1 - (embedding <=> $1::vector) as similarity
        FROM knowledge_base
        ORDER BY embedding <=> $1::vector
        LIMIT $2
    """, embedding, max_results)
    
    return [
        {
            "section": r["section"],
            "content": r["content"][:500],
            "similarity_score": float(r["similarity"])
        }
        for r in results
    ]
```

**Benefits:**
- Semantic understanding
- "reset password" ≈ "forgot password" ≈ "can't login"
- Typo tolerant
- Relevance scores
- Falls back to keyword search if vector unavailable

---

## 5. Logging

### MCP (Incubation)
```python
# Print statements
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "escalate_to_human":
        ticket_id = arguments.get("ticket_id", "")
        reason = arguments.get("reason", "")
        print(f"Escalating ticket {ticket_id} for reason {reason}")  # Print
        # No error logging
```

**Problems:**
- No log levels (info/warning/error)
- No structured format
- No log aggregation
- No search/filter capabilities
- Production debugging impossible

### OpenAI Agents SDK (Production)
```python
# Structured logging with levels
@function_tool(name="escalate_to_human", description="...")
async def escalate_to_human(input: EscalationInput) -> str:
    try:
        # Info level for normal operations
        logger.info(f"Escalating ticket: {input.ticket_id}, reason='{input.reason[:50]}...', urgency={input.urgency}")
        
        # ... escalation logic ...
        
        logger.info(f"Ticket {input.ticket_id} escalated to {team}")
        
    except Exception as e:
        # Error level with full traceback
        logger.error(f"Failed to escalate ticket {input.ticket_id}: {e}", exc_info=True)
        # Graceful fallback
        return f"Escalation requested for ticket {input.ticket_id}..."
```

**Benefits:**
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Structured format (JSON)
- Aggregation ready (ELK, Splunk)
- Searchable/filterable
- Traceback on errors
- Production debugging enabled

---

## 6. Documentation

### MCP (Incubation)
```python
# Minimal docstrings
async def search_knowledge_base(query: str) -> str:
    """Search product docs."""
    # No usage guidance for LLM
```

**Problems:**
- No guidance for LLM agent
- When to use not specified
- Expected output not documented
- Edge cases not covered

### OpenAI Agents SDK (Production)
```python
@function_tool(
    name="search_knowledge_base",
    description="""
Search the TechCorp product documentation for relevant information using vector similarity.

WHEN TO USE THIS TOOL:
- Customer asks a product-related question (how to reset password, how to integrate with Slack, etc.)
- Customer needs factual information from documentation
- You need to verify information before providing a response
- Customer reports an issue that may have documented troubleshooting steps

DO NOT USE THIS TOOL:
- For pricing inquiries (escalate to Sales Team)
- For refund requests (escalate to Billing Team)
- When customer explicitly requests human agent

SEARCH STRATEGY:
1. Use specific keywords from customer's question
2. If first search returns no results, try rephrasing with synonyms
3. Maximum 2 search attempts before considering escalation
4. Category filter can narrow results (billing, technical, api, integrations, etc.)

EXPECTED OUTPUT:
- Formatted string with relevant sections and excerpts
- Includes relevance scores for each result
- Returns helpful message if no results found
"""
)
async def search_knowledge_base(input: KnowledgeSearchInput) -> str:
    """
    Search product documentation using vector similarity search.
    
    INCUBATION EQUIVALENT: search_knowledge_base in src/mcp_server.py
    - Incubation: Simple keyword matching, returns formatted string
    - Production: pgvector similarity search, Pydantic validation, graceful fallback
    
    Args:
        input: KnowledgeSearchInput with query, max_results, category
        
    Returns:
        Formatted string with search results or fallback message
    """
```

**Benefits:**
- Clear usage guidance for LLM
- When to use explicitly stated
- When NOT to use documented
- Search strategy documented
- Expected output described
- Incubation equivalent noted for traceability

---

## Summary: Key Production Upgrades

| Upgrade | Impact |
|---------|--------|
| **Pydantic Validation** | Prevents invalid inputs, clear error messages |
| **Graceful Error Handling** | System never crashes, always helpful |
| **PostgreSQL Storage** | Persistent, queryable, concurrent-safe |
| **Vector Search** | Semantic understanding, typo tolerant |
| **Structured Logging** | Production debugging, monitoring |
| **LLM Documentation** | Agent uses tools correctly |

---

## Migration Checklist

For each tool migrated from MCP to Production:

- [ ] Create Pydantic input model
- [ ] Add field validators
- [ ] Wrap in try/except with logger.error()
- [ ] Replace dict storage with asyncpg calls
- [ ] Replace keyword search with pgvector
- [ ] Add detailed docstring with "WHEN TO USE" section
- [ ] Add graceful fallback messages
- [ ] Add SLA tracking (if applicable)
- [ ] Add Kafka event publishing (if applicable)
- [ ] Test with invalid inputs
- [ ] Test with database unavailable
- [ ] Test with vector search unavailable

---

**End of Comparison Document**

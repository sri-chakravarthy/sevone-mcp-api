# SevOne API Expert Mode - Efficiency Design Proposal

## Current Problem Analysis

### Issue
Every request in Bob chat using the `sevone-api-expert` mode currently:
1. Reads the entire 64,774-line `swagger.json` file (via `read_file` tool)
2. Parses and processes the complete API specification
3. Then uses the MCP tool to perform the actual API call

This creates significant inefficiency for frequently used operations.

### Performance Impact
- **File Size**: 64,774 lines of JSON
- **Processing Overhead**: Full Swagger parsing on every request
- **Token Cost**: Large context window consumption
- **Latency**: Unnecessary delay for common operations

---

## Proposed Design Solutions

### Solution 1: **Intelligent Caching Layer with MCP Resources**

#### Architecture
Add MCP resources to expose pre-processed API documentation:

```
MCP Server Enhancement:
├── Resources (New)
│   ├── common-endpoints (frequently used endpoints)
│   ├── endpoint-index (searchable endpoint catalog)
│   └── api-categories (grouped by functionality)
└── Tools (Existing)
    └── run_api_endpoint
```

#### Implementation Details

**1. Add MCP Resources to Server**
```python
# src/resources/api_catalog.py
class APICatalog:
    """Pre-processed API endpoint catalog"""
    
    COMMON_ENDPOINTS = {
        "devices": {
            "list": {"method": "GET", "path": "/api/v3/devices"},
            "get": {"method": "GET", "path": "/api/v3/devices/{id}"},
            "create": {"method": "POST", "path": "/api/v3/devices"},
            "update": {"method": "PUT", "path": "/api/v3/devices/{id}"},
            "delete": {"method": "DELETE", "path": "/api/v3/devices/{id}"}
        },
        "metadata": {
            "get": {"method": "GET", "path": "/api/v3/entity/{type}/id/{id}/metadata"},
            "update": {"method": "PUT", "path": "/api/v3/entity/{type}/id/{id}/metadata"}
        },
        "alerts": {
            "list_policies": {"method": "GET", "path": "/api/v3/alerts/policies"},
            "get_policy": {"method": "GET", "path": "/api/v3/alerts/policies/{id}"}
        },
        "objects": {
            "list": {"method": "GET", "path": "/api/v3/objects"},
            "get": {"method": "GET", "path": "/api/v3/objects/{id}"}
        }
    }
    
    @staticmethod
    def get_endpoint_info(category: str, operation: str):
        """Quick lookup for common operations"""
        return APICatalog.COMMON_ENDPOINTS.get(category, {}).get(operation)
```

**2. Expose as MCP Resources**
```python
# In server.py
@server.list_resources()
async def list_resources():
    return [
        Resource(
            uri="sevone://api/common-endpoints",
            name="Common SevOne API Endpoints",
            description="Frequently used API endpoints with quick reference",
            mimeType="application/json"
        ),
        Resource(
            uri="sevone://api/endpoint-index",
            name="Complete Endpoint Index",
            description="Searchable index of all API endpoints",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def read_resource(uri: str):
    if uri == "sevone://api/common-endpoints":
        return json.dumps(APICatalog.COMMON_ENDPOINTS, indent=2)
    elif uri == "sevone://api/endpoint-index":
        return json.dumps(load_endpoint_index(), indent=2)
```

**3. Update Custom Mode Instructions**
```yaml
customInstructions: |
  EFFICIENCY STRATEGY:
  
  1. **Check Common Operations First**
     - Access the `sevone://api/common-endpoints` resource
     - 80% of requests use these common endpoints
     - Only read swagger.json for uncommon operations
  
  2. **Use Endpoint Index for Search**
     - Access `sevone://api/endpoint-index` for quick lookup
     - Search by keyword, category, or operation
     - Avoid full swagger.json reads
  
  3. **Fallback to Full Documentation**
     - Only read `api-docs/sevone-swagger.json` when:
       * Operation not in common endpoints
       * Need detailed schema information
       * Complex nested object structures required
```

#### Benefits
- ✅ **80-90% reduction** in swagger.json reads
- ✅ **Faster response times** for common operations
- ✅ **Lower token costs** per request
- ✅ **No breaking changes** to existing functionality
- ✅ **Graceful fallback** to full documentation when needed

---

### Solution 2: **Smart Documentation Chunking**

#### Architecture
Pre-process swagger.json into categorized chunks:

```
api-docs/
├── sevone-swagger.json (original, kept for reference)
└── chunks/
    ├── devices.json
    ├── alerts.json
    ├── metadata.json
    ├── objects.json
    ├── indicators.json
    └── index.json (maps operations to chunks)
```

#### Implementation Details

**1. Build-time Chunking Script**
```python
# scripts/chunk_swagger.py
def chunk_swagger_by_category():
    """Split swagger.json into logical chunks"""
    with open('api-docs/sevone-swagger.json') as f:
        swagger = json.load(f)
    
    chunks = {
        'devices': [],
        'alerts': [],
        'metadata': [],
        'objects': [],
        'indicators': []
    }
    
    for path, methods in swagger['paths'].items():
        category = categorize_endpoint(path)
        chunks[category].append({path: methods})
    
    # Write chunks
    for category, endpoints in chunks.items():
        with open(f'api-docs/chunks/{category}.json', 'w') as f:
            json.dump(endpoints, f, indent=2)
```

**2. Update Mode Instructions**
```yaml
customInstructions: |
  DOCUMENTATION STRATEGY:
  
  1. **Identify Operation Category**
     - Devices → read `api-docs/chunks/devices.json`
     - Alerts → read `api-docs/chunks/alerts.json`
     - Metadata → read `api-docs/chunks/metadata.json`
  
  2. **Read Only Relevant Chunk**
     - Each chunk is 1,000-5,000 lines (vs 64,774)
     - 90% faster to read and process
  
  3. **Use Index for Unknown Operations**
     - Read `api-docs/chunks/index.json` first
     - Maps operations to correct chunk file
```

#### Benefits
- ✅ **10-20x smaller** file reads
- ✅ **Faster parsing** and processing
- ✅ **Better organization** by domain
- ⚠️ Requires build-time processing
- ⚠️ Need to maintain chunk consistency

---

### Solution 3: **Hybrid Approach with LLM Context Optimization**

#### Architecture
Combine caching with intelligent context management:

**1. Three-Tier Documentation Access**
```
Tier 1: In-Memory Cache (MCP Resources)
  └── Common endpoints (devices, alerts, metadata)
  
Tier 2: Chunked Documentation
  └── Category-specific files (5-10KB each)
  
Tier 3: Full Swagger (Fallback)
  └── Complete specification (rare cases)
```

**2. Smart Context Window Management**
```python
class ContextManager:
    """Optimize what gets loaded into LLM context"""
    
    def get_documentation(self, user_query: str):
        # Analyze query intent
        intent = self.classify_intent(user_query)
        
        if intent in COMMON_OPERATIONS:
            # Return minimal, focused documentation
            return self.get_common_endpoint_docs(intent)
        elif intent.category in KNOWN_CATEGORIES:
            # Return category chunk
            return self.get_category_docs(intent.category)
        else:
            # Full swagger search
            return self.search_full_swagger(intent.keywords)
```

#### Benefits
- ✅ **Best of both worlds**: Speed + Completeness
- ✅ **Adaptive**: Learns from usage patterns
- ✅ **Minimal overhead**: Only loads what's needed
- ✅ **Future-proof**: Can add ML-based optimization

---

## Recommended Implementation Plan

### Phase 1: Quick Win (Solution 1)
**Timeline**: 1-2 days

1. Create `APICatalog` with 20-30 most common endpoints
2. Add MCP resources to expose catalog
3. Update custom mode instructions
4. Test with common operations

**Expected Impact**: 70-80% reduction in swagger.json reads

### Phase 2: Enhanced Efficiency (Solution 2)
**Timeline**: 3-5 days

1. Build chunking script
2. Generate categorized documentation chunks
3. Update mode to use chunks
4. Add automated chunk regeneration

**Expected Impact**: 90% reduction in documentation load time

### Phase 3: Optimization (Solution 3)
**Timeline**: 1-2 weeks

1. Implement context manager
2. Add usage analytics
3. Build adaptive caching
4. Performance monitoring

**Expected Impact**: 95%+ efficiency improvement

---

## Metrics to Track

### Before Optimization
- Average swagger.json reads per request: **1.0**
- Average documentation size loaded: **64,774 lines**
- Average response time: **X seconds**
- Token cost per request: **Y tokens**

### After Phase 1
- Average swagger.json reads per request: **0.2-0.3**
- Average documentation size loaded: **500-1,000 lines**
- Average response time: **X/3 seconds**
- Token cost per request: **Y/10 tokens**

### After Phase 2
- Average swagger.json reads per request: **0.05-0.1**
- Average documentation size loaded: **200-500 lines**
- Average response time: **X/5 seconds**
- Token cost per request: **Y/20 tokens**

---

## Additional Considerations

### 1. Documentation Updates
- **Problem**: Swagger.json may change with SevOne updates
- **Solution**: 
  - Version-aware caching
  - Automated chunk regeneration on swagger.json changes
  - Cache invalidation strategy

### 2. Backward Compatibility
- All solutions maintain existing functionality
- Graceful fallback to full documentation
- No breaking changes to MCP tool interface

### 3. Memory Management
- MCP resources are lightweight (JSON strings)
- Chunks stored on disk, loaded on demand
- No significant memory overhead

### 4. Developer Experience
- Faster responses = better UX
- More predictable performance
- Lower costs for users

---

## Conclusion

**Recommended Approach**: Start with **Solution 1** (MCP Resources) for immediate impact, then add **Solution 2** (Chunking) for long-term efficiency.

This hybrid approach provides:
- ✅ Immediate 70-80% efficiency gain
- ✅ Minimal implementation complexity
- ✅ No breaking changes
- ✅ Clear path to further optimization
- ✅ Measurable performance improvements

The key insight is that **most API operations fall into common patterns**, and we can optimize for the 80% case while maintaining full capability for edge cases.
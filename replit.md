# Interactive Network Graph Visualization

## Overview

This is a Flask-based web application that creates an interactive network graph visualization using D3.js, NetworkX, and Gravis. The application displays relationships between nodes in a cyberpunk-themed force-directed graph with two distinct node types: graphic nodes (visual content with images) positioned in the center, and keyword nodes positioned on an outer circle. The visualization features a black background, purple keyword nodes, green edges, and interactive hover/zoom capabilities.

The project has undergone significant refactoring, achieving an 87% code reduction (from 3,108 to 426 lines) by externalizing all data to JSON files and applying DRY principles.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Visualization Layer**
- **D3.js Force-Directed Graph**: Interactive graph rendering with zoom, pan, and hover capabilities
- **Gravis Library**: Python-to-D3.js bridge that generates the visualization HTML
- **Static HTML Generation**: Pre-rendered graph served from `templates/index.html` (616KB)
- **Cyberpunk Theme**: Custom styling with black background (#000000), purple keyword nodes, green edges, and image thumbnails

**Layout Algorithm**
- **Circular Positioning**: Keyword nodes arranged on outer circle (radius: 1177.1px)
- **Central Clustering**: Graphic nodes positioned in center (radius: 360px)
- **Force Simulation Parameters**: Configurable many-body forces, link forces, and collision detection for optimal node spacing

### Backend Architecture

**Application Framework**
- **Flask 3.0+**: Lightweight web server with single-route architecture
- **Template Serving**: Serves pre-generated HTML with cache control headers
- **On-Demand Generation**: Graph regeneration only when needed, with caching to avoid repeated computation

**Data Management Pattern**
- **JSON-Driven Architecture**: All node and edge data externalized to JSON files
- **Separation of Concerns**: 
  - `data/nodes.json` - 133 node definitions with metadata
  - `data/edges.json` - 235 active edge relationships  
  - `data/edges_keyword_circular_commented.json` - 16 disabled circular edges
  - `config/graph_config.json` - Visualization parameters and styling
- **Modular Loading**: Reusable functions for JSON parsing and validation

**Graph Generation Pipeline**
1. Load node and edge data from JSON files
2. Create NetworkX directed graph structure
3. Calculate node positions (circular for keywords, central for graphics)
4. Apply visual styling from configuration
5. Generate D3.js HTML using Gravis
6. Cache result to avoid regeneration

**Performance Optimizations**
- **LRU Caching**: Function-level caching with `@lru_cache` decorator
- **Lazy Loading**: Graph generated only on first request
- **Position Pre-calculation**: Node positions computed once and reused
- **Cache Control Headers**: HTTP headers prevent stale browser caching

### Data Storage Solutions

**File-Based JSON Storage**
- No database required - all data stored as JSON files
- Version controllable and human-readable
- Easy to update without code changes

**Data Structure**
- **Nodes**: Objects with `graphicLabel`, `graphicName`, `xPostURL`, `xGraphicURL` for graphics; keyword nodes prefixed with `kw-`
- **Edges**: Objects with `source`, `target`, and optional `label` fields
- **Configuration**: Nested JSON with colors, positions, metadata, and visualization parameters

**Data Organization**
```
data/
├── nodes.json                              # Primary node definitions
├── edges.json                              # Active edges (235)
├── edges_keyword_circular_commented.json   # Disabled edges (16)
└── README_edges.md                         # Edge documentation

config/
└── graph_config.json                       # All visualization settings
```

### Authentication and Authorization

**None Required**
- Public-facing visualization with no authentication
- Read-only access model
- No user accounts or sessions needed

### External Dependencies

**Python Libraries**
- **Flask 3.0.0+**: Web application framework
- **NetworkX 3.3**: Graph data structure and algorithms
- **Gravis 0.1.0**: D3.js visualization generation from NetworkX graphs
- **Gunicorn 21.2.0+**: Production WSGI server for deployment

**Frontend Libraries (Embedded via Gravis)**
- **D3.js**: Force-directed graph rendering and interactions
- Browser-based rendering, no external CDN dependencies

**Social Media Integration**
- **X (Twitter) Post URLs**: Each graphic node links to associated X posts
- **Image Hosting**: Uses X's image CDN (pbs.twimg.com) for thumbnail display
- No API integration - uses direct URL references

**Deployment Platform**
- **Replit**: Target deployment platform
- **Procfile**: Configured for Gunicorn with 4 workers
- **Poetry**: Dependency management via `pyproject.toml` and `poetry.lock`

**Development Tools**
- **Test Scripts**: `test_app.py` for data validation, `verify_deployment.py` for production readiness
- **Logging**: Standard Python logging for debugging and monitoring

**No Database Required**
- Pure file-based architecture eliminates database dependency
- Could be extended with Postgres/SQLite if dynamic data updates are needed in future
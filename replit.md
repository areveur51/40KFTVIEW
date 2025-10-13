# Interactive Network Graph Visualization

## Overview

This is a Flask-based web application that creates an interactive D3.js network graph visualization to display relationships between nodes and concepts. The application uses NetworkX for graph structure and Gravis for D3.js rendering, featuring a cyberpunk-themed interface with force-directed layout. The project has been heavily refactored to follow DRY principles, achieving an 87% code reduction by externalizing all data to JSON files.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Application Structure

**Backend Framework**: Flask 3.0.0+ web application
- Single-route application serving a pre-generated static HTML graph
- Graph generation happens on first request and is cached
- Cache control headers prevent browser caching issues
- Logging configured for monitoring and debugging

**Graph Generation Pipeline**:
1. Load node and edge data from JSON files
2. Load visualization configuration from JSON
3. Build NetworkX directed graph structure
4. Calculate node positions (keyword nodes on outer circle, graphic nodes in center)
5. Generate interactive D3.js visualization using Gravis
6. Save to static HTML template
7. Serve with proper cache control headers

**Data-Driven Architecture**:
- All graph data externalized to `data/` directory
- Node definitions in `nodes.json` (133 nodes)
- Edge relationships in `edges.json` (235 active edges)
- Commented/disabled edges in separate file for optional restoration
- Visualization settings in `config/graph_config.json`
- No hardcoded data in Python code - pure data separation

### Node Architecture

**Two Node Types**:

1. **Graphic Nodes** (Visual content):
   - Center-positioned using circular layout
   - Contains image thumbnails
   - Links to X (Twitter) posts and images
   - Properties: graphicLabel, graphicName, xPostURL, xGraphicURL

2. **Keyword Nodes** (Conceptual):
   - Positioned on outer circle
   - Larger radius for visual separation
   - Prefixed with "kw-" identifier
   - Purple colored for distinction

### Positioning System

**Circular Layout Algorithm**:
- Keyword nodes: Positioned on outer circle (radius: 1177.1)
- Graphic nodes: Positioned on inner circle (radius: 360.0)
- Automatic angle calculation based on node count
- Position caching with `@lru_cache` for performance

### Frontend Visualization

**D3.js Force Simulation**:
- Many-body force for node repulsion (strength: -1776.0)
- Link force for edge connections (distance: 107.0)
- Collision force to prevent overlap (radius: 100.0)
- Custom positioning forces (x: 0.07, y: 0.1)
- Edge curvature for visual clarity (0.11)

**Visual Theme**:
- Background: Black (#000000)
- Keyword nodes: Purple
- Edges: Green with low opacity (0.1)
- Image thumbnails for graphic nodes
- Hover interactions with neighborhood highlighting

### Performance Optimizations

**Caching Strategy**:
- Graph HTML generated once and cached
- Position calculations cached with `@lru_cache`
- Only regenerates when needed (first request or forced)
- HTTP cache control headers for fresh delivery

**Code Organization**:
- Original: 3,108 lines in single file
- Refactored: 426 lines (87% reduction)
- Modular functions for data loading, position calculation, graph building
- Clear separation between data, config, and logic

## External Dependencies

### Python Libraries
- **Flask 3.0.0+**: Web framework for serving the application
- **NetworkX 3.3**: Graph data structure and algorithms
- **Gravis 0.1.0**: D3.js graph visualization generator
- **Gunicorn 21.2.0+**: Production WSGI server

### Frontend Libraries (via Gravis)
- **D3.js**: Force-directed graph layout and rendering
- Embedded in generated HTML, no separate CDN dependencies

### Data Storage
- **JSON files**: Primary data storage format
  - `nodes.json`: Node definitions
  - `edges.json`: Active edge relationships
  - `edges_keyword_circular_commented.json`: Disabled edges
  - `graph_config.json`: Visualization parameters
- No database required - file-based data persistence

### Deployment
- **Poetry**: Dependency management (pyproject.toml, poetry.lock)
- **Procfile**: Deployment configuration for platforms like Heroku/Replit
- Static file serving via Flask's send_from_directory

### Development Tools
- Python logging module for application monitoring
- Path and pathlib for cross-platform file handling
- JSON module for data serialization
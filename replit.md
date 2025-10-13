# Overview

An interactive network graph visualization application that displays complex relationships between nodes using D3.js force-directed layouts. Built with Flask, NetworkX, and Gravis, the application renders a cyberpunk-themed visualization with two node types: graphic nodes (visual content with social media links) positioned in the center, and keyword nodes positioned on an outer circular radius. The system has been refactored to follow DRY principles, achieving 87% code reduction by externalizing all data to JSON files.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Application Structure

**Problem**: Need a maintainable, data-driven web application for visualizing network graphs
**Solution**: Flask-based web server with externalized data architecture
**Rationale**: Separates data from code, making updates possible without modifying application logic

### Core Components

1. **Web Framework**: Flask 3.0.0+
   - Single route (`/`) serves the visualization
   - Static file serving for generated HTML
   - Cache control headers to ensure fresh content

2. **Graph Generation Pipeline**:
   - **NetworkX**: Creates directed graph structure from node/edge data
   - **Gravis 0.1.0**: Renders interactive D3.js visualization
   - **Caching Strategy**: Graph generated once per session, cached to avoid regeneration on each request

3. **Data Layer** (Externalized):
   - `data/nodes.json`: 133 nodes with metadata (graphic labels, URLs, X/Twitter post links)
   - `data/edges.json`: 235 active edges defining relationships
   - `data/edges_keyword_circular_commented.json`: 16 disabled circular edges (for optional features)
   - `config/graph_config.json`: Visualization settings (colors, positions, force parameters)

## Data Architecture

**Problem**: Original 3,108-line monolith with hardcoded data was unmaintainable
**Solution**: Complete data externalization to JSON files
**Results**: 
- Reduced to 426 lines (87% reduction)
- Zero code changes needed for data updates
- Clear separation between application logic and content

### Node Structure
Two node types with distinct positioning:
- **Graphic Nodes**: Visual content with image thumbnails, social media links, positioned at radius 360 (center cluster)
- **Keyword Nodes**: Conceptual nodes prefixed with "kw-", positioned at radius 1177.1 (outer circle)

### Position Calculation
- Keyword nodes: Circular layout using trigonometry (evenly distributed)
- Graphic nodes: Staggered intervals (every 5 degrees) for visual separation
- Coordinates calculated using configurable radius values

## Visualization Configuration

**Problem**: Need fine-tuned control over graph appearance and physics
**Solution**: Comprehensive JSON configuration for all visual parameters

### Key Configuration Areas:
1. **Colors**: Background (#000000 black), highlight (green), default node colors
2. **Force Simulation**: 
   - Many-body force strength: -1776.0 (repulsion)
   - Link force distance: 107.0
   - Collision radius: 100.0
3. **Layout**: Graph height (1100px), zoom factor (0.5), edge curvature (0.11)
4. **Node/Edge Styling**: Opacity, size factors, label sizes

## Code Organization

### Main Application (`main.py`)
- JSON file loading utilities with error handling
- Position calculation functions (circular layout for keywords)
- Graph construction from data files
- Flask routes with cache control

### Backup & History
- `main_old_backup.py`: Original 3,108-line version preserved for reference
- Demonstrates evolution from monolithic to modular architecture

# External Dependencies

## Python Packages
- **Flask 3.0.0+**: Web framework for serving visualization
- **NetworkX 3.3**: Graph data structure and algorithms
- **Gravis 0.1.0**: D3.js graph rendering library
- **Gunicorn 21.2.0+**: WSGI HTTP server for production deployment

## Data Storage
- **File-based JSON**: All data stored in local JSON files
- No database system currently implemented
- Data files serve as the single source of truth

## Frontend Technologies (via Gravis)
- **D3.js**: Force-directed graph layout and interactive visualization
- Embedded in generated HTML template

## Deployment
- **Poetry**: Dependency management (pyproject.toml, poetry.lock)
- **Procfile**: Deployment configuration for platforms like Heroku/Replit
- Static file serving from Flask (templates/index.html generated at 616KB)

## Third-Party Integrations
- **X/Twitter**: Node metadata includes X post URLs and image URLs (pbs.twimg.com)
- Links embedded in node data for external content references
- No API integration, only hyperlinks to social media content
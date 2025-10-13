# Interactive Network Graph Visualization

## Overview

This is a Flask-based web application that creates interactive D3.js network graph visualizations to display complex relationships between nodes. The system uses NetworkX for graph structure and Gravis for D3.js rendering, presenting a cyberpunk-themed visualization with two distinct node types: graphic nodes (visual content with linked images) positioned centrally, and keyword nodes (conceptual nodes) arranged in an outer circle.

The application has been heavily refactored to follow DRY principles, achieving an 87% code reduction by externalizing all data to JSON files, making it easy to update content without modifying code.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Application Structure

**Data-Driven Architecture**: The application separates data, configuration, and presentation logic completely. All node and edge data lives in JSON files under the `data/` directory, while visualization settings are stored in `config/graph_config.json`. This allows non-technical updates to content without touching Python code.

**Graph Generation Strategy**: The system uses a caching mechanism to avoid regenerating the graph on every request. The graph is built once using NetworkX, positions are calculated using radial layouts (keyword nodes on outer circle at 1177.1px radius, graphic nodes centrally at 360px radius), and then rendered to static HTML using Gravis. The Flask application serves this pre-generated HTML file.

**Position Calculation**: Keyword nodes are distributed evenly around a circle using trigonometric calculations (2π radians divided by node count). Graphic nodes are positioned at smaller intervals within a central radius. This creates the distinctive radial layout pattern.

### Frontend Architecture

**Visualization Layer**: Uses D3.js force-directed graph rendering via the Gravis library. The graph is interactive with zoom, pan, and hover capabilities. Nodes are styled with a cyberpunk theme: black background (#000000), purple keyword nodes, green edges (with 0.1 opacity), and image thumbnails for graphic nodes.

**Force Simulation Parameters**: The D3.js force simulation is heavily customized through config settings:
- Many-body force strength: -1776.0 (repulsion)
- Links force distance: 107.0px
- Collision force radius: 100.0px
- Node hover neighborhood highlighting enabled
- Edge curvature: 0.11 for visual clarity

### Backend Architecture

**Flask Application**: Simple Flask server (`main.py`, 426 lines) that:
1. Loads JSON data files at startup
2. Builds NetworkX directed graph from nodes/edges
3. Calculates node positions using radial formulas
4. Generates HTML visualization using Gravis
5. Serves the visualization with proper cache control headers

**Data Loading Pattern**: Uses a centralized `load_json_file()` function with error handling for all data imports. Configuration is loaded separately from operational data to maintain clear separation of concerns.

**Graph Construction**: 
- 133 nodes total (graphic + keyword nodes)
- 235 active edges defined in `edges.json`
- 16 disabled keyword-circular edges stored separately
- Directed graph structure with labeled edges

### Data Storage

**Node Data Structure** (`data/nodes.json`):
- Graphic nodes: Include `graphicLabel`, `graphicName`, `xPostURL`, `xGraphicURL`
- Keyword nodes: Include `keywordLabel` and `keywordName`
- All nodes stored in a single flat JSON array

**Edge Data Structure** (`data/edges.json`):
- Source and target node identifiers
- Optional edge labels for relationship description
- Separate file for commented/disabled edges

**Configuration Data** (`config/graph_config.json`):
- Colors (background, highlights, defaults)
- Position parameters (radii, intervals)
- Graph metadata (sizes, opacities)
- Visualization settings (forces, curvature, zoom)

### Performance Optimization

**Graph Caching**: The application uses a module-level flag (`_graph_generated`) to track whether the visualization has been built. Once generated, subsequent requests serve the cached HTML file directly without rebuilding the graph structure.

**Position Pre-calculation**: Node positions are calculated once during graph generation using mathematical formulas, then stored in the NetworkX graph structure. This avoids runtime position calculations.

**Static HTML Serving**: The final visualization is a 616KB static HTML file with embedded D3.js, served via Flask's `send_from_directory()` for optimal performance.

## External Dependencies

### Python Packages
- **Flask 3.0.0+**: Web framework for serving the application
- **NetworkX 3.3**: Graph data structure and algorithms library
- **Gravis 0.1.0**: D3.js graph visualization wrapper for Python
- **Gunicorn 21.2.0+**: Production WSGI server for deployment

### Frontend Libraries
- **D3.js**: Embedded via Gravis for force-directed graph rendering
- No separate JavaScript dependencies - all bundled in generated HTML

### Deployment Platform
- **Replit**: Configured via `Procfile` for deployment
- Uses Gunicorn with 4 workers binding to `0.0.0.0:5000`
- Poetry for dependency management (`pyproject.toml`, `poetry.lock`)

### Data Sources
- Node images hosted on external URLs (Twitter/X media CDN)
- Social media post links to Twitter/X platform
- No database required - all data in JSON files

### Development Tools
- **Poetry**: Python dependency management
- **Logging**: Python's built-in logging module for debugging
- **Pathlib**: Cross-platform file path handling
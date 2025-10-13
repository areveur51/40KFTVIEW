# Overview

This is an Interactive Network Graph Visualization application that visualizes complex relationships between nodes using D3.js force-directed graphs. Built with Flask, NetworkX, and Gravis, it creates a cyberpunk-themed network visualization with two types of nodes: graphic nodes (visual content with linked images) positioned in the center, and keyword nodes positioned on an outer circle, connected by labeled edges.

The application has undergone significant refactoring, achieving an 87% code reduction by externalizing all data to JSON files and following DRY principles. The graph displays 133 nodes connected by 235 active edges, with an additional 16 commented keyword circular edges available for activation.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Application Structure

**Monolithic Flask Application**: The system uses a single Flask application (`main.py`, 426 lines) that serves as both the web server and graph generation engine. A backup of the original monolithic implementation exists (`main_old_backup.py`, 3,108 lines) showing the evolution from hardcoded data to data-driven architecture.

**Data-Driven Architecture**: All node and edge data has been externalized from code into JSON files in the `data/` directory. This separation allows for easy updates to the graph content without modifying the application code. Configuration settings for visualization (colors, positions, force parameters) are stored in `config/graph_config.json`.

**Caching Strategy**: The application implements graph caching to avoid regenerating the visualization on every request. The graph HTML is generated once and cached in `templates/index.html` (616KB), with cache control headers ensuring browsers receive fresh content when needed.

## Graph Generation Pipeline

**NetworkX Graph Building**: The application loads nodes and edges from JSON files, then constructs a directed NetworkX graph. Each node type (graphic vs keyword) receives specific positioning based on configuration parameters.

**Positioning Algorithm**: 
- **Keyword nodes**: Positioned on an outer circle with radius 1177.1 units, evenly distributed
- **Graphic nodes**: Positioned in center area with radius 360.0 units, with 5-unit intervals
- Positions are calculated using trigonometric functions and cached using `@lru_cache` decorator

**D3.js Rendering via Gravis**: The NetworkX graph is converted to an interactive D3.js visualization using the Gravis library. Force simulation parameters (many-body force, collision force, link force) are configurable through JSON to fine-tune the visual layout.

## Node and Edge Data Model

**Two Node Types**:
1. **Graphic Nodes**: Visual content nodes with properties:
   - `graphicLabel`: Display text
   - `graphicName`: Unique identifier
   - `xPostURL`: Social media post link
   - `xGraphicURL`: Thumbnail image URL

2. **Keyword Nodes**: Conceptual nodes with prefix "kw-" in their identifiers, positioned on outer circle

**Edge Structure**: Each edge contains:
- `source`: Origin node identifier
- `target`: Destination node identifier  
- `label`: Relationship description/context

**Edge Management**: Active edges (235) are in `edges.json`, while disabled keyword circular edges (16) are preserved in `edges_keyword_circular_commented.json` for potential reactivation.

## Deployment Configuration

**Poetry Dependency Management**: The project uses Poetry for Python dependency management with locked versions in `poetry.lock`. Core dependencies are Flask 3.0+, NetworkX 3.3, Gravis 0.1.0, and Gunicorn 21.2+ for production serving.

**Production Server**: Configured to use Gunicorn WSGI server via `Procfile` for deployment on platforms like Replit or Heroku.

**Python Version**: Requires Python 3.10 or 3.11 for compatibility with dependencies.

# External Dependencies

## Python Libraries

**Flask 3.0.0+**: Web framework providing the HTTP server and routing for serving the visualization page.

**NetworkX 3.3**: Graph theory library used for constructing and managing the directed graph data structure before visualization.

**Gravis 0.1.0**: Visualization library that converts NetworkX graphs into interactive D3.js force-directed layouts with customizable parameters.

**Gunicorn 21.2.0+**: Production-grade WSGI HTTP server for serving the Flask application in deployment environments.

## Frontend Libraries (Embedded)

**D3.js**: JavaScript library for interactive graph visualization, embedded in the generated HTML template via Gravis.

## External Services

**Twitter/X Image Hosting**: Graphic nodes reference images hosted on Twitter's CDN (`pbs.twimg.com`) for thumbnail display in the visualization.

**Twitter/X Post Links**: Each graphic node links to social media posts on x.com (formerly Twitter) for context and source material.

## Data Storage

**File-based JSON Storage**: All application data stored in local JSON files:
- `data/nodes.json`: 133 nodes (33KB)
- `data/edges.json`: 235 active edges (24KB)
- `data/edges_keyword_circular_commented.json`: 16 disabled edges
- `config/graph_config.json`: Visualization configuration

**Static HTML Cache**: Generated graph visualization cached in `templates/index.html` (616KB) to improve performance.

**No Database Required**: The application operates entirely on file-based storage without requiring PostgreSQL, MongoDB, or any other database system.
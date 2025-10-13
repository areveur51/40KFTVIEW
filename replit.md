# Interactive Network Graph Visualization

## Overview

This is a Flask-based web application that creates an interactive D3.js network graph visualization. It displays relationships between two types of nodes: graphic nodes (visual content with images and social media links) and keyword nodes (conceptual nodes positioned on the outer circle). The application uses NetworkX for graph structure and Gravis for D3.js rendering, featuring a cyberpunk-themed visualization with black background, purple keyword nodes, and green connecting edges.

The project has been refactored from a monolithic 3,100-line codebase to a modular, data-driven architecture with only ~400 lines of application code, achieving an 87% code reduction through DRY principles.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Application Architecture

**Web Framework**: Flask 3.0.0+ is used as a lightweight web server to serve the visualization and handle HTTP requests. The application uses a single-route architecture (`/` endpoint) that generates and serves the interactive graph.

**Graph Generation Strategy**: The application uses a lazy generation pattern with in-memory caching. The graph HTML is generated once on first request and cached globally to avoid regeneration overhead. Cache control headers prevent browser caching issues while maintaining server-side performance.

**Data-Driven Design**: The architecture separates data from logic through JSON-based configuration:
- **Node data** (`data/nodes.json`): 133 graphic nodes with metadata including labels, names, social media URLs, and image URLs
- **Edge data** (`data/edges.json`): 251 active edges defining relationships between nodes, with support for disabled/commented edges stored separately
- **Configuration** (`config/graph_config.json`): Centralized visualization settings including colors, positions, graph metadata, and D3.js force simulation parameters

**Graph Construction**: NetworkX is used to build the directed graph structure from JSON data. The system supports two node types with different positioning strategies:
- **Keyword nodes**: Positioned in a circular pattern at a fixed radius (1177.1 units)
- **Graphic nodes**: Positioned in the center at a smaller radius (360.0 units) with interval-based spacing

**Visualization Layer**: Gravis library converts the NetworkX graph into interactive D3.js visualizations. Custom styling includes node colors (black default, green highlights), edge opacity (0.1 for subtle connections), and force-directed layout with configurable strength parameters.

### File Structure Philosophy

The codebase follows a strict separation of concerns:
- **Application logic** (`main.py`): Loads data, constructs graph, applies positioning, generates visualization
- **Data layer** (`data/` directory): Pure JSON data files that can be edited without touching code
- **Configuration layer** (`config/` directory): Centralized settings for easy theme/layout adjustments
- **Utilities**: Standalone scripts for data extraction, validation, and maintenance
- **Backup strategy**: Original monolithic code preserved as `main_old_backup.py` for reference

### Performance Optimizations

**Caching Strategy**: Graph generation uses global state tracking (`_graph_generated` flag and `_generation_time` timestamp) to prevent redundant computations. The generated HTML template is reused across requests.

**Position Calculation**: Node positions are pre-calculated using mathematical formulas (circular distribution with trigonometric functions) rather than relying solely on D3.js force simulation, ensuring consistent initial layouts.

**Resource Optimization**: Static files served directly from Flask's template directory with appropriate cache control headers. Image assets referenced via external URLs (Twitter/X CDN) to minimize server storage.

### Logging and Monitoring

Structured logging configured at INFO level with timestamp, logger name, level, and message formatting. Key operations logged include page requests, graph generation events, and data loading processes.

## External Dependencies

### Python Libraries

**Flask (>=3.0.0)**: Web application framework for HTTP request handling and HTML serving. Chosen for its simplicity and minimal overhead for single-page applications.

**Gunicorn (>=21.2.0)**: WSGI HTTP server for production deployment. Handles concurrent requests and process management.

**NetworkX (3.3)**: Graph data structure library. Provides directed graph construction, node/edge management, and algorithms. Fixed version to ensure consistent graph behavior.

**Gravis (0.1.0)**: D3.js graph visualization wrapper. Converts NetworkX graphs to interactive web visualizations with minimal code. Fixed version to maintain visualization compatibility.

### External Services

**Twitter/X CDN**: All graphic node images hosted on `pbs.twimg.com`. The application references these images via URL rather than storing them locally. Each node includes both a post URL (linking to the full tweet) and a graphic URL (direct image link).

**Social Media Integration**: Each graphic node links to specific X.com (Twitter) posts, creating a connection between the visualization and social media content. The URLs follow the pattern `https://x.com/areveur51/status/[ID]`.

### Data Storage

**File-Based JSON Storage**: No database required. All data persisted in JSON files:
- Node data: 33KB JSON file with 133 entries
- Edge data: 26KB JSON file with 251 active relationships
- Separate file for disabled edges (16 keyword-circular edges)

**Static Assets**: Generated visualization saved as `templates/index.html` (616KB). This approach trades disk space for runtime performance.

### Browser Requirements

**D3.js Visualization**: Requires modern browser with JavaScript enabled. The Gravis library generates D3.js v6+ compatible code with force simulation, zoom, pan, and hover interactions.

**Responsive Design**: SVG-based rendering adapts to different screen sizes. Graph height configurable via JSON (default 1100px).
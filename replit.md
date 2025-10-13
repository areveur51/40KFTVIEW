# Interactive Network Graph Visualization

## Overview

This is a Flask-based web application that creates interactive network graph visualizations using D3.js force-directed layouts. The application visualizes complex relationships between two types of nodes: "Graphic Nodes" (visual content with linked images and social media) and "Keyword Nodes" (conceptual nodes positioned on an outer circle). Built with NetworkX for graph structure and Gravis for D3.js rendering, the system features performance optimizations including graph caching and efficient position calculations.

## Recent Changes (October 2025)

- **Added comprehensive documentation**: Full docstrings for all functions following Google style guide
- **Implemented graph caching**: Prevents regeneration on every request, significantly improving performance
- **Created README.md**: Complete setup guide, API documentation, and troubleshooting section
- **Added requirements.txt**: Dual installation support (pip and Poetry)
- **Enhanced logging**: Improved log formatting with timestamps and context
- **HTTP cache control**: Proper headers to prevent browser caching issues
- **Created config_loader.py**: Centralized configuration management module
- **Updated .gitignore**: Added project-specific exclusions for generated files

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology Stack**: Pure HTML/CSS with D3.js visualization library embedded via Gravis

**Rendering Strategy**: Server-side HTML generation with client-side D3.js interactivity
- The application generates static HTML files containing embedded D3.js visualizations
- Gravis library handles the D3.js force simulation and graph rendering
- No frontend build process required; all visualization logic is embedded in served HTML

**Design Pattern**: Template-based rendering
- Flask serves pre-generated HTML from `templates/` directory
- Graph visualizations are generated on-demand and cached
- Responsive design with zoom, pan, and hover interactions built into D3.js

### Backend Architecture

**Framework**: Flask (Python web microframework)
- **Version**: 3.0.0+
- **Deployment**: Gunicorn WSGI server for production (21.2.0+)

**Core Components**:

1. **Graph Generation System** (`main.py`)
   - Uses NetworkX (v3.3) for graph data structure
   - Gravis (v0.1.0) for D3.js visualization generation
   - LRU caching decorator for performance optimization
   - Lazy loading: graphs generated only on first request

2. **Configuration Management** (`config_loader.py`)
   - JSON-based configuration system
   - Fallback to default configuration if file missing
   - Centralized settings for colors, positions, and visualization parameters

3. **Position Calculation Algorithm**
   - Two-tier circular layout system:
     - **Keyword nodes**: Positioned on outer circle (radius: 1177.1)
     - **Graphic nodes**: Positioned on inner circle with interval-based spacing (radius: 360.0)
   - Mathematical positioning using polar coordinates

**Performance Optimizations**:
- Graph caching with global state flags (`_graph_generated`, `_generation_time`)
- Prevents redundant graph regeneration on subsequent requests
- Cache control HTTP headers to ensure fresh content delivery
- Pre-calculated position formulas to avoid repeated computations

**Data Flow**:
1. Client requests index route (`/`)
2. Server checks if graph has been generated
3. If not cached, generates graph using NetworkX/Gravis
4. Saves HTML to `templates/index.html`
5. Serves cached HTML with no-cache headers
6. Subsequent requests serve cached version

### Data Storage

**Configuration Storage**:
- **Format**: JSON files
- **Location**: `config/graph_config.json`
- **Structure**: Hierarchical configuration containing:
  - Color schemes (default, highlight, background)
  - Position parameters (radii, intervals)
  - Graph metadata (labels, dimensions)
  - D3.js force simulation parameters

**Node Data Storage**:
- Currently embedded in application code
- `extract_data.py` utility exists for extracting node data to JSON format
- Designed for potential migration to `data/nodes.json`

**Template Storage**:
- Generated HTML files stored in `templates/` directory
- Multiple versions maintained (`index.html`, `index_orig.html`)
- Static file serving via Flask's `send_from_directory`

**No Database**: Application is stateless and configuration-driven; no persistent database required

### Authentication & Authorization

**Current Implementation**: None
- Application serves public visualizations
- No user authentication or access control implemented
- All routes are publicly accessible

**Security Considerations**:
- Suitable for read-only public visualizations
- Would require authentication layer if user-specific data or editing features added

## External Dependencies

### Python Libraries

**Core Frameworks**:
- **Flask** (>=3.0.0): Web application framework
- **Gunicorn** (>=21.2.0): Production WSGI server

**Graph & Visualization**:
- **NetworkX** (3.3): Graph data structure and algorithms
- **Gravis** (0.1.0): D3.js visualization generation library

### JavaScript Libraries

**D3.js**: Embedded via Gravis for force-directed graph visualization
- Handles interactive features (zoom, pan, hover)
- Force simulation for automatic node positioning
- No direct D3.js dependency management; bundled with Gravis output

### External Services

**None**: Application is fully self-contained with no external API dependencies

### Development Tools

**Utility Scripts**:
- `extract_data.py`: Data extraction utility for refactoring node data from code to JSON

**Python Version Requirements**:
- Python 3.10 or 3.11 (specified in README)

### Configuration Files

- `requirements.txt`: pip dependency specification
- `config/graph_config.json`: Visualization configuration parameters
- Poetry support available but pip is recommended installation method
# Interactive Network Graph Visualization

## Overview

This is a Flask web application that creates an interactive D3.js network graph visualization displaying relationships between nodes. The project uses NetworkX for graph structure and Gravis for D3.js rendering, featuring a cyberpunk-themed design with force-directed layout. The application has been heavily refactored to follow DRY principles, achieving an 87% code reduction by externalizing all data to JSON files.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Visualization Engine**: D3.js force-directed graph rendered via Gravis library
- **UI Theme**: Cyberpunk aesthetic with black background, purple keyword nodes, green edges, and image thumbnails
- **Interactive Features**: Zoom, pan, and hover interactions for exploring node relationships
- **Responsive Design**: Adapts to different screen sizes
- **Node Types**:
  - Graphic nodes: Visual content with linked images and social media posts (positioned in center)
  - Keyword nodes: Conceptual nodes positioned on outer circle in radial layout

### Backend Architecture
- **Framework**: Flask 3.0.0+ (lightweight Python web framework)
- **Graph Library**: NetworkX 3.3 for graph data structure and manipulation
- **Rendering**: Gravis 0.1.0 for D3.js visualization generation
- **Data Loading**: JSON-based configuration system with centralized data management
- **Caching Strategy**: 
  - Graph generation cached to avoid regeneration on every request
  - LRU caching for JSON file loading
  - HTTP cache control headers to ensure fresh content delivery
- **Code Organization**:
  - Data-driven architecture with complete separation of data from code
  - Modular functions for graph building, position calculation, and visualization
  - 426 lines of application code (down from 3,108 lines)

### Data Storage Solutions
- **File-Based Storage**: All data stored in JSON files (no database required)
- **Data Structure**:
  - `data/nodes.json`: 133 nodes with graphic metadata (labels, URLs, images)
  - `data/edges.json`: 235 active edges defining relationships
  - `data/edges_keyword_circular_commented.json`: 16 commented/disabled circular edges for keyword nodes
  - `config/graph_config.json`: Visualization settings (colors, positions, forces, layout)
- **Node Positioning**: 
  - Calculated positions for keyword nodes on outer circle (radius: 1177.1)
  - Graphics nodes positioned in center (radius: 360.0)
  - Position calculations using trigonometry for radial layout

### Authentication and Authorization
- **Current State**: No authentication implemented
- **Access Control**: None - publicly accessible application
- **Rationale**: Visualization tool designed for public access without sensitive data

### Performance Optimizations
- Function-level caching with `@lru_cache` decorator for JSON loading
- Graph caching to prevent regeneration on every HTTP request
- Optimized D3.js force simulation parameters for rendering performance
- Edge size normalization for visual clarity (min: 0.45, max: 1.07)

### Deployment Configuration
- **Production Server**: Gunicorn 21.2.0+ WSGI server
- **Configuration**: `Procfile` for deployment (Replit/Heroku compatible)
- **Dependency Management**: 
  - `requirements.txt` for pip-based deployment
  - `pyproject.toml` and `poetry.lock` for Poetry-based development
- **Python Version**: 3.10 or 3.11

## External Dependencies

### Third-Party Libraries
- **Flask** (3.0.0+): Web application framework for serving the visualization
- **NetworkX** (3.3): Graph theory library for building and manipulating the network structure
- **Gravis** (0.1.0): D3.js visualization wrapper for generating interactive graphs
- **Gunicorn** (21.2.0+): Production-grade WSGI HTTP server

### Frontend Dependencies
- **D3.js**: Force-directed graph layout and rendering (loaded via Gravis)
- **SVG**: Vector graphics for visualization rendering

### External Services
- **X/Twitter**: Image hosting and social media post links
  - Node images hosted on `pbs.twimg.com`
  - Post URLs linking to `x.com` (formerly Twitter)
  - Used for graphic node visual content and social context

### File System Dependencies
- **Static Assets**: No local image storage; all images are external URLs
- **Template System**: Flask Jinja2 templates for HTML generation
- **Data Files**: JSON configuration files in `data/` and `config/` directories

### Development Tools
- **Testing**: Custom test suite (`test_app.py`, `verify_deployment.py`) for data validation and deployment readiness
- **Logging**: Python standard library logging for debugging and monitoring
- **Version Control**: Project includes cleanup and refactoring documentation
"""
Interactive Network Graph Visualization Application

This Flask application generates an interactive D3.js network graph visualization
that displays relationships between various nodes and concepts. The graph uses the
gravis library for D3.js rendering and NetworkX for graph structure.

Author: AREVEUR5117
Version: 3.0 - Refactored with DRY principles
"""

import json
import math
import os
from datetime import datetime
from functools import lru_cache
from pathlib import Path
import logging

import networkx as nx
import gravis as gv
from flask import Flask, send_from_directory, Response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Cache control to prevent browser caching issues
_graph_generated = False
_generation_time = None

# Data paths
DATA_DIR = Path('data')
NODES_FILE = DATA_DIR / 'nodes.json'
EDGES_FILE = DATA_DIR / 'edges.json'
CONFIG_FILE = Path('config') / 'graph_config.json'


def load_json_file(filepath):
    """
    Load and parse a JSON file.
    
    Args:
        filepath (Path): Path to the JSON file
        
    Returns:
        dict or list: Parsed JSON data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    with open(filepath, 'r') as f:
        return json.load(f)


def load_nodes():
    """
    Load node data from JSON file.
    
    Returns:
        list: List of node dictionaries containing graphicLabel, graphicName,
              xPostURL, and xGraphicURL
    """
    logger.info(f'Loading nodes from {NODES_FILE}')
    nodes = load_json_file(NODES_FILE)
    logger.info(f'Loaded {len(nodes)} nodes')
    return nodes


def load_edges():
    """
    Load edge data from JSON file.
    
    Returns:
        list: List of edge dictionaries containing source, target, and label
    """
    logger.info(f'Loading edges from {EDGES_FILE}')
    edges = load_json_file(EDGES_FILE)
    logger.info(f'Loaded {len(edges)} edges')
    return edges


def load_config():
    """
    Load configuration from JSON file with fallback to defaults.
    
    Returns:
        dict: Configuration dictionary with colors, positions, and visualization settings
    """
    try:
        return load_json_file(CONFIG_FILE)
    except FileNotFoundError:
        logger.warning(f'Config file not found at {CONFIG_FILE}, using defaults')
        return get_default_config()


def get_default_config():
    """
    Get default configuration values.
    
    Returns:
        dict: Default configuration settings
    """
    return {
        "colors": {
            "default_color": "black",
            "highlight_color": "green",
            "background_color": "#000000"
        },
        "positions": {
            "keyword_radius": 1177.1,
            "graphics_radius": 360.0,
            "graphics_interval": 5
        }
    }


def calculate_positions(node_names, radius, interval=None):
    """
    Calculate circular or spiral positions for graph nodes.
    
    Args:
        node_names (list): List of node name strings to position
        radius (float): Base radius for node placement
        interval (int, optional): If provided, creates a spiral pattern
        
    Returns:
        dict: Dictionary mapping node names to {'x': float, 'y': float}
    """
    num_nodes = len(node_names)
    
    if interval is None:
        # Simple circular positions for outer (keyword) nodes
        return {
            name: {
                'x': radius * math.cos(2 * math.pi * i / num_nodes),
                'y': radius * math.sin(2 * math.pi * i / num_nodes)
            }
            for i, name in enumerate(node_names)
        }
    else:
        # Spiral positions for inner (graphic) nodes
        interval_factor = 170 / radius
        return {
            name: {
                'x': radius * (1 + (i % interval) * interval_factor) *
                     math.cos(2 * math.pi * (i // interval) / (num_nodes // interval + 1)),
                'y': radius * (1 + (i % interval) * interval_factor) *
                     math.sin(2 * math.pi * (i // interval) / (num_nodes // interval + 1))
            }
            for i, name in enumerate(node_names)
        }


def separate_node_types(nodes):
    """
    Separate nodes into keyword and graphic types.
    
    Args:
        nodes (list): List of all node dictionaries
        
    Returns:
        tuple: (keyword_nodes, graphics_nodes) - two lists of node names
    """
    keyword_nodes = [
        node["graphicName"] for node in nodes
        if node["graphicName"].startswith("kw-")
    ]
    graphics_nodes = [
        node["graphicName"] for node in nodes
        if not node["graphicName"].startswith("kw-")
    ]
    return keyword_nodes, graphics_nodes


def create_node_metadata(node, positions, config):
    """
    Create metadata dictionary for a graph node.
    
    Args:
        node (dict): Node data dictionary
        positions (dict): Position mapping for the node
        config (dict): Configuration dictionary
        
    Returns:
        dict: Node metadata for gravis
    """
    node_name = node["graphicName"]
    node_label = node["graphicLabel"]
    
    if node_name.startswith("kw-"):
        # Keyword node metadata
        return {
            'label': node_label,
            'metadata': {
                'opacity': 1.0,
                'label_color': 'purple',
                'label_size': 26,
                'color': 'purple',
                'size': 36.0,
                'x': positions[node_name]['x'],
                'y': positions[node_name]['y'],
            }
        }
    else:
        # Graphic node metadata
        x_post_url = node["xPostURL"]
        x_graphic_url = node["xGraphicURL"]
        highlight_color = config["colors"]["highlight_color"]
        
        hover_text = (
            f'<b><span style="font-size: 17px;">{node_label}</span></b><br>'
            f'<a href="{x_post_url}" target="_blank" style="font-size: 17px;">View X post</a><br>'
            f'<a href="{x_graphic_url}" target="_blank" style="font-size: 17px;">View image</a>'
        )
        
        return {
            'label': node_label,
            'metadata': {
                'opacity': 1.0,
                'label_color': highlight_color,
                'label_size': 7,
                'hover': hover_text,
                'image': x_graphic_url,
                'color': highlight_color,
                'size': 7.0,
                'x': positions[node_name]['x'],
                'y': positions[node_name]['y'],
            }
        }


def build_graph_structure(nodes, edges, config):
    """
    Build the graph structure with nodes and edges.
    
    Args:
        nodes (list): List of node dictionaries
        edges (list): List of edge dictionaries
        config (dict): Configuration dictionary
        
    Returns:
        dict: Graph structure for gravis
    """
    # Separate node types
    keyword_nodes, graphics_nodes = separate_node_types(nodes)
    
    # Calculate positions
    keyword_positions = calculate_positions(
        keyword_nodes, 
        config["positions"]["keyword_radius"]
    )
    graphics_positions = calculate_positions(
        graphics_nodes,
        config["positions"]["graphics_radius"],
        config["positions"]["graphics_interval"]
    )
    
    # Combine positions
    all_positions = {**keyword_positions, **graphics_positions}
    
    # Initialize graph structure
    graph = {
        'graph': {
            'nodes': {},
            'edges': []
        }
    }
    
    # Add nodes
    for node in nodes:
        node_name = node["graphicName"]
        logger.info(node["graphicLabel"])
        
        node_data = create_node_metadata(node, all_positions, config)
        graph['graph']['nodes'][node_name] = node_data
    
    # Add edges
    default_edge_metadata = {
        'directed': True,
        'color': config["colors"]["default_color"],
        'size': 1
    }
    
    for edge in edges:
        graph['graph']['edges'].append({
            'source': edge['source'],
            'target': edge['target'],
            'label': edge.get('label', ''),
            'metadata': default_edge_metadata
        })
    
    return graph


def generate_map_v2():
    """
    Generate the interactive network graph visualization.
    
    Loads data from JSON files, builds the graph structure, and exports
    as an HTML file with D3.js visualization.
    
    Returns:
        str: Path to the exported HTML file
    """
    # Load all data
    nodes = load_nodes()
    edges = load_edges()
    config = load_config()
    
    # Build graph structure
    graph_data = build_graph_structure(nodes, edges, config)
    
    # Create NetworkX graph
    G = nx.DiGraph()
    
    # Add nodes to NetworkX graph
    for node_name, node_data in graph_data['graph']['nodes'].items():
        G.add_node(node_name, **node_data)
    
    # Add edges to NetworkX graph
    for edge in graph_data['graph']['edges']:
        G.add_edge(
            edge['source'], 
            edge['target'], 
            label=edge['label'], 
            metadata=edge['metadata']
        )
    
    # Generate D3.js visualization
    fig = gv.d3(
        G,
        graph_height=1100,
        edge_curvature=0.11,
        zoom_factor=0.5,
        layout_algorithm_active=True,
        node_hover_neighborhood=True,
        use_edge_size_normalization=True,
        edge_size_normalization_min=0.45,
        edge_size_normalization_max=1.07,
        many_body_force_strength=-1776.0,
        many_body_force_theta=1.17,
        many_body_force_min_distance=0.01,
        many_body_force_max_distance=589.0,
        links_force_distance=107.00,
        links_force_strength=0.11,
        use_collision_force=True,
        collision_force_radius=100.00,
        collision_force_strength=0.07,
        use_x_positioning_force=True,
        x_positioning_force_strength=0.07,
        use_y_positioning_force=True,
        y_positioning_force_strength=0.10,
        use_centering_force=False,
    )
    
    # Export HTML
    os.makedirs('templates', exist_ok=True)
    output_path = 'templates/index.html'
    fig.export_html(filepath=output_path, overwrite=True)
    
    logger.info(f'Graph visualization exported to {output_path}')
    return output_path


@app.route('/')
def index() -> Response:
    """
    Serve the main index page with the network graph visualization.
    
    Returns:
        Response: Flask response with index.html and cache control headers
    """
    global _graph_generated, _generation_time
    
    logger.info('Index page requested')
    
    # Check if we need to generate the graph
    template_path = 'templates/index.html'
    if not _graph_generated or not os.path.exists(template_path):
        logger.info('Generating new graph visualization...')
        generate_map_v2()
        _graph_generated = True
        _generation_time = datetime.now()
        logger.info(f'Graph generated successfully at {_generation_time}')
    else:
        logger.info(f'Serving cached graph (generated at {_generation_time})')
    
    response = send_from_directory('templates', 'index.html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

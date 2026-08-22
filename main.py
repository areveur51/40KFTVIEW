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
import tempfile
from datetime import datetime, timezone
from pathlib import Path
import logging

import gravis as gv
from flask import Flask, Response, jsonify, make_response, render_template, request, send_from_directory

from ingest import api as x_api
from ingest.archive import load_archive_posts
from ingest.catalog import build_catalog, load_state, merge_inbox, save_state

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 512 * 1024 * 1024

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
            "highlight_size": 1.5,
            "background_color": "#000000",
            "highlight2_color": "green"
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
        # Graphic node metadata with image display
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
                'click': x_post_url,
                'image': x_graphic_url,
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
    
    # Initialize graph structure with visual metadata
    graph = {
        'graph': {
            'label': '40,000 FT. VIEW',
            'directed': True,
            'metadata': {
                'graph_height': 771,
                'arrow_color': config["colors"]["highlight_color"],
                'arrow_size': 11,
                'background_color': config["colors"]["background_color"],
                'show_node': True,
                'node_size_factor': 2,
                'node_color': config["colors"]["background_color"],
                'node_opacity': 0.8,
                'node_size': 117,
                'node_border_color': config["colors"]["default_color"],
                'node_border_size': 0.0,
                'node_label_color': config["colors"]["default_color"],
                'node_label_size': 1.77,
                'node_hover': 'Node: $label',
                'node_click': '$hover',
                'show_node_label': False,
                'show_edge': True,
                'edge_size_factor': 0.51,
                'edge_color': config["colors"]["default_color"],
                'edge_opacity': 0.1,
                'edge_size': 0.1,
                'edge_label_color': 'black',
                'edge_label_size': 1,
                'edge_hover': '$label',
                'edge_click': '$label',
            },
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
    
    # Add edges with cyberpunk styling
    default_edge_metadata = {
        'color': config["colors"]["highlight_color"],
        'opacity': 1.0,
        'size': config["colors"]["highlight_size"],
        'label_color': config["colors"]["highlight2_color"],
        'label_size': 5,
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
    
    # Generate D3.js visualization with graph data structure
    fig = gv.d3(
        graph_data,
        graph_height=1100,
        node_label_data_source='label',
        edge_label_data_source='label',
        show_edge_label=True,
        edge_curvature=0.11,
        zoom_factor=0.5,
        layout_algorithm_active=True,
        node_hover_neighborhood=True,
        use_edge_size_normalization=True,
        edge_size_normalization_min=0.45,
        edge_size_normalization_max=1.07,
        use_many_body_force=True,
        many_body_force_strength=-1776.0,
        many_body_force_theta=1.17,
        use_many_body_force_min_distance=True,
        many_body_force_min_distance=0.01,
        use_many_body_force_max_distance=True,
        many_body_force_max_distance=589.0,
        use_links_force=True,
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


def _no_store(response) -> Response:
    response = make_response(response)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


def _ensure_classic_graph() -> None:
    global _graph_generated, _generation_time
    template_path = 'templates/index.html'
    if not _graph_generated or not os.path.exists(template_path):
        logger.info('Generating new graph visualization...')
        generate_map_v2()
        _graph_generated = True
        _generation_time = datetime.now()
        logger.info(f'Graph generated successfully at {_generation_time}')


def _stamp_sync_state(source, records):
    state = load_state()
    tweet_ids = [item.get("tweet_id") for item in records if item.get("tweet_id")]
    newest = max(tweet_ids, key=lambda value: int(value)) if tweet_ids else state.get("newest_tweet_id")
    state.update({
        "last_sync_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "last_source": source,
        "newest_tweet_id": newest or "",
        "api_available": x_api.api_available(),
    })
    save_state(state)
    return state


@app.route('/')
def index() -> Response:
    """Serve the searchable timeline/constellation decode explorer."""
    logger.info('Explorer page requested')
    return _no_store(render_template('explorer.html'))


@app.route('/classic')
def classic() -> Response:
    """Serve the original Gravis force-directed graph."""
    logger.info('Classic graph page requested')
    _ensure_classic_graph()
    return _no_store(send_from_directory('templates', 'index.html'))


@app.route('/api/catalog')
def api_catalog():
    """Return confirmed decodes plus inbox candidates as JSON."""
    catalog = build_catalog()
    return _no_store(jsonify(catalog))


@app.route('/api/sync', methods=['POST'])
def api_sync():
    """Pull new posts from the X API and merge detected decodes into the inbox."""
    if not x_api.api_available():
        return jsonify({
            "ok": False,
            "error": "missing_token",
            "message": (
                "X_BEARER_TOKEN is not set. For complete history from account "
                "creation, import your official X archive. The user-timeline API "
                "only covers recent posts (about 3,200) and full-archive search "
                "needs paid X API access."
            ),
        }), 400

    payload = request.get_json(silent=True) or {}
    username = payload.get("username") or "areveur51"
    state = load_state()
    try:
        if payload.get("full"):
            records = x_api.fetch_full_archive(
                username=username,
                start_time=payload.get("start_time"),
            )
            source = "api_full_archive"
        else:
            since_id = None if payload.get("backfill") else state.get("newest_tweet_id")
            records = x_api.fetch_user_timeline(
                username=username,
                since_id=since_id or None,
                start_time=payload.get("start_time"),
            )
            source = "api_timeline"
    except x_api.XApiError as exc:
        logger.exception("X API sync failed")
        return jsonify({"ok": False, "error": "api_error", "message": str(exc)}), 502

    decodes = [item for item in records if item.get("is_decode")]
    stats = merge_inbox(decodes)
    _stamp_sync_state(source, records)
    return jsonify({
        "ok": True,
        "source": source,
        "fetched": len(records),
        "decodes": len(decodes),
        **stats,
        "message": (
            f"Synced {len(records)} posts, detected {len(decodes)} decodes, "
            f"added {stats['added']} new inbox items."
        ),
    })


@app.route('/api/ingest/archive', methods=['POST'])
def api_ingest_archive():
    """Import an official X archive zip or tweets.js file."""
    uploaded = request.files.get("archive")
    if uploaded is None or not uploaded.filename:
        return jsonify({
            "ok": False,
            "error": "missing_file",
            "message": "Choose an official X archive .zip or a tweets.js file.",
        }), 400

    suffix = Path(uploaded.filename).suffix or ".zip"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        uploaded.save(tmp.name)
        temp_path = tmp.name
    try:
        posts = load_archive_posts(temp_path)
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        return jsonify({"ok": False, "error": "bad_archive", "message": str(exc)}), 400
    finally:
        try:
            os.unlink(temp_path)
        except OSError:
            pass

    decodes = [item for item in posts if item.get("is_decode")]
    stats = merge_inbox(decodes)
    _stamp_sync_state("archive", posts)
    return jsonify({
        "ok": True,
        "source": "archive",
        "fetched": len(posts),
        "decodes": len(decodes),
        **stats,
        "message": (
            f"Archive scanned {len(posts)} posts, detected {len(decodes)} decodes, "
            f"added {stats['added']} new inbox items."
        ),
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

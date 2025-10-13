"""
Configuration Loader Module

This module loads and provides access to graph visualization configuration
settings including colors, positions, and visualization parameters.

Author: AREVEUR5117
"""

import json
from typing import Dict, Any


def load_config(config_path: str = 'config/graph_config.json') -> Dict[str, Any]:
    """
    Load graph configuration from JSON file.
    
    Args:
        config_path (str): Path to the configuration JSON file.
        
    Returns:
        Dict[str, Any]: Configuration dictionary containing colors, positions,
                       graph metadata, and visualization settings.
                       
    Raises:
        FileNotFoundError: If the config file doesn't exist.
        json.JSONDecodeError: If the config file contains invalid JSON.
    """
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default configuration if file doesn't exist
        return get_default_config()


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration settings for the graph visualization.
    
    Returns:
        Dict[str, Any]: Default configuration dictionary.
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
        },
        "graph_metadata": {
            "label": "40,000 FT. VIEW",
            "directed": True,
            "graph_height": 771,
            "arrow_size": 11,
            "node_size_factor": 2,
            "node_opacity": 0.8,
            "node_size": 117,
            "node_border_size": 0.0,
            "node_label_size": 1.77,
            "show_node_label": False,
            "show_edge": True,
            "edge_size_factor": 0.51,
            "edge_opacity": 0.1,
            "edge_size": 0.1,
            "edge_label_size": 1
        },
        "visualization": {
            "graph_height": 1100,
            "edge_curvature": 0.11,
            "zoom_factor": 0.5,
            "layout_algorithm_active": True,
            "node_hover_neighborhood": True,
            "use_edge_size_normalization": True,
            "edge_size_normalization_min": 0.45,
            "edge_size_normalization_max": 1.07,
            "many_body_force_strength": -1776.0,
            "many_body_force_theta": 1.17,
            "many_body_force_min_distance": 0.01,
            "many_body_force_max_distance": 589.0,
            "links_force_distance": 107.00,
            "links_force_strength": 0.11,
            "collision_force_radius": 100.00,
            "collision_force_strength": 0.07,
            "x_positioning_force_strength": 0.07,
            "y_positioning_force_strength": 0.10,
            "use_centering_force": False
        }
    }

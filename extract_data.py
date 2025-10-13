"""
Utility script to extract data from the original main.py for refactoring.
This script parses the main.py file and extracts node and edge data into separate JSON files.
"""

import json
import re

# Read the original main.py
with open('main.py', 'r') as f:
    content = f.read()

# Extract the data array using regex (it starts at line 54 and ends before colors definition)
data_match = re.search(r'data = \[(.*?)\](?=\s+default_color)', content, re.DOTALL)
if data_match:
    data_str = '[' + data_match.group(1) + ']'
    # Fix the data string to make it valid JSON
    data_str = data_str.replace("'", '"')
    data_str = data_str.replace('graphicLabel":', '"graphicLabel":')
    data_str = data_str.replace('graphicName":', '"graphicName":')
    data_str = data_str.replace('xPostURL":', '"xPostURL":')
    data_str = data_str.replace('xGraphicURL":', '"xGraphicURL":')
    
    # Parse and save
    try:
        node_data = json.loads(data_str)
        with open('data/nodes.json', 'w') as f:
            json.dump(node_data, f, indent=2)
        print(f"Extracted {len(node_data)} nodes to data/nodes.json")
    except json.JSONDecodeError as e:
        print(f"Error parsing node data: {e}")
        print("Will need to extract manually")

# Extract graph configuration
config = {
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

with open('config/graph_config.json', 'w') as f:
    json.dump(config, f, indent=2)
print("Created config/graph_config.json")

print("Data extraction complete!")

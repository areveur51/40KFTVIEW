# Interactive Network Graph Visualization

An interactive web application that visualizes complex relationships between nodes using D3.js network graphs. Built with Flask, NetworkX, and Gravis for dynamic, force-directed graph rendering.

## 📸 Visualization Preview

![Network Graph Visualization](screenshots/visualization.png)

*Interactive force-directed graph with cyberpunk theme: black background, purple keyword nodes on outer circle, image thumbnails in center, and green connecting edges.*

## 🌟 Features

- **Interactive Visualization**: Zoom, pan, and hover over nodes to explore relationships
- **Dynamic Force Layout**: Automatic node positioning using D3.js force simulation
- **Two Node Types**:
  - **Graphic Nodes**: Visual content with linked images and social media posts
  - **Keyword Nodes**: Conceptual nodes positioned on the outer circle
- **Performance Optimized**: 
  - Graph caching to avoid regeneration on every request
  - Optimized position calculations
  - Efficient rendering with gravis/D3.js
- **Responsive Design**: Works across different screen sizes
- **Cache Control**: Proper HTTP headers to ensure fresh content delivery

## 📋 Requirements

- Python 3.10 or 3.11
- Flask 3.0.0+
- NetworkX 3.3
- Gravis 0.1.0
- Gunicorn 21.2.0+ (for production deployment)

## 🚀 Getting Started

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd <repo-name>
```

2. Install dependencies using one of these methods:

**Option A: Using pip (recommended for quick setup)**
```bash
pip install -r requirements.txt
```

**Option B: Using Poetry (for development)**
```bash
poetry install
```

Note: This project uses Python 3.10 or 3.11. Make sure you have a compatible version installed.

### Running the Application

#### Development Mode

Run the Flask development server:

```bash
python main.py
```

The application will be available at `http://localhost:5000`

#### Production Mode

For production deployment, use Gunicorn:

```bash
gunicorn --bind=0.0.0.0:5000 --reuse-port main:app
```

## 📁 Project Structure

```
.
├── main.py                 # Main Flask application with graph generation
├── config_loader.py        # Configuration management module
├── extract_data.py         # Utility script for data extraction
├── templates/              # Flask templates directory
│   └── index.html         # Generated graph visualization
├── data/                   # Data storage directory
├── config/                 # Configuration files
│   └── graph_config.json  # Graph styling and layout configuration
├── pyproject.toml         # Python project configuration
├── Procfile               # Deployment configuration
└── README.md              # This file
```

## 🎨 Configuration

The graph visualization can be customized by modifying the configuration in `config_loader.py` or by editing `config/graph_config.json`:

### Color Scheme
```python
{
  "colors": {
    "default_color": "black",
    "highlight_color": "green",
    "background_color": "#000000"
  }
}
```

### Node Positioning
```python
{
  "positions": {
    "keyword_radius": 1177.1,
    "graphics_radius": 360.0,
    "graphics_interval": 5
  }
}
```

### Force Simulation Parameters
```python
{
  "visualization": {
    "many_body_force_strength": -1776.0,
    "links_force_distance": 107.00,
    "collision_force_radius": 100.00
  }
}
```

## 🔧 API Documentation

### Main Routes

#### `GET /`
Serves the interactive graph visualization.

**Response**: HTML page with embedded D3.js graph

**Headers**:
- `Cache-Control: no-cache, no-store, must-revalidate`
- `Pragma: no-cache`
- `Expires: 0`

## 📊 Graph Data Structure

### Node Format
Each node contains:
- `graphicLabel`: Display label for the node
- `graphicName`: Unique identifier
- `xPostURL`: Link to associated social media post (optional)
- `xGraphicURL`: Link to associated image (optional)

### Node Types
1. **Graphic Nodes**: Standard nodes with visual content
2. **Keyword Nodes**: Nodes prefixed with `kw-` positioned on the outer circle

## 🔄 How It Works

1. **First Request**: 
   - Server generates the graph visualization
   - Calculates node positions using circular/spiral algorithms
   - Creates D3.js interactive HTML output
   - Caches the result

2. **Subsequent Requests**:
   - Serves cached HTML for faster load times
   - Only regenerates if cache is missing

3. **Node Positioning**:
   - Keyword nodes: Circular layout on outer radius
   - Graphic nodes: Spiral layout on inner radius
   - Force-directed layout for natural spacing

## 🚀 Performance Optimizations

- **Caching**: Graph generated once and cached
- **Lazy Loading**: Visualization only created when needed
- **Optimized Math**: Pre-calculated trigonometric values
- **Efficient Data Structures**: Dictionary-based node/edge storage

## 🛠️ Development

### Adding New Nodes

Edit the `data` array in `generate_map_v2()` function:

```python
{
    "graphicLabel": "Your Label",
    "graphicName": "unique_id",
    "xPostURL": "https://...",
    "xGraphicURL": "https://..."
}
```

### Adding New Edges

Add to the `edges` array in `graph5` dictionary:

```python
{
    'source': 'source_node_id',
    'target': 'target_node_id',
    'label': 'Relationship description',
    'metadata': default_edge_metadata
}
```

## 📝 Code Documentation

All functions include comprehensive docstrings following Google style:

```python
def function_name(arg1, arg2):
    """
    Brief description.
    
    Detailed description of what the function does.
    
    Args:
        arg1 (type): Description of arg1.
        arg2 (type): Description of arg2.
    
    Returns:
        type: Description of return value.
    """
```

## 🐛 Troubleshooting

### Graph Not Displaying
- Check browser console for JavaScript errors
- Ensure `templates/` directory exists
- Verify all dependencies are installed

### Performance Issues
- Graph generation is CPU-intensive for first load
- Consider pre-generating graph for production
- Use production-ready WSGI server (Gunicorn)

### Cache Issues
- Clear browser cache (Ctrl+Shift+R / Cmd+Shift+R)
- Delete `templates/index.html` to force regeneration
- Check server logs for generation status

## 📄 License

[Specify your license here]

## 👤 Author

**AREVEUR5117**

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## ⭐ Show Your Support

Give a ⭐️ if this project helped you!

## 📮 Contact

For questions or support, please open an issue in the repository.

---

**Built with ❤️ using Flask, NetworkX, and D3.js**

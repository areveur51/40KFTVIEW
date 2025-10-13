"""
Interactive Network Graph Visualization Application

This Flask application generates an interactive D3.js network graph visualization
that displays relationships between various nodes and concepts. The graph uses the
gravis library for D3.js rendering and NetworkX for graph structure.

Author: AREVEUR5117
Version: 2.0
"""

import networkx as nx
import gravis as gv
from flask import Flask, send_from_directory, Response
import logging
import math
import os
from functools import lru_cache
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Cache control to prevent browser caching issues
_graph_generated = False
_generation_time = None


@app.route('/')
def index() -> Response:
    """
    Serve the main index page with the network graph visualization.
    
    This route generates the graph visualization on the first request and serves
    the cached HTML on subsequent requests unless regeneration is forced.
    
    Returns:
        Response: Flask response object with the index.html file and cache control headers.
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


def calculate_positions(node_names, radius, interval=None):
    """
    Calculate circular or spiral positions for graph nodes.
    
    This function positions nodes either in a simple circle (for keyword nodes) or
    in a spiral pattern (for graphic nodes). The spiral pattern helps distribute
    nodes more evenly when there are many nodes.
    
    Args:
        node_names (list): List of node name strings to position.
        radius (float): Base radius for node placement.
        interval (int, optional): If provided, creates a spiral pattern with this
                                 many nodes per revolution. If None, creates a simple
                                 circle. Defaults to None.
    
    Returns:
        dict: Dictionary mapping node names to position dictionaries with 'x' and 'y' keys.
              For example: {'node1': {'x': 100.5, 'y': 200.3}, ...}
    
    Examples:
        >>> names = ['node1', 'node2', 'node3']
        >>> positions = calculate_positions(names, radius=100)
        >>> 'node1' in positions
        True
        >>> 'x' in positions['node1']
        True
    """
    num_nodes = len(node_names)
    
    if interval is None:
        # Calculate simple circular positions for outer (keyword) nodes
        return {
            name: {
                'x': radius * math.cos(2 * math.pi * i / num_nodes),
                'y': radius * math.sin(2 * math.pi * i / num_nodes)
            }
            for i, name in enumerate(node_names)
        }
    else:
        # Calculate spiral positions for inner (graphic) nodes
        # Pre-calculate interval factor to optimize performance
        interval_factor = 170 / radius
        return {
            name: {
                'x':
                radius * (1 + (i % interval) * interval_factor) *
                math.cos(2 * math.pi * (i // interval) /
                         (num_nodes // interval + 1)),
                'y':
                radius * (1 + (i % interval) * interval_factor) *
                math.sin(2 * math.pi * (i // interval) /
                         (num_nodes // interval + 1))
            }
            for i, name in enumerate(node_names)
        }


def generate_map_v2():
    """
    Generate the interactive network graph visualization.
    
    This function creates a complex D3.js network graph visualization with:
    - Multiple node types (graphics nodes and keyword nodes)
    - Interconnected edges representing relationships
    - Custom positioning using circular and spiral layouts
    - Interactive features (hover, click, zoom)
    - Custom styling and visual properties
    
    The generated graph is exported as an HTML file to both 'index.html' and 
    'templates/index.html' for serving via Flask.
    
    Node Types:
        - Graphic nodes: Visual content nodes with images and X (Twitter) post links
        - Keyword nodes: Text-only nodes positioned on the outer circle (prefix: 'kw-')
    
    Returns:
        str: Path to the exported HTML file ('templates/index.html').
        
    Side Effects:
        - Creates/overwrites 'index.html' in the root directory
        - Creates/overwrites 'templates/index.html' for Flask serving
        - Logs node information during generation
    
    Note:
        This function contains all node and edge data inline. For better
        maintainability, consider externalizing this data to JSON files.
    """
    data = [
        {
            "graphicLabel":
            "MSM_ATTACK[Q].jpg",
            "graphicName":
            "msmattack",
            "xPostURL":
            "https://x.com/areveur51/status/1818697259866865764?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GT1PgkEWMAAX4Vn?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "YOU AWAKE IS THEIR GREATEST FEAR",
            "graphicName":
            "greatestfear",
            "xPostURL":
            "https://x.com/areveur51/status/1801729790577086752?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GQEHsYCXcAAOI-Z?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "FREE THOUGHT",
            "graphicName":
            "freethought",
            "xPostURL":
            "https://x.com/areveur51/status/1803467510483968104?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GQc0JG9WIAAyRNy?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "BACKCHANNELS",
            "graphicName":
            "backchannels",
            "xPostURL":
            "https://x.com/areveur51/status/1795294297169760388?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GOoqpArWQAAMBlm?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "NO ONE PERSON IS ABOVE ANOTHER",
            "graphicName":
            "noonepersonisaboveanother",
            "xPostURL":
            "https://x.com/areveur51/status/1804534921966325794?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GQr-8m0XQAALcnf?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "ENOU[G]H IS EN[O]UGH",
            "graphicName":
            "enoughisenough",
            "xPostURL":
            "https://x.com/areveur51/status/1804576149839987171?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GQskcUVXEAAYq18?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "A clean [H]ouse is very important",
            "graphicName":
            "cleanhouse",
            "xPostURL":
            "https://x.com/areveur51/status/1806102437150724586?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GRCQl4sWQAA6yGn?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "Q CLEARANCE PATRIOT",
            "graphicName":
            "qclearancepatriot",
            "xPostURL":
            "https://x.com/areveur51/status/1797283228128076211?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GPE7keRXcAEvPrB?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "PROTECT_MOGUL",
            "graphicName":
            "protectmogul",
            "xPostURL":
            "https://x.com/areveur51/status/1796365443000566055?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GO342SVWgAIfPC2?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "VIPANON",
            "graphicName":
            "vipanon",
            "xPostURL":
            "https://x.com/areveur51/status/1804545498575143102?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GUBa5HWWMAA85j9?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "KEYHOLE",
            "graphicName":
            "keyhole",
            "xPostURL":
            "https://x.com/areveur51/status/1798356078540849349?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GPULUlIWoAANbdo?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "[INFO WARS]",
            "graphicName":
            "infowars",
            "xPostURL":
            "https://x.com/areveur51/status/1797435415412056117?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GPHF-1IXwAAHsEP?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "RENEGADE",
            "graphicName":
            "renegade",
            "xPostURL":
            "https://x.com/areveur51/status/1795879113892266399?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GOw-iOgWAAEzji3?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "END OF THE D PARTY",
            "graphicName":
            "endofthedparty",
            "xPostURL":
            "https://x.com/areveur51/status/1801662550435602699?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GQDKiiCWAAMu4iY?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "ECW",
            "graphicName":
            "ecw",
            "xPostURL":
            "https://x.com/areveur51/status/1793287498585518118?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GOMJeYzXEAAL_hp?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "_\ COUNCIL OF FOREIGN RELATIONS",
            "graphicName":
            "councilofforeignrelations",
            "xPostURL":
            "https://x.com/areveur51/status/1795603869914878362?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GOtEM8oXQAAsgNx?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "SHADOW GOVERNMENT",
            "graphicName":
            "shadowgovernment",
            "xPostURL":
            "https://x.com/areveur51/status/1791780339246850215?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GN2uuNAXEAEZywU?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "SUBVERSION",
            "graphicName":
            "subversion",
            "xPostURL":
            "https://x.com/areveur51/status/1804369712035299368?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GQposF5WIAAcNLY?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "PDB PAPER-TRAIL",
            "graphicName":
            "pdbpapertrail",
            "xPostURL":
            "https://x.com/areveur51/status/1800742801279189019?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GP2GCFtXMAEFWyg?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "WIZARDS & WARLOCKS",
            "graphicName":
            "wizardsandwarlocks",
            "xPostURL":
            "https://x.com/areveur51/status/1805721219700080704?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GQ814MfXwAAdob9?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "WE STAND AT THE READY",
            "graphicName":
            "westandattheready",
            "xPostURL":
            "https://x.com/areveur51/status/1809423813941293310?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GRxdXfoW4AAp2eL?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "MIL INTEL",
            "graphicName":
            "milintel",
            "xPostURL":
            "https://x.com/areveur51/status/1785147128408403969?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GMYd2edXcAAOCg0?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "[CROWDSTRIKE]",
            "graphicName":
            "crowdstrike",
            "xPostURL":
            "https://x.com/areveur51/status/1799931544355659921?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GPqkMvmWkAAUUqk?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "COMMS GOOD",
            "graphicName":
            "commsgood",
            "xPostURL":
            "https://x.com/areveur51/status/1801704911383445842?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GQDxEU7WMAAjbGP?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "SNOWDEN",
            "graphicName":
            "snowden",
            "xPostURL":
            "https://x.com/areveur51/status/1803194988601417915?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GQY8SOeWUAAf4_6?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "HUSSEIN IRAN CONN",
            "graphicName":
            "husseiniran",
            "xPostURL":
            "https://x.com/areveur51/status/1792503245518123292?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GOBAMqzWMAE5fEp?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "XKEYSCORE",
            "graphicName":
            "xkeyscore",
            "xPostURL":
            "https://x.com/areveur51/status/1806381100383502568?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GRGOCXdXQAAjA7k?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "PROJECT DEEPDREAM V2",
            "graphicName":
            "projectdeepdreamv2",
            "xPostURL":
            "https://x.com/areveur51/status/1814205893619392959?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GS1aj-CWMAAnA5M?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "DISCLOSURE",
            "graphicName":
            "disclosure",
            "xPostURL":
            "https://x.com/areveur51/status/1793585053672362304?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GOQYGAjXUAEzYsf?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "BILL 'B2' BARR",
            "graphicName":
            "billb2barr",
            "xPostURL":
            "https://x.com/areveur51/status/1800339702442074373?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GPwXasYXoAAcqRh?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "DO NOT BE AFRAID",
            "graphicName":
            "donotbeafraid",
            "xPostURL":
            "https://x.com/areveur51/status/1796666950606635486?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GO8LDf0W8AAceOz?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "YOU ARE BEING TRACKED",
            "graphicName":
            "youarebeingtracked",
            "xPostURL":
            "https://x.com/areveur51/status/1797826017026847056?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GPMpO32WkAABmoB?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "ROTHSCHILD OWNED & CONTROLLED BANKS",
            "graphicName":
            "rothsownedcontrolledbanks",
            "xPostURL":
            "https://x.com/areveur51/status/1806368502384603204?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GRGCk_-XgAA0l0p?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "CLASSIFIED",
            "graphicName":
            "classified",
            "xPostURL":
            "https://x.com/areveur51/status/1793920337429553187?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GOVJCa5XwAAu69i?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "ENJOY THE SHOW",
            "graphicName":
            "enjoytheshow",
            "xPostURL":
            "https://x.com/areveur51/status/1794387949104075224?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GObyVFJXIAAWCVY?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "BRING THE THUNDER",
            "graphicName":
            "bringthethunder",
            "xPostURL":
            "https://x.com/areveur51/status/1803603747437994128?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GQewC5qXcAAb6Ej?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "ARE YOU READY TO SERVE YOUR COUNTRY AGAIN?",
            "graphicName":
            "readytoserve",
            "xPostURL":
            "https://x.com/areveur51/status/1805647435894493563?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GQ7yxZbXcAAxXEx?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "GO ORDERS",
            "graphicName":
            "goorders",
            "xPostURL":
            "https://x.com/areveur51/status/1794703829612585422?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GOgRnrVXoAAW6AU?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "MANILA EXTRACTION",
            "graphicName":
            "manilaextraction",
            "xPostURL":
            "https://x.com/areveur51/status/1795149040373395901?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GOmL4wXXsAAE3-c?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "NOTHING IS HAPPENING",
            "graphicName":
            "nothingishappening",
            "xPostURL":
            "https://x.com/areveur51/status/1806022171002650982?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GRBHl4LWQAA5YGa?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "C.A.T.",
            "graphicName":
            "cat",
            "xPostURL":
            "https://x.com/areveur51/status/1790761178198602046?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GNoPzM2XAAA-Im2?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "KEYSTONE = DNI",
            "graphicName":
            "keystonedni",
            "xPostURL":
            "https://x.com/areveur51/status/1798779606872248340?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GPaMhItWYAAYIAw?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "SARS-COV-2",
            "graphicName":
            "sarscov2",
            "xPostURL":
            "https://x.com/areveur51/status/1798487434658783655?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GPWCyddWsAA_oXW?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "VIRUS OR ELECTION?",
            "graphicName":
            "virusorelection",
            "xPostURL":
            "https://x.com/areveur51/status/1816000682920477102?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GTO6_VAXgAAWUi2?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "ILLEGALS VOTE BLUE",
            "graphicName":
            "illegalsvoteblue",
            "xPostURL":
            "https://x.com/areveur51/status/1797816661652709490?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GPMguXtWYAA3t42?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "[HERD THE SHEEP]",
            "graphicName":
            "herdthesheep",
            "xPostURL":
            "https://x.com/areveur51/status/1816509365140050366?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GTWJnebW0AAbarN?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "LAND SALES TO FOREIGNERS",
            "graphicName":
            "landsales",
            "xPostURL":
            "https://x.com/areveur51/status/1817644500816105900?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GTmSCHgXcAAxHeX?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "HUNTERS BECOME THE HUNTED",
            "graphicName":
            "huntersbecomethehunted",
            "xPostURL":
            "https://x.com/areveur51/status/1818000025525346663?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GTrVXUiWEAANI-d?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "LIQUIDITY EVENTS",
            "graphicName":
            "liquidityevents",
            "xPostURL":
            "https://x.com/areveur51/status/1818382429679452596?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GTwxEdiWwAAo3x3?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "FOR ANONS/PATRIOTS",
            "graphicName":
            "foranonspatriots",
            "xPostURL":
            "https://x.com/areveur51/status/1819489984841392185?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GUbqgoVXMAAgM9H?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "GEN. FLYNN",
            "graphicName":
            "genflynn",
            "xPostURL":
            "https://x.com/Areveur51/status/1822293844748128506?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GUoWgvqXQAAnHQ1?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "MEDIA BRAINWASHING",
            "graphicName":
            "mediabrainwashing",
            "xPostURL":
            "https://x.com/Areveur51/status/1822852832443175095?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GUwS95nWUAAe_6M?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "TRUMP/ELON X SPACE",
            "graphicName":
            "trumpelonxspace",
            "xPostURL":
            "https://x.com/Areveur51/status/1823198656163426360?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GU1Nft2XkAAmMe0?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "CENSORSHIP",
            "graphicName":
            "censorship",
            "xPostURL":
            "https://x.com/Areveur51/status/1826689432285512086?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GVm0WTGXQAAowSJ?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "UNFOOKWITABLE",
            "graphicName":
            "unfookwitable",
            "xPostURL":
            "https://x.com/Areveur51/status/1830030525316149557?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GWWTBWdXkAIURiV?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "CLINTON-OBAMA TICKET",
            "graphicName":
            "clintonobamaticket",
            "xPostURL":
            "https://x.com/Areveur51/status/1846303475375710577?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GZ9iQPLXYAAJN80?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "'#2' QANON",
            "graphicName":
            "number2qanon",
            "xPostURL":
            "https://x.com/Areveur51/status/1846753860871758207?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GaD82SEWMAAjxDu?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "DECLAS OF FISA",
            "graphicName":
            "declassoffisa",
            "xPostURL":
            "https://x.com/Areveur51/status/1847806564423377167?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GaS6RbJXUAAzsbh?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "UNMASKING",
            "graphicName":
            "unmasking",
            "xPostURL":
            "https://x.com/areveur51/status/1848306495726715087?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GaaA9gfXkAAQDTC?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "Q KNOWLEDGE IS POWER",
            "graphicName":
            "qknowledgeispower",
            "xPostURL":
            "https://x.com/Areveur51/status/1848490144141365576?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/Gacn_RHXQAAQXce?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "THE AGE OF THE MSM IS OVER",
            "graphicName":
            "msmisover",
            "xPostURL":
            "https://x.com/areveur51/status/1849483865712169428?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GaqvxU-XEAUyoTN?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "HISTORY BOOKS",
            "graphicName":
            "historybooks",
            "xPostURL":
            "https://x.com/Areveur51/status/1851021191261405256?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GbAl9oiWUAA98sA?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "'QANON'",
            "graphicName":
            "qanon",
            "xPostURL":
            "https://x.com/areveur51/status/1851274290282279272?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GbEMJxbW4AAwRL8?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "DESTINATION SPACE",
            "graphicName":
            "destinationspace",
            "xPostURL":
            "https://x.com/areveur51/status/1851371121188487599?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GbFkNB8XEAA2hQs?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "WRAY IS A SLEEPER",
            "graphicName":
            "wrayisasleeper",
            "xPostURL":
            "https://x.com/areveur51/status/1851866104542511491?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GbMmaAZXoAAI0PV?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "TIME TO SHOW THE WORLD",
            "graphicName":
            "timetoshowtheworld",
            "xPostURL":
            "https://x.com/areveur51/status/1853849271881412791?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GboyFTmXgAAwkJm?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "_SKY FORTRESS ENGAGED]_yes",
            "graphicName":
            "skyfortressengaged",
            "xPostURL":
            "https://x.com/Areveur51/status/1854710624783073715?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/Gb1Be4uX0A0xfYS?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "MY FELLOW AMERICANS",
            "graphicName":
            "myfellowamericans",
            "xPostURL":
            "https://x.com/Areveur51/status/1855709176825082226?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GcDNqRrXYAArzTB?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "SNOWDEN",
            "graphicName":
            "snowdenvspotus",
            "xPostURL":
            "https://x.com/Areveur51/status/1836047751366246582?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GXrzsisW4AA1Vsy?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "FIGHT, FIGHT, FIGHT!",
            "graphicName":
            "fightfightfight",
            "xPostURL":
            "https://x.com/Areveur51/status/1812344076844278016?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GcJo0teW4AElxzb?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "NOT POTUS",
            "graphicName":
            "notpotus",
            "xPostURL":
            "https://x.com/Areveur51/status/1800569940719866106?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GPzo0TlXMAAx9bc?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "THE MORE YOU INDICT THE MORE WE UNITE",
            "graphicName":
            "themoreyouindict",
            "xPostURL":
            "https://x.com/Areveur51/status/1797000416082714624?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GcJ2gzKXIAAxZ56?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "MARKER: RED WAVE MISSION ACCOMPLISHED",
            "graphicName":
            "markerredwave",
            "xPostURL":
            "https://x.com/Areveur51/status/1856179218939330757?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GcJ5GOSXgAAda01?format=png&name=large",
        },
        {
            "graphicLabel":
            "THANK YOU VETERANS",
            "graphicName":
            "thankyouveterans",
            "xPostURL":
            "https://x.com/Areveur51/status/1857509045579731215?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GccyoZwXoAAu0-w?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "TRAP CARD PLAYED",
            "graphicName":
            "trapcardplayed",
            "xPostURL":
            "https://x.com/areveur51/status/1858904537152586080?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/Gcwn0u1W0AAzrl9?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "MORE CONFUSING?",
            "graphicName":
            "moreconfusing",
            "xPostURL":
            "https://x.com/Areveur51/status/1861851773507444902?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GdagPtcWIAAeVVy?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "HAPPY HOLIDAYS CA.JPG",
            "graphicName":
            "happyholidays",
            "xPostURL":
            "https://x.com/Areveur51/status/1861889579688812821?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GdbCoAkWoAAtRjD?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "IT WAS OVER BEFORE IT BEGAN",
            "graphicName":
            "itwasoverbeforeitbegan",
            "xPostURL":
            "https://x.com/Areveur51/status/1868141678911230462?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/Gez49GBWMAAj3Qa?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "THE GREAT AWAKENING",
            "graphicName":
            "thegreatawakening",
            "xPostURL":
            "https://x.com/areveur51/status/1874006579080815069?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GgHPDNhX0AAm0RX?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "UNFOOKWITABLE AMERICANS",
            "graphicName":
            "unfookwitableamericans",
            "xPostURL":
            "https://x.com/Areveur51/status/1874677430524211452?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GgQyXwcWIAEPWSz?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "HUMANITY IS GOOD",
            "graphicName":
            "humanityisgood",
            "xPostURL":
            "https://x.com/areveur51/status/1878154669937119527?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GhCLt5yXoAAxl7h?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "OBAMAGATE",
            "graphicName":
            "obamagate",
            "xPostURL":
            "https://x.com/Areveur51/status/1879560774282039604?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GhWKj1tXEAAT8bG?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "THE SHOT HEARD AROUND THE WORLD",
            "graphicName":
            "theshot",
            "xPostURL":
            "https://x.com/Areveur51/status/1883702964021301450?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GiRB3EcXEAAfR4i?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "NOW PLAYING",
            "graphicName":
            "nowplaying",
            "xPostURL":
            "https://x.com/Areveur51/status/1885866158538056133?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GivxRmPWUAAEzcX?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "HELLO GEORGE",
            "graphicName":
            "hellogeorge",
            "xPostURL":
            "https://x.com/Areveur51/status/1887441499626811762?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GjGKChcWUAAdSd6?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "HELLO GEORGE",
            "graphicName":
            "hellogeorge2",
            "xPostURL":
            "https://x.com/Areveur51/status/1907835843114389506?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/Gnn-lgXXwAAeuMc?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "THE FIRST WILL SEND A SHOCK WAVE",
            "graphicName":
            "thefirstwillsendashockwave",
            "xPostURL":
            "https://x.com/areveur51/status/1891714252324348394?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GkC4Fg0WwAAASJx?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "THANK YOU USSS",
            "graphicName":
            "thankyouusss",
            "xPostURL":
            "https://x.com/Areveur51/status/1893854421894754426?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GkhSjyaXgAEQ-cR?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "ALL FOR A LARP",
            "graphicName":
            "allforalarp",
            "xPostURL":
            "https://x.com/Areveur51/status/1897363401413685584?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GlTJ9OGX0AAft0v?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "MATCHING USA PIN",
            "graphicName":
            "matchingusapin",
            "xPostURL":
            "https://x.com/Areveur51/status/1897416520017629283?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GlT6RI-XwAAkzWO?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "MARCH MADNESS",
            "graphicName":
            "marchmadness",
            "xPostURL":
            "https://x.com/Areveur51/status/1899107004200669228?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/Glr7wH-XUAEi_m5?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "GOOGLE",
            "graphicName":
            "google",
            "xPostURL":
            "https://x.com/Areveur51/status/1899147411018154475?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GlsgV4mXQAAD0vw?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "CHAIN OF COMMAND",
            "graphicName":
            "chainofcommand",
            "xPostURL":
            "https://x.com/Areveur51/status/1901688461997801929?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GmQnkl7WcAADvPo?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "RUSSIA PROBE & FISA ABUSE",
            "graphicName":
            "russiaprobeandfisaabuse",
            "xPostURL":
            "https://x.com/Areveur51/status/1902121464356061524?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GmWxY1iXYAAk_-z?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "NEW DISCOVERY UNDERNEATH THE PYRAMIDS",
            "graphicName":
            "newdiscoveryunderneaththepyramids",
            "xPostURL":
            "https://x.com/Areveur51/status/1903868260681965729?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GmvmF4TbgAA3H9s?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "MARATHON END",
            "graphicName":
            "marathonend",
            "xPostURL":
            "https://x.com/Areveur51/status/1932461849473069435?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GtF7z1_WYAADl6u?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "PATRIOTS MAKE SACRIFICES",
            "graphicName":
            "patriotsmakesacrifices",
            "xPostURL":
            "https://x.com/Areveur51/status/1932845632655405320?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GtLY24WXcAAy0fe?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "WELCOME TO YOUR NEW REALITY",
            "graphicName":
            "welcometoyournewreality",
            "xPostURL":
            "https://x.com/Areveur51/status/1933183743306416389?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GtQMXc1XYAE58TQ?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "DEPT OF DEFENSE TEST",
            "graphicName":
            "deptofdefensetest",
            "xPostURL":
            "https://x.com/Areveur51/status/1933441068101509279?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GtT2Z3tXwAAdlXz?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "WE MUST FIGHT",
            "graphicName":
            "wemustfight",
            "xPostURL":
            "https://x.com/Areveur51/status/1934413058467848668?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GthqyB8XkAABO-b?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "AS THE WORLD TURNS",
            "graphicName":
            "astheworldturns",
            "xPostURL":
            "https://x.com/Areveur51/status/1934424087616442571?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/Gth0dJEXkAEVqtL?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "WAS BLIND, BUT NOW... [YOU SEE]",
            "graphicName":
            "wasblindbutnowyousee",
            "xPostURL":
            "https://x.com/Areveur51/status/1934436587799974206?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/Gth_0pLWEAA0wPp?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "IRAN IS NEXT",
            "graphicName":
            "iranisnext",
            "xPostURL":
            "https://x.com/Areveur51/status/1935082720016621986?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GtrLedDXUAEw8gu?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "WHY IS POTUS FOCUSED ON SA/CHINA/RUSSIA?",
            "graphicName":
            "whyispotusfocusedonsachinarussia",
            "xPostURL":
            "https://x.com/Areveur51/status/1937225148672717167?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GuJoAVrXcAE1XZf?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "TRUST THE PLAN",
            "graphicName":
            "trusttheplan",
            "xPostURL":
            "https://x.com/Areveur51/status/1937270612462043202?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GuKRWrfWMAAWjD7?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "BADGE OF HONOR",
            "graphicName":
            "badgeofhonor",
            "xPostURL":
            "https://x.com/Areveur51/status/1938001777565306972?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GuUqV_TWUAAyZj0?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "WATCH THE NEWS",
            "graphicName":
            "watchthenews",
            "xPostURL":
            "https://x.com/Areveur51/status/1939724202279383422?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GutI4TwXYAAYkwc?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "RUNWAY IS CLEAR FOR TAKEOFF",
            "graphicName":
            "runwayisclearfortakeoff",
            "xPostURL":
            "https://x.com/Areveur51/status/1939765797829640594?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/Gututm1WkAA2YTN?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "A WORLD UNITED IS A BEAUTIFUL THING",
            "graphicName":
            "aworldunitedisabeautifulthing",
            "xPostURL":
            "https://x.com/Areveur51/status/1940471093145317765?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/Gu3wJuZX0AE3zrS?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "WE THE PEPE",
            "graphicName":
            "wethepepe",
            "xPostURL":
            "https://x.com/Areveur51/status/1940980161001759228?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/Gu-_KIgXUAAB4y9?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "SHEEP NO MORE",
            "graphicName":
            "sheepnomore",
            "xPostURL":
            "https://x.com/Areveur51/status/1944882867508490732?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/Gv2cpZsWUAA4KSK?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "FIREWALL : MAURENE COMEY",
            "graphicName":
            "firewall",
            "xPostURL":
            "https://x.com/Areveur51/status/1945697061652832632?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GwCBKUUXEAAzbVb?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "OUT OF SHADOWS",
            "graphicName":
            "outofshadows",
            "xPostURL":
            "https://x.com/Areveur51/status/1946996467174154748?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GwUe96oWoAE5U6l?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "DON'T BELIEVE EVERYTHING YOU READ",
            "graphicName":
            "dontbelieveeverythingyouread",
            "xPostURL":
            "https://x.com/Areveur51/status/1947019966730981720?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GwU0VQhWgAANw7x?format=jpg&name=large",
        },
        {
            "graphicLabel":
            "WE ARE TALKING TO YOU",
            "graphicName":
            "wearetalkingtoyou",
            "xPostURL":
            "https://x.com/Areveur51/status/1947038344245846169?s=61&t=ZoFVBiZqOoyaYVvUb8ZMcw",
            "xGraphicURL":
            "https://pbs.twimg.com/media/GwVFC8vXwAAR4UF?format=jpg&name=large",
        },
        # keywords
        {
            "graphicLabel": "NCSWIC",
            "graphicName": "kw-NCSWIC",
            "xPostURL": "",
            "xGraphicURL": "",
        },
        {
            "graphicLabel": "COVID",
            "graphicName": "kw-COVID",
            "xPostURL": "",
            "xGraphicURL": "",
        },
        {
            "graphicLabel": "DECLAS",
            "graphicName": "kw-DECLAS",
            "xPostURL": "",
            "xGraphicURL": "",
        },
        {
            "graphicLabel": "NewsUnlocksMap",
            "graphicName": "kw-NewsUnlocksMap",
            "xPostURL": "",
            "xGraphicURL": "",
        },
        {
            "graphicLabel": "NOSUCHAGENCY",
            "graphicName": "kw-NOSUCHAGENCY",
            "xPostURL": "",
            "xGraphicURL": "",
        },
        {
            "graphicLabel": "PanicInDC",
            "graphicName": "kw-PanicInDC",
            "xPostURL": "",
            "xGraphicURL": "",
        },
        {
            "graphicLabel": "LogicalThinking",
            "graphicName": "kw-LogicalThinking",
            "xPostURL": "",
            "xGraphicURL": "",
        },
        {
            "graphicLabel": "MathematicallyImpossible",
            "graphicName": "kw-MathematicallyImpossible",
            "xPostURL": "",
            "xGraphicURL": "",
        },
        {
            "graphicLabel": "PATRIOTS",
            "graphicName": "kw-PATRIOTS",
            "xPostURL": "",
            "xGraphicURL": "",
        },
        {
            "graphicLabel": "QANON",
            "graphicName": "kw-QANON",
            "xPostURL": "",
            "xGraphicURL": "",
        },
        {
            "graphicLabel": "FISA",
            "graphicName": "kw-FISA",
            "xPostURL": "",
            "xGraphicURL": "",
        },
        {
            "graphicLabel": "SESSIONS",
            "graphicName": "kw-SESSIONS",
            "xPostURL": "",
            "xGraphicURL": "",
        },
        {
            "graphicLabel": "SNOWDEN",
            "graphicName": "kw-SNOWDEN",
            "xPostURL": "",
            "xGraphicURL": "",
        },
        {
            "graphicLabel": "TheGreatAwakening",
            "graphicName": "kw-TheGreatAwakening",
            "xPostURL": "",
            "xGraphicURL": "",
        },
        {
            "graphicLabel": "USMIL",
            "graphicName": "kw-USMIL",
            "xPostURL": "",
            "xGraphicURL": "",
        },
        {
            "graphicLabel": "VirusOrElection",
            "graphicName": "kw-VirusOrElection",
            "xPostURL": "",
            "xGraphicURL": "",
        },
        {
            "graphicLabel": "WWG1WGA",
            "graphicName": "kw-WWG1WGA",
            "xPostURL": "",
            "xGraphicURL": "",
        },
        {
            "graphicLabel": "RussiaHoax",
            "graphicName": "kw-RussiaHoax",
            "xPostURL": "",
            "xGraphicURL": "",
        },
    ]

    default_color = 'black'
    highlight_color = 'green'
    highlight_size = 1.5
    background_color = '#000000'
    highlight2_color = 'green'

    default_edge_metadata = {
        'color': highlight_color,
        'opacity': 1.0,
        'size': highlight_size,
        'label_color': highlight2_color,
        'label_size': 5,
    }

    graph5 = {
        'graph': {
            'label':
            '40,000 FT. VIEW',
            'directed':
            True,
            'metadata': {
                'graph_height': 771,
                'arrow_color': highlight_color,
                'arrow_size': 11,
                'background_color': background_color,
                # nodes
                'show_node': True,
                'node_size_factor': 2,
                'node_color': background_color,
                'node_opacity': 0.8,
                'node_size': 117,
                # 'node_position': 'Release fixed nodes',
                'node_border_color': default_color,
                'node_border_size': 0.0,
                'node_label_color': default_color,
                'node_label_size': 1.77,
                'node_hover': 'Node: $label',
                'node_click': '$hover',
                'show_node_label': False,
                'show_edge': True,
                'edge_size_factor': 0.51,
                'edge_color': default_color,
                'edge_opacity': 0.1,
                'edge_size': 0.1,
                'edge_label_color': 'black',
                'edge_label_size': 1,
                'edge_hover': '$label',
                'edge_click': '$label',
            },
            'nodes': {},
            'edges': [
                {
                    'source': 'aworldunitedisabeautifulthing',
                    'target': 'fightfightfight',
                    'label': "Trump should be shot!",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'greatestfear',
                    'target': 'freethought',
                    'label': 'Great Awakening',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'greatestfear',
                    'target': 'enoughisenough',
                    'label': 'ENOUGH IS ENOUGH',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'greatestfear',
                    'target': 'qclearancepatriot',
                    'label': 'WE ARE HERE TO UNITE THE CORE. YOU.',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'greatestfear',
                    'target': 'noonepersonisaboveanother',
                    'label': 'No one person is abover another.',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'greatestfear',
                    'target': 'endofthedparty',
                    'label': 'SESSIONS APPOINTING UTAH FEDERAL PROSECUTOR',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'greatestfear',
                    'target': 'councilofforeignrelations',
                    'label':
                    'members hear and attend with senior American officials and world leaders',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'greatestfear',
                    'target': 'illegalsvoteblue',
                    'label':
                    'IN NOV TO DEFEND/IMPEACH/STOP INVESTIGATIONS. THEIR ONLY HOPE.',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'freethought',
                    'target': 'backchannels',
                    'label': 'backchannel to the public.',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'freethought',
                    'target': 'wasblindbutnowyousee',
                    'label': 'Free thought',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'cleanhouse',
                    'target': 'backchannels',
                    'label': 'How is information transmitted?',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'cleanhouse',
                    'target': 'freethought',
                    'label': '(NEW) Age of Enlightenment.',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'qclearancepatriot',
                    'target': 'protectmogul',
                    'label':
                    'Ability to decipher complex info-strings is a valued asset.',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'qclearancepatriot',
                    'target': 'renegade',
                    'label': 'CHANGE WE CAN BELIEVE IN [OBAMA-BIDEN]',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'qclearancepatriot',
                    'target': 'foranonspatriots',
                    'label': '11.3',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'qclearancepatriot',
                    'target': 'wearetalkingtoyou',
                    'label': 'Great job, Patriot',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'backchannels',
                    'target': 'vipanon',
                    'label': '#qproofs',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'keyhole',
                    'target': 'renegade',
                    'label':
                    '[R]enegade_(Borack Obama) + [4] OUTSIDE CONTRACTORS',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'keyhole',
                    'target': 'google',
                    'label': 'KEYHOLE INC',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'infowars',
                    'target': 'renegade',
                    'label': 'Alex Jones is a traitor to our country',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'ecw',
                    'target': 'endofthedparty',
                    'label': 'ECW will serve AG Jeff Sessions',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'councilofforeignrelations',
                    'target': 'shadowgovernment',
                    'label': 'Spy.png',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'subversion',
                    'target': 'endofthedparty',
                    'label': 'SESSIONS APPOINTING UTAH FEDERAL PROSECUTOR',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'subversion',
                    'target': 'renegade',
                    'label': 'missing [R] = Renegade',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'pdbpapertrail',
                    'target': 'endofthedparty',
                    'label': 'Clinton investigation',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'pdbpapertrail',
                    'target': 'wizardsandwarlocks',
                    'label': 'PDB via No Such Agency?',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'wizardsandwarlocks',
                    'target': 'westandattheready',
                    'label': "Our promise to 'counter'.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'wizardsandwarlocks',
                    'target': 'xkeyscore',
                    'label': "Snowden made public NSA CLAS tools",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'wizardsandwarlocks',
                    'target': 'marathonend',
                    'label': "We've got plenty of information on these crooks",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'milintel',
                    'target': 'westandattheready',
                    'label': "We are a threat to their livelihood [+CLAS].",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'crowdstrike',
                    'target': 'endofthedparty',
                    'label': "Hillary Clinton & Foundation",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'crowdstrike',
                    'target': 'commsgood',
                    'label':
                    "@Snowden. SecureDrop>Clowns In America. Nice try.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'crowdstrike',
                    'target': 'snowden',
                    'label': "Snowden. Traitor. Mission to harm NSA.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'snowden',
                    'target': 'renegade',
                    'label': "Snowden is a traitor to our country.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'snowden',
                    'target': 'obamagate',
                    'label': "BOOZ ALLEN SPY",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'snowden',
                    'target': 'enjoytheshow',
                    'label': "Snowden is a traitor to our country.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'husseiniran',
                    'target': 'renegade',
                    'label': "Hussein is a traitor to our country.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'husseiniran',
                    'target': 'iranisnext',
                    'label':
                    "Obama was able to send $1.7 Billion Dollars in CASH to Iran",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'xkeyscore',
                    'target': 'snowden',
                    'label': "Snowden open source Prism/Keyscore",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'xkeyscore',
                    'target': 'endofthedparty',
                    'label': "THEY NEVER THOUGHT SHE WOULD LOSE",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'dontbelieveeverythingyouread',
                    'target': 'endofthedparty',
                    'label': "Clinton emails",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'projectdeepdreamv2',
                    'target': 'snowden',
                    'label': "Clown_Comm_Narrative.png",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'vipanon',
                    'target': 'wearetalkingtoyou',
                    'label': 'Proofs',
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'westandattheready',
                    'target': 'aworldunitedisabeautifulthing',
                    'label': "Trump should be shot!",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'wethepepe',
                    'target': 'milintel',
                    'label':
                    "Autists should consider joining ABCs/Mil Intel programs",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'wizardsandwarlocks',
                    'target': 'disclosure',
                    'label': "No Such Agency",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'wizardsandwarlocks',
                    'target': 'youarebeingtracked',
                    'label': "Agencies attached.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'wizardsandwarlocks',
                    'target': 'classified',
                    'label': "SEC 702",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'wizardsandwarlocks',
                    'target': 'bringthethunder',
                    'label': "KILL_BOX",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'wizardsandwarlocks',
                    'target': 'keystonedni',
                    'label': "No Such Agency = key",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'wizardsandwarlocks',
                    'target': 'msmattack',
                    'label': "NSA INSCOM BRIDGE",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'billb2barr',
                    'target': 'disclosure',
                    'label': "Advice from insiders",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'donotbeafraid',
                    'target': 'disclosure',
                    'label': "Jurisdiction",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'rothsownedcontrolledbanks',
                    'target': 'shadowgovernment',
                    'label': "Endless wars",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'classified',
                    'target': 'snowden',
                    'label': "SEC 702",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'classified',
                    'target': 'enjoytheshow',
                    'label': "FISA - ILLEGALLY TARGETED",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'bringthethunder',
                    'target': 'snowden',
                    'label': "PAIN. PAIN. PAIN.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'readytoserve',
                    'target': 'enjoytheshow',
                    'label': "The People's General. Soon.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'enjoytheshow',
                    'target': 'goorders',
                    'label': "It flushed Borack Obama Out.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'enjoytheshow',
                    'target': 'genflynn',
                    'label': "WWG1WGA",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'enjoytheshow',
                    'target': 'nowplaying',
                    'label': "PANIC IN DC",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'goorders',
                    'target': 'manilaextraction',
                    'label':
                    "Phil(ippines)_B(arack)_O(bama)_Extract(ion)_Conf(irmed) 02:00 Zulu",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'nothingishappening',
                    'target': 'enjoytheshow',
                    'label': "FISA BRINGS DOWN THE HOUSE.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'nothingishappening',
                    'target': 'disclosure',
                    'label': "PUBLIC AWARENESS - FISA/SPYING.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'msmattack',
                    'target': 'nothingishappening',
                    'label': "HUSSEIN DIRECT ORDERS",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'msmattack',
                    'target': 'hellogeorge',
                    'label':
                    "MSM coming - BIG WAY. MSM LOST CONTROL. FAKE NEWS.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'classified',
                    'target': 'cat',
                    'label': "PSYOP to pump liquidity",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'crowdstrike',
                    'target': 'keystonedni',
                    'label': "DNI & NSA",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'keystonedni',
                    'target': 'westandattheready',
                    'label': "directly serves POTUS.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'sarscov2',
                    'target': 'keystonedni',
                    'label': "Release the transcripts from DNI office.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'sarscov2',
                    'target': 'infowars',
                    'label': "Adam Schiff is a traitor to our country.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'sarscov2',
                    'target': 'virusorelection',
                    'label': "reclassified as murder?",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'virusorelection',
                    'target': 'illegalsvoteblue',
                    'label': "why D's depends on illegal immigrants",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'herdthesheep',
                    'target': 'virusorelection',
                    'label': "Anons already knew D's playbook",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'herdthesheep',
                    'target': 'clintonobamaticket',
                    'label': "[s] D's playbook election",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'herdthesheep',
                    'target': 'sheepnomore',
                    'label': "The More You Know....",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'hellogeorge',
                    'target': 'hellogeorge2',
                    'label': "HELLO GEORGE",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'landsales',
                    'target': 'qclearancepatriot',
                    'label': "LAND OF THE FREE. HOME OF THE BRAVE",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'huntersbecomethehunted',
                    'target': 'nothingishappening',
                    'label': "public unaware",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'huntersbecomethehunted',
                    'target': 'cleanhouse',
                    'label': "The calm before the storm",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'liquidityevents',
                    'target': 'cat',
                    'label': "sell-off",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'mediabrainwashing',
                    'target': 'msmattack',
                    'label': "[FAKE NEWS MEDIA]",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'mediabrainwashing',
                    'target': 'outofshadows',
                    'label': "[MK_active]",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'watchthenews',
                    'target': 'mediabrainwashing',
                    'label': "These people are stupid.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'watchthenews',
                    'target': 'msmattack',
                    'label': "These people are stupid.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'trumpelonxspace',
                    'target': 'westandattheready',
                    'label': "we will be ready",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'censorship',
                    'target': 'readytoserve',
                    'label': "serve your country, Information Warfare",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'censorship',
                    'target': 'backchannels',
                    'label': "Information Warfare",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'unfookwitable',
                    'target': 'freethought',
                    'label': "A FREE-THINKING 'LOGICAL' PERSON",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'unfookwitable',
                    'target': 'badgeofhonor',
                    'label': "Unfookwitable",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'badgeofhonor',
                    'target': 'unfookwitableamericans',
                    'label': "Unfookwitable",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'badgeofhonor',
                    'target': 'number2qanon',
                    'label': "SOMETHING BIG IS ABOUT TO DROP.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'msmattack',
                    'target': 'number2qanon',
                    'label':
                    "COORDINATED BLITZ ATTACK. SOMETHING BIG IS ABOUT TO DROP.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'declassoffisa',
                    'target': 'nothingishappening',
                    'label': "NOTHING TO SEE HERE",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'unmasking',
                    'target': 'declassoffisa',
                    'label': "Gitmo_Fisa_Declas.jpg",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'genflynn',
                    'target': 'unmasking',
                    'label': "[SET UP _FBI entrap + FISA [late] justify]",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'genflynn',
                    'target': 'runwayisclearfortakeoff',
                    'label': "FIRE AT WILL, COMMANDER",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'shadowgovernment',
                    'target': 'unmasking',
                    'label':
                    "Obama Officials Involved in ‘Unmasking’ General Flynn ",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'thankyouusss',
                    'target': 'genflynn',
                    'label': "Flynn is a patriot",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'qknowledgeispower',
                    'target': 'nothingishappening',
                    'label': "something VERY BIG is about to drop",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'qknowledgeispower',
                    'target': 'number2qanon',
                    'label': "SOMETHING BIG IS ABOUT TO DROP",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'qknowledgeispower',
                    'target': 'declassoffisa',
                    'label': "[FISA CORRUPTION]",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'qknowledgeispower',
                    'target': 'qclearancepatriot',
                    'label': "WE STAND TOGETHER",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'qknowledgeispower',
                    'target': 'backchannels',
                    'label': "Knowledge is >power<",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'msmisover',
                    'target': 'mediabrainwashing',
                    'label': "Social media control is everything.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'historybooks',
                    'target': 'enjoytheshow',
                    'label': "Justice.jpg",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'historybooks',
                    'target': 'patriotsmakesacrifices',
                    'label': "The next phase will bring JUSTICE",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'historybooks',
                    'target': 'welcometoyournewreality',
                    'label': "HISTORY BOOKS",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'endofthedparty',
                    'target': 'historybooks',
                    'label': "ONE FOR THE HISTORY BOOKS? NOT LONG NOW.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'qanon',
                    'target': 'number2qanon',
                    'label': "[Past 7 Days]",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'number2qanon',
                    'target': 'allforalarp',
                    'label':
                    "targeted and attacked by the largest media co's in the world",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'destinationspace',
                    'target': 'unmasking',
                    'label': "for a [specific] reason",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'wrayisasleeper',
                    'target': 'donotbeafraid',
                    'label': "Timing is everything",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'wrayisasleeper',
                    'target': 'milintel',
                    'label': "MIL INTEL",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'wrayisasleeper',
                    'target': 'enjoytheshow',
                    'label': "JUSTICE",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'wrayisasleeper',
                    'target': 'endofthedparty',
                    'label': "SESSIONS",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'timetoshowtheworld',
                    'target': 'wizardsandwarlocks',
                    'label': "No rigging / blackmail this time.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'timetoshowtheworld',
                    'target': 'matchingusapin',
                    'label': "Patriots in trusted positions.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'timetoshowtheworld',
                    'target': 'astheworldturns',
                    'label': "Those [good] who cannot sleep.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'skyfortressengaged',
                    'target': 'enjoytheshow',
                    'label': "FOR GOD & COUNTRY",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'myfellowamericans',
                    'target': 'skyfortressengaged',
                    'label': "insulated/protected on AF1",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'myfellowamericans',
                    'target': 'qclearancepatriot',
                    'label': "My fellow Americans",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'snowdenvspotus',
                    'target': 'snowden',
                    'label': "Whistleblower(s) vs. POTUS | NSA v C_A",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'snowdenvspotus',
                    'target': 'obamagate',
                    'label': "IDEN another leaker",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'fightfightfight',
                    'target': 'enjoytheshow',
                    'label': "WWG1WGA",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'fightfightfight',
                    'target': 'wemustfight',
                    'label': "We Must Fight - President Reagan",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'notpotus',
                    'target': 'endofthedparty',
                    'label': "NOT LONG NOW",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'themoreyouindict',
                    'target': 'historybooks',
                    'label': "JUSTICE",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'markerredwave',
                    'target': 'themoreyouindict',
                    'label': "AMERICA WILL BE UNIFIED AGAIN 11.11.18",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'thankyouveterans',
                    'target': 'markerredwave',
                    'label': "11:11 on 11/11",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'trapcardplayed',
                    'target': 'enjoytheshow',
                    'label': "HOW DO YOU LURE A DANGEROUS ANIMAL",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'trapcardplayed',
                    'target': 'herdthesheep',
                    'label': "playbook",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'trapcardplayed',
                    'target': 'declassoffisa',
                    'label': "BAIT",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'moreconfusing',
                    'target': 'xkeyscore',
                    'label': "Sniffer progs",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'happyholidays',
                    'target': 'bringthethunder',
                    'label': "Thor's Hammer, Thunder",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'itwasoverbeforeitbegan',
                    'target': 'projectdeepdreamv2',
                    'label': "IRON EAGLE",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'itwasoverbeforeitbegan',
                    'target': 'youarebeingtracked',
                    'label': "Tracking",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'thefirstwillsendashockwave',
                    'target': 'matchingusapin',
                    'label':
                    "Half the people involved in the Russian investigation are going to jail.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'thegreatawakening',
                    'target': 'freethought',
                    'label': "THE GREAT AWAKENING",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'thegreatawakening',
                    'target': 'unfookwitable',
                    'label': "Prosecution and Transparency",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'thegreatawakening',
                    'target': 'wasblindbutnowyousee',
                    'label': "The Great Awakening",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'theshot',
                    'target': 'sarscov2',
                    'label':
                    "𝚆𝚞𝚑𝚊𝚗 𝙸𝚗𝚜𝚝𝚒𝚝𝚞𝚝𝚎 𝚘𝚏 𝚅𝚒𝚛𝚘𝚕𝚘𝚐𝚢 𝚘𝚏 𝚝𝚑𝚎 𝙲𝚑𝚒𝚗𝚎𝚜𝚎 𝙰𝚌𝚊𝚍𝚎𝚖𝚢 𝚘𝚏 𝚂𝚌𝚒𝚎𝚗𝚌𝚎𝚜",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'unfookwitableamericans',
                    'target': 'unfookwitable',
                    'label': "We are UNITED in these STATES OF AMERICA",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'matchingusapin',
                    'target': 'bringthethunder',
                    'label': "PAIN",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'matchingusapin',
                    'target': 'historybooks',
                    'label': "JUSTICE",
                    'metadata': default_edge_metadata
                },
                # keywords : graphics connections
                {
                    'source': 'kw-COVID',
                    'target': 'sarscov2',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-COVID',
                    'target': 'virusorelection',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-COVID',
                    'target': 'theshot',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-DECLAS',
                    'target': 'endofthedparty',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-DECLAS',
                    'target': 'subversion',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-DECLAS',
                    'target': 'censorship',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-DECLAS',
                    'target': 'marchmadness',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-DECLAS',
                    'target': 'newdiscoveryunderneaththepyramids',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-DECLAS',
                    'target': 'trusttheplan',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-FISA',
                    'target': 'enjoytheshow',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-FISA',
                    'target': 'qknowledgeispower',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-FISA',
                    'target': 'unmasking',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-FISA',
                    'target': 'classified',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-FISA',
                    'target': 'msmattack',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-FISA',
                    'target': 'disclosure',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-FISA',
                    'target': 'russiaprobeandfisaabuse',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-FISA',
                    'target': 'firewall',
                    'label':
                    "James Comey signed off on 3 of 4 illegal FISA warrants",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-LogicalThinking',
                    'target': 'enjoytheshow',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-LogicalThinking',
                    'target': 'whyispotusfocusedonsachinarussia',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-LogicalThinking',
                    'target': 'firewall',
                    'label': "Firewall : Maurene Comey Fired",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-PATRIOTS',
                    'target': 'qclearancepatriot',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-PATRIOTS',
                    'target': 'timetoshowtheworld',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-PATRIOTS',
                    'target': 'foranonspatriots',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-PATRIOTS',
                    'target': 'thankyouveterans',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-PATRIOTS',
                    'target': 'msmattack',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-PATRIOTS',
                    'target': 'moreconfusing',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-PATRIOTS',
                    'target': 'humanityisgood',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-PATRIOTS',
                    'target': 'patriotsmakesacrifices',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-PATRIOTS',
                    'target': 'wethepepe',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-PATRIOTS',
                    'target': 'wearetalkingtoyou',
                    'label': "Proofs only meant for you",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-MathematicallyImpossible',
                    'target': 'foranonspatriots',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-NCSWIC',
                    'target': 'unfookwitableamericans',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-NewsUnlocksMap',
                    'target': 'itwasoverbeforeitbegan',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-NewsUnlocksMap',
                    'target': 'watchthenews',
                    'label': "These people are stupid.",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-NOSUCHAGENCY',
                    'target': 'disclosure',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-NOSUCHAGENCY',
                    'target': 'wizardsandwarlocks',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-NOSUCHAGENCY',
                    'target': 'bringthethunder',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-NOSUCHAGENCY',
                    'target': 'classified',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-NOSUCHAGENCY',
                    'target': 'keystonedni',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-NOSUCHAGENCY',
                    'target': 'msmattack',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-NOSUCHAGENCY',
                    'target': 'snowden',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-NOSUCHAGENCY',
                    'target': 'cleanhouse',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-NOSUCHAGENCY',
                    'target': 'thankyouusss',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-NOSUCHAGENCY',
                    'target': 'deptofdefensetest',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-PanicInDC',
                    'target': 'enjoytheshow',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-PanicInDC',
                    'target': 'classified',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-PanicInDC',
                    'target': 'nowplaying',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-QANON',
                    'target': 'qanon',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-QANON',
                    'target': 'number2qanon',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-QANON',
                    'target': 'vipanon',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-QANON',
                    'target': 'sarscov2',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-QANON',
                    'target': 'allforalarp',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-QANON',
                    'target': 'qclearancepatriot',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-QANON',
                    'target': 'qknowledgeispower',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-QANON',
                    'target': 'chainofcommand',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-SESSIONS',
                    'target': 'ecw',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-SESSIONS',
                    'target': 'wrayisasleeper',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-SESSIONS',
                    'target': 'endofthedparty',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-SESSIONS',
                    'target': 'subversion',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-SNOWDEN',
                    'target': 'snowden',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-SNOWDEN',
                    'target': 'snowdenvspotus',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-SNOWDEN',
                    'target': 'commsgood',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-SNOWDEN',
                    'target': 'crowdstrike',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-SNOWDEN',
                    'target': 'projectdeepdreamv2',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-SNOWDEN',
                    'target': 'obamagate',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-TheGreatAwakening',
                    'target': 'thegreatawakening',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-TheGreatAwakening',
                    'target': 'freethought',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-USMIL',
                    'target': 'milintel',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-USMIL',
                    'target': 'subversion',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-USMIL',
                    'target': 'wrayisasleeper',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-USMIL',
                    'target': 'keystonedni',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-USMIL',
                    'target': 'foranonspatriots',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-USMIL',
                    'target': 'chainofcommand',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-USMIL',
                    'target': 'deptofdefensetest',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-VirusOrElection',
                    'target': 'herdthesheep',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-WWG1WGA',
                    'target': 'noonepersonisaboveanother',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-WWG1WGA',
                    'target': 'enjoytheshow',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-WWG1WGA',
                    'target': 'genflynn',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-WWG1WGA',
                    'target': 'readytoserve',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-WWG1WGA',
                    'target': 'bringthethunder',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-WWG1WGA',
                    'target': 'freethought',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-WWG1WGA',
                    'target': 'projectdeepdreamv2',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-WWG1WGA',
                    'target': 'foranonspatriots',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-DECLAS',
                    'target': 'unfookwitable',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-RussiaHoax',
                    'target': 'thefirstwillsendashockwave',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'kw-RussiaHoax',
                    'target': 'russiaprobeandfisaabuse',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'whyispotusfocusedonsachinarussia',
                    'target': 'kw-RussiaHoax',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'whyispotusfocusedonsachinarussia',
                    'target': 'husseiniran',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'whyispotusfocusedonsachinarussia',
                    'target': 'iranisnext',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                {
                    'source': 'whyispotusfocusedonsachinarussia',
                    'target': 'russiaprobeandfisaabuse',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                # keywords clockwise order
                {
                    'source': 'kw-COVID',
                    'target': 'kw-VirusOrElection',
                    'label': "",
                    'metadata': default_edge_metadata
                },
                """
                    {
                        'source': 'kw-NCSWIC',
                        'target': 'kw-COVID',
                        'label': "",
                        'metadata': default_edge_metadata
                    },
            
                    {
                        'source': 'kw-COVID',
                        'target': 'kw-NewsUnlocksMap',
                        'label': "",
                        'metadata': default_edge_metadata
                    },
                    {
                        'source': 'kw-NewsUnlocksMap',
                        'target': 'kw-NOSUCHAGENCY',
                        'label': "",
                        'metadata': default_edge_metadata
                    },
                    {
                        'source': 'kw-NOSUCHAGENCY',
                        'target': 'kw-PanicInDC',
                        'label': "",
                        'metadata': default_edge_metadata
                    },
                    {
                        'source': 'kw-PanicInDC',
                        'target': 'kw-MathematicallyImpossible',
                        'label': "",
                        'metadata': default_edge_metadata
                    },
                    {
                        'source': 'kw-MathematicallyImpossible',
                        'target': 'kw-PATRIOTS',
                        'label': "",
                        'metadata': default_edge_metadata
                    },
                    {
                        'source': 'kw-PATRIOTS',
                        'target': 'kw-QANON',
                        'label': "",
                        'metadata': default_edge_metadata
                    },
                    {
                        'source': 'kw-QANON',
                        'target': 'kw-FISA',
                        'label': "",
                        'metadata': default_edge_metadata
                    },
                    {
                        'source': 'kw-FISA',
                        'target': 'kw-SESSIONS',
                        'label': "",
                        'metadata': default_edge_metadata
                    },
                    {
                        'source': 'kw-SESSIONS',
                        'target': 'kw-SNOWDEN',
                        'label': "",
                        'metadata': default_edge_metadata
                    },
                    {
                        'source': 'kw-SNOWDEN',
                        'target': 'kw-TheGreatAwakening',
                        'label': "",
                        'metadata': default_edge_metadata
                    },
                    {
                        'source': 'kw-TheGreatAwakening',
                        'target': 'kw-USMIL',
                        'label': "",
                        'metadata': default_edge_metadata
                    },
                    {
                        'source': 'kw-USMIL',
                        'target': 'kw-VirusOrElection',
                        'label': "",
                        'metadata': default_edge_metadata
                    },
                    {
                        'source': 'kw-VirusOrElection',
                        'target': 'kw-WWG1WGA',
                        'label': "",
                        'metadata': default_edge_metadata
                    },
                    {
                        'source': 'kw-WWG1WGA',
                        'target': 'kw-RussiaHoax',
                        'label': "",
                        'metadata': default_edge_metadata
                    },
                """
            ],
        }
    }

    # Collect names of keyword nodes
    keyword_nodes = [
        item["graphicName"] for item in data
        if item["graphicName"].startswith("kw-")
    ]
    graphics_nodes = [
        item["graphicName"] for item in data
        if not item["graphicName"].startswith("kw-")
    ]

    # Calculate positions for keyword nodes
    outer_positions = calculate_positions(keyword_nodes, 1177.1)

    # Calculate positions for graphics nodes with an interval of 17
    graphics_positions = calculate_positions(graphics_nodes,
                                             radius=360.0,
                                             interval=5)

    # creating nodes
    for item in data:
        logger.info(item["graphicLabel"])
        node_label = item["graphicLabel"]
        node_name = item["graphicName"]
        x_post_url = item["xPostURL"]
        x_graphic_url = item["xGraphicURL"]
        # x_graphic_url_img = gv.convert.image_to_data_url(x_graphic_url)

        # keywords
        if node_name.startswith("kw-"):
            graph5['graph']['nodes'][node_name] = {
                'label': node_label,
                'metadata': {
                    'opacity': 1.0,
                    'label_color': 'purple',
                    'label_size': 26,
                    'color': 'purple',
                    'size': 36.0,
                    'x':
                    outer_positions[node_name]['x'],  # Use calculated position
                    'y': outer_positions[node_name]['y'],
                }
            }
        else:
            # Graphics nodes
            graph5['graph']['nodes'][node_name] = {
                'label': node_label,
                'metadata': {
                    'opacity':
                    1.0,
                    'label_color':
                    highlight_color,
                    'label_size':
                    7,
                    'hover':
                    '<b><span style="font-size: 17px;">{node_label}</span></b><br><a href="{x_link}" target="_blank" style="font-size: 17px;">View X post</a><br><a href="{node_img}" target="_blank" style="font-size: 17px;">View image</a>'
                    .format(node_label=node_label,
                            x_link=x_post_url,
                            node_img=x_graphic_url),
                    'click':
                    x_post_url,
                    'image':
                    x_graphic_url,
                    'x':
                    graphics_positions[node_name]['x'],
                    'y':
                    graphics_positions[node_name]['y']
                }
            }

    fig = gv.d3(
        graph5,
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

        # specific for D3
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
    # fig.display()  # opens the plot in a browser window, can be stored as SVG/JPG/PNG
    # fig.export_html(filepath='templates/index.html', overwrite=True)

    fig.export_html(filepath='index.html', overwrite=True)
    return fig.export_html(filepath='templates/index.html', overwrite=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

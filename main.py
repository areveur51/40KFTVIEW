## AREVEUR5117
import networkx as nx
import gravis as gv
from flask import Flask, send_from_directory
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a flask app
app = Flask(__name__)


# Index page
@app.route('/')
def index():
    logger.info('Index page is loaded')
    # generate in dev mode to create index file
    # then deploy with updated index file
    # generate_map()
    generate_map_v2()
    return send_from_directory('templates', 'index.html')


def generate_map_v2():
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
                'node_hover': 'Decode: $label',
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
                    'source': 'projectdeepdreamv2',
                    'target': 'snowden',
                    'label': "Clown_Comm_Narrative.png",
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
                    'source': 'herdthesheep',
                    'target': 'clintonobamaticket',
                    'label': "[s] D's playbook election",
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
                    'source': 'shadowgovernment',
                    'target': 'unmasking',
                    'label':
                    "Obama Officials Involved in ‘Unmasking’ General Flynn ",
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
                    'source': 'fightfightfight',
                    'target': 'enjoytheshow',
                    'label': "WWG1WGA",
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
                    'source': 'thegreatawakening',
                    'target': 'freethought',
                    'label': "THE GREAT AWAKENING",
                    'metadata': default_edge_metadata
                },
            ],
        }
    }

    # creating nodes
    for item in data:
        logger.info(item["graphicLabel"])
        node_label = item["graphicLabel"]
        node_name = item["graphicName"]
        x_post_url = item["xPostURL"]
        x_graphic_url = item["xGraphicURL"]
        # x_graphic_url_img = gv.convert.image_to_data_url(x_graphic_url)

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
                '<b>{node_label}</b><br><a href="{x_link}" target="_blank">View X post</a><br><a href="{node_img}" target="_blank">View image</a>'
                .format(node_label=node_label,
                        x_link=x_post_url,
                        node_img=x_graphic_url),
                'click':
                x_post_url,
                'image':
                x_graphic_url,
            }
        }

    fig = gv.d3(
        graph5,
        graph_height=1100,
        node_label_data_source='label',
        edge_label_data_source='label',
        show_edge_label=True,
        edge_curvature=0.3,
        zoom_factor=1,
        layout_algorithm_active=True,
        node_hover_neighborhood=True,

        # specific for D3
        use_many_body_force=True,
        many_body_force_strength=-1776.0,
        many_body_force_theta=1.17,
        use_many_body_force_min_distance=True,
        many_body_force_min_distance=0.01,
        use_many_body_force_max_distance=True,
        many_body_force_max_distance=2963.0,
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
        use_centering_force=True,
    )
    # fig.display()  # opens the plot in a browser window, can be stored as SVG/JPG/PNG
    # fig.export_html(filepath='templates/index.html', overwrite=True)

    fig.export_html(filepath='index.html', overwrite=True)
    return fig.export_html(filepath='templates/index.html', overwrite=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

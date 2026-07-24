#!/usr/bin/env python3
"""
Taranis Intelligence — Agrégateur news Afrique de l'Ouest + Est
================================================================
3 thèmes prioritaires : Macro · Énergies renouvelables · Financement Afrique
30 pays sub-sahariens (15 W + 15 E). Nord & Sud exclus.

Sortie : news.json
Aucune dépendance externe (stdlib uniquement).
"""

import json
import re
import sys
import time
import unicodedata
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from hashlib import md5

OUT_PATH = Path(__file__).parent / "news.json"
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36 "
              "Taranis-Intelligence-Aggregator/1.0")
TIMEOUT = 12
MAX_AGE_DAYS = 250

# =============================================================================
# SOURCES — tier 1 = wire / grands médias ; tier 2 = spécialisé Africa / énergie
# =============================================================================
SOURCES = [
    # ---- Wire services & grands médias internationaux (tier 1) ----
    {"id": "bbc-afr",    "name": "BBC Africa",          "tier": 1, "lang": "en",
     "url": "https://feeds.bbci.co.uk/news/world/africa/rss.xml"},
    {"id": "f24-afr",    "name": "France 24 Afrique",   "tier": 1, "lang": "fr",
     "url": "https://www.france24.com/fr/afrique/rss"},
    {"id": "rfi-afr",    "name": "RFI Afrique",         "tier": 1, "lang": "fr",
     "url": "https://www.rfi.fr/fr/afrique/rss"},
    {"id": "aljazeera",  "name": "Al Jazeera",          "tier": 1, "lang": "en",
     "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"id": "ft-africa",  "name": "Financial Times · Africa", "tier": 1, "lang": "en",
     "url": "https://www.ft.com/africa?format=rss"},
    {"id": "worldbank",  "name": "World Bank News",     "tier": 1, "lang": "en",
     "url": "https://www.worldbank.org/en/news/all?rss=1"},

    # ---- Médias dédiés Afrique (tier 2) ----
    {"id": "afnews-en",  "name": "Africanews",          "tier": 2, "lang": "en",
     "url": "https://www.africanews.com/feed/rss"},
    {"id": "afnews-fr",  "name": "Africanews FR",       "tier": 2, "lang": "fr",
     "url": "https://fr.africanews.com/feed/rss"},
    {"id": "ja",         "name": "Jeune Afrique",       "tier": 2, "lang": "fr",
     "url": "https://www.jeuneafrique.com/feed/"},
    {"id": "ecofin",     "name": "Agence Ecofin",       "tier": 2, "lang": "fr",
     "url": "https://www.agenceecofin.com/feed"},
    {"id": "financ-afr", "name": "Financial Afrik",     "tier": 2, "lang": "fr",
     "url": "https://www.financialafrik.com/feed/"},
    {"id": "africa-rep", "name": "The Africa Report",   "tier": 2, "lang": "en",
     "url": "https://www.theafricareport.com/feed/"},
    {"id": "african-biz","name": "African Business",    "tier": 2, "lang": "en",
     "url": "https://african.business/feed"},

    # ---- Énergie / renouvelables (tier 2) ----
    {"id": "energy-na",  "name": "Energy News Africa",  "tier": 2, "lang": "en",
     "url": "https://www.energynewsafrica.com/feed/"},
    {"id": "energy-voice","name":"Energy Voice · Africa","tier": 2, "lang": "en",
     "url": "https://www.energyvoice.com/category/africa/feed/"},
    {"id": "mining-tech","name": "Mining Technology",   "tier": 2, "lang": "en",
     "url": "https://www.mining-technology.com/rss/"},

    # ---- Tech / VC / startups Africa (financement, tier 2) ----
    {"id": "techcabal",  "name": "TechCabal",           "tier": 2, "lang": "en",
     "url": "https://techcabal.com/feed/"},
    {"id": "ventureburn","name": "Ventureburn",         "tier": 2, "lang": "en",
     "url": "https://ventureburn.com/feed/"},
    {"id": "weetracker", "name": "WeeTracker",          "tier": 2, "lang": "en",
     "url": "https://weetracker.com/feed/"},
    {"id": "thecable",   "name": "TheCable Nigeria",    "tier": 2, "lang": "en",
     "url": "https://www.thecable.ng/feed/"},

    # ---- Est-Afrique en anglais (tier 2) ----
    {"id": "east-afr",   "name": "The East African",    "tier": 2, "lang": "en",
     "url": "https://www.theeastafrican.co.ke/rss.xml"},
    {"id": "addis-fort", "name": "Addis Fortune",       "tier": 2, "lang": "en",
     "url": "https://addisfortune.news/feed/"},
    {"id": "ethio-rep",  "name": "Ethiopian Reporter",  "tier": 2, "lang": "en",
     "url": "https://www.ethiopianreporter.com/feed"},
    {"id": "cio-afr",    "name": "CIO Africa",          "tier": 2, "lang": "en",
     "url": "https://cioafrica.co/feed/"},
    {"id": "further-af", "name": "Further Africa",      "tier": 2, "lang": "en",
     "url": "https://furtherafrica.com/feed/"},

    # ---- Afrique lusophone (tier 2) ----
    {"id": "rfi-pt",     "name": "RFI Português",       "tier": 1, "lang": "pt",
     "url": "https://www.rfi.fr/pt/rss"},
    {"id": "lusa",       "name": "Lusa (Agência)",      "tier": 1, "lang": "pt",
     "url": "https://www.lusa.pt/rss"},
    {"id": "jorn-ang",   "name": "Jornal de Angola",    "tier": 2, "lang": "pt",
     "url": "https://www.jornaldeangola.ao/rss"},
    {"id": "club-moz",   "name": "Club of Mozambique",  "tier": 2, "lang": "en", "force_country": "MOZ",
     "url": "https://clubofmozambique.com/feed/"},
    {"id": "observador", "name": "Observador",          "tier": 2, "lang": "pt",
     "url": "https://observador.pt/seccao/mundo/feed/"},

    # ---- AllAfrica per-country — équilibré W + E ----
    # West Africa
    {"id": "aa-nga", "name": "AllAfrica · Nigeria",     "tier": 2, "lang": "en", "force_country": "NGA",
     "url": "https://allafrica.com/tools/headlines/rdf/nigeria/headlines.rdf"},
    {"id": "aa-gha", "name": "AllAfrica · Ghana",       "tier": 2, "lang": "en", "force_country": "GHA",
     "url": "https://allafrica.com/tools/headlines/rdf/ghana/headlines.rdf"},
    {"id": "aa-civ", "name": "AllAfrica · Côte d'Ivoire","tier": 2,"lang": "fr", "force_country": "CIV",
     "url": "https://allafrica.com/tools/headlines/rdf/cotedivoire/headlines.rdf"},
    {"id": "aa-sen", "name": "AllAfrica · Sénégal",     "tier": 2, "lang": "fr", "force_country": "SEN",
     "url": "https://allafrica.com/tools/headlines/rdf/senegal/headlines.rdf"},
    {"id": "aa-mli", "name": "AllAfrica · Mali",        "tier": 2, "lang": "fr", "force_country": "MLI",
     "url": "https://allafrica.com/tools/headlines/rdf/mali/headlines.rdf"},
    # East Africa
    {"id": "aa-ken", "name": "AllAfrica · Kenya",       "tier": 2, "lang": "en", "force_country": "KEN",
     "url": "https://allafrica.com/tools/headlines/rdf/kenya/headlines.rdf"},
    {"id": "aa-eth", "name": "AllAfrica · Éthiopie",    "tier": 2, "lang": "en", "force_country": "ETH",
     "url": "https://allafrica.com/tools/headlines/rdf/ethiopia/headlines.rdf"},
    {"id": "aa-tza", "name": "AllAfrica · Tanzanie",    "tier": 2, "lang": "en", "force_country": "TZA",
     "url": "https://allafrica.com/tools/headlines/rdf/tanzania/headlines.rdf"},
    {"id": "aa-uga", "name": "AllAfrica · Ouganda",     "tier": 2, "lang": "en", "force_country": "UGA",
     "url": "https://allafrica.com/tools/headlines/rdf/uganda/headlines.rdf"},
    {"id": "aa-moz", "name": "AllAfrica · Mozambique",  "tier": 2, "lang": "en", "force_country": "MOZ",
     "url": "https://allafrica.com/tools/headlines/rdf/mozambique/headlines.rdf"},
]

# =============================================================================
# PAYS TARANIS — 30 pays (15 W + 15 E), détection multilingue
# =============================================================================
COUNTRIES = [
    # ==== Afrique de l'Ouest ====
    {"code": "NGA", "name": "Nigeria",       "kw": ["nigeria", "nigerian", "nigérian", "lagos", "abuja", "kano", "ibadan", "port harcourt"]},
    {"code": "GHA", "name": "Ghana",         "kw": ["ghana", "ghanaian", "ghanéen", "accra", "kumasi", "tema"]},
    {"code": "CIV", "name": "Côte d'Ivoire", "kw": ["côte d'ivoire", "cote d'ivoire", "ivory coast", "ivorian", "ivoirien", "ivoirienne", "abidjan", "yamoussoukro", "bouaké"]},
    {"code": "SEN", "name": "Sénégal",       "kw": ["sénégal", "senegal", "senegalese", "sénégalais", "dakar", "saint-louis", "thiès"]},
    {"code": "MLI", "name": "Mali",          "kw": ["mali ", "malian", "malien", "bamako", "tombouctou", "timbuktu", "gao", "kidal"]},
    {"code": "BFA", "name": "Burkina Faso",  "kw": ["burkina", "burkinabè", "burkinabe", "burkinabé", "ouagadougou", "bobo-dioulasso"]},
    {"code": "NER", "name": "Niger",         "kw": ["niger ", "nigerien", "nigérien", "niamey", "agadez", "zinder"]},
    {"code": "GIN", "name": "Guinée",        "kw": ["guinée", "guinea ", "guinean", "guinéen", "conakry", "kankan", "nzérékoré"]},
    {"code": "SLE", "name": "Sierra Leone",  "kw": ["sierra leone", "sierra-leone", "sierra leonean", "sierra-léonais", "sierra léonais", "freetown"]},
    {"code": "LBR", "name": "Libéria",       "kw": ["liberia", "libéria", "liberian", "libérien", "monrovia"]},
    {"code": "TGO", "name": "Togo",          "kw": ["togo ", "togolese", "togolais", "lomé", "lome", "sokodé"]},
    {"code": "BEN", "name": "Bénin",         "kw": ["bénin", "benin ", "beninese", "béninois", "cotonou", "porto-novo"]},
    {"code": "CPV", "name": "Cap-Vert",      "kw": ["cap-vert", "cape verde", "cabo verde", "cape verdean", "praia"]},
    {"code": "GMB", "name": "Gambie",        "kw": ["gambia", "gambie", "gambian", "gambien", "banjul"]},
    {"code": "GNB", "name": "Guinée-Bissau", "kw": ["guinea-bissau", "guiné-bissau", "guinée-bissau", "bissau"]},

    # ==== Afrique de l'Est ====
    {"code": "KEN", "name": "Kenya",         "kw": ["kenya", "kenyan", "nairobi", "mombasa", "kisumu"]},
    {"code": "ETH", "name": "Éthiopie",      "kw": ["ethiopia", "éthiopie", "ethiopian", "éthiopien", "addis-abeba", "addis ababa", "amhara", "tigray"]},
    {"code": "TZA", "name": "Tanzanie",      "kw": ["tanzania", "tanzanie", "tanzanian", "tanzanien", "dar es salaam", "dodoma", "zanzibar"]},
    {"code": "UGA", "name": "Ouganda",       "kw": ["uganda", "ouganda", "ugandan", "ougandais", "kampala", "entebbe"]},
    {"code": "RWA", "name": "Rwanda",        "kw": ["rwanda", "rwandan", "rwandais", "kigali"]},
    {"code": "BDI", "name": "Burundi",       "kw": ["burundi", "burundian", "burundais", "bujumbura", "gitega"]},
    {"code": "DJI", "name": "Djibouti",      "kw": ["djibouti", "djiboutian", "djiboutien"]},
    {"code": "SOM", "name": "Somalie",       "kw": ["somalia", "somalie", "somali", "somalien", "mogadishu", "mogadiscio"]},
    {"code": "MOZ", "name": "Mozambique",    "kw": ["mozambique", "mozambican", "mozambicain", "maputo", "beira", "pemba", "cabo delgado"]},
    {"code": "MDG", "name": "Madagascar",    "kw": ["madagascar", "malagasy", "malgache", "antananarivo", "tananarive"]},
    {"code": "MUS", "name": "Maurice",       "kw": ["mauritius", "île maurice", "maurice ", "mauritian", "port-louis", "port louis"]},
    {"code": "MWI", "name": "Malawi",        "kw": ["malawi", "malawian", "malawien", "lilongwe", "blantyre"]},
    {"code": "SSD", "name": "Soudan du Sud", "kw": ["south sudan", "soudan du sud", "sud-soudanais", "juba"]},
    {"code": "ERI", "name": "Érythrée",      "kw": ["eritrea", "érythrée", "eritrean", "érythréen", "asmara"]},
    {"code": "COM", "name": "Comores",       "kw": ["comoros", "comores", "comoran", "comorien", "moroni"]},
]

# =============================================================================
# 3 CATÉGORIES TARANIS
# =============================================================================
CATEGORIES = {
    "MACRO": [
        "pib", "gdp", "inflation", "croissance", "growth",
        "banque centrale", "central bank", "bceao", "beac", "cbn ",
        "fmi", "imf", "world bank", "banque mondiale",
        "dette", "debt", "eurobond", "obligation souveraine", "sovereign bond",
        "monnaie", "currency", "devaluation", "dévaluation",
        "budget", "loi de finances", "finance bill",
        "récession", "recession", "économie", "economy",
        "trade balance", "balance commerciale", "exportations", "exports",
        "reserves", "réserves", "moody", "fitch", "s&p ",
        "rate cut", "rate hike", "taux directeur", "policy rate",
        "reform", "réforme", "subsidy", "subvention",
    ],
    "RENEWABLE": [
        "solar", "solaire", "photovoltaic", "photovoltaïque", "pv ",
        "wind farm", "wind power", "wind ", "éolien", "eolien", "éolienne",
        "hydro", "hydroelectric", "hydropower", "hydroélectrique", "barrage",
        "geothermal", "géothermie", "géothermique",
        "biomass", "biomasse", "biogas",
        "renewable", "renouvelable", "clean energy", "énergie propre",
        "energy transition", "transition énergétique",
        "off-grid", "mini-grid", "mini grid", "hors-réseau", "microgrid",
        "energy access", "accès à l'énergie", "électrification",
        "irena", "iea africa",
        "power purchase agreement", "ppa ",
        "battery storage", "energy storage",
        "power plant", "centrale électrique", "power project",
        "megawatt", "gigawatt", " mw ", " gw ",
        "electricity", "électricité",
        "green hydrogen", "hydrogène vert",
    ],
    "FINANCING": [
        "ifc ", "afdb", "bad ", "world bank", "banque mondiale",
        "proparco", "fmo ", "norfund", "cdc group", "bii ", "kfw", "aiib",
        "africa50", "boad ", "adb ", "afd ", "ebrd", "gates foundation",
        "private equity", "venture capital", "capital-risque", "capital-investissement",
        "levée de fonds", "raises", "raised", "funding round", "funding",
        "series a", "series b", "series c", "seed round",
        "tour de table",
        "eurobond", "green bond", "obligation verte", "sovereign bond",
        "debt facility", "credit facility", "loan agreement", "prêt",
        "blended finance", "guarantee facility", "mixed finance", "guarantee",
        "grant", "subvention",
        "syndicated loan", "prêt syndiqué",
        "financial closure", "financial close", "bouclage financier",
        "acquisition", "acquière", "acquiert", "buyout", "acquires",
        "invests", "invest ", "investit", "investment",
        "stake in", "prend une part", "acquire",
        "close deal", "closes deal", "million ", "billion",
    ],
}

# Mots qui boostent la sévérité (1..4)
SEVERITY_HIGH = ["mort", "morts", "killed", "dead", "deaths", "tué",
                 "catastrophe", "catastrophic",
                 "urgence", "emergency", "état d'urgence",
                 "massacre", "victims", "victimes",
                 "disaster", "désastre",
                 "financial close", "financial closure", "bouclage financier",
                 "billion", "milliards", "milliard"]
SEVERITY_MEDIUM = ["explosion", "incendie", "fire", "attaque", "attack",
                   "crash", "effondrement", "collapse",
                   "coup d'état", "coup", "putsch",
                   "épidémie", "outbreak",
                   "fuite", "leak", "cyberattaque",
                   "blessé", "wounded", "injured",
                   "invest", "invests", "investit",
                   "raises", "raised", "levée de fonds",
                   "million", "millions",
                   "launch", "lance"]
SEVERITY_LOW = ["réforme", "reform", "signe", "signs",
                "annonce", "announce", "lance", "launch",
                "hausse", "baisse", "growth", "increase"]

# =============================================================================
# TECHNOLOGIES RENOUVELABLES (page "Renewables" — alias "themes")
# =============================================================================
THEMES = {
    "HYDRO":      ["hydroelectric", "hydro-electric", "hydropower", "hydroélectrique",
                   "barrage hydro", "dam ", "grand inga", "renaissance dam", "gerd",
                   "hydro plant", "hydro project"],
    "SOLAR":      ["solar", "solaire", "pv ", "photovoltaic", "photovoltaïque",
                   "solar plant", "solar park", "centrale solaire",
                   "concentrated solar", "csp ", "solar auction"],
    "WIND":       ["wind farm", "wind power", "wind park", "eolien", "éolien",
                   "éolienne", "wind turbine", "wind project", "lake turkana"],
    "GEOTHERMAL": ["geothermal", "géothermie", "géothermique", "olkaria", "menengai"],
    "BIOMASS":    ["biomass", "biomasse", "biogas", "biogaz", "waste-to-energy",
                   "sugarcane bagasse"],
    "GRID":       ["mini-grid", "mini grid", "off-grid", "hors-réseau", "microgrid",
                   "smart grid", "réseau intelligent", "grid extension",
                   "battery storage", "stockage énergie", "energy storage"],
}

# =============================================================================
# STATUTS PROJET (alias "legal_statuses")
# =============================================================================
LEGAL_STATUSES = {
    "OPERATIONAL":  ["operational", "commissioned", "mis en service", "opérationnel",
                     "commercial operation", "cod ", "power generation started"],
    "CONSTRUCTION": ["under construction", "construction begins", "groundbreaking",
                     "en construction", "en chantier", "construction lancée",
                     "topping out"],
    "FINANCING":    ["financial close", "financial closure", "bouclage financier",
                     "loan signed", "raises", "raised", "levée de fonds"],
    "ANNOUNCED":    ["announced", "annoncé", "unveiled", "reveals plan",
                     "plans to build", "envisage", "prévoit de", "will invest",
                     "à venir"],
}

# =============================================================================
# TYPES DE FINANCEMENT (alias "sectors")
# =============================================================================
SECTORS = {
    "DFI":     ["ifc ", "afdb", "world bank", "banque mondiale", "proparco",
                "fmo ", "norfund", "cdc group", "bii ", "kfw", "aiib",
                "africa50", "boad ", "adb ", "afd ", "ebrd"],
    "PE_VC":   ["private equity", "venture capital", "capital-risque",
                "capital-investissement", "seed round", "series a", "series b",
                "series c", "pre-seed", "growth equity", "tour de table"],
    "DEBT":    ["eurobond", "green bond", "obligation verte", "sovereign bond",
                "debt facility", "credit facility", "loan ", "prêt",
                "obligation souveraine", "syndicated loan"],
    "BLENDED": ["blended finance", "guarantee facility", "guarantee scheme",
                "concessional loan", "mixed finance"],
    "GRANT":   ["grant", "subvention", "aid ", "aide publique", "oda ",
                "gates foundation", "usaid"],
}

# Trigger booléen "is renewable" (nom REGULATORY_TRIGGER conservé pour compat OLEA)
REGULATORY_TRIGGER = [
    "solar", "solaire", "wind", "éolien", "hydro", "hydropower", "hydroélectrique",
    "geothermal", "géothermie", "biomass", "biomasse",
    "renewable", "renouvelable", "clean energy",
    "energy transition", "transition énergétique",
    "mini-grid", "off-grid", "energy access",
    "power plant", "centrale électrique", "power project",
    "megawatt", "gigawatt", "mw ", "gw ",
    "ppa ", "power purchase agreement",
    "battery storage", "energy storage",
]

# Trigger booléen "is financing" (nom FDI_KEYWORDS conservé pour compat OLEA)
FDI_KEYWORDS = [
    "invests in", "investit dans", "prend une part", "stake in",
    "acquires", "acquière", "acquiert", "acquisition of",
    "buyout", "raises fund", "raised $", "raises $",
    "series a", "series b", "series c", "seed round",
    "financial close", "financial closure", "bouclage financier",
    "eurobond", "green bond", "loan agreement", "prêt signé",
    "ifc ", "afdb", "proparco", "fmo ", "africa50",
    "syndicated loan", "prêt syndiqué",
    "blended finance", "guarantee facility",
    "grant ", "subvention",
    "capital injection", "levée de fonds",
]

# =============================================================================
# HELPERS
# =============================================================================
class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
    def handle_data(self, d): self.text.append(d)
    def get(self): return "".join(self.text)

def strip_html(s):
    if not s: return ""
    p = _HTMLStripper()
    try: p.feed(s)
    except Exception: return re.sub(r"<[^>]+>", "", s)
    return p.get()

def norm(s):
    if not s: return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"\s+", " ", s)
    return s

def fetch_url(url, retries=2):
    last_err = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            })
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return resp.read()
        except Exception as e:
            last_err = e
            time.sleep(1.2 * (attempt + 1))
    raise last_err

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rss10": "http://purl.org/rss/1.0/",
}

def _text(el):
    if el is None: return ""
    if el.text: return el.text.strip()
    return ""

def parse_date(s):
    if not s: return None
    s = s.strip()
    try: return parsedate_to_datetime(s).astimezone(timezone.utc)
    except Exception: pass
    try:
        s2 = s.replace("Z", "+00:00")
        d = datetime.fromisoformat(s2)
        if d.tzinfo is None: d = d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc)
    except Exception: pass
    return None

def parse_feed(xml_bytes, source):
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        text = xml_bytes.decode("utf-8", errors="replace")
        text = text.lstrip("﻿").strip()
        text = re.sub(r"^[^<]*", "", text)
        root = ET.fromstring(text.encode("utf-8"))

    items = []
    tag = root.tag.lower()
    is_atom = tag.endswith("feed") or "atom" in tag
    is_rdf  = tag.endswith("rdf")

    if is_atom:
        for entry in root.findall("atom:entry", NS):
            title = _text(entry.find("atom:title", NS))
            link_el = entry.find("atom:link", NS)
            link = link_el.attrib.get("href", "") if link_el is not None else ""
            summary = _text(entry.find("atom:summary", NS)) or _text(entry.find("atom:content", NS))
            published = _text(entry.find("atom:published", NS)) or _text(entry.find("atom:updated", NS))
            items.append({"title": title, "link": link, "summary": summary, "published": published})
    elif is_rdf:
        for item in root.findall("rss10:item", NS):
            title = _text(item.find("rss10:title", NS))
            link  = _text(item.find("rss10:link",  NS))
            summary = _text(item.find("rss10:description", NS)) or _text(item.find("dc:description", NS))
            published = _text(item.find("dc:date", NS))
            items.append({"title": title, "link": link, "summary": summary, "published": published})
    else:
        for item in root.iter("item"):
            title = _text(item.find("title"))
            link  = _text(item.find("link"))
            summary = _text(item.find("description"))
            if not summary:
                ce = item.find("{http://purl.org/rss/1.0/modules/content/}encoded")
                if ce is not None: summary = ce.text or ""
            published = _text(item.find("pubDate"))
            if not published:
                dc = item.find("{http://purl.org/dc/elements/1.1/}date")
                if dc is not None: published = dc.text or ""
            items.append({"title": title, "link": link, "summary": summary, "published": published})

    for it in items:
        it["title"] = (it["title"] or "").strip()
        it["summary"] = strip_html(it["summary"] or "").strip()
        if len(it["summary"]) > 480:
            it["summary"] = it["summary"][:477].rsplit(" ", 1)[0] + "…"
        it["published_dt"] = parse_date(it["published"])
    return items

# =============================================================================
# CLASSIFICATION
# =============================================================================
def detect_country(text_norm, force=None):
    if force: return force
    matches = []
    for c in COUNTRIES:
        for kw in c["kw"]:
            kwn = norm(kw)
            pattern = r"(?<![a-z])" + re.escape(kwn) + r"(?![a-z])"
            if re.search(pattern, text_norm):
                matches.append(c["code"])
                break
    if not matches: return None
    first, first_pos = None, 10**9
    for code in matches:
        c = next(c for c in COUNTRIES if c["code"] == code)
        for kw in c["kw"]:
            kwn = norm(kw)
            m = re.search(r"(?<![a-z])" + re.escape(kwn) + r"(?![a-z])", text_norm)
            if m and m.start() < first_pos:
                first_pos = m.start()
                first = code
    return first

def detect_category(text_norm):
    scores = {}
    for cat, keywords in CATEGORIES.items():
        s = 0
        for kw in keywords:
            kwn = norm(kw)
            s += len(re.findall(r"(?<![a-z])" + re.escape(kwn), text_norm))
        if s > 0: scores[cat] = s
    if not scores: return "AUTRE"
    return max(scores, key=scores.get)

def detect_severity(text_norm):
    score = 1
    def has(kw):
        return re.search(r"(?<![a-z])" + re.escape(norm(kw)), text_norm) is not None
    for kw in SEVERITY_HIGH:
        if has(kw): score = max(score, 4)
    for kw in SEVERITY_MEDIUM:
        if has(kw): score = max(score, 3)
    for kw in SEVERITY_LOW:
        if has(kw): score = max(score, 2)
    return score

def detect_theme(text_norm):
    scores = {}
    for theme, keywords in THEMES.items():
        s = 0
        for kw in keywords:
            kwn = norm(kw)
            s += len(re.findall(r"(?<![a-z])" + re.escape(kwn), text_norm))
        if s > 0: scores[theme] = s
    if not scores: return None
    return max(scores, key=scores.get)

def detect_legal_status(text_norm):
    order = ["OPERATIONAL", "CONSTRUCTION", "FINANCING", "ANNOUNCED"]
    for status in order:
        for kw in LEGAL_STATUSES[status]:
            kwn = norm(kw)
            if re.search(r"(?<![a-z])" + re.escape(kwn), text_norm):
                return status
    return None

def is_regulatory(text_norm, theme):
    if theme is not None: return True
    for kw in REGULATORY_TRIGGER:
        kwn = norm(kw)
        if re.search(r"(?<![a-z])" + re.escape(kwn), text_norm):
            return True
    return False

def is_fdi_news(text_norm):
    for kw in FDI_KEYWORDS:
        kwn = norm(kw)
        if re.search(r"(?<![a-z])" + re.escape(kwn), text_norm):
            return True
    return False

def detect_sectors(text_norm):
    hits = []
    for code, keywords in SECTORS.items():
        for kw in keywords:
            kwn = norm(kw)
            if re.search(r"(?<![a-z])" + re.escape(kwn), text_norm):
                hits.append(code)
                break
    return hits

# =============================================================================
# DEDUPE & CROSS-VERIFICATION
# =============================================================================
STOPWORDS = set("""
le la les un une des du de et à a au aux en dans pour par sur avec sans ce cet cette ces
the a an and or of in on at to by for with from is are was were be been being
that this it its his her their our we you they i
""".split())

def signature(title):
    t = norm(title)
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    words = [w for w in t.split() if len(w) >= 4 and w not in STOPWORDS]
    return set(words)

def jaccard(a, b):
    if not a or not b: return 0.0
    return len(a & b) / len(a | b)

def dedupe_and_verify(articles):
    clusters = []
    for art in articles:
        sig = art["_sig"]
        placed = False
        for cl in clusters:
            if jaccard(sig, cl["sig"]) >= 0.45:
                cl["members"].append(art)
                cl["sig"] |= sig
                placed = True
                break
        if not placed:
            clusters.append({"sig": set(sig), "members": [art]})

    final = []
    for cl in clusters:
        cl["members"].sort(key=lambda a: (a["source_tier"], -(a["published_dt"].timestamp() if a["published_dt"] else 0)))
        lead = dict(cl["members"][0])
        sources_seen = []
        seen_ids = set()
        for m in cl["members"]:
            if m["source_id"] not in seen_ids:
                sources_seen.append({"id": m["source_id"], "name": m["source_name"],
                                     "tier": m["source_tier"], "url": m["link"]})
                seen_ids.add(m["source_id"])

        lead["confirming_sources"] = sources_seen
        lead["confirmation_count"] = len(sources_seen)
        tier1 = sum(1 for s in sources_seen if s["tier"] == 1)
        tier2 = sum(1 for s in sources_seen if s["tier"] == 2)
        cred = 1 + min(tier1, 3) + min(tier2, 2)
        if lead["confirmation_count"] >= 2:
            cred += 1
        lead["credibility"] = min(cred, 5)
        lead["verified"] = lead["confirmation_count"] >= 2
        if lead["verified"]:
            lead["severity"] = min(4, lead["severity"] + 1)
        final.append(lead)
    return final

# =============================================================================
# MAIN
# =============================================================================
def main():
    print("\n┌─ Taranis Intelligence · agrégation des sources ─────────────────")
    all_articles = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)

    for i, src in enumerate(SOURCES):
        label = f"│  [{i+1:>2}/{len(SOURCES)}] {src['name']:<30}"
        try:
            t0 = time.time()
            data = fetch_url(src["url"])
            items = parse_feed(data, src)
            kept = 0
            for it in items:
                if not it["title"]: continue
                if it["published_dt"] and it["published_dt"] < cutoff: continue
                text = it["title"] + " " + (it["summary"] or "")
                text_norm = norm(text)
                country = detect_country(text_norm, force=src.get("force_country"))
                if not country: continue
                cat = detect_category(text_norm)
                sev = detect_severity(text_norm)
                theme = detect_theme(text_norm)
                lstatus = detect_legal_status(text_norm)
                regu = is_regulatory(text_norm, theme)
                fdi  = is_fdi_news(text_norm)
                sectors = detect_sectors(text_norm)
                all_articles.append({
                    "title": it["title"],
                    "summary": it["summary"],
                    "link": it["link"],
                    "published": it["published_dt"].isoformat() if it["published_dt"] else None,
                    "published_dt": it["published_dt"] or datetime.now(timezone.utc),
                    "source_id": src["id"],
                    "source_name": src["name"],
                    "source_tier": src["tier"],
                    "country": country,
                    "category": cat,
                    "severity": sev,
                    "theme": theme,
                    "legal_status": lstatus,
                    "regulatory": regu,
                    "fdi": fdi,
                    "sectors": sectors,
                    "lang": src.get("lang", "fr"),
                    "_sig": signature(it["title"]),
                })
                kept += 1
            print(f"{label} OK   ({kept:>3} pertinents / {len(items):>3} articles · {time.time()-t0:.1f}s)")
        except Exception as e:
            print(f"{label} SKIP ({type(e).__name__})")
        time.sleep(0.7)

    print(f"│")
    print(f"│  → {len(all_articles)} articles pré-filtrés")

    clusters = dedupe_and_verify(all_articles)
    clusters.sort(key=lambda a: (-(a["severity"]), -(a["published_dt"].timestamp())))

    verified = sum(1 for c in clusters if c["verified"])
    per_country = {}
    for c in clusters: per_country[c["country"]] = per_country.get(c["country"], 0) + 1

    print(f"│  → {len(clusters)} signaux uniques après dédoublonnage")
    print(f"│  → {verified} signaux cross-vérifiés (≥2 sources)")
    print(f"│  → {len(per_country)} pays Taranis couverts par la veille")

    west_codes = {"NGA","GHA","CIV","SEN","MLI","BFA","NER","GIN","SLE","LBR","TGO","BEN","CPV","GMB","GNB"}
    east_codes = {"KEN","ETH","TZA","UGA","RWA","BDI","DJI","SOM","MOZ","MDG","MUS","MWI","SSD","ERI","COM"}
    w = sum(v for k,v in per_country.items() if k in west_codes)
    e = sum(v for k,v in per_country.items() if k in east_codes)
    print(f"│     · Afrique de l'Ouest : {w}")
    print(f"│     · Afrique de l'Est   : {e}")

    per_cat = {}
    for c in clusters: per_cat[c["category"]] = per_cat.get(c["category"], 0) + 1
    print(f"│  Par catégorie :")
    for k,v in sorted(per_cat.items(), key=lambda x:-x[1]):
        print(f"│     · {k:<10} {v}")

    fdi = [c for c in clusters if c.get("fdi")]
    print(f"│  → {len(fdi)} signaux Financement détectés")
    regu = [c for c in clusters if c.get("regulatory")]
    print(f"│  → {len(regu)} signaux Énergies Renouvelables détectés")

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stats": {
            "total_signals": len(clusters),
            "verified_signals": verified,
            "countries_covered": len(per_country),
            "sources_active": len(SOURCES),
            "per_country": per_country,
            "west_signals": w,
            "east_signals": e,
        },
        "sources": [{"id": s["id"], "name": s["name"], "tier": s["tier"], "url": s["url"]} for s in SOURCES],
        "signals": [{
            "id": md5((c["title"] + c["source_id"]).encode("utf-8")).hexdigest()[:10],
            "title": c["title"],
            "summary": c["summary"],
            "country": c["country"],
            "category": c["category"],
            "severity": c["severity"],
            "credibility": c["credibility"],
            "verified": c["verified"],
            "theme": c.get("theme"),
            "legal_status": c.get("legal_status"),
            "regulatory": c.get("regulatory", False),
            "fdi": c.get("fdi", False),
            "sectors": c.get("sectors", []),
            "lang": c.get("lang", "fr"),
            "published": c["published"],
            "lead_source": {"id": c["source_id"], "name": c["source_name"], "tier": c["source_tier"], "url": c["link"]},
            "confirming_sources": c["confirming_sources"],
            "confirmation_count": c["confirmation_count"],
        } for c in clusters],
    }

    OUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"│")
    print(f"└─ ✓ news.json écrit ({OUT_PATH.stat().st_size // 1024} KB)\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrompu.")
        sys.exit(130)

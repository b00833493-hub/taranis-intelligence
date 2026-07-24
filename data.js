// ============================================================
// Taranis Intelligence — Métadonnées pays & thèmes
// ============================================================
// Focus : Afrique Sub-Saharienne (Afrique de l'Ouest + Afrique de l'Est)
// Volontairement exclus : Afrique du Nord, Afrique Australe.
// 30 pays au total, équilibrés 15 W / 15 E.

const TARANIS_COUNTRIES = [
  // ===== AFRIQUE DE L'OUEST (15) =====
  { code: "NGA", name: "Nigeria",         flag: "🇳🇬", region: "Afrique de l'Ouest", lat: 9.08,   lon: 8.68,   city: "Abuja" },
  { code: "GHA", name: "Ghana",           flag: "🇬🇭", region: "Afrique de l'Ouest", lat: 5.55,   lon: -0.20,  city: "Accra" },
  { code: "CIV", name: "Côte d'Ivoire",   flag: "🇨🇮", region: "Afrique de l'Ouest", lat: 5.32,   lon: -4.03,  city: "Abidjan" },
  { code: "SEN", name: "Sénégal",         flag: "🇸🇳", region: "Afrique de l'Ouest", lat: 14.69,  lon: -17.45, city: "Dakar" },
  { code: "MLI", name: "Mali",            flag: "🇲🇱", region: "Afrique de l'Ouest", lat: 12.65,  lon: -8.00,  city: "Bamako" },
  { code: "BFA", name: "Burkina Faso",    flag: "🇧🇫", region: "Afrique de l'Ouest", lat: 12.37,  lon: -1.52,  city: "Ouagadougou" },
  { code: "NER", name: "Niger",           flag: "🇳🇪", region: "Afrique de l'Ouest", lat: 13.51,  lon: 2.11,   city: "Niamey" },
  { code: "GIN", name: "Guinée",          flag: "🇬🇳", region: "Afrique de l'Ouest", lat: 9.64,   lon: -13.58, city: "Conakry" },
  { code: "SLE", name: "Sierra Leone",    flag: "🇸🇱", region: "Afrique de l'Ouest", lat: 8.48,   lon: -13.23, city: "Freetown" },
  { code: "LBR", name: "Libéria",         flag: "🇱🇷", region: "Afrique de l'Ouest", lat: 6.30,   lon: -10.80, city: "Monrovia" },
  { code: "TGO", name: "Togo",            flag: "🇹🇬", region: "Afrique de l'Ouest", lat: 6.13,   lon: 1.22,   city: "Lomé" },
  { code: "BEN", name: "Bénin",           flag: "🇧🇯", region: "Afrique de l'Ouest", lat: 6.36,   lon: 2.42,   city: "Cotonou" },
  { code: "CPV", name: "Cap-Vert",        flag: "🇨🇻", region: "Afrique de l'Ouest", lat: 14.93,  lon: -23.51, city: "Praia" },
  { code: "GMB", name: "Gambie",          flag: "🇬🇲", region: "Afrique de l'Ouest", lat: 13.45,  lon: -16.58, city: "Banjul" },
  { code: "GNB", name: "Guinée-Bissau",   flag: "🇬🇼", region: "Afrique de l'Ouest", lat: 11.86,  lon: -15.60, city: "Bissau" },

  // ===== AFRIQUE DE L'EST (15) =====
  { code: "KEN", name: "Kenya",           flag: "🇰🇪", region: "Afrique de l'Est", lat: -1.29,  lon: 36.82,  city: "Nairobi" },
  { code: "ETH", name: "Éthiopie",        flag: "🇪🇹", region: "Afrique de l'Est", lat: 9.03,   lon: 38.74,  city: "Addis-Abeba" },
  { code: "TZA", name: "Tanzanie",        flag: "🇹🇿", region: "Afrique de l'Est", lat: -6.79,  lon: 39.21,  city: "Dar es Salaam" },
  { code: "UGA", name: "Ouganda",         flag: "🇺🇬", region: "Afrique de l'Est", lat: 0.31,   lon: 32.58,  city: "Kampala" },
  { code: "RWA", name: "Rwanda",          flag: "🇷🇼", region: "Afrique de l'Est", lat: -1.94,  lon: 30.06,  city: "Kigali" },
  { code: "BDI", name: "Burundi",         flag: "🇧🇮", region: "Afrique de l'Est", lat: -3.43,  lon: 29.93,  city: "Gitega" },
  { code: "DJI", name: "Djibouti",        flag: "🇩🇯", region: "Afrique de l'Est", lat: 11.83,  lon: 42.59,  city: "Djibouti" },
  { code: "SOM", name: "Somalie",         flag: "🇸🇴", region: "Afrique de l'Est", lat: 2.04,   lon: 45.34,  city: "Mogadiscio" },
  { code: "MOZ", name: "Mozambique",      flag: "🇲🇿", region: "Afrique de l'Est", lat: -25.97, lon: 32.58,  city: "Maputo" },
  { code: "MDG", name: "Madagascar",      flag: "🇲🇬", region: "Afrique de l'Est", lat: -18.88, lon: 47.51,  city: "Antananarivo" },
  { code: "MUS", name: "Maurice",         flag: "🇲🇺", region: "Afrique de l'Est", lat: -20.16, lon: 57.50,  city: "Port-Louis" },
  { code: "MWI", name: "Malawi",          flag: "🇲🇼", region: "Afrique de l'Est", lat: -13.98, lon: 33.78,  city: "Lilongwe" },
  { code: "SSD", name: "Soudan du Sud",   flag: "🇸🇸", region: "Afrique de l'Est", lat: 4.85,   lon: 31.58,  city: "Juba" },
  { code: "ERI", name: "Érythrée",        flag: "🇪🇷", region: "Afrique de l'Est", lat: 15.34,  lon: 38.93,  city: "Asmara" },
  { code: "COM", name: "Comores",         flag: "🇰🇲", region: "Afrique de l'Est", lat: -11.70, lon: 43.26,  city: "Moroni" },
];

// Rétro-compat : app.js utilise OLEA_COUNTRIES ; on aliase.
const OLEA_COUNTRIES = TARANIS_COUNTRIES;

const ISO_NUMERIC = {
  // West Africa
  NGA: 566, GHA: 288, CIV: 384, SEN: 686, MLI: 466, BFA: 854, NER: 562,
  GIN: 324, SLE: 694, LBR: 430, TGO: 768, BEN: 204, CPV: 132, GMB: 270, GNB: 624,
  // East Africa
  KEN: 404, ETH: 231, TZA: 834, UGA: 800, RWA: 646, BDI: 108,
  DJI: 262, SOM: 706, MOZ: 508, MDG: 450, MUS: 480, MWI: 454,
  SSD: 728, ERI: 232, COM: 174,
};

// ============================================================
// 3 THÈMES TARANIS
// ============================================================
// MACRO      : PIB, inflation, dette, banques centrales, politique éco
// RENEWABLE  : hydro, solaire, éolien, géothermie, biomasse, transition
// FINANCING  : DFIs (AfDB, IFC), private equity, VC, obligations, blended
const CATEGORIES = {
  MACRO:     { label: "Macro & économie",       color: "#0B4F8B", short: "Macro" },
  RENEWABLE: { label: "Énergies renouvelables", color: "#22C55E", short: "Renouvelables" },
  FINANCING: { label: "Financement Afrique",    color: "#F4B942", short: "Financement" },
  AUTRE:     { label: "Autres",                 color: "#94A3B8", short: "Autre" },
};

// Sous-thèmes renouvelable (page dédiée)
const RENEWABLE_TECHS = {
  HYDRO:      { label: "Hydro",               color: "#0EA5E9", short: "Hydro" },
  SOLAR:      { label: "Solaire",             color: "#F59E0B", short: "Solaire" },
  WIND:       { label: "Éolien",              color: "#06B6D4", short: "Éolien" },
  GEOTHERMAL: { label: "Géothermie",          color: "#DC2626", short: "Géothermie" },
  BIOMASS:    { label: "Biomasse",            color: "#65A30D", short: "Biomasse" },
  GRID:       { label: "Réseaux / Mini-grid", color: "#7C3AED", short: "Grid" },
};

// Sous-thèmes financement (page dédiée)
const FINANCING_TYPES = {
  DFI:      { label: "DFI (banques de dév.)", color: "#0B4F8B", short: "DFI" },
  PE_VC:    { label: "Private equity / VC",   color: "#7C3AED", short: "PE / VC" },
  DEBT:     { label: "Dette / obligations",   color: "#65A30D", short: "Dette" },
  BLENDED:  { label: "Blended finance",       color: "#F4B942", short: "Blended" },
  GRANT:    { label: "Subventions & aid",     color: "#0EA5E9", short: "Grants" },
};

// Statuts projet (renewables — inspiré du workflow régulatoire OLEA)
const PROJECT_STATUSES = {
  ANNOUNCED:    { label: "Annoncé",         color: "#94A3B8", short: "Annoncé",    order: 1 },
  FINANCING:    { label: "En financement",  color: "#F4B942", short: "Financement", order: 2 },
  CONSTRUCTION: { label: "En construction", color: "#0EA5E9", short: "Chantier",   order: 3 },
  OPERATIONAL:  { label: "Opérationnel",    color: "#22C55E", short: "Live",       order: 4 },
};

// Alias vers les noms utilisés par app.js (originellement pour OLEA).
// Page 2 (Regulatory → Renewables) : THEMES = techs renouvelables, LEGAL_STATUSES = étape projet
// Page 3 (Markets → Financement)   : reste dans le format markets ; SECTORS = types de financement
const THEMES = RENEWABLE_TECHS;
const LEGAL_STATUSES = PROJECT_STATUSES;
const SECTORS = FINANCING_TYPES;

const REGION_KEY = {
  "Afrique de l'Ouest": "region.west",
  "Afrique de l'Est":   "region.east",
};

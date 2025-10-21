#!/usr/bin/env python3
"""
Deep Research Wrapper Script
Simplified interface for running deep research with detailed instructions
"""
from datetime import datetime
import os
import asyncio
from dotenv import load_dotenv
from gpt_researcher import GPTResearcher
from gpt_researcher.utils.enum import ReportType, Tone
import logging
import sys
from pathlib import Path

# ============================================================================
# CRITICAL: Configure logging FIRST before any imports
# ============================================================================
logging.basicConfig(
    level=logging.INFO,  # Set to INFO level
    format='%(levelname)s:     [%(asctime)s] %(message)s',
    datefmt='%H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Force all loggers to INFO
logging.getLogger().setLevel(logging.INFO)
for logger_name in ['gpt_researcher', 'research', '__main__']:
    logging.getLogger(logger_name).setLevel(logging.INFO)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


# Load environment variables
load_dotenv()

# ============================================================================
# YOUR RESEARCH QUERY - EDIT THIS SECTION
# ============================================================================

RESEARCH_QUERY = """
# Forschungsauftrag für Research Agent: Machbarkeitsstudie zur europäischen Servo-Produktion

## MISSIONSZIEL

Durchführung gezielter Informationsbeschaffung zur Validierung und Verfeinerung des österreichischen Servo-Produktionsplans für die Kriegszeit-UAV-Fertigung, mit Fokus auf unmittelbar umsetzbare Daten, 
die den 18-Monats-Zeitplan bis zur skalierten Produktion beeinflussen.
Sie müssen 200+ URLs besuchen und relevante Daten sammeln, um einen umfassenden Bericht zu erstellen. Dies ist ein Marathon und kein Sprint.
Die meisten offiziellen Quellen im DACH-Raum sind auf Deutsch. Verwenden Sie daher ausgiebig die deutsche Sprache, Englisch ist die zweite Option, aber nicht die erste Wahl.

*** SIE MÜSSEN DEUTSCH VERWENDEN, UM INFORMATIONEN ÜBER LOKALE UNTERNEHMEN, VORSCHRIFTEN UND REGIERUNGSPROGRAMME ZU ERHALTEN. ***

### KONTEXT ZUR EIGNUNG DER AUTOMOBILINDUSTRIE
Die Automobil-Sensor- und Komponentenfertigungsindustrie verwendet nahezu identische Prozesse wie die Servo-Produktion: Präzisions-Spritzguss für Kunststoffgehäuse und Zahnräder, 
SMT-Bestückungslinien für Steuerungselektronik und Hochvolumen-Qualitätsprüfsysteme. Insolvente Automobilwerke bieten schlüsselfertige Anlagen mit Klimatisierung, Reinräumen
und geschulten Arbeitskräften, die mit elektromechanischen Baugruppen im exakt benötigten Maßstab (10K-100K Einheiten monatlich) vertraut sind. Der Zusammenbruch der Automobilindustrie
in Österreich und Mitteleuropa aufgrund der chinesischen E-Mobilitäts-Konkurrenz schafft verfügbare Anlagen zu Notverkaufspreisen, arbeitslose Fachkräfte, die Beschäftigung benötigen, 
und bestehende Zulieferernetzwerke für Motoren, Elektronik und Präzisionsbauteile. Automotive-Qualitätsstandards (Vibrationsfestigkeit, Temperaturbereiche, Lebensdauertests)
überschneiden sich erheblich mit militärischen UAV-Anforderungen, was bedeutet, dass bestehende Ausrüstung und Expertise direkt auf die Servo-Produktion übertragbar sind 
mit minimaler Umschulung. Zusätzlich haben Automotive-Elektronikingenieure umfassende Erfahrung mit CAN-Bus und kabelgebundenen Kommunikationsprotokollen, die natürlich 
immun gegen Hochfrequenzstörungen und elektronische Kriegsführung sind, was diese Expertise kritisch für Glasfaser-Drohnensteuerungssysteme macht, die drahtlose Verwundbarkeiten 
umgehen. Der Wechsel von PWM-Funksteuerung zu kabelgebundener digitaler Kommunikation für EW-resistente Drohnen passt perfekt zu Automotive-Netzwerkprotokollen (CAN, LIN, FlexRay), 
die von dieser Belegschaft bereits beherrscht werden.

## PRIORITÄRE NACHRICHTENDIENSTLICHE ANFORDERUNGEN (PIR)

### 1. ANLAGEN & INFRASTRUKTUR (KRITISCH - Woche 1-2)

Identifizierung von 3-5 insolventen oder notleidenden Automobil-Komponentenherstellern in der Region Linz/Wels in Österreich mit bestehenden Spritzguss- und SMT-Fähigkeiten,
einschließlich aktueller Angebotspreise, Maschinenbeständen und Anlagengrößen. Bestimmung, welche Anlagen über Reinräume, Klimatisierung und Strominfrastruktur verfügen, die 
für Elektronikhersteller geeignet sind. Recherche des österreichischen Gewerbeimmobilienmarktes für Produktionsanlagen zwischen 5.000-20.000 m² und aktuelle Miet-/Kaufpreise in 
der Zielregion.

### 2. MAGNETEN-LIEFERKETTE (KRITISCH - Woche 1)

Identifizierung aktueller chinesischer NdFeB-Magneten-Lieferanten, die bereit sind, Großbestellungen (€2-3M Wert) mit Lieferzeiten zu versenden, und Bewertung ihrer Bereitschaft, 
an österreichische Zivilunternehmen vor möglichen Exportbeschränkungen zu liefern. Recherche alternativer Seltenerd-Magnetquellen einschließlich bestehender europäischer Lagerbestände,
Schrott-/Recyclingbetriebe und Sekundärmärkte von Festplattenhersteller oder Automotive-Sensorhersteller. Untersuchung europäischer Ferrit-Magnetenhersteller mit Kapazität
zur Lieferung von 100.000+ Einheiten monatlich und deren aktuellen Produktionsfähigkeiten und Vorlaufzeiten.

### 3. KOMPONENTENBESCHAFFUNG (HOHE PRIORITÄT - Woche 2-3)

Kartierung der STM32F030-Mikrocontroller-Verfügbarkeit bei europäischen Distributoren einschließlich aktueller Lagerbestände, Lieferzeiten und Mengenpreise für 100K+
Einheitenbestellungen. Identifizierung von Infineon-Leistungs-MOSFET-Modellen, die für H-Brücken-Motortreiber geeignet sind, mit europäischer Lagerverfügbarkeit und Preisen. 
Recherche von Potentiometerherstellern außerhalb Chinas (Europa, Türkei, Japan, Taiwan) mit Spezifikationen, die für Servo-Positionssensoren geeignet sind, und deren Bereitschaft 
zur Lieferung von Notbestellungen. Bestimmung der Leiterplatten-Fertigungskapazität in Österreich, Polen und Tschechien für 2-lagige Platinen mit Lieferzeiten für
50K-200K monatliche Produktion.

### 4. UKRAINISCHE GEFECHTSFELDDATEN-ZUGANG (HOHE PRIORITÄT - Woche 1-2)

Identifizierung ukrainischer UAV-Ingenieurgruppen, die derzeit in Österreich tätig oder für Zusammenarbeit erreichbar sind, einschließlich ihrer Organisationsstruktur und Kontaktmethoden. 
Recherche, welche spezifischen chinesischen Servo-Modelle (mit exakten Teilenummern) derzeit in ukrainischen FPV-Kampfdrohnen verwendet werden, basierend auf öffentlichen Aussagen, 
Beschaffungsunterlagen oder technischen Dokumentationen. Bestimmung typischer Ausfallmodi und Ausfallraten von Servos in ukrainischen Kampfeinsätzen aus verfügbaren 
Einsatzberichten, technischen Foren oder Ingenieursdiskussionen. Bewertung der ukrainischen Bereitschaft zur Teilnahme an Rapid-Prototyping- und Gefechtsfeldtestprogrammen mit österreichischen Herstellern.

### 5. ARBEITSKRÄFTE & ARBEITSMARKT (MITTLERE PRIORITÄT - Woche 2-3)

Quantifizierung von Vertriebenen und Asylsuchenden in der Region Linz/Wels mit Fertigungs- oder technischem Hintergrund, einschließlich ihres rechtlichen Arbeitserlaubnisstatus 
und Sprachkenntnissen. Recherche österreichischer Vorschriften für die Beschäftigung von Flüchtlingen und Asylsuchenden in verteidigungsbezogener Fertigung einschließlich etwaiger 
Beschränkungen oder beschleunigter Prozesse für Kriegsproduktion. Identifizierung von Personalvermittlungsagenturen oder NGOs, die mit vertriebenen Bevölkerungen arbeiten und die 
Arbeitskräfteentwicklung erleichtern könnten. Bewertung der Verfügbarkeit pensionierter österreichischer Automobilarbeiter oder solcher, die von Entlassungen bei angeschlagenen 
Herstellern bedroht sind und Schulung und Aufsicht bieten könnten.

### 6. SPRITZGUSSKAPAZITÄT (HOHE PRIORITÄT - Woche 2)

Identifizierung europäischer Spritzguss-Werkzeugbauer, die in der Lage sind, Einkavitäten-Formen für kleine Servo-Gehäuse und Zahnradkomponenten in 4-6 Wochen Notlieferung zu fertigen. 
Recherche türkischer und polnischer Werkzeuglieferanten mit schnelleren Zeitplänen und niedrigeren Kosten, auch wenn die Präzision reduziert ist. Bestimmung der Verfügbarkeit gebrauchter 
oder generalüberholter Spritzgussmaschinen (8-15 Tonnen Kapazität), die für Kleinteile auf europäischen Sekundärmärkten geeignet sind. Bewertung der Kosten für Notwerkzeugmodifikationen 
und typische Iterationszeitpläne für Präzisions-Kunststoffzahnradfertigung.

### 7. DEUTSCHE BUNDESWEHR-BESCHAFFUNG (HOHE PRIORITÄT - Woche 1-2)

Identifizierung aktueller Bundeswehr-UAV-Beschaffungsprogramme, Budgetzuweisungen für 2026-2027 und Kontaktinformationen für relevante Beschaffungsbeamte. Recherche deutscher 
otfall-Verteidigungsbeschaffungsverfahren, die normale mehrjährige Prozesse bei kritischen Engpässen umgehen könnten. Bestimmung, ob die Bundeswehr irgendwelche Informationsanfragen 
(RFI) oder Angebotsanfragen (RFP) im Zusammenhang mit Drohnenkomponenten oder Servo-Lieferungen herausgegeben hat. Bewertung deutscher Regierungspolitik zu inländischer vs.
EU-Verteidigungsfertigung und etwaiger Präferenzprogramme für österreichische Lieferanten.

### 8. WETTBEWERBSLANDSCHAFT (MITTLERE PRIORITÄT - Woche 3)

Identifizierung bestehender europäischer Servo-Hersteller, die versuchen, in den militärischen UAV-Markt einzutreten, einschließlich ihrer Produktionskapazität, Preisgestaltung und 
Zeitpläne. Recherche türkischer Drohnenkomponenten-Hersteller angesichts ihrer UAV-Industriereife und potenzieller Partnerschafts- oder Wettbewerbsbedrohung. Bestimmung, ob andere 
EU-Länder Servo-Produktionsprogramme oder ähnliche Importsubstitutionsinitiativen angekündigt haben. Bewertung israelischer Verteidigungs-Elektronikexporteure, die Europa während 
asiatischer Lieferkettenstörungen beliefern könnten.

### 9. REGULATORISCHES & POLITISCHES UMFELD (MITTLERE PRIORITÄT - Woche 2-3)

Recherche österreichischer Regierungsprogramme zur Unterstützung der Verteidigungsindustrie, einschließlich Zuschüsse, Darlehen oder Garantien, die für kritische Verteidigungsfertigung 
verfügbar sind. Bestimmung des Status von EU-Dual-Use-Exportkontrollvorschriften und ob Notfall-Kriegszeitausnahmen diskutiert werden. Identifizierung österreichischer politischer 
Persönlichkeiten oder Ministerialbeamter, die die Entwicklung der verteidigungsindustriellen Basis befürworten und Verbündete sein könnten. Bewertung der Wahrscheinlichkeit und des 
Zeitplans für Umweltregulierungs-Ausnahmen für Verteidigungsfertigung basierend auf Präzedenzfällen oder aktuellen politischen Diskussionen.

### 10. TECHNISCHE VALIDIERUNG (NIEDRIGE PRIORITÄT - Woche 3-4)

Validierung, dass Tower Pro SG90, MG90S und Emax ES08MA Servos tatsächlich die dominierenden Modelle in ukrainischen FPV-Operationen sind durch fotografische Beweise oder Beschaffungsdaten. 
Recherche offener ukrainischer Drohnen-Designs (Lyutyi/Bober) für detaillierte Servo-Spezifikationen und Integrationsanforderungen. Identifizierung technischer Spezifikationen für 
iranische Shahed-Drohnen-Steuerflächen und Servo-Anforderungen aus Analyse- oder Nachrichtenberichten. Bestimmung, ob vereinfachte Servo-Designs existieren, die Leistung für 
Herstellbarkeit opfern, basierend auf historischen Kriegsproduktionsbeispielen.

## AUSGABEANFORDERUNGEN

Erstellung eines strukturierten Nachrichtendienstberichts mit Executive Summary, der kritische Blocker oder Enabler hervorhebt, die während der Recherche entdeckt wurden. Einbeziehung 
spezifischer Firmennamen, Kontaktinformationen, Preisdaten und Zeitschätzungen wo immer möglich, anstelle allgemeiner Aussagen. Priorisierung von Informationen, die die Entscheidungsfindung 
verändern: Wenn die österreichische Produktion aufgrund entdeckter Einschränkungen nicht durchführbar ist, dies klar mit Beweisen darlegen. Bereitstellung von Quellen für alle 
Behauptungen mit Daten der Informationsbeschaffung, da sich Lieferketten und politische Situationen schnell entwickeln. Kennzeichnung aller Informationslücken, bei denen weitere 
menschliche Nachrichtendienstbeschaffung oder direkter Kontakt erforderlich ist.

## FORSCHUNGSBESCHRÄNKUNGEN & METHODIK

Fokus auf öffentlich verfügbare Informationen, Branchendatenbanken, Firmenwebsites, Beschaffungsportale und Nachrichtenquellen, die nach Januar 2024 veröffentlicht wurden. Verwendung
primär deutscher und englischer Sprachquellen, aber Notierung kritischer Informationen, die nur auf Ukrainisch, Polnisch oder anderen Sprachen verfügbar sind. Priorisierung aktueller 
Informationen über historische Daten angesichts der raschen Veränderungen in der verteidigungsindustriellen Basis und Lieferkettensituationen. Wo exakte Daten nicht verfügbar sind, 
Bereitstellung fundierter Schätzungen mit expliziten Unsicherheitsbereichen und Begründung. Keine Spekulation über klassifizierte militärische Fähigkeiten oder sensible operative Details.

## ERFOLGSKRITERIEN

Die Forschung ist erfolgreich, wenn sie eine klare GO/NO-GO-Entscheidung zum österreichischen Servo-Produktionsplan innerhalb von 3-4 Wochen nach Abschluss der Recherche ermöglicht. 
Kritische Unbekannte, die den 18-Monats-Zeitplan verzögern oder entgleisen lassen würden, müssen identifiziert und quantifiziert werden. Umsetzbare nächste Schritte mit spezifischen
Kontakten, Lieferanten oder Partnern sollten für jede Hauptkomponente des Plans bereitgestellt werden. Der Bericht sollte entweder das Vertrauen in die Machbarkeit der
Kriegszeit-Servo-Produktion erhöhen oder fatale Mängel identifizieren, die eine größere Planrevision erfordern, bevor bedeutendes Kapital gebunden wird.
"""

# English version of the research query for reference

"""
# Research Agent Task Specification: European Servo Production Feasibility Study

## MISSION OBJECTIVE

Conduct targeted intelligence gathering to validate and refine the Austrian servo production plan for wartime UAV manufacturing, 
with focus on immediate actionable data that impacts the 18-month timeline to production at scale.
You would need to visit 200+ URLs and gather relevant data to produce a comprehensive report. This is a marathon and not sprint.
The most of official sources in DACH region are in German. Therefore use German language extensively, English is the second option,
but not the first choice. 

*** YOU MUST USE GERMAN TO GET INFORMATION ABOUT LOCAL COMPANIES, REGULATIONS, AND GOVERNMENT PROGRAMS. ***


### AUTOMOTIVE INDUSTRY SUITABILITY CONTEXT
The automotive sensor and component manufacturing industry uses nearly identical processes to servo production: precision 
injection molding for plastic housings and gears, SMT assembly lines for control electronics, and high-volume quality 
testing systems. Bankrupt automotive factories offer turnkey facilities with environmental controls, clean rooms, 
and trained workforces familiar with electromechanical assemblies at the exact scale needed (10K-100K units monthly). 
The automotive industry collapse in Austria and Central Europe due to Chinese EV competition creates available 
facilities at distressed prices, displaced workers needing employment, and existing supplier networks for motors, 
electronics, and precision components. Automotive quality standards (vibration resistance, temperature ranges, 
lifecycle testing) overlap significantly with military UAV requirements, meaning existing equipment and expertise
translate directly to servo production with minimal retraining. Additionally, automotive electronics engineers have 
extensive experience with CAN bus and wired communication protocols which are naturally immune to radio frequency 
jamming and electronic warfare, making this expertise critical for fiber-optic drone control systems that bypass 
wireless vulnerabilities. The shift from PWM radio control to hardwired digital communication for EW-resistant drones 
aligns perfectly with automotive networking protocols (CAN, LIN, FlexRay) already mastered by this workforce.

## PRIORITY INTELLIGENCE REQUIREMENTS (PIR)

### 1. FACILITY & INFRASTRUCTURE (CRITICAL - Week 1-2)

Identify 3-5 bankrupt or distressed automotive component manufacturers in Linz/Wels region of Austria with existing injection
molding and SMT capabilities, including current asking prices, equipment inventories, and facility sizes. Determine which facilities
have clean rooms, environmental controls, and power infrastructure suitable for electronics manufacturing. Research Austrian commercial
real estate market for manufacturing facilities between 5,000-20,000 m² and current lease/purchase rates in the target region.

### 2. MAGNET SUPPLY CHAIN (CRITICAL - Week 1)

Identify current Chinese NdFeB magnet suppliers willing to ship large orders (€2-3M worth) with delivery timelines, and assess 
their willingness to ship to Austrian civilian companies before potential export restrictions. Research alternative rare earth 
magnet sources including existing European stockpiles, scrap/recycling operations, and secondary markets from hard drive
manufacturers or automotive sensor producers. Investigate European ferrite magnet manufacturers with capacity to supply 100,000+ 
units monthly and their current production capabilities and lead times.

### 3. COMPONENT SOURCING (HIGH PRIORITY - Week 2-3)

Map STM32F030 microcontroller availability across European distributors including current stock levels, lead times, and bulk 
pricing for 100K+ unit orders. Identify Infineon power MOSFET models suitable for H-bridge motor drivers with European stock 
availability and pricing. Research potentiometer manufacturers outside China (Europe, Turkey, Japan, Taiwan) with specifications 
suitable for servo position sensing and their willingness to supply emergency orders. Determine PCB manufacturing capacity in 
Austria, Poland, and Czech Republic for 2-layer boards with delivery times for 50K-200K monthly production.

### 4. UKRAINIAN BATTLEFIELD DATA ACCESS (HIGH PRIORITY - Week 1-2)

Identify Ukrainian UAV engineering groups currently operating in Austria or accessible for collaboration, including their
organizational structure and contact methods. Research which specific Chinese servo models (with exact part numbers) are currently 
used in Ukrainian FPV strike drones based on public statements, procurement records, or technical documentation. Determine typical 
failure modes and failure rates of servos in Ukrainian combat operations from any available after-action reports, technical forums, 
or engineering discussions. Assess Ukrainian willingness to participate in rapid prototyping and battlefield 
testing programs with Austrian manufacturers.

### 5. WORKFORCE & LABOR MARKET (MEDIUM PRIORITY - Week 2-3)

Quantify displaced persons and asylum seekers in Linz/Wels region with manufacturing or technical backgrounds, including 
their legal work authorization status and language capabilities. Research Austrian regulations for employing refugees and
asylum seekers in defense-related manufacturing including any restrictions or expedited processes for wartime production. 
Identify recruiting agencies or NGOs working with displaced populations that could facilitate workforce development. 
Assess availability of retired Austrian automotive workers or those facing layoffs from struggling manufacturers who 
could provide training and supervision.

### 6. INJECTION MOLDING CAPACITY (HIGH PRIORITY - Week 2)

Identify European injection molding toolmakers capable of 4-6 week emergency delivery for single-cavity molds suitable 
for small servo housings and gear components. Research Turkish and Polish tooling suppliers with faster timelines and 
lower costs even if precision is reduced. Determine availability of used or refurbished injection molding machines
(8-15 ton capacity) suitable for small parts in European secondary markets. Assess costs for emergency mold modifications
and typical iteration timelines for precision plastic gear manufacturing.

### 7. GERMAN BUNDESWEHR PROCUREMENT (HIGH PRIORITY - Week 1-2)

Identify current Bundeswehr UAV procurement programs, budget allocations for 2026-2027, and contact information 
for relevant procurement officers. Research German emergency defense procurement procedures that could bypass 
normal multi-year processes for critical shortages. Determine if Bundeswehr has issued any requests for information (RFI) 
or requests for proposals (RFP) related to drone components or servo supplies. Assess German government policies on 
domestic vs. EU defense manufacturing and any preference programs for Austrian suppliers.

### 8. COMPETITIVE LANDSCAPE (MEDIUM PRIORITY - Week 3)

Identify any existing European servo manufacturers attempting to enter the military UAV market including their 
production capacity, pricing, and timeline. Research Turkish drone component manufacturers given their UAV industry 
maturity and potential partnership or competitive threat. Determine if any other EU countries have announced servo 
production programs or similar import substitution initiatives. Assess Israeli defense electronics exporters who 
might supply Europe during Asian supply chain disruptions.

### 9. REGULATORY & POLITICAL ENVIRONMENT (MEDIUM PRIORITY - Week 2-3)

Research Austrian government defense industry support programs including grants, loans, or guarantees available 
for critical defense manufacturing. Determine status of EU dual-use export control regulations and whether emergency 
wartime exemptions are being discussed. Identify Austrian political figures or ministry officials championing defense
industrial base development who could be allies. Assess likelihood and timeline for environmental regulation waivers
for defense manufacturing based on precedent or current political discussions.

### 10. TECHNICAL VALIDATION (LOW PRIORITY - Week 3-4)

Validate that Tower Pro SG90, MG90S, and Emax ES08MA servos are actually the dominant models in Ukrainian FPV 
operations through photographic evidence or procurement data. Research any open-source Ukrainian drone designs (Lyutyi/Bober)
for detailed servo specifications and integration requirements. Identify technical specifications for 
Iranian Shahed drones' control surfaces and servo requirements from analysis or intelligence reports. Determine if
simplified servo designs exist that sacrifice performance for manufacturability based on wartime production examples from history.

## OUTPUT REQUIREMENTS

Produce a structured intelligence report with executive summary highlighting critical blockers or enablers 
discovered during research. Include specific company names, contact information, pricing data, and timeline 
estimates wherever possible rather than general statements. Prioritize information that changes decision-making: 
if Austrian production is infeasible due to discovered constraints, state this clearly with evidence. Provide 
sourcing for all claims with dates of information gathering since supply chains and political situations are rapidly 
evolving. Flag any information gaps where further human intelligence gathering or direct contact is necessary.

## RESEARCH CONSTRAINTS & METHODOLOGY

Focus on publicly available information, industry databases, company websites, procurement portals, and news sources 
published after January 2024. Use German and English language sources primarily but note any critical information
available only in Ukrainian, Polish, or other languages. Prioritize recent information over historical data given 
the rapid changes in defense industrial base and supply chain situations. Where exact data is unavailable, provide informed 
estimates with explicit uncertainty ranges and reasoning. Do not engage in speculation about classified military 
capabilities or sensitive operational details.

## SUCCESS CRITERIA

The research is successful if it enables a clear GO/NO-GO decision on the Austrian servo production plan within
3-4 weeks of research completion. Critical unknowns that would delay or derail the 18-month timeline must be identified 
and quantified. Actionable next steps with specific contacts, suppliers, or partners should be provided for each major
component of the plan. The report should either increase confidence in the feasibility of wartime servo production or identify 
fatal flaws requiring major plan revision before significant capital is committed.
"""

# ============================================================================
# CONFIGURATION - CUSTOMIZE AS NEEDED
# ============================================================================

# Report configuration
REPORT_TYPE = "deep"  # Options: "research_report", "detailed_report", "deep"
REPORT_SOURCE = "web"  # Options: "web", "local", "hybrid"
# Options: Objective, Formal, Analytical, Persuasive, etc.
TONE = Tone.Analytical

# Deep research specific settings (only used if REPORT_TYPE = "deep")
DEEP_RESEARCH_CONFIG = {
    "breadth": 8,        # Number of queries per depth level (default: 4)
    "depth": 4,          # How many levels deep to research (default: 2)
    "concurrency": 3,    # Concurrent sub-queries (default: 2)
}

# ============================================================================
# ADVANCED CONFIGURATION FOR UNLIMITED DOCUMENTS WITH QDRANT
# ============================================================================
# Qdrant vector storage handles MILLIONS of documents efficiently.
# NO artificial limits needed - let Qdrant do its job!
#
# RECOMMENDED CONFIGURATION (maximum coverage with quality filtering):
# DEEP_RESEARCH_CONFIG = {
#     "breadth": 10,                        # 10 queries per level
#     "depth": 3,                           # 3 levels deep
#     "concurrency": 4,                     # 4 parallel queries
# }
# MAX_SEARCH_RESULTS_PER_QUERY = 20        # 20 URLs per search query
# MAX_CONTEXT_RESULTS_PER_QUERY = None     # NO LIMIT - store ALL in Qdrant
# CURATE_SOURCES = True                     # ✅ Enable garbage filtering
#
# → Result: ~1,110 sub-queries × 20 URLs = ~22,200 URLs searched
#           → ALL quality documents stored in Qdrant (after garbage filtering)
#           → Qdrant handles millions of documents without performance issues
#
# EXTREME COVERAGE (for comprehensive research):
# DEEP_RESEARCH_CONFIG = {
#     "breadth": 12,                        # 12 queries per level
#     "depth": 4,                           # 4 levels deep (VERY INTENSIVE!)
#     "concurrency": 5,                     # 5 parallel queries
# }
# MAX_SEARCH_RESULTS_PER_QUERY = 25        # 25 URLs per search query
# MAX_CONTEXT_RESULTS_PER_QUERY = None     # NO LIMIT - Qdrant handles it all
# CURATE_SOURCES = True                     # ✅ Enable garbage filtering
#
# → Result: ~20,700+ sub-queries × 25 URLs = ~500,000+ URLs searched
#           → ALL quality documents stored in Qdrant (garbage filtered)
#           → Semantic search across the entire corpus
#
# ⚠️  IMPORTANT NOTES:
#     - With MAX_CONTEXT_RESULTS_PER_QUERY = None, NO artificial limits
#     - Qdrant is designed for millions of documents - let it work!
#     - CURATE_SOURCES=True automatically filters out:
#       * Error pages ("Access Denied", 404, 403)
#       * Installation guides ("Windows 11 Installation")
#       * Login/registration pages
#       * Cookie consent pages
#       * Empty or very short content (<100 chars)
#     - Extreme settings require:
#       * Embedding microservice MUST be running
#       * Sufficient GPU memory (8GB+ recommended)
#       * Extended runtime (hours to days for extreme coverage)
#       * Higher API costs (more LLM calls for curation)
#       * Qdrant with sufficient disk space (GB to TB scale)
#     - Qdrant semantic search is FAST even with millions of documents
#     - NO performance penalty for storing everything - that's what vector DBs are for!
# ============================================================================

# Max results per search query (affects total URL count)
MAX_SEARCH_RESULTS_PER_QUERY = 20  # Increased from 5 to 20 for better coverage

# Max context results per query - SET TO None FOR NO LIMIT (recommended with Qdrant)
# Qdrant is designed to handle millions of documents without performance issues
# None = NO LIMIT, use ALL documents (best with Qdrant)
MAX_CONTEXT_RESULTS_PER_QUERY = None

# Enable source curation (filters out garbage content like "Access Denied", error pages)
# Set to True for better quality, False for speed
CURATE_SOURCES = True  # Enabled by default to filter garbage content

# Embedding configuration
# The script will automatically use the embedding microservice if it's running
# Make sure to start it first: ./embedding_service/start.sh
# Timeout increased to 3000 seconds (50 minutes) for large document batches
USE_EMBEDDING_MICROSERVICE = True  # Set to False to use OpenAI embeddings instead

# Output configuration
OUTPUT_DIR = "outputs"
OUTPUT_FORMAT = "md"  # Options: "md", "pdf", "docx"

# Search configuration (optional)
QUERY_DOMAINS = []  # e.g., ["example.com", "specific-site.org"]

# ============================================================================
# MAIN EXECUTION - DO NOT EDIT BELOW UNLESS YOU KNOW WHAT YOU'RE DOING
# ============================================================================


async def run_deep_research():
    """Execute deep research and save report"""

    print("=" * 80)
    print("🔬 DEEP RESEARCH AGENT")
    print("=" * 80)
    print(f"\n📋 Query Preview:")
    print("-" * 80)
    # Show first 200 chars of query
    preview = RESEARCH_QUERY[:200].strip()
    if len(RESEARCH_QUERY) > 200:
        preview += "..."
    print(preview)
    print("-" * 80)
    print(f"\n⚙️  Configuration:")
    print(f"   Report Type: {REPORT_TYPE}")
    print(f"   Report Source: {REPORT_SOURCE}")
    print(f"   Tone: {TONE.value if hasattr(TONE, 'value') else TONE}")

    if REPORT_TYPE == "deep":
        print(f"\n🔍 Deep Research Settings:")
        print(f"   Breadth: {DEEP_RESEARCH_CONFIG['breadth']} queries/level")
        print(f"   Depth: {DEEP_RESEARCH_CONFIG['depth']} levels")
        print(
            f"   Concurrency: {DEEP_RESEARCH_CONFIG['concurrency']} parallel queries")
        total_queries = sum(
            DEEP_RESEARCH_CONFIG['breadth'] ** i for i in range(1, DEEP_RESEARCH_CONFIG['depth'] + 1))
        print(f"   📊 Estimated sub-queries: ~{total_queries}")

    print(f"\n🎯 Quality Settings:")
    print(
        f"   Max Search Results: {MAX_SEARCH_RESULTS_PER_QUERY} URLs per query")
    if MAX_CONTEXT_RESULTS_PER_QUERY is None:
        print(f"   Max Context Results: ∞ UNLIMITED (Qdrant handles millions of docs)")
    else:
        print(
            f"   Max Context Results: {MAX_CONTEXT_RESULTS_PER_QUERY} documents per query")
    print(
        f"   Source Curation: {'✅ ENABLED (filters garbage content)' if CURATE_SOURCES else '❌ DISABLED (faster but lower quality)'}")

    print("\n" + "=" * 80)
    print("🚀 Starting research... This may take several minutes.")
    print("=" * 80 + "\n")

    # Set environment variables for deep research if specified
    if REPORT_TYPE == "deep":
        os.environ["DEEP_RESEARCH_BREADTH"] = str(
            DEEP_RESEARCH_CONFIG["breadth"])
        os.environ["DEEP_RESEARCH_DEPTH"] = str(DEEP_RESEARCH_CONFIG["depth"])
        os.environ["DEEP_RESEARCH_CONCURRENCY"] = str(
            DEEP_RESEARCH_CONFIG["concurrency"])

    # Set max search results per query (affects total URL count)
    os.environ["MAX_SEARCH_RESULTS_PER_QUERY"] = str(
        MAX_SEARCH_RESULTS_PER_QUERY)

    # Set max context results per query (None = unlimited for Qdrant)
    if MAX_CONTEXT_RESULTS_PER_QUERY is None:
        os.environ["MAX_CONTEXT_RESULTS_PER_QUERY"] = "0"  # 0 means unlimited
    else:
        os.environ["MAX_CONTEXT_RESULTS_PER_QUERY"] = str(
            MAX_CONTEXT_RESULTS_PER_QUERY)

    # Enable/disable source curation (garbage content filtering)
    os.environ["CURATE_SOURCES"] = "true" if CURATE_SOURCES else "false"

    # Configure embedding service
    if USE_EMBEDDING_MICROSERVICE:
        # Enable embedding microservice (assumes it's running)
        # The _try_embedding_service() function will automatically use it
        # for ANY embedding provider when EMBEDDING_SERVICE_ENABLED=true
        os.environ["EMBEDDING_SERVICE_ENABLED"] = "true"
        os.environ["EMBEDDING_SERVICE_URL"] = "http://localhost:8001"

        # CRITICAL: Set OPENAI_BASE_URL with /v1 suffix for OpenAI SDK compatibility
        # The SDK will append /embeddings, making full path: /v1/embeddings
        os.environ["OPENAI_BASE_URL"] = "http://localhost:8001/v1"

        # Use custom embedding type - will trigger _try_embedding_service()
        # The model name will be converted to openai:model format for compatibility
        os.environ["EMBEDDING"] = "custom:Snowflake/snowflake-arctic-embed-m"

        print("🔧 Using embedding microservice at http://localhost:8001")
        print("   Timeout: 3000 seconds (50 minutes) for large batches")
        print("   The microservice will be used for ALL embeddings (Memory + Qdrant)")
        print("   Model: Snowflake Arctic Embed")
    else:
        # Use default embeddings from config
        print("🔧 Using default embeddings from config (microservice disabled)")

    try:
        # Initialize researcher
        researcher = GPTResearcher(
            query=RESEARCH_QUERY,
            report_type=REPORT_TYPE,
            report_source=REPORT_SOURCE,
            tone=TONE,
            query_domains=QUERY_DOMAINS,
            verbose=True
        )

        # Conduct research
        print("\n📚 Phase 1: Conducting research...\n")
        await researcher.conduct_research()

        # Write report
        print("\n✍️  Phase 2: Writing report...\n")
        report = await researcher.write_report()

        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Create safe filename from query (first 50 chars)
        safe_query = "".join(c if c.isalnum() or c in (
            ' ', '-', '_') else '_' for c in RESEARCH_QUERY[:50])
        # Replace spaces with underscores
        safe_query = "_".join(safe_query.split())
        filename = f"{timestamp}_{safe_query}.{OUTPUT_FORMAT}"

        # Save report
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)

        # Print summary
        print("\n" + "=" * 80)
        print("✅ RESEARCH COMPLETED!")
        print("=" * 80)
        print(f"\n📄 Report saved to: {output_path}")
        print(
            f"📊 Report length: {len(report)} characters ({len(report.split())} words)")
        print(f"🔗 URLs visited: {len(researcher.visited_urls)}")
        print(f"📚 Sources collected: {len(researcher.research_sources)}")

        if hasattr(researcher, 'context'):
            print(
                f"💾 Context collected: {len(str(researcher.context))} characters")

        print("\n" + "=" * 80)
        print("🎉 SUCCESS!")
        print("=" * 80 + "\n")

        return output_path

    except KeyboardInterrupt:
        print("\n\n⚠️  Research interrupted by user (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {str(e)}")
        import traceback
        print("\n📋 Full traceback:")
        print("-" * 80)
        traceback.print_exc()
        print("-" * 80)
        sys.exit(1)


def check_prerequisites():
    """Check if all prerequisites are met"""
    issues = []

    # Check if .env file exists
    if not os.path.exists(".env"):
        issues.append("❌ .env file not found - create from .env.example")

    # Check if embedding service is enabled
    if os.getenv("EMBEDDING_SERVICE_ENABLED", "").lower() != "true":
        issues.append(
            "⚠️  EMBEDDING_SERVICE_ENABLED not set to 'true' in .env")

    # Check if embedding service is running (only if enabled)
    if os.getenv("EMBEDDING_SERVICE_ENABLED", "").lower() == "true":
        import requests
        service_url = os.getenv("EMBEDDING_SERVICE_URL",
                                "http://localhost:8001")
        try:
            response = requests.get(f"{service_url}/health", timeout=2)
            if response.status_code != 200:
                issues.append(
                    f"⚠️  Embedding service not healthy at {service_url}")
        except Exception:
            issues.append(
                f"⚠️  Embedding service not running at {service_url}")
            issues.append(f"   Start with: ./embedding_service/start.sh")

    # Check required API keys
    required_keys = []

    # Check retriever
    retriever = os.getenv("RETRIEVER", "tavily")
    if "tavily" in retriever and not os.getenv("TAVILY_API_KEY"):
        required_keys.append("TAVILY_API_KEY")
    if "google" in retriever and not os.getenv("GOOGLE_API_KEY"):
        required_keys.append("GOOGLE_API_KEY")
    if "bing" in retriever and not os.getenv("BING_API_KEY"):
        required_keys.append("BING_API_KEY")

    # Check LLM provider
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        required_keys.append("OPENAI_API_KEY or ANTHROPIC_API_KEY")

    if required_keys:
        issues.append(f"❌ Missing API keys: {', '.join(required_keys)}")

    if issues:
        print("=" * 80)
        print("⚠️  PREREQUISITE CHECKS FAILED")
        print("=" * 80)
        for issue in issues:
            print(f"  {issue}")
        print("\n💡 Fix the above issues and try again.\n")
        print("=" * 80)
        return False

    return True


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "DEEP RESEARCH AGENT v1.0" + " " * 34 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)

    # Run research
    asyncio.run(run_deep_research())

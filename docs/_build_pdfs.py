"""Generates three Bosnian PDFs for the Agro-Predict hackathon deliverable."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

DOCS_DIR = Path(__file__).resolve().parent

pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Italic", r"C:\Windows\Fonts\ariali.ttf"))
pdfmetrics.registerFont(TTFont("Arial-BoldItalic", r"C:\Windows\Fonts\arialbi.ttf"))
try:
    pdfmetrics.registerFont(TTFont("Mono", r"C:\Windows\Fonts\consola.ttf"))
    pdfmetrics.registerFont(TTFont("Mono-Bold", r"C:\Windows\Fonts\consolab.ttf"))
except Exception:
    pass

GREEN = colors.HexColor("#0A9454")
GREEN_LIGHT = colors.HexColor("#E8F7EF")
AMBER = colors.HexColor("#C27810")
DARK = colors.HexColor("#0E1214")
MUTED = colors.HexColor("#5C6A72")
BORDER = colors.HexColor("#D6DCDF")
CODE_BG = colors.HexColor("#F5F7F8")
FILE_HEADER_BG = colors.HexColor("#E1E6E9")


def styles():
    ss = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=ss["Title"],
                                fontName="Arial-Bold", fontSize=26,
                                textColor=DARK, spaceAfter=6, leading=30),
        "h1": ParagraphStyle("h1", parent=ss["Heading1"], fontName="Arial-Bold",
                             fontSize=17, textColor=GREEN, spaceBefore=18,
                             spaceAfter=8, leading=22),
        "h2": ParagraphStyle("h2", parent=ss["Heading2"], fontName="Arial-Bold",
                             fontSize=13, textColor=DARK, spaceBefore=14,
                             spaceAfter=6, leading=17),
        "h3": ParagraphStyle("h3", parent=ss["Heading3"], fontName="Arial-Bold",
                             fontSize=11, textColor=DARK, spaceBefore=10,
                             spaceAfter=4, leading=14),
        "body": ParagraphStyle("body", parent=ss["BodyText"],
                               fontName="Arial", fontSize=10.5,
                               textColor=DARK, leading=15, spaceAfter=6,
                               alignment=TA_LEFT),
        "bullet": ParagraphStyle("bullet", parent=ss["BodyText"],
                                 fontName="Arial", fontSize=10.5,
                                 textColor=DARK, leading=15,
                                 leftIndent=14, bulletIndent=0, spaceAfter=3),
        "code": ParagraphStyle("code", parent=ss["Code"],
                               fontName="Mono", fontSize=8.5,
                               textColor=DARK, leading=11.5,
                               leftIndent=10, rightIndent=10,
                               spaceBefore=0, spaceAfter=10,
                               backColor=CODE_BG,
                               borderColor=BORDER, borderWidth=0.5,
                               borderPadding=8),
        "code_attached": ParagraphStyle(
            "code_attached", parent=ss["Code"],
            fontName="Mono", fontSize=8.5,
            textColor=DARK, leading=11.5,
            leftIndent=10, rightIndent=10,
            spaceBefore=0, spaceAfter=10,
            backColor=CODE_BG,
            borderColor=BORDER, borderWidth=0.5,
            borderPadding=8),
        "file_label": ParagraphStyle(
            "file_label", parent=ss["Normal"],
            fontName="Mono-Bold", fontSize=9,
            textColor=DARK, leading=12,
            leftIndent=10, rightIndent=10,
            spaceBefore=4, spaceAfter=0,
            backColor=FILE_HEADER_BG,
            borderColor=BORDER, borderWidth=0.5,
            borderPadding=6),
        "small": ParagraphStyle("small", parent=ss["Normal"],
                                fontName="Arial", fontSize=9,
                                textColor=MUTED, leading=12),
        "cover_title": ParagraphStyle("cover_title", parent=ss["Title"],
                                      fontName="Arial-Bold", fontSize=34,
                                      textColor=DARK, leading=40, alignment=0),
        "cover_sub": ParagraphStyle("cover_sub", parent=ss["Normal"],
                                    fontName="Arial", fontSize=13,
                                    textColor=MUTED, leading=18),
        "cover_label": ParagraphStyle("cover_label", parent=ss["Normal"],
                                      fontName="Arial-Bold", fontSize=10,
                                      textColor=GREEN, leading=14),
    }


S = styles()


def hr():
    return HRFlowable(width="100%", thickness=0.6, color=BORDER,
                      spaceBefore=4, spaceAfter=10)


def bullets(items):
    return [Paragraph(f"\u2022&nbsp;&nbsp;{t}", S["bullet"]) for t in items]


def code(src, filename=None):
    """Code block using Preformatted (preserves whitespace, splits across pages).

    Returns a list of flowables. For small blocks wrap caller-side in KeepTogether
    if desired; long blocks naturally flow across page breaks.
    """
    out = []
    if filename:
        out.append(Paragraph(filename, S["file_label"]))
    out.append(Preformatted(src, S["code"]))
    return out


_KV_KEY_STYLE = ParagraphStyle(
    "kv_key", fontName="Arial-Bold", fontSize=9.5,
    textColor=DARK, leading=13)
_KV_VAL_STYLE = ParagraphStyle(
    "kv_val", fontName="Arial", fontSize=9.5,
    textColor=DARK, leading=13)
_DATA_HEAD_STYLE = ParagraphStyle(
    "data_head", fontName="Arial-Bold", fontSize=9,
    textColor=colors.white, leading=12)
_DATA_CELL_STYLE = ParagraphStyle(
    "data_cell", fontName="Arial", fontSize=9,
    textColor=DARK, leading=12)


def _wrap(cell, style):
    if hasattr(cell, "wrap"):
        return cell
    return Paragraph(str(cell), style)


def kv_table(rows, col_widths=None):
    col_widths = col_widths or [4.5 * cm, 11.5 * cm]
    wrapped = [
        [_wrap(r[0], _KV_KEY_STYLE), _wrap(r[1], _KV_VAL_STYLE)]
        for r in rows
    ]
    tbl = Table(wrapped, colWidths=col_widths)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), GREEN_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("BOX", (0, 0), (-1, -1), 0.4, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return tbl


def data_table(header, rows, col_widths=None):
    wrapped_header = [_wrap(h, _DATA_HEAD_STYLE) for h in header]
    wrapped_rows = [
        [_wrap(cell, _DATA_CELL_STYLE) for cell in r] for r in rows
    ]
    all_rows = [wrapped_header] + wrapped_rows
    tbl = Table(all_rows, colWidths=col_widths)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("BOX", (0, 0), (-1, -1), 0.4, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#FAFBFC")]),
    ]))
    return tbl


def cover_block(label, title_text, subtitle):
    return [
        Spacer(1, 4 * cm),
        Paragraph(label, S["cover_label"]),
        Spacer(1, 10),
        Paragraph(title_text, S["cover_title"]),
        Spacer(1, 16),
        Paragraph(subtitle, S["cover_sub"]),
        Spacer(1, 0.4 * cm),
        HRFlowable(width="30%", thickness=2, color=GREEN),
        Spacer(1, 0.6 * cm),
        Paragraph("Adria Future Hackathon 2026 \u00b7 Crna Gora",
                  S["cover_sub"]),
        Paragraph("Agro-Predict AI \u00b7 Zapadni Balkan",
                  S["cover_sub"]),
        Spacer(1, 6 * cm),
        Paragraph("Autor: Rudolf Petru\u0161i\u0107", S["small"]),
    ]


def add_footer(canv, doc):
    canv.saveState()
    canv.setFont("Arial", 8)
    canv.setFillColor(MUTED)
    canv.drawRightString(A4[0] - 1.8 * cm, 1.2 * cm, f"{doc.page}")
    canv.drawString(1.8 * cm, 1.2 * cm, "Agro-Predict dokumentacija")
    canv.restoreState()


def make_doc(path: Path, story):
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title=path.stem.replace("_", " ").title(),
        author="Rudolf Petru\u0161i\u0107",
    )
    doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=add_footer)
    print(f"  OK {path.name}")


# ======================================================================
# PDF 1: BACKEND ARHITEKTURA
# ======================================================================

def build_backend_pdf() -> None:
    path = DOCS_DIR / "01_Backend_arhitektura.pdf"
    s = []

    s += cover_block(
        "DOKUMENT 1",
        "Backend<br/>arhitektura",
        "Python + FastAPI servis, ML model za predvi\u0111anje mraza, i opciono GPT-4o obja\u0161njenja. "
        "Jedan REST API koji mobilna app konzumira.",
    )
    s.append(PageBreak())

    s.append(Paragraph("1. \u0160ta backend radi", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "Backend prima GPS koordinate i listu kultura od mobilne aplikacije. Povla\u010di "
        "20 godina istorijskih vremenskih podataka sa Open-Meteo, pokre\u0107e trenirani ML "
        "model za predikciju mraza, ra\u010duna optimalan datum sjetve i vra\u0107a JSON. "
        "Ako je OpenAI klju\u010d postavljen u <font face='Mono'>.env</font>, GPT-4o dodatno "
        "napi\u0161e obja\u0161njenje na bosanskom.",
        S["body"]))

    s.append(Paragraph("2. Tehnologije", S["h1"]))
    s.append(hr())
    s.append(kv_table([
        ["Jezik", "Python 3.13"],
        ["Web framework", "FastAPI 0.115 (automatski OpenAPI docs)"],
        ["ASGI server", "Uvicorn 0.32"],
        ["HTTP klijent", "httpx 0.27 (async)"],
        ["ML", "scikit-learn 1.5 (Gradient Boosting)"],
        ["Podaci", "pandas 2.2, numpy 2.1"],
        ["Serijalizacija modela", "joblib (pickle)"],
        ["Konfiguracija", "python-dotenv"],
        ["Vremenski podaci", "Open-Meteo API (besplatno, bez klju\u010da)"],
        ["LLM", "OpenAI GPT-4o / gpt-4o-mini (opciono)"],
    ]))

    s.append(Paragraph("3. Struktura foldera", S["h1"]))
    s.append(hr())
    s += code(
"""predictApp/
|-- app/
|   |-- main.py         # FastAPI aplikacija + endpoints
|   |-- config.py       # putanje, URL-ovi, konstante
|   |-- weather.py      # Open-Meteo klijent + disk cache
|   |-- model.py        # FrostModel: load, save, predict
|   |-- crops.py        # lookup tabela kultura
|   |-- predict.py      # pipeline: weather + model + crop
|   |-- explain.py      # rule-based generator objašnjenja (BS/EN)
|   `-- gpt.py          # GPT-4o integracija (opciona)
|-- data/
|   `-- crops.json      # 10 kultura i njihovi optimalni uslovi
|-- models/
|   `-- frost_model.pkl # trenirani klasifikator mraza
|-- scripts/
|   `-- train.py        # trening skripta (12 gradova, 20 godina)
|-- cache/              # disk cache za Open-Meteo odgovore
|-- .env                # API klju\u010devi (ne ide u git)
`-- requirements.txt""")

    s.append(PageBreak())
    s.append(Paragraph("4. \u0160ta se de\u0161ava na jedan /predict poziv", S["h1"]))
    s.append(hr())
    s.append(Paragraph("Redoslijed koraka kad stigne GET /predict zahtjev:", S["body"]))
    s += bullets([
        "Validira lat, lon, listu kultura. Ako ne\u0161to nije validno, vra\u0107a HTTP 400.",
        "Ako elevation nije poslat, dohvati ga sa Open-Meteo Elevation API-ja.",
        "Povla\u010di 20 godina istorijskih vremenskih podataka za tu lokaciju (kesirano na disku).",
        "Povla\u010di 14-dnevnu prognozu (nije kesirana jer se mijenja).",
        "Dodaje feature-e: dan u godini, mjesec, prosje\u010dna temp 7d/14d, minimalna temp 7d, padavine 7d.",
        "ML model (Gradient Boosting) ra\u010duna vjerovatno\u0107u mraza za svaki od narednih 14 dana.",
        "Za svaku tra\u017eenu kulturu primjenjuje se njen specifi\u010dan prag mraza iz crops.json.",
        "U window-u sjetve iz crops.json bira se dan sa najmanjim kombinovanim rizikom.",
        "Ra\u010duna se semafor (green / yellow / red) i confidence score.",
        "Generi\u0161e se rule-based obja\u0161njenje (\u010detiri do \u0161est bullet-a na BS ili EN).",
        "Ako postoji OpenAI klju\u010d, GPT dopisuje dodatno obja\u0161njenje bazirano na istim brojevima.",
        "Vra\u0107a se JSON sa kompletnom strukturom.",
    ])

    s.append(Paragraph("5. API endpoints", S["h1"]))
    s.append(hr())

    s.append(Paragraph("GET /health", S["h2"]))
    s.append(Paragraph("Provjera statusa, da li je model u\u010ditan, da li je GPT konfigurisan.",
                       S["body"]))
    s += code(
"""{
  "status": "ok",
  "model_loaded": true,
  "model_auc": 0.994,
  "gpt_configured": true,
  "gpt_model": "gpt-4o-mini"
}""")

    s.append(Paragraph("GET /crops", S["h2"]))
    s.append(Paragraph("Lista podr\u017eanih kultura sa id-em i nazivom na BS i EN.", S["body"]))
    s += code(
"""{
  "crops": [
    { "id": "corn",  "name_en": "Corn",  "name_bs": "Kukuruz" },
    { "id": "wheat", "name_en": "Wheat", "name_bs": "Pšenica" },
    ...
  ]
}""")

    s.append(Paragraph("GET /predict", S["h2"]))
    s.append(Paragraph("Query parametri:", S["body"]))
    s.append(kv_table([
        ["lat", "latituda u decimalnim stepenima (obavezno)"],
        ["lon", "longituda (obavezno)"],
        ["crop", "id kulture ili zarezom odvojena lista (npr. corn,wheat)"],
        ["elevation", "opciono, metri; ako izostavi\u0161 povu\u010di se automatski"],
        ["lang", "<font face='Mono'>bs</font> ili <font face='Mono'>en</font>"],
        ["use_gpt", "<font face='Mono'>true</font> ili <font face='Mono'>false</font> (default true)"],
        ["gpt_model", "override server modela \u2014 npr. <font face='Mono'>gpt-4o</font>"],
    ]))
    s.append(Paragraph(
        "Header <font face='Mono'>X-OpenAI-Key</font> (opciono): klijent mo\u017ee poslati "
        "svoj klju\u010d koji ima prednost nad onim iz .env-a za taj zahtjev.",
        S["body"]))

    s.append(PageBreak())
    s.append(Paragraph("Primjer odgovora (skra\u0107eno)", S["h3"]))
    s += code(
"""{
  "location": { "latitude": 43.86, "longitude": 18.41, "elevation_m": 543.0 },
  "predictions": [{
    "crop": { "id": "corn", "name_en": "Corn", "name_bs": "Kukuruz",
              "frost_tolerance": "none", "growing_days": 120 },
    "recommended_planting": {
      "date": "2026-05-04",
      "confidence": 0.98,
      "historical_frost_rate": 0.0,
      "window_start": "2026-04-15",
      "window_end": "2026-05-31"
    },
    "risk": {
      "traffic_light": "yellow",
      "label": "Moderate risk - monitor weather closely",
      "avg_frost_probability_14d": 0.17,
      "crop_frost_risk_days_14d": 4
    },
    "forecast_14d": [
      { "date": "2026-04-19", "temp_min_c": 3.8, "temp_max_c": 19.7,
        "precipitation_mm": 0.0, "frost_probability": 0.0,
        "crop_frost_risk": false }
    ],
    "confidence": { "overall": 0.88, "model_auc": 0.99 },
    "explanation": [
      "Optimalni datum sjetve za Corn: 2026-05-04.",
      "..."
    ],
    "gpt_explanation": [
      "Preporu\u010deni datum 4. maja je optimalan zbog...",
      "..."
    ],
    "gpt_model": "gpt-4o-mini"
  }],
  "gpt_enabled": true
}""")

    s.append(Paragraph("6. GPT-4o integracija", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "GPT dio je opcionalan. Brojevi (datum sjetve, vjerovatno\u0107a mraza, semafor) uvijek "
        "dolaze iz ML modela. GPT samo pretvara te brojeve u re\u010denice koje farmer razumije.",
        S["body"]))

    s.append(Paragraph("Kako se aktivira", S["h2"]))
    s += bullets([
        "U <font face='Mono'>.env</font> dodaj <font face='Mono'>OPENAI_API_KEY=sk-...</font> i po \u017eelji <font face='Mono'>OPENAI_MODEL=gpt-4o-mini</font>.",
        "Backend automatski \u0161alje GPT-u strukturiran JSON i tra\u017ei 3 do 5 bullet-a na tra\u017eenom jeziku.",
        "Ako GPT ne odgovori ili nema klju\u010da, klijent dobija samo rule-based obja\u0161njenje.",
        "Klijent mo\u017ee poslati svoj klju\u010d kroz X-OpenAI-Key header za override.",
    ])

    s.append(Paragraph("Za\u0161to klju\u010d \u017eivi na backend-u", S["h2"]))
    s += bullets([
        "Klju\u010d nije u APK-u, ne mo\u017ee se izvu\u0107i iz mobilne aplikacije.",
        "Jedno mjesto za rotaciju klju\u010da \u2014 restartuje\u0161 backend, sve klijente automatski koriste novi.",
        "Ako treba disable, samo obri\u0161i iz <font face='Mono'>.env</font> i restartuj server.",
    ])

    s.append(Paragraph("7. Cache i performanse", S["h1"]))
    s.append(hr())
    s.append(kv_table([
        ["Prvi poziv za novu lokaciju", "5 do 15 sekundi (dohvat 20 godina istorije)"],
        ["Naredni pozivi za istu lokaciju", "manje od 500 ms (iz disk cache-a)"],
        ["GPT dodatno", "1 do 3 sekunde"],
        ["Gradient Boosting predikcija", "manje od 10 ms"],
        ["Dodatna kultura u istom pozivu", "oko 50 ms"],
    ]))
    s.append(Paragraph(
        "Istorijski podaci se ke\u0161iraju trajno (istorija se ne mijenja). Prognoza se ne ke\u0161ira. "
        "Cache fajlovi su u <font face='Mono'>cache/</font> folderu, imenovani MD5 hash-om "
        "query parametara.",
        S["body"]))

    s.append(Paragraph("8. Pokretanje lokalno", S["h1"]))
    s.append(hr())
    s += code(
"""# 1. venv
cd predictApp
python -m venv .venv
.venv\\Scripts\\activate            # Windows
# source .venv/bin/activate         # Linux/Mac

# 2. dependencies
pip install -r requirements.txt

# 3. .env (kopiraj primjer i dodaj OpenAI ključ ako ga imaš)
copy .env.example .env

# 4. trening modela (2 do 5 minuta, povla\u010di podatke sa Open-Meteo)
python -m scripts.train

# 5. pokreni API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8765

# 6. provjera
curl http://localhost:8765/health
# Swagger UI: http://localhost:8765/docs""")

    s.append(Paragraph("9. Sigurnost za produkciju", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "Ovaj setup je demo. Za produkciju dodaj:",
        S["body"]))
    s += bullets([
        "CORS ograni\u010den na stvarnu domenu umjesto <font face='Mono'>*</font>.",
        "Rate limiting (npr. slowapi) da te ne DoS-uju.",
        "HTTPS kroz nginx ili caddy reverse proxy.",
        "Autentifikacija na <font face='Mono'>/predict</font> endpoint-u.",
        "OpenAI klju\u010d u dedicated secret manageru (AWS Secrets Manager, GCP Secret Manager).",
        "Logging, ali bez koordinata u plain text-u (GDPR).",
        "Redovno retreniranje modela \u2014 klima se mijenja, obrasci gube snagu.",
    ])

    make_doc(path, s)


# ======================================================================
# PDF 2: PREDIKCIJA
# ======================================================================

def build_prediction_pdf() -> None:
    path = DOCS_DIR / "02_Predikcija_podaci_i_metode.pdf"
    s = []

    s += cover_block(
        "DOKUMENT 2",
        "Predikcija:<br/>podaci i metode",
        "Kako aplikacija predvi\u0111a mraz i preporu\u010duje datum sjetve. Objasnjenje pisano "
        "za one koji nikad nisu radili sa ML-om. Od sirovih meteo podataka do konkretne "
        "preporuke.",
    )
    s.append(PageBreak())

    s.append(Paragraph("1. Problem koji rje\u0161avamo", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "Mali poljoprivrednici gube usjeve zbog kasnih mrazeva. Tradicionalan kalendar sjetve "
        "koji pro\u0111e sa djeda na unuka sve je manje pouzdan jer se klima mijenja. Ono \u0161to "
        "je bilo sigurno 2005. vi\u0161e nije danas. Na\u0161 cilj: na osnovu istorijskih podataka "
        "i trenutne prognoze, dati konkretnu preporuku \u2014 koji datum je optimalan za sjetvu, "
        "koliki je rizik, i \u0161ta raditi ako je rizik visok.",
        S["body"]))

    s.append(Paragraph("2. Odakle dolaze podaci", S["h1"]))
    s.append(hr())

    s.append(Paragraph("Open-Meteo", S["h2"]))
    s.append(Paragraph(
        "Open-Meteo je besplatan meteorolo\u0161ki servis koji agregira podatke iz dr\u017eavnih "
        "meteoro-lo\u0161kih slu\u017ebi (ECMWF, DWD, NOAA). Pokriva cijeli svijet sa 1-11 km "
        "rezolucijom. Ne tra\u017ei registraciju ni API klju\u010d \u2014 samo HTTP pozivi.",
        S["body"]))

    s.append(Paragraph("Tri endpoint-a koja koristimo", S["h2"]))
    s.append(kv_table([
        ["Archive API", "Istorijski dnevni podaci od 2006. \u2014 za trening modela i za izra\u010dun istorijske stope mraza po danu u godini."],
        ["Forecast API", "14 dnevnih prognoza \u2014 ulaz za model kad korisnik tra\u017ei predikciju."],
        ["Elevation API", "Nadmorska visina za lokaciju \u2014 koristi se kao feature."],
    ]))

    s.append(Paragraph("Koje varijable vu\u010demo", S["h2"]))
    s.append(data_table(
        ["Naziv", "Opis", "Jedinica"],
        [
            ["temperature_2m_min", "Dnevni minimum temperature na 2m visine", "\u00b0C"],
            ["temperature_2m_max", "Dnevni maximum", "\u00b0C"],
            ["temperature_2m_mean", "Dnevni prosjek", "\u00b0C"],
            ["precipitation_sum", "Ukupne dnevne padavine", "mm"],
            ["snowfall_sum", "Ukupan snijeg", "cm"],
            ["elevation", "Nadmorska visina za lokaciju", "m"],
        ],
        col_widths=[5 * cm, 9 * cm, 2 * cm]
    ))

    s.append(Paragraph("Geografska pokrivenost treninga", S["h2"]))
    s.append(Paragraph(
        "Model je treniran na podacima iz 12 gradova regiona, odabranih tako da pokriju "
        "razli\u010dite nadmorske visine, klime (mediteranska, kontinentalna, planinska) i "
        "geografske \u0161irine.",
        S["body"]))
    s.append(data_table(
        ["Grad", "Latituda", "Longituda", "Klima"],
        [
            ["Sarajevo, BiH", "43.86", "18.41", "Kontinentalna, visoravan"],
            ["Banja Luka, BiH", "44.77", "17.19", "Kontinentalna"],
            ["Mostar, BiH", "43.34", "17.81", "Mediteranska"],
            ["Podgorica, CG", "42.44", "19.26", "Mediteranska"],
            ["Nik\u0161i\u0107, CG", "42.77", "18.95", "Planinska"],
            ["Beograd, RS", "44.79", "20.45", "Kontinentalna"],
            ["Novi Sad, RS", "45.27", "19.83", "Panonska"],
            ["Zagreb, HR", "45.82", "15.98", "Kontinentalna"],
            ["Osijek, HR", "45.56", "18.70", "Panonska"],
            ["Skopje, MK", "41.99", "21.43", "Kontinentalna"],
            ["Tirana, AL", "41.33", "19.82", "Mediteranska"],
            ["Ljubljana, SI", "46.06", "14.51", "Alpska"],
        ],
        col_widths=[4.5 * cm, 3 * cm, 3 * cm, 5.5 * cm]
    ))
    s.append(Paragraph(
        "Ukupno: 12 gradova \u00d7 20 godina \u00d7 365 dana \u2248 87,600 dnevnih redova.",
        S["body"]))

    s.append(PageBreak())
    s.append(Paragraph("3. Feature engineering", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "Sirove dnevne vrijednosti ne dajemo modelu direktno. Prvo izra\u010dunamo dodatne "
        "varijable koje hvataju trend:",
        S["body"]))
    s.append(data_table(
        ["Feature", "Kako se ra\u010duna"],
        [
            ["day_of_year", "Redni broj dana u godini (1 - 366), hvata sezonalnost"],
            ["month", "Mjesec (1 - 12)"],
            ["temperature_2m_mean", "Dnevni prosjek (sirov)"],
            ["temp_mean_7d", "Prosjek dnevnih prosjeka u zadnjih 7 dana"],
            ["temp_mean_14d", "Prosjek zadnjih 14 dana (sporiji trend)"],
            ["temp_min_7d", "Minimum od minimalnih temperatura u zadnjih 7 dana"],
            ["precip_7d", "Suma padavina u zadnjih 7 dana"],
            ["elevation", "Nadmorska visina (konstantna za lokaciju)"],
            ["latitude", "Geografska \u0161irina"],
        ],
        col_widths=[4.5 * cm, 11.5 * cm]
    ))

    s.append(Paragraph("4. \u0160ta uop\u0161te radi ML model", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "Prije nego objasnimo Gradient Boosting, evo osnovne ideje \u0161ta je ML model. "
        "To je funkcija koja prima brojeve na ulazu i vra\u0107a broj na izlazu. U na\u0161em "
        "slu\u010daju:",
        S["body"]))
    s += code(
"""Ulaz (9 brojeva):           ->  Model  ->  Izlaz:
  day_of_year = 110                        vjerovatno\u0107a mraza = 0.12
  month = 4                                   (12%)
  temp_mean = 9.3
  temp_mean_7d = 8.1
  temp_mean_14d = 7.6
  temp_min_7d = 2.4
  precip_7d = 14.2
  elevation = 543
  latitude = 43.86""")
    s.append(Paragraph(
        "Pitanje je kako napraviti tu funkciju. Mogli bismo je ru\u010dno pisati (\"ako je "
        "temp_min_7d manji od 0, vjerovatno\u0107a je 80%...\"), ali takvih pravila bi bilo "
        "hiljade i ne bismo ih znali pogoditi. Umjesto toga damo ra\u010dunaru primjere iz "
        "pro\u0161losti (87,600 dana gdje znamo \u0161ta se desilo) i ka\u017eemo mu: \"nauci sam "
        "obrazac\". To u\u010denje zovemo trening.",
        S["body"]))

    s.append(Paragraph("Klasifikacija vs regresija", S["h2"]))
    s += bullets([
        "<b>Regresija</b>: izlaz je realan broj (npr. \"koja \u0107e ta\u010dno biti temperatura?\" \u2192 3.7\u00b0C).",
        "<b>Klasifikacija</b>: izlaz je kategorija \u2014 kod nas DA / NE (mraz / ne mraz).",
    ])
    s.append(Paragraph(
        "Mi radimo binarnu klasifikaciju jer nas ne zanima ta\u010dan broj stepeni, nego samo "
        "da li \u0107e biti mraza.",
        S["body"]))

    s.append(Paragraph("5. Decision tree: jedno stablo odluke", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "Najlak\u0161e \u0107e\u0161 razumjeti Gradient Boosting ako prvo razumije\u0161 jedno stablo. "
        "Decision tree je niz if-else pitanja:",
        S["body"]))
    s += code(
"""ako je temp_min_7d < -1.2:
    ako je day_of_year < 100:
        -> vjerovatno\u0107a mraza = 0.91  (zima / rano prolje\u0107e + hladno)
    ina\u010de:
        -> vjerovatno\u0107a = 0.45       (kasnije ali i dalje hladno)
ina\u010de:
    ako je elevation > 800:
        -> vjerovatno\u0107a = 0.31       (planinski, rizik ostaje)
    ina\u010de:
        -> vjerovatno\u0107a = 0.04       (nizina, topli trend)""")
    s.append(Paragraph(
        "Algoritam sam odlu\u010duje koje pitanje postaviti prvo (ono koje najbolje razdvaja "
        "podatke), na koju vrijednost testirati (npr. \"< -1.2\" a ne \"< -1.5\"), i kada "
        "prestati sa dijeljenjem.",
        S["body"]))
    s.append(Paragraph(
        "Problem: jedno stablo je obi\u010dno glupo. Ili je prekratko pa ne hvata nijanse, "
        "ili je preduga\u010dko pa pamti \u0161um iz trening podataka. Rje\u0161enje je napraviti "
        "mnogo stabala i kombinovati ih.",
        S["body"]))

    s.append(PageBreak())
    s.append(Paragraph("6. Gradient Boosting: timski rad malih stabala", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "Umjesto jednog velikog, gradimo 200 malih stabala (svako dubine 4), jedno po jedno. "
        "Svako naredno stablo u\u010di samo gdje su prethodna pogrije\u0161ila.",
        S["body"]))

    s.append(Paragraph("Analogija sa \u0161kolskim zadatkom", S["h2"]))
    s.append(Paragraph(
        "Zamisli te\u017eak ispit iz matematike. Umjesto da poku\u0161ava\u0161 sve odmah, ti\u0161e "
        "ga rje\u0161avamo sekvencijalno:",
        S["body"]))
    s += bullets([
        "U\u010denik 1 napi\u0161e svoj odgovor. Gre\u0161an za 12 poena.",
        "U\u010denik 2 ne po\u010dinje ispo\u010detka. Gleda gdje je U\u010denik 1 pogrije\u0161io i dodaje korekciju. Gre\u0161ka pada na 7.",
        "U\u010denik 3 gleda kombinaciju prva dva i popravlja ostatak. Gre\u0161ka 4.",
        "... ponavljamo 200 puta. Svaki sljede\u0107i dodaje sve manju korekciju dok ne do\u0111emo blizu ta\u010dnog rje\u0161enja.",
    ])
    s.append(Paragraph(
        "To je \"boosting\". Dio \"gradient\" u imenu zna\u010di da svaki u\u010denik matemati\u010dki "
        "zna u kom smjeru da se kre\u0107e (derivacija funkcije gre\u0161ke) da smanji gre\u0161ku "
        "\u0161to br\u017ee.",
        S["body"]))

    s.append(Paragraph("Za\u0161to ovo dobro radi", S["h2"]))
    s += bullets([
        "Svako stablo je slabo i ne mo\u017ee mnogo pogrije\u0161iti ni u jednom smjeru.",
        "Kombinacija je jaka jer se gre\u0161ke pojedinih stabala poni\u0161tavaju, a korekcije akumuliraju.",
        "Fokus se stavlja na te\u0161ke primjere \u2014 svako sljede\u0107e stablo gleda dane gdje smo do sad gre\u0161ili, ne gdje smo ve\u0107 ta\u010dni.",
    ])

    s.append(Paragraph("Hiperparametri \u2014 \u0161ta podesavamo", S["h2"]))
    s.append(data_table(
        ["Parametar", "Vrijednost", "\u0160ta radi"],
        [
            ["n_estimators", "200", "Koliko ukupno stabala u timu. Vi\u0161e = bolja ta\u010dnost ali sporiji trening i ve\u0107i rizik overfitting-a."],
            ["max_depth", "4", "Dubina svakog stabla. 4 zna\u010di \u010detiri if-else nivoa. Plitko namjerno."],
            ["learning_rate", "0.08", "Koliko svaki u\u010denik mo\u017ee da promijeni ukupni odgovor. Malo = oprezno, treba vi\u0161e stabala."],
            ["random_state", "42", "Fiksiran seed slu\u010dajnosti \u2014 svi koji treniraju sa istim podacima dobiju iste rezultate."],
            ["train/test split", "80/20", "80% za trening, 20% za test na podacima koje model nikad ne vidi."],
        ],
        col_widths=[3.5 * cm, 2.5 * cm, 10 * cm]
    ))

    s.append(Paragraph("Za\u0161to Gradient Boosting a ne ne\u0161to drugo", S["h2"]))
    s += bullets([
        "Na\u0161i podaci su tabelarni (redovi \u00d7 kolone). Gradient Boosting najbolje radi za tabelarne probleme.",
        "Imamo malo podataka (87k). Neuronske mre\u017ee treba 100 puta vi\u0161e \u2014 za manje podatke GB je bolji izbor.",
        "Brzo trenira \u2014 30 do 60 sekundi na obi\u010dnom laptopu, bez GPU-a.",
        "Interpretabilan \u2014 mo\u017eemo pogledati koji feature je najva\u017eniji.",
        "Mali fajl \u2014 serijaliziran model je oko 2 MB.",
        "Stabilan \u2014 ne zavisi kriti\u010dno od hiperparametara ni od normalizacije ulaza.",
    ])

    s.append(PageBreak())
    s.append(Paragraph("7. Overfitting: najve\u0107i problem u ML-u", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "Overfitting (\"pre-prilago\u0111avanje\") se desi kada model napamet nau\u010di trening "
        "podatke \u2014 uklju\u010duju\u0107i slu\u010dajne gre\u0161ke i \u0161um \u2014 umjesto da nau\u010di "
        "pravi obrazac.",
        S["body"]))

    s.append(Paragraph("Analogija: u\u010denik koji buba napamet", S["h2"]))
    s += bullets([
        "<b>U\u010denik A</b> razumije \u0161iri kontekst, uzrok-posljedicu, trendove. Na ispitu dobro pro\u0111e \u010dak i za pitanja koja nije direktno vidio.",
        "<b>U\u010denik B</b> je nau\u010dio napamet odgovore sa 500 probnih pitanja. Ako dobije ista pitanja \u2014 savr\u0161eno. Ako druga\u010dija iz iste oblasti \u2014 nema pojma.",
    ])
    s.append(Paragraph(
        "U\u010denik B je overfit model. Na trening podacima savr\u0161en, na novim katastrofa.",
        S["body"]))

    s.append(Paragraph("Kako overfitting izgleda u brojkama", S["h2"]))
    s.append(data_table(
        ["Tip modela", "Ta\u010dnost na trening podacima", "Ta\u010dnost na novim podacima"],
        [
            ["Nedovoljno u\u010den", "75%", "74%"],
            ["Dobro balansiran", "95%", "93%"],
            ["Overfit", "99.9%", "68%"],
        ],
        col_widths=[5 * cm, 5 * cm, 5.5 * cm]
    ))
    s.append(Paragraph(
        "Overfit model izgleda savr\u0161eno na poznatim podacima ali pada \u010dim do\u0111e "
        "ne\u0161to novo. Zato uvijek podatke dijelimo:",
        S["body"]))
    s += bullets([
        "<b>Trening set (80%)</b> \u2014 podaci na kojima model u\u010di (probna pitanja).",
        "<b>Test set (20%)</b> \u2014 podaci koje model nikad ne vidi do finalnog testa (pravi ispit).",
    ])
    s.append(Paragraph(
        "Metrike koje prijavljujemo su uvijek sa test seta, ne sa trening seta. Ina\u010de "
        "la\u017eemo i sebe i druge.",
        S["body"]))

    s.append(Paragraph("Kako \u0161titimo od overfitting-a", S["h2"]))
    s += bullets([
        "Plitka stabla (max_depth=4) \u2014 stablo ne mo\u017ee memori\u0161e pojedine primjere, samo ograni\u010den broj pravila.",
        "Mali learning_rate (0.08) \u2014 svaki u\u010denik mo\u017ee malo promijeniti odgovor. Bez dramati\u010dnih skokova.",
        "Dovoljno podataka (87k uzoraka) \u2014 model nema kapaciteta da sve napamet nau\u010di.",
        "Stratified split \u2014 u trening i test setu ima proporcionalno isto dana sa i bez mraza, ne slu\u010dajno.",
    ])

    s.append(Paragraph("8. Evaluacija: kako znamo da je model dobar", S["h1"]))
    s.append(hr())
    s.append(Paragraph("Na test setu (oko 17,500 dana) dobijamo:", S["body"]))
    s.append(kv_table([
        ["AUC (ROC)", "<b>0.994</b>"],
        ["Precision (frost=1)", "~0.96"],
        ["Recall (frost=1)", "~0.93"],
        ["F1 (frost=1)", "~0.94"],
        ["Base rate (frost=1)", "~15% dana"],
    ]))

    s.append(Paragraph("Confusion matrix: \u010detiri mogu\u0107a ishoda", S["h2"]))
    s.append(data_table(
        ["", "Stvarnost: mraz", "Stvarnost: nije mraz"],
        [
            ["Model ka\u017ee: mraz", "True Positive (dobro pogodio)", "False Positive (la\u017ena uzbuna)"],
            ["Model ka\u017ee: nema mraz", "False Negative (propustio \u2014 opasno)", "True Negative (dobro rekao da nema)"],
        ],
        col_widths=[4 * cm, 6 * cm, 6 * cm]
    ))
    s.append(Paragraph("Iz ova \u010detiri broja ra\u010dunamo sve ostale metrike.", S["body"]))

    s.append(Paragraph("Precision: kad ka\u017eem mraz, koliko \u010desto sam u pravu", S["h3"]))
    s.append(Paragraph(
        "Precision = TP / (TP + FP) = 0.96. Od svih dana za koje model ka\u017ee \"bi\u0107e mraz\", "
        "stvarno je mraz u 96% slu\u010dajeva. Ostatak su la\u017ene uzbune.",
        S["body"]))

    s.append(Paragraph("Recall: od svih stvarnih mrazeva, koliko hvatam", S["h3"]))
    s.append(Paragraph(
        "Recall = TP / (TP + FN) = 0.93. Od svih stvarno mraznih dana, model je upozorio na "
        "93%. Propu\u0161ta 7% \u2014 to su opasni propusti.",
        S["body"]))

    s.append(Paragraph("F1: balans precision i recall", S["h3"]))
    s.append(Paragraph(
        "F1 = 2 \u00d7 (precision \u00d7 recall) / (precision + recall) = 0.94. Visok je samo "
        "ako su obje metrike visoke.",
        S["body"]))

    s.append(PageBreak())
    s.append(Paragraph("AUC: najva\u017eniji broj, obja\u0161njen", S["h2"]))
    s.append(Paragraph(
        "AUC (Area Under the ROC Curve, kod nas 0.994) je broj koji ljudi iz ML oblasti "
        "najvi\u0161e pominju.",
        S["body"]))
    s.append(Paragraph(
        "Intuitivna definicija: ako nasumi\u010dno uzmemo jedan dan sa mrazom i jedan bez mraza, "
        "AUC je vjerovatno\u0107a da \u0107e model mraznom danu dati ve\u0107i score (vjerovatno\u0107u mraza) "
        "nego nemraznom.",
        S["body"]))
    s += bullets([
        "<b>AUC = 0.5</b> \u2014 model je totalno slu\u010dajan, ne razlikuje ni\u0161ta. Kao bacanje nov\u010di\u0107a.",
        "<b>AUC = 0.7</b> \u2014 model je OK, ima informaciju, ali se \u010desto gre\u0161i.",
        "<b>AUC = 0.9</b> \u2014 jako dobar model, industrijski standard za produkciju.",
        "<b>AUC = 0.99+</b> \u2014 (na\u0161) prakti\u010dno savr\u0161en za razdvajanje klasa.",
    ])
    s.append(Paragraph(
        "Za\u0161to AUC a ne puka ta\u010dnost? Jer ta\u010dnost la\u017ee kada su klase debalansirane. "
        "Primjer: ako je 85% dana bez mraza, glup model koji uvijek ka\u017ee \"nema mraza\" "
        "ima ta\u010dnost 85%. AUC bi mu bio 0.5 i jasno pokazuje da je beskoristan.",
        S["body"]))

    s.append(Paragraph("9. Iskreno o na\u0161em AUC-u 0.994", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "AUC 0.994 izgleda sumnjivo visoko. Evo \u0161ta je realno iza toga:",
        S["body"]))

    s.append(Paragraph("Problem je prirodno lak", S["h2"]))
    s.append(Paragraph(
        "Mraz se po definiciji desi kad min temp padne ispod 0\u00b0C. Mi modelu dajemo min "
        "temp zadnjih 7 dana kao feature. Model u\u010di: ako je temp_min_7d ve\u0107 bila ispod 0, "
        "vjerovatno \u0107e opet biti ispod 0. To je prirodno lako nau\u010diti iz vremenskog niza.",
        S["body"]))

    s.append(Paragraph("Potencijalni data leakage", S["h2"]))
    s.append(Paragraph(
        "Trening i test set su podjeljeni slu\u010dajno po redovima. Zna\u010di model mo\u017ee da "
        "vidi 15. april 2018. u treningu i 16. april 2018. u testu. Temperature su jako "
        "korelisane \u2014 model efektivno zna odgovor zato \u0161to je vidio susjedni dan.",
        S["body"]))
    s.append(Paragraph("Po\u0161teniji test bi bio:", S["body"]))
    s += bullets([
        "<b>Time-based split</b> \u2014 trening na 2006-2022, test na 2023-2025.",
        "<b>Location-based split</b> \u2014 trening na 10 gradova, test na 2 koja model nikad ne vidi.",
        "<b>Leave-one-year-out</b> \u2014 trenira\u0161 vi\u0161e puta, svaki put izostavljaju\u0107i drugu godinu.",
    ])
    s.append(Paragraph(
        "Za demo 0.994 je reprezentativna cifra, dovoljna da poka\u017ee da model ima signal. "
        "Za produkciju treba pro\u0161iriti sa time-based cross-validation. Realno o\u010dekivanje "
        "bi bilo AUC oko 0.92 do 0.95 \u2014 i dalje odli\u010dno, ali po\u0161tenije.",
        S["body"]))

    s.append(Paragraph("10. Od vjerovatno\u0107e mraza do datuma sjetve", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "ML model daje samo vjerovatno\u0107u mraza po danu. Od toga do preporuke treba jo\u0161 "
        "dva koraka.",
        S["body"]))

    s.append(Paragraph("A. Istorijska stopa mraza po danu u godini", S["h2"]))
    s.append(Paragraph(
        "Iz istorijskih 20 godina ra\u010dunamo, za svaki od 366 dana u godini, u kolikom "
        "procentu godina se u ovom gradu desio mraz tog dana. Rezultat je glatka krivulja "
        "koja ka\u017ee: u Sarajevu 15. aprila mraz 12% istorijski, 30. aprila 3%, 15. maja 0.5%.",
        S["body"]))
    s.append(Paragraph(
        "Ovo je bitno jer prognoza dr\u017ei samo 14 dana. Za odluke dalje u budu\u0107nost "
        "oslanjamo se na istoriju.",
        S["body"]))

    s.append(Paragraph("B. Kombinovani risk score", S["h2"]))
    s.append(Paragraph(
        "Za svaki dan u planting window-u kulture ra\u010dunamo:",
        S["body"]))
    s += code(
"""combined_risk(day) = 0.6 * forecast_frost_probability(day)
                   + 0.4 * historical_frost_rate(day_of_year)

recommended_date = argmin(combined_risk) across window days""")
    s.append(Paragraph(
        "Te\u017eine 60/40 favorizuju trenutnu prognozu kad je dostupna. Za dane van 14-dnevnog "
        "prozora koristimo samo istorijski prosjek.",
        S["body"]))

    s.append(Paragraph("C. Semafor (green / yellow / red)", S["h2"]))
    s += code(
"""risk_14d = 0.6 * avg_forecast_frost_probability
         + 0.4 * (crop_frost_risk_days / 14)

if risk_14d < 0.15:   traffic_light = "green"
elif risk_14d < 0.35: traffic_light = "yellow"
else:                 traffic_light = "red" """)

    s.append(PageBreak())
    s.append(Paragraph("11. Crop-specifi\u010dni pragovi mraza", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "Svaka kultura ima razli\u010ditu osjetljivost. crops.json tabela sadr\u017ei za svaku:",
        S["body"]))
    s += bullets([
        "<b>frost_risk_threshold_c</b> \u2014 temperatura ispod koje je rizik za tu kulturu.",
        "<b>frost_tolerance</b> \u2014 <i>none</i>, <i>low</i>, ili <i>moderate</i>.",
        "<b>planting_window_start / end</b> \u2014 tipi\u010dan po\u010detak i kraj sezone sjetve.",
        "<b>min_soil_temp_c</b> \u2014 minimalna temperatura zemlji\u0161ta za klijanje.",
        "<b>growing_days</b> \u2014 koliko traje vegetacija.",
    ])
    s.append(data_table(
        ["Kultura", "Prag mraza", "Tolerancija", "Window sjetve"],
        [
            ["Kukuruz", "2.0\u00b0C", "none", "15.04 - 31.05"],
            ["P\u0161enica ozima", "-4.0\u00b0C", "moderate", "01.10 - 15.11"],
            ["Soja", "0.0\u00b0C", "none", "20.04 - 05.06"],
            ["Je\u010dam", "-5.0\u00b0C", "moderate", "15.03 - 20.04"],
            ["Krompir", "-1.0\u00b0C", "low", "20.03 - 10.05"],
            ["Paradajz", "2.0\u00b0C", "none", "01.05 - 10.06"],
            ["Luk", "-3.0\u00b0C", "moderate", "15.03 - 30.04"],
            ["Paprika", "3.0\u00b0C", "none", "10.05 - 15.06"],
            ["Uljana repica", "-6.0\u00b0C", "moderate", "20.08 - 25.09"],
            ["Suncokret", "-1.0\u00b0C", "low", "10.04 - 20.05"],
        ],
        col_widths=[4.5 * cm, 3 * cm, 3 * cm, 5.5 * cm]
    ))

    s.append(Paragraph("12. Ograni\u010denja", S["h1"]))
    s.append(hr())
    s.append(Paragraph("\u0160ta ovaj sistem ne radi:", S["body"]))
    s += bullets([
        "Ne predvi\u0111a koli\u010dinu prinosa. Samo rizik mraza i optimalan datum. Prinos zavisi od bolesti, tipa tla, navodnjavanja.",
        "Ne koristi podatke o tlu (samo proxy kroz nadmorsku visinu). Dodavanje SoilGrids bi popravilo ta\u010dnost.",
        "Cross-validation nije po godini \u2014 realan test bi bio \"trenira\u0161 na 2006-2022, predvi\u0111a\u0161 2023-2025\".",
        "Ne modelira ekstreme (tu\u010da, olujne \u0107elije). Tu\u010dni rizik bi tra\u017eio druge izvore (radar).",
        "Globalan prag 0\u00b0C za klasifikaciju; crop-specifi\u010dne pragove primjenjujemo naknadno.",
    ])

    make_doc(path, s)


# ======================================================================
# PDF 3: REACT NATIVE INTEGRACIJA
# ======================================================================

def build_rn_integration_pdf() -> None:
    path = DOCS_DIR / "03_React_Native_integracija.pdf"
    s = []

    s += cover_block(
        "DOKUMENT 3",
        "Integracija u<br/>React Native",
        "Upustvo za spajanje Agro-Predict backend-a sa va\u0161om React Native aplikacijom. "
        "Pokrivamo Android i iOS, GPS, TypeScript tipove i gotove komponente koje mo\u017eete "
        "kopirati 1:1.",
    )
    s.append(PageBreak())

    s.append(Paragraph("Pregled", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "Backend izla\u017ee jedan HTTP endpoint (<font face='Mono'>GET /predict</font>). "
        "React Native strana treba tri stvari:",
        S["body"]))
    s += bullets([
        "Dohvatiti GPS koordinate korisnika (expo-location).",
        "Pozvati backend sa lat, lon, i listom odabranih kultura.",
        "Prikazati odgovor u ekranima (dashboard, predict, history).",
    ])
    s.append(Paragraph(
        "Kompletna integracija je ispod 200 linija koda bez UI-ja koji ve\u0107 imate. "
        "Na narednim stranicama su svi fajlovi koje treba da kopirate.",
        S["body"]))

    s.append(Paragraph("Struktura koju \u0107emo dodati", S["h2"]))
    s += code(
"""src/
|-- config.ts
|-- api/
|   |-- types.ts
|   `-- client.ts
|-- services/
|   `-- location.ts
`-- hooks/
    `-- usePrediction.ts""")

    s.append(Paragraph("Korak 1: podesavanje backend URL-a", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "Telefon ili simulator i ra\u010dunar sa backend-om moraju biti na istoj mre\u017ei. "
        "U dev modu backend sluša na laptop IP-u (npr. 192.168.1.7:8765). U produkciji \u0107e "
        "biti puna HTTPS domena.",
        S["body"]))
    s += code(
"""import { Platform } from 'react-native';

const DEV_BACKEND = Platform.select({
  ios: 'http://localhost:8765',        // iOS simulator dijeli localhost sa Mac-om
  android: 'http://10.0.2.2:8765',     // Android emulator (AVD)
  default: 'http://192.168.1.7:8765',  // pravi telefon na istoj WiFi mre\u017ei
});

export const API_BASE = __DEV__
  ? DEV_BACKEND
  : 'https://agro-predict.example.com';""",
        filename="src/config.ts")

    s.append(Paragraph(
        "Napomena: iOS simulator koristi <font face='Mono'>localhost</font>, Android emulator "
        "koristi posebnu adresu <font face='Mono'>10.0.2.2</font> koja je alias za host. "
        "Pravi ure\u0111aj koristi pravu IP adresu laptop-a (provjeri\u0161 sa <font face='Mono'>ipconfig</font> "
        "na Windows-u ili <font face='Mono'>ifconfig</font> na Mac-u).",
        S["body"]))

    s.append(Paragraph("Korak 2: Android konfiguracija", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "Android od verzije 9 (Pie) po defaultu blokira HTTP (cleartext) saobra\u0107aj. Za dev "
        "mode dodaj u AndroidManifest:",
        S["body"]))
    s += code(
"""<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />

    <application
        ...
        android:usesCleartextTraffic="true">
        <!-- ostatak aplikacije -->
    </application>
</manifest>""",
        filename="android/app/src/main/AndroidManifest.xml")
    s.append(Paragraph(
        "Za produkciju obri\u0161i <font face='Mono'>usesCleartextTraffic</font> \u2014 backend \u0107e "
        "biti na HTTPS-u.",
        S["body"]))

    s.append(PageBreak())
    s.append(Paragraph("Korak 3: iOS konfiguracija", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "iOS App Transport Security blokira HTTP po defaultu. Za dev simulator dodaj "
        "izuze\u0107e. Ne zaboravi i location permission description \u2014 bez nje iOS odbija "
        "prompt za GPS.",
        S["body"]))
    s += code(
"""<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
    <!-- ...ostali klju\u010devi u Info.plist... -->

    <!-- Location permission prompt (obavezno) -->
    <key>NSLocationWhenInUseUsageDescription</key>
    <string>Potrebna nam je va\u0161a lokacija da predvidimo rizik od mraza za va\u0161e polje.</string>

    <!-- Dev HTTP izuzece (samo za dev, obrisati prije App Store) -->
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsLocalNetworking</key>
        <true/>
        <key>NSExceptionDomains</key>
        <dict>
            <key>localhost</key>
            <dict>
                <key>NSExceptionAllowsInsecureHTTPLoads</key>
                <true/>
            </dict>
            <key>192.168.1.7</key>
            <dict>
                <key>NSExceptionAllowsInsecureHTTPLoads</key>
                <true/>
            </dict>
        </dict>
    </dict>
</dict>
</plist>""",
        filename="ios/YourApp/Info.plist")

    s.append(Paragraph("Pokretanje iOS simulatora", S["h2"]))
    s += code(
"""cd ios
pod install             # samo ako ste dodali nove native pakete
cd ..

npx expo run:ios        # Expo projekat
# ili
npx react-native run-ios    # bare React Native""")
    s.append(Paragraph(
        "Ako backend radi na istom Mac-u kao simulator, <font face='Mono'>localhost:8765</font> "
        "radi iz simulatora direktno \u2014 nema potrebe za pravim IP-em.",
        S["body"]))

    s.append(Paragraph("Korak 4: instalacija paketa", S["h1"]))
    s.append(hr())
    s.append(Paragraph("Za Expo projekat:", S["h3"]))
    s += code(
"""npx expo install expo-location
# fetch je ugra\u0111en, nema instalacije za HTTP klijent""")

    s.append(Paragraph("Za bare React Native:", S["h3"]))
    s += code(
"""npm install @react-native-community/geolocation
cd ios && pod install && cd ..
# za Android dodaj permissije u AndroidManifest (ve\u0107 ura\u0111eno u koraku 2)""")

    s.append(PageBreak())
    s.append(Paragraph("Korak 5: TypeScript tipovi", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "Svi tipovi koji odgovaraju JSON odgovoru backend-a. Kopirajte u jedan fajl i imate "
        "autocomplete odmah u cijeloj aplikaciji.",
        S["body"]))
    s += code(
"""export type TrafficLight = 'green' | 'yellow' | 'red';
export type FrostTolerance = 'none' | 'low' | 'moderate';

export interface Crop {
  id: string;
  name_en: string;
  name_bs: string;
}

export interface CropDetail extends Crop {
  frost_tolerance: FrostTolerance;
  growing_days: number;
}

export interface DailyForecast {
  date: string;                 // ISO 8601, "2026-04-19"
  temp_min_c: number;
  temp_max_c: number;
  precipitation_mm: number;
  frost_probability: number;    // 0..1
  crop_frost_risk: boolean;
}

export interface RecommendedPlanting {
  date: string | null;
  confidence: number;
  historical_frost_rate: number;
  forecast_frost_probability: number;
  window_start: string;
  window_end: string;
}

export interface Risk {
  traffic_light: TrafficLight;
  label: string;
  avg_frost_probability_14d: number;
  max_frost_probability_14d: number;
  crop_frost_risk_days_14d: number;
}

export interface Confidence {
  overall: number;
  model_auc: number;
  historical_coverage: number;
}

export interface CropPrediction {
  crop: CropDetail;
  recommended_planting: RecommendedPlanting;
  risk: Risk;
  forecast_14d: DailyForecast[];
  confidence: Confidence;
  explanation: string[];        // rule-based, uvijek prisutno
  gpt_explanation?: string[];   // samo ako je GPT aktivan na backend-u
  gpt_model?: string;
}

export interface PredictionResponse {
  location: {
    latitude: number;
    longitude: number;
    elevation_m: number;
  };
  predictions: CropPrediction[];
  gpt_enabled: boolean;
}""",
        filename="src/api/types.ts")

    s.append(PageBreak())
    s.append(Paragraph("Korak 6: API klijent", S["h1"]))
    s.append(hr())
    s += code(
"""import { API_BASE } from '../config';
import type { Crop, PredictionResponse } from './types';

// Dohvata listu kultura podr\u017eanih na backend-u.
export async function fetchCrops(): Promise<Crop[]> {
  const r = await fetch(`${API_BASE}/crops`);
  if (!r.ok) {
    throw new Error(`Crops endpoint failed with status ${r.status}`);
  }
  const data = await r.json();
  return data.crops;
}

export interface PredictParams {
  lat: number;
  lon: number;
  cropIds: string[];            // npr. ['corn', 'wheat']
  lang?: 'bs' | 'en';
  useGpt?: boolean;
  signal?: AbortSignal;
}

// Glavni poziv \u2014 tra\u017ei predikciju za lokaciju i jedan ili vi\u0161e usjeva.
export async function fetchPrediction(
  p: PredictParams
): Promise<PredictionResponse> {
  const params = new URLSearchParams({
    lat: String(p.lat),
    lon: String(p.lon),
    crop: p.cropIds.join(','),
    lang: p.lang ?? 'bs',
    use_gpt: String(p.useGpt ?? true),
  });

  const url = `${API_BASE}/predict?${params}`;
  const response = await fetch(url, { signal: p.signal });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Predict failed (${response.status}): ${errorBody}`);
  }

  return response.json();
}

// Zdravstvena provjera \u2014 korisno za provjeru pri startu aplikacije.
export async function fetchHealth(): Promise<{
  status: string;
  model_loaded: boolean;
  model_auc: number | null;
  gpt_configured: boolean;
  gpt_model: string | null;
}> {
  const r = await fetch(`${API_BASE}/health`);
  return r.json();
}""",
        filename="src/api/client.ts")

    s.append(PageBreak())
    s.append(Paragraph("Korak 7: GPS servis sa reverse geocoding-om", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "Koristimo <font face='Mono'>expo-location</font> za GPS i besplatan BigDataCloud API "
        "da pretvorimo koordinate u \u010ditljivo ime grada. Ima fallback na Sarajevo ako "
        "korisnik odbije dozvolu.",
        S["body"]))
    s += code(
"""import * as Location from 'expo-location';

export interface LocationResult {
  lat: number;
  lon: number;
  label: string;
  isFallback: boolean;
  errorMessage?: string;
}

const FALLBACK_LAT = 43.8563;
const FALLBACK_LON = 18.4131;
const FALLBACK_LABEL = 'Sarajevo, BiH';

function fallback(reason: string): LocationResult {
  return {
    lat: FALLBACK_LAT,
    lon: FALLBACK_LON,
    label: FALLBACK_LABEL,
    isFallback: true,
    errorMessage: reason,
  };
}

export async function getCurrentLocation(): Promise<LocationResult> {
  try {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') {
      return fallback('Location permission denied');
    }

    const pos = await Location.getCurrentPositionAsync({
      accuracy: Location.Accuracy.Balanced,
      timeInterval: 10000,
    });

    const name = await reverseGeocode(
      pos.coords.latitude,
      pos.coords.longitude
    );

    const fallbackLabel =
      `${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}`;

    return {
      lat: pos.coords.latitude,
      lon: pos.coords.longitude,
      label: name ?? fallbackLabel,
      isFallback: false,
    };
  } catch (e) {
    return fallback(e instanceof Error ? e.message : String(e));
  }
}

async function reverseGeocode(
  lat: number,
  lon: number
): Promise<string | null> {
  try {
    const url = `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=en`;
    const r = await fetch(url);
    if (!r.ok) return null;
    const d = await r.json();
    const name = d.city || d.locality || d.principalSubdivision;
    return name ? `${name}, ${d.countryCode}` : null;
  } catch {
    return null;
  }
}""",
        filename="src/services/location.ts")

    s.append(PageBreak())
    s.append(Paragraph("Korak 8: React hook za jednostavnu upotrebu", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "Hook koji radi loading / error / data state i automatski otka\u017eava stari fetch "
        "kad korisnik promijeni lokaciju ili listu kultura. Kopirajte i zovite gdje vam "
        "treba predikcija.",
        S["body"]))
    s += code(
"""import { useEffect, useState } from 'react';
import { fetchPrediction } from '../api/client';
import type { PredictionResponse } from '../api/types';

interface State {
  loading: boolean;
  data?: PredictionResponse;
  error?: string;
}

export function usePrediction(
  lat: number | null,
  lon: number | null,
  cropIds: string[],
  lang: 'bs' | 'en' = 'bs'
) {
  const [state, setState] = useState<State>({ loading: false });
  const [tick, setTick] = useState(0);

  useEffect(() => {
    if (lat == null || lon == null || cropIds.length === 0) {
      return;
    }

    const ac = new AbortController();
    setState({ loading: true });

    fetchPrediction({
      lat,
      lon,
      cropIds,
      lang,
      signal: ac.signal,
    })
      .then((data) => setState({ loading: false, data }))
      .catch((err) => {
        if (err.name !== 'AbortError') {
          setState({ loading: false, error: String(err) });
        }
      });

    return () => ac.abort();
  }, [lat, lon, cropIds.join(','), lang, tick]);

  return {
    ...state,
    refresh: () => setTick((t) => t + 1),
  };
}""",
        filename="src/hooks/usePrediction.ts")

    s.append(PageBreak())
    s.append(Paragraph("Korak 9: primjer ekrana", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "Minimalan Dashboard koji koristi sve iznad. U pravoj aplikaciji \u0107ete ovo zamijeniti "
        "sa va\u0161im postoje\u0107im komponentama, ali logika je ista.",
        S["body"]))
    s += code(
"""import { useEffect, useState } from 'react';
import {
  View,
  Text,
  ActivityIndicator,
  RefreshControl,
  ScrollView,
} from 'react-native';
import { getCurrentLocation, type LocationResult } from '../services/location';
import { usePrediction } from '../hooks/usePrediction';

interface Props {
  selectedCrops: string[];      // npr. ['corn', 'wheat']
}

export function DashboardScreen({ selectedCrops }: Props) {
  const [loc, setLoc] = useState<LocationResult | null>(null);

  useEffect(() => {
    getCurrentLocation().then(setLoc);
  }, []);

  const { loading, data, error, refresh } = usePrediction(
    loc?.lat ?? null,
    loc?.lon ?? null,
    selectedCrops,
    'bs'
  );

  const primary = data?.predictions[0];

  if (!loc) return <ActivityIndicator />;
  if (loading && !data) return <ActivityIndicator />;
  if (error) return <Text>Gre\u0161ka: {error}</Text>;
  if (!primary) return null;

  return (
    <ScrollView
      refreshControl={
        <RefreshControl refreshing={loading} onRefresh={refresh} />
      }
    >
      <Text>Lokacija: {loc.label}</Text>
      <Text>Preporu\u010deni datum: {primary.recommended_planting.date}</Text>
      <Text>Semafor: {primary.risk.traffic_light}</Text>

      {primary.gpt_explanation ? (
        <View>
          <Text>GPT advisor ({primary.gpt_model}):</Text>
          {primary.gpt_explanation.map((b, i) => (
            <Text key={i}>\u2022 {b}</Text>
          ))}
        </View>
      ) : (
        primary.explanation.map((b, i) => (
          <Text key={i}>\u2022 {b}</Text>
        ))
      )}
    </ScrollView>
  );
}""",
        filename="src/screens/Dashboard.tsx")

    s.append(PageBreak())
    s.append(Paragraph("Rukovanje gre\u0161kama", S["h1"]))
    s.append(hr())
    s.append(data_table(
        ["Scenarij", "HTTP status", "Postupak"],
        [
            ["Nepoznata kultura", "400", "Prika\u017ei gre\u0161ku, ponudi listu iz /crops"],
            ["Open-Meteo down", "502", "Retry sa backoff-om, fallback na zadnji cache"],
            ["Backend unreachable", "Network", "Offline poruka + zadnji payload iz AsyncStorage"],
            ["GPS odbijen", "(nije HTTP)", "Fallback koordinate + toast o dozvolama"],
            ["Rate limit", "429", "\"Previ\u0161e zahtjeva, poku\u0161ajte za 30s\""],
        ],
        col_widths=[4 * cm, 3 * cm, 9 * cm]
    ))

    s.append(Paragraph("Cache na klijentu", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "Prva predikcija za novu lokaciju traje 5 do 15 sekundi (backend povla\u010di 20 godina "
        "istorije). Zato klijent treba cache da prika\u017ee ne\u0161to odmah pri restartu:",
        S["body"]))
    s += bullets([
        "Koristi <font face='Mono'>@react-native-async-storage/async-storage</font> za zadnji payload (TTL ~1 sat).",
        "Klju\u010d cache-a: <font face='Mono'>predict:{lat2dp}:{lon2dp}:{cropsCsv}:{lang}</font>.",
        "Na mount prvo prika\u017ei cache, zatim fetch u pozadini, update UI kad stigne svje\u017e podatak.",
    ])

    s.append(Paragraph("Semafor na UI komponente", S["h1"]))
    s.append(hr())
    s.append(kv_table([
        ["green", "Zelena pozadina, check ikona, tekst \"Povoljno za sjetvu\""],
        ["yellow", "Narandzasta pozadina, warning ikona, tekst \"Pratiti prognozu\""],
        ["red", "Crvena pozadina, alert ikona, tekst \"Odgoditi sjetvu\""],
    ]))

    s.append(Paragraph("Checklist za integraciju", S["h1"]))
    s.append(hr())
    s += bullets([
        "Instalirati <font face='Mono'>expo-location</font> ili <font face='Mono'>@react-native-community/geolocation</font>.",
        "Kopirati <font face='Mono'>config.ts</font>, <font face='Mono'>api/types.ts</font>, <font face='Mono'>api/client.ts</font>, <font face='Mono'>services/location.ts</font>.",
        "Kopirati <font face='Mono'>hooks/usePrediction.ts</font>.",
        "Postaviti IP u <font face='Mono'>DEV_BACKEND</font> kad testirate na pravom ure\u0111aju.",
        "Dodati <font face='Mono'>usesCleartextTraffic=\"true\"</font> i location permissije u AndroidManifest.",
        "Dodati <font face='Mono'>NSLocationWhenInUseUsageDescription</font> i NSAppTransportSecurity izuze\u0107a u Info.plist.",
        "Wire-ovati UI komponente u <font face='Mono'>fetchPrediction</font> odgovor.",
        "Testirati na iOS simulatoru (localhost radi).",
        "Testirati na Android emulatoru (10.0.2.2 radi).",
        "Testirati na pravom ure\u0111aju (WiFi + laptop IP).",
        "Dodati AsyncStorage cache za offline.",
    ])

    s.append(Paragraph("Kontakt", S["h1"]))
    s.append(hr())
    s.append(Paragraph(
        "Backend podr\u017eava automatski generisanu OpenAPI dokumentaciju na "
        "<font face='Mono'>http://backend/docs</font> \u2014 mo\u017eete testirati pozive direktno "
        "iz browser-a. Za bilo kakvu promjenu u shemi (novi endpoint, novo polje), javite "
        "\u2014 mogu brzo pushovati izmjenu uz backward compatibility.",
        S["body"]))

    make_doc(path, s)


if __name__ == "__main__":
    print("Generating PDFs...")
    build_backend_pdf()
    build_prediction_pdf()
    build_rn_integration_pdf()
    print("\nGotovo. Fajlovi u:", DOCS_DIR)

"""
SMG LMN packet renderer (v3): real signature images + tuned Y positions.
"""
from io import BytesIO
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.utils import ImageReader

SMG_PDF_PATH = "/sessions/dazzling-cool-ramanujan/mnt/uploads/SMG - Paperwork Complete Set 2024.pdf"

# Field positions per page (PDF coords; x right, y bottom-origin; 612x792 letter)
# Y values tuned to land ON the underline (not above it).
P1 = {
    "patient_name":      (62, 623),
    "street_address":    (100, 603),
    "city_state_zip":    (121, 582),
    "insurance_carrier": (128, 560),
    "date_of_injury":    (475, 600),
    "mobile_phone":      (397, 580),
    "patient_dob":       (391, 560),
    "icd_primary":       (352, 310),  # next to "Enter Primary Diagnosis Code (Required):"
    "physician_name":    (137, 44),
    "physician_phone":   (425, 43),
    "physician_signature_date":   (411, 23),
}
P1_ITEMS_Y = {
    "lso":525,"tens":502,"ctu":479,"ltu":448,"tlso":421,"ptlso":400,"knee":383,"conductive":364
}
P1_ITEMS_CB_X = 34
P1_SIG = {
    "physician_signature": (150, 17, 175, 14),  # x, y, w, h on signature line
}

P2 = {
    "patient_name":     (98, 563),
    "patient_email":    (161, 145),
    "date":             (143, 118),
}
P2_ITEMS_Y = {"tens":481,"lso":453,"ltu":432,"ctu":412,"tlso":391,"knee":370,"other":350}
P2_ITEMS_CB_X = 74
P2_SIG = {
    "patient_signature": (142, 168, 220, 14),
}

P3 = {
    "patient_name":     (126, 654),  # I (Print Name)
    "date_of_receipt":  (276, 83),
    "patient_address":  (162, 60),
    "patient_email":    (143, 35),
    "primary_phone":    (418, 33),
}
P3_ITEMS_Y = {"tens":610,"lso":574,"ctu":555,"ltu":527,"tlso":499,"ptlso":471,"knee":448,"conductive":430}
P3_ITEMS_CB_X = 51
P3_SIG = {
    "patient_signature": (160, 102, 220, 14),
}

P4 = {
    "nf_claim_number":      (324, 554),
    "patient_name_assignor":(117, 524),
    "nf_accident_date":     (44, 443),
    "patient_signature_date":(318, 207),
    "patient_print_name":   (50, 239),
}
P4_ITEMS_Y_X = {  # (x, y) of where to draw X for each piece of equipment (X in the ___ blank)
    "tens":  (89, 66),    # TENS UNIT/SUPPLIES
    "lso":   (189, 66),   # LUMBAR BRACE (LSO)
    "ltu":   (309, 66),   # LUMBAR BRACE WITH PNEUMATIC TRACTION
    "ctu":   (54, 48),    # CERVICAL TRACTION UNIT
    "tlso":  (194, 48),   # THORACIC BRACE (TLSO)
    "ptlso": (329, 48),   # POSTURAL BRACE (TLSO)
    "knee":  (464, 48),   # KNEE BRACE
}
P4_SIG = {
    "patient_signature": (310, 237, 175, 18),
}

P5 = {
    "physician_name":   (93, 556),
    "invoice_date":     (353, 554),
    "patient_name":     (157, 521),
    "signature_date":   (376, 60),
}
P5_ITEMS_Y_X = {
    "tens":  (142, 420),
    "lso":   (242, 420),
    "ltu":   (402, 420),
    "tlso":  (92, 397),
    "ctu":   (267, 397),
    "knee":  (457, 397),
}
# Services checkboxes - SMG always-on (all three checked when packet sent)
P5_SERVICES_XY = {
    "administrative":   (40, 333),
    "instructional":    (39, 268),
    "monitoring":       (37, 200),
}
P5_SIG = {
    "patient_signature": (57, 56, 220, 18),
}

# ────────────────────────────────────────────────────────────────────
def _txt(c, fields, data, size=10):
    c.setFont("Helvetica", size)
    for k, (x, y) in fields.items():
        v = data.get(k)
        if v: c.drawString(x, y, str(v))

def _check(c, x, y):
    # Draw a larger, bolder, distinctive X mark
    c.setFont("Helvetica-Bold", 16)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(x, y, "X")

def _has(d,k): return bool(d.get(k))

def _sig_image(c, image_path, x, y, w, h):
    """Draw a signature image at the given position."""
    if image_path:
        try:
            img = ImageReader(image_path)
            c.drawImage(img, x, y, width=w, height=h, mask='auto', preserveAspectRatio=True)
            return True
        except Exception as e:
            print(f"Signature embed failed: {e}")
    return False

def _circle_word(c, x, y, w, h):
    """Draw an oval around a word at given position."""
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1.2)
    c.ellipse(x-3, y-3, x+w+3, y+h+3, stroke=1, fill=0)

def _draw_p1(c, data):
    _txt(c, P1, data)
    cb = P1_ITEMS_CB_X
    if _has(data,"has_aspen_lso"):       _check(c, cb, P1_ITEMS_Y["lso"])
    if _has(data,"has_tens"):            _check(c, cb, P1_ITEMS_Y["tens"])
    if _has(data,"has_theratrac_ctu"):   _check(c, cb, P1_ITEMS_Y["ctu"])
    if _has(data,"has_theratrac_ltu"):   _check(c, cb, P1_ITEMS_Y["ltu"])
    if _has(data,"has_aspen_tlso"):      _check(c, cb, P1_ITEMS_Y["tlso"])
    if _has(data,"has_active_ptlso"):    _check(c, cb, P1_ITEMS_Y["ptlso"])
    if _has(data,"has_knee_brace"):      _check(c, cb, P1_ITEMS_Y["knee"])
    if _has(data,"has_conductive_garment"): _check(c, cb, P1_ITEMS_Y["conductive"])
    # Sex circle disabled per Lou — was landing on the wrong word.
    # Period (X over 6/9/12 months underline)
    p = (data.get("period_months") or "").strip()
    if "12" in p:   _check(c, 501, 341)
    elif "9" in p:  _check(c, 425, 348)
    elif "6" in p:  _check(c, 348, 348)
    # Payer type
    py = (data.get("payer_type") or "").lower()
    if any(t in py for t in ["major","commercial","bcbs","blue","aetna","united","cigna","ghi","medicare"]):
        _check(c, 400, 620)
    elif any(t in py for t in ["workers","comp"]):
        _check(c, 458, 624)
    elif "fault" in py:
        _check(c, 528, 624)
    elif "auto" in py:
        _check(c, 575, 624)
    # Physician signature image
    sig = data.get("physician_signature_image")
    x,y,w,h = P1_SIG["physician_signature"]
    _sig_image(c, sig, x, y, w, h)

def _draw_p2(c, data):
    _txt(c, P2, data)
    cb = P2_ITEMS_CB_X
    if _has(data,"has_tens"):            _check(c, cb, P2_ITEMS_Y["tens"])
    if _has(data,"has_aspen_lso"):       _check(c, cb, P2_ITEMS_Y["lso"])
    if _has(data,"has_theratrac_ltu"):   _check(c, cb, P2_ITEMS_Y["ltu"])
    if _has(data,"has_theratrac_ctu"):   _check(c, cb, P2_ITEMS_Y["ctu"])
    if _has(data,"has_aspen_tlso") or _has(data,"has_active_ptlso"):
        _check(c, cb, P2_ITEMS_Y["tlso"])
    if _has(data,"has_knee_brace"):      _check(c, cb, P2_ITEMS_Y["knee"])
    sig = data.get("patient_signature_image")
    x,y,w,h = P2_SIG["patient_signature"]
    _sig_image(c, sig, x, y, w, h)

def _draw_p3(c, data):
    _txt(c, P3, data)
    cb = P3_ITEMS_CB_X
    for has_k, key in [("has_tens","tens"),("has_aspen_lso","lso"),("has_theratrac_ctu","ctu"),
                       ("has_theratrac_ltu","ltu"),("has_aspen_tlso","tlso"),("has_active_ptlso","ptlso"),
                       ("has_knee_brace","knee"),("has_conductive_garment","conductive")]:
        if _has(data, has_k): _check(c, cb, P3_ITEMS_Y[key])
    sig = data.get("patient_signature_image")
    x,y,w,h = P3_SIG["patient_signature"]
    _sig_image(c, sig, x, y, w, h)

def _draw_p4(c, data):
    _txt(c, P4, data)
    # Equipment X marks at bottom
    for has_k, key in [("has_tens","tens"),("has_aspen_lso","lso"),("has_theratrac_ltu","ltu"),
                       ("has_theratrac_ctu","ctu"),("has_knee_brace","knee")]:
        if _has(data, has_k):
            x, y = P4_ITEMS_Y_X[key]
            _check(c, x, y)
    if _has(data,"has_aspen_tlso") or _has(data,"has_active_ptlso"):
        x, y = P4_ITEMS_Y_X["tlso"]
        _check(c, x, y)
    sig = data.get("patient_signature_image")
    x,y,w,h = P4_SIG["patient_signature"]
    _sig_image(c, sig, x, y, w, h)

def _draw_p5(c, data):
    _txt(c, P5, data)
    for has_k, key in [("has_tens","tens"),("has_aspen_lso","lso"),("has_theratrac_ltu","ltu"),
                       ("has_theratrac_ctu","ctu"),("has_knee_brace","knee")]:
        if _has(data, has_k):
            x, y = P5_ITEMS_Y_X[key]
            _check(c, x, y)
    if _has(data,"has_aspen_tlso") or _has(data,"has_active_ptlso"):
        x, y = P5_ITEMS_Y_X["tlso"]
        _check(c, x, y)
    # Services X - all three checked on signed packets
    for k in ["administrative","instructional","monitoring"]:
        x, y = P5_SERVICES_XY[k]
        _check(c, x, y)
    sig = data.get("physician_signature_image")
    x,y,w,h = P5_SIG["patient_signature"]
    _sig_image(c, sig, x, y, w, h)

def build_overlay(data):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=LETTER)
    _draw_p1(c, data); c.showPage()
    _draw_p2(c, data); c.showPage()
    _draw_p3(c, data); c.showPage()
    _draw_p4(c, data); c.showPage()
    _draw_p5(c, data); c.showPage()
    c.save()
    buf.seek(0)
    return buf

def render_smg(data, out_path):
    smg = PdfReader(SMG_PDF_PATH)
    overlay = PdfReader(build_overlay(data))
    writer = PdfWriter()
    for i, smg_page in enumerate(smg.pages):
        if i < len(overlay.pages):
            smg_page.merge_page(overlay.pages[i])
        writer.add_page(smg_page)
    with open(out_path, "wb") as f:
        writer.write(f)
    return out_path

if __name__ == "__main__":
    sample = {
        "patient_name": "John A. Sample",
        "patient_dob": "04/12/1965",
        "patient_address": "123 Test Lane, Brooklyn, NY 11201",
        "street_address": "123 Test Lane",
        "city_state_zip": "Brooklyn, NY 11201",
        "patient_email": "patient@example.com",
        "primary_phone": "(555) 555-5555",
        "mobile_phone": "(555) 555-5555",
        "insurance_carrier": "Blue Cross Blue Shield",
        "policy_number": "POL-12345",
        "payer_type": "Commercial",
        "patient_sex": "Male",
        "date_of_injury": "06/15/2026",
        "date_of_receipt": "06/20/2026",
        "date": "06/20/2026",
        "invoice_date": "06/20/2026",
        "icd_primary": "M54.5",
        "period_months": "12",
        "physician_name": "Dr. Sample Smith",
        "physician_phone": "(555) 111-2222",
        "physician_signature_date": "06/20/2026",
        "patient_name_assignor": "John A. Sample",
        "patient_print_name": "John A. Sample",
        "patient_signature_date": "06/20/2026",
        "signature_date": "06/20/2026",
        "nf_claim_number": "",
        "nf_accident_date": "",
        "patient_signature_image": "/sessions/dazzling-cool-ramanujan/mnt/outputs/_smg_build/sigs/patient_sig.png",
        "physician_signature_image": "/sessions/dazzling-cool-ramanujan/mnt/outputs/_smg_build/sigs/provider_sig.png",
        "has_tens": True,
        "has_aspen_lso": False,
        "has_theratrac_ctu": False,
        "has_theratrac_ltu": False,
        "has_aspen_tlso": False,
        "has_active_ptlso": False,
        "has_knee_brace": False,
        "has_conductive_garment": False,
    }
    out = "/sessions/dazzling-cool-ramanujan/mnt/outputs/SMG_LMN_Filled_SAMPLE.pdf"
    render_smg(sample, out)
    print(f"Saved: {out}")

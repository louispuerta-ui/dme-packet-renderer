"""
SMG LMN packet PDF renderer — Flask web service for Render.com.
POST JSON -> get back a rendered PDF.
"""
import os
import sys
import json
import logging
import traceback
from io import BytesIO

from flask import Flask, request, send_file, jsonify

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def _render(data):
    import render_smg
    from pypdf import PdfReader, PdfWriter

    render_smg.SMG_PDF_PATH = os.path.join(HERE, "SMG_packet.pdf")

    sigs_dir = HERE
    if data.get("has_patient_sig") and not data.get("patient_signature_image"):
        data["patient_signature_image"] = os.path.join(sigs_dir, "patient_sig.png")
    if data.get("has_provider_sig") and not data.get("physician_signature_image"):
        data["physician_signature_image"] = os.path.join(sigs_dir, "provider_sig.png")

    overlay = PdfReader(render_smg.build_overlay(data))
    smg = PdfReader(render_smg.SMG_PDF_PATH)
    writer = PdfWriter()
    for i, page in enumerate(smg.pages):
        if i < len(overlay.pages):
            page.merge_page(overlay.pages[i])
        writer.add_page(page)
    buf = BytesIO()
    writer.write(buf)
    buf.seek(0)
    return buf


@app.route("/", methods=["GET"])
def health():
    return "dme_packet_renderer alive", 200, {"Content-Type": "text/plain"}


@app.route("/render", methods=["POST"])
@app.route("/", methods=["POST"])
def render_pdf():
    try:
        body = request.get_data(as_text=True) or "{}"
        try:
            data = json.loads(body) if body else {}
        except Exception as e:
            logger.exception("bad json")
            return jsonify({"error": f"bad json: {e}", "body_preview": body[:200]}), 400

        logger.info("rendering pdf: %d keys", len(data))
        pdf_buf = _render(data)
        order_id = data.get("order_id", "packet")
        return send_file(
            pdf_buf,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"SMG_LMN_{order_id}.pdf",
        )
    except Exception as e:
        logger.exception("render failed")
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

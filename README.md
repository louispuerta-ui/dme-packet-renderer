# DME SMG LMN Packet Renderer

Flask web service that renders the SMG LMN packet PDF.

## Endpoints

- `GET /` — health check
- `POST /` or `POST /render` — JSON in, PDF out

## Deploy on Render.com

1. Create a public or private GitHub repo, upload all files here.
2. https://render.com → New + → Web Service → Connect repo.
3. Render auto-detects `render.yaml` (Free, Python).
4. Click Deploy. Wait ~3 min.
5. Copy the `https://dme-packet-renderer.onrender.com` URL.

## Local test

```
pip install -r requirements.txt
python app.py
# in another shell
curl -X POST http://localhost:10000/ -H "Content-Type: application/json" -d '{"patient_name":"Test","has_tens":true}' -o test.pdf
```

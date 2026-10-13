"""Servidor HTTP simples para o frontend (substitui file://)."""
import http.server
import socketserver
from pathlib import Path

PORT = 5500
DIRETORIO = Path(__file__).parent / "frontend" / "web"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRETORIO), **kwargs)

    def end_headers(self):
        # CORS liberado para o backend
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, format, *args):
        # Silencia o log padrao (deixa o console limpo)
        pass

print(f"Servindo: {DIRETORIO}")
print(f"Acesse: http://localhost:{PORT}/index.html")
print("Pressione Ctrl+C para parar.")
print()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
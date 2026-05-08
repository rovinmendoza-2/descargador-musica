#!/usr/bin/env python3
"""
Servidor Flask para la interfaz de descarga de música.
Ejecutar: python app.py
Acceder: http://localhost:5000
"""

import os
import sys
from pathlib import Path

from flask import Flask, render_template, request, jsonify, send_from_directory

# Agregar la carpeta actual al path para importar descargar_musica
sys.path.insert(0, str(Path(__file__).parent))

from descargar_musica import descargar_audio

app = Flask(__name__)

# Carpeta de descargas
CARPETA_DESCARGAS = Path(__file__).resolve().parent / "descargas"
CARPETA_DESCARGAS.mkdir(exist_ok=True)


@app.route("/")
def index():
    """Serve the main interface."""
    return render_template("index.html")


@app.route("/descargar", methods=["POST"])
def descargar():
    """Handle download requests from the form."""
    data = request.get_json()
    url = data.get("url", "").strip()
    formato = data.get("formato", "m4a")

    if not url:
        return jsonify({"success": False, "error": "URL requerida"}), 400

    try:
        archivo = descargar_audio(url, CARPETA_DESCARGAS, formato)
        
        if archivo and archivo.exists():
            return jsonify({
                "success": True,
                "mensaje": f"✅ Descarga completada: {archivo.name}",
                "archivo": archivo.name
            })
        else:
            return jsonify({
                "success": False,
                "error": "No se pudo descargar el audio. Verifica la URL."
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error: {str(e)}"
        }), 500


@app.route("/descargas/<path:filename>")
def servir_descarga(filename):
    """Serve downloaded files."""
    return send_from_directory(CARPETA_DESCARGAS, filename)


if __name__ == "__main__":
    print("🚀 Servidor iniciado en http://localhost:5000")
    app.run(debug=True, port=5000)
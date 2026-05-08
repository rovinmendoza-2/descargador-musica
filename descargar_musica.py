#!/usr/bin/env python3
"""
Descargador de música desde YouTube en la más alta calidad disponible.
Soporta asignar una imagen como portada (máscara/cover) al archivo de audio.

Requisitos: FFmpeg instalado y en PATH (para yt-dlp).
Uso:
  python descargar_musica.py "https://www.youtube.com/watch?v=..."
  python descargar_musica.py "URL" --portada "ruta/imagen.jpg"
  python descargar_musica.py "URL" --portada "portada.png" --formato mp3
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("Falta instalar yt-dlp. Ejecuta: pip install -r requirements.txt")
    sys.exit(1)

try:
    from mutagen.id3 import ID3, APIC
    from mutagen.mp3 import MP3
    from mutagen.mp4 import MP4, MP4Cover
except ImportError:
    print("Falta instalar mutagen. Ejecuta: pip install -r requirements.txt")
    sys.exit(1)


# Carpeta donde se guardan las descargas (la misma carpeta del proyecto "musica")
CARPETA_DESCARGAS = Path(__file__).resolve().parent


def _ultimo_archivo_audio(carpeta: Path, formato: str) -> Path | None:
    """Devuelve el archivo de audio más reciente en carpeta con la extensión indicada."""
    ext = formato.lstrip(".")
    archivos = list(carpeta.glob(f"*.{ext}"))
    if not archivos:
        return None
    archivos.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return archivos[0]


def descargar_audio(url: str, carpeta: Path, formato: str = "m4a") -> Path | None:
    """
    Descarga solo el audio de una URL de YouTube en la mejor calidad posible.
    Devuelve la ruta del archivo descargado o None si falla.
    """
    # Mejor audio disponible: priorizar m4a (AAC), luego opus/webm
    # preferredquality 0 = mejor calidad al recodificar
    formato_selector = "bestaudio/best"
    if formato == "m4a":
        formato_selector = "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best"

    # extractor_args: probar clientes que a veces evitan 403 (YouTube PO Token/SABR)
    # Si sigue fallando, instala Deno y usa: pip install -U "yt-dlp[default]"
    opciones = {
        "format": formato_selector,
        "outtmpl": str(carpeta / "%(title)s.%(ext)s"),
        "writethumbnail": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": formato,
                "preferredquality": "0",
            },
            {"key": "FFmpegMetadata"},
            {"key": "EmbedThumbnail"},
        ],
        "quiet": False,
        "extractor_args": {
            "youtube": {
                "player_client": ["tv_embedded", "web", "android"],
            },
        },
        # Descargar scripts EJS desde GitHub si hay runtime JS (Deno/Node); ayuda a evitar 403
        "remote_components": ["ejs:github"],
    }

    with yt_dlp.YoutubeDL(opciones) as ydl:
        try:
            ydl.extract_info(url, download=True)
            return _ultimo_archivo_audio(carpeta, formato)
        except yt_dlp.utils.DownloadError as e:
            print(f"Error al descargar: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None


def aplicar_portada(ruta_audio: Path, ruta_imagen: Path) -> bool:
    """
    Aplica una imagen como portada al archivo de audio.
    Soporta MP3 (ID3/APIC) y M4A/MP4 (covr).
    """
    if not ruta_imagen.exists():
        print(f"La imagen no existe: {ruta_imagen}")
        return False

    sufijo = ruta_audio.suffix.lower()
    datos_imagen = ruta_imagen.read_bytes()

    # Detectar tipo de imagen por cabecera
    if datos_imagen[:8].startswith(b"\x89PNG"):
        mime = "image/png"
        formato_mp4 = MP4Cover.FORMAT_PNG
    else:
        mime = "image/jpeg"
        formato_mp4 = MP4Cover.FORMAT_JPEG

    try:
        if sufijo == ".mp3":
            try:
                audio = MP3(str(ruta_audio), ID3=ID3)
            except Exception:
                audio = MP3(str(ruta_audio))
            try:
                audio.add_tags()
            except Exception:
                pass
            audio.tags.add(
                APIC(
                    encoding=3,
                    mime=mime,
                    type=3,  # 3 = portada frontal
                    desc="Cover",
                    data=datos_imagen,
                )
            )
            audio.save()
        elif sufijo in (".m4a", ".mp4"):
            audio = MP4(str(ruta_audio))
            audio["covr"] = [MP4Cover(datos_imagen, formato_mp4)]
            audio.save()
        else:
            print(f"Formato no soportado para portada: {sufijo}. Use .mp3 o .m4a.")
            return False
        print(f"Portada aplicada correctamente a: {ruta_audio.name}")
        return True
    except Exception as e:
        print(f"Error al aplicar la portada: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Descarga audio de YouTube en la más alta calidad y opcionalmente le asigna una imagen como portada."
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="URL del vídeo de YouTube (o se pide por consola).",
    )
    parser.add_argument(
        "--portada", "-p",
        metavar="IMAGEN",
        help="Ruta a una imagen (JPG/PNG) para usar como portada del audio.",
    )
    parser.add_argument(
        "--formato", "-f",
        choices=["m4a", "mp3", "opus", "flac"],
        default="m4a",
        help="Formato de salida (m4a = mejor calidad por defecto, flac = sin pérdida si hay fuente).",
    )
    parser.add_argument(
        "--carpeta", "-o",
        metavar="DIR",
        default=CARPETA_DESCARGAS,
        help=f"Carpeta de descarga (por defecto: {CARPETA_DESCARGAS}).",
    )
    args = parser.parse_args()

    url = args.url
    if not url or not url.strip():
        url = input("Pega la URL de YouTube: ").strip()
    if not url:
        print("No se indicó ninguna URL.")
        sys.exit(1)

    carpeta = Path(args.carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)

    print("Descargando en la mejor calidad disponible...")
    ruta_final = descargar_audio(url, carpeta, formato=args.formato)

    if ruta_final is None:
        ruta_final = _ultimo_archivo_audio(carpeta, args.formato)
    if ruta_final is None:
        for ext in (args.formato, "m4a", "mp3", "webm", "opus"):
            ruta_final = _ultimo_archivo_audio(carpeta, ext)
            if ruta_final is not None:
                break

    if ruta_final is None or not ruta_final.exists():
        print("No se pudo obtener el archivo de audio.")
        sys.exit(1)

    print(f"Guardado: {ruta_final}")

    if args.portada:
        aplicar_portada(ruta_final, Path(args.portada))

    print("Listo.")


if __name__ == "__main__":
    main()

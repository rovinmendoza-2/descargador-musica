# Descargador de música desde YouTube (máxima calidad)

Script en Python para descargar **solo el audio** de vídeos de YouTube en la **mejor calidad disponible** y, si quieres, aplicar una **imagen como portada** al archivo.

## Requisitos

1. **Python 3.10+**
2. **FFmpeg** instalado y accesible desde la terminal (necesario para yt-dlp).  
   - Windows: [descarga FFmpeg](https://ffmpeg.org/download.html) y añade su carpeta `bin` al PATH.  
   - O con winget: `winget install ffmpeg`
3. Dependencias de Python (ver más abajo).

## Instalación

```bash
cd musica
pip install -r requirements.txt
```

## Uso

### Solo descargar audio en la mejor calidad

```bash
python descargar_musica.py "https://www.youtube.com/watch?v=XXXXXXXX"
```

O sin argumentos; el programa te pedirá la URL por consola.

### Descargar y poner una imagen como portada

```bash
python descargar_musica.py "https://www.youtube.com/watch?v=XXXXXXXX" --portada "ruta/a/mi_imagen.jpg"
```

La imagen se incrusta en los metadatos del audio (portada/album art). Soporta **JPG** y **PNG**.

### Formato de salida

Por defecto se guarda en **M4A** (calidad alta y buen soporte).

Otras opciones:

- `--formato mp3` — MP3 (máxima compatibilidad).
- `--formato flac` — FLAC si la fuente lo permite (sin pérdida).
- `--formato opus` — Opus (buena relación calidad/tamaño).

Ejemplo:

```bash
python descargar_musica.py "URL" --portada "portada.png" --formato mp3
```

### Interfaz web (guardar en carpeta **descargas**)

Puedes usar una página web en tu navegador para pegar la URL y descargar; los archivos se guardan en la subcarpeta **`descargas`** del proyecto.

1. Instala las dependencias (incluye Flask):  
   `pip install -r requirements.txt`
2. Ejecuta la aplicación:  
   `python app.py`
3. Abre en el navegador:  
   **http://127.0.0.1:5000**
4. Pega la URL de YouTube, elige el formato (M4A, MP3, etc.) y pulsa **Descargar**. El audio se guarda en la carpeta `descargas` y podrás abrirlo desde el enlace que aparece al terminar.

### Carpeta de descarga (línea de comandos)

Por defecto el script de consola guarda en la misma carpeta del proyecto (`musica`). Para otro directorio:

```bash
python descargar_musica.py "URL" --carpeta "C:\Mis descargas"
```

## Si aparece "HTTP Error 403: Forbidden" o "No supported JavaScript runtime"

YouTube a veces bloquea descargas sin un runtime JavaScript y los scripts EJS. Haz esto:

1. **Actualizar yt-dlp e instalar EJS (obligatorio):**
   ```bash
   pip install -U "yt-dlp[default]"
   ```
   Así se instala el paquete `yt-dlp-ejs` que necesita yt-dlp para YouTube.

2. **Instalar un runtime JavaScript (recomendado):**  
   [Deno](https://deno.com) es el que recomienda yt-dlp. Instálalo y déjalo en el PATH:
   - Windows (PowerShell): `irm https://deno.land/install.ps1 | iex`
   - O descarga desde: https://docs.deno.com/runtime/getting_started/installation/

   Si prefieres **Node.js** (v20+), instálalo y en la primera ejecución puedes usar:  
   `set YT_DLP_JS_RUNTIMES=node` (o añadir `--js-runtimes node` si usas yt-dlp por línea de comandos).

Sin Deno/Node, yt-dlp intentará otros clientes de YouTube; si sigue saliendo 403, instalar Deno suele solucionarlo.

## Librerías utilizadas

- **yt-dlp** — Descarga desde YouTube (y otros sitios) en la mejor calidad de audio disponible.
- **mutagen** — Gestión de metadatos y portada en archivos MP3 y M4A.

## Notas

- La “máscara de imagen” es la **portada** (cover/album art) que ves en reproductores al mostrar la pista.
- Por defecto yt-dlp puede incrustar la **miniatura del vídeo** como portada si no usas `--portada`. Si usas `--portada`, esa imagen reemplaza la miniatura.
- Si un vídeo no ofrece audio en la calidad que pides, yt-dlp usará la mejor disponible.

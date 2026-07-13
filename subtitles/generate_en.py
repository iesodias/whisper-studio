"""
Geração de legendas em inglês (VTT).
Transcreve vídeos PT → EN usando Whisper AI (task="translate").

Processamento em lote de todos os vídeos na pasta videos/.
"""

import whisper
from pathlib import Path
from tqdm import tqdm
import sys

# Configurar output imediato
sys.stdout.reconfigure(line_buffering=True)

# Imports do projeto
from shared.config import (
    AUDIO_FORMATS,
    VIDEO_FORMATS,
    TECH_PROMPT,
    VIDEOS_INPUT_DIR,
    SUBTITLES_OUTPUT_DIR,
    DEFAULT_MODEL,
)

print("Iniciando script...", flush=True)
print("Importações concluídas.", flush=True)

# Diretório com os vídeos ou áudios
input_dir = Path(VIDEOS_INPUT_DIR)

# Formatos aceitos
extensoes_validas = list(AUDIO_FORMATS) + list(VIDEO_FORMATS)

print(f"Carregando modelo '{DEFAULT_MODEL}' do Whisper (isso pode demorar se precisar baixar)...", flush=True)

# Carrega o modelo
model = whisper.load_model(DEFAULT_MODEL)
print("Modelo carregado com sucesso!", flush=True)


# Função para formatar tempo no padrão VTT
def format_time_vtt(s):
    """Formata segundos para timestamp VTT (HH:MM:SS.mmm)."""
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    ms = int((s % 1) * 1000)
    return f"{h:02}:{m:02}:{sec:02}.{ms:03}"


# Lista de arquivos válidos
arquivos = [f for f in input_dir.iterdir() if f.suffix.lower() in extensoes_validas]

if not arquivos:
    print(f"⚠️  Nenhum arquivo válido encontrado em {input_dir}/")
    sys.exit(0)

# Processa os arquivos com barra de progresso
for file_path in tqdm(arquivos, desc="Processando vídeos", unit="arquivo"):
    print(f"\n🎙️ Transcrevendo: {file_path.name}")
    
    result = model.transcribe(
        str(file_path),
        task="translate",  # Traduz para inglês automaticamente
        verbose=False,
        initial_prompt=TECH_PROMPT
    )

    # Salva no diretório de output de legendas
    output_file = Path(SUBTITLES_OUTPUT_DIR) / file_path.with_suffix(".vtt").name

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for segment in result["segments"]:
            start = format_time_vtt(segment["start"])
            end = format_time_vtt(segment["end"])
            text = segment["text"].strip()
            f.write(f"{start} --> {end}\n{text}\n\n")

    print(f"✅ Legenda salva: {output_file.name}")

print("\n🎉 Processamento completo!")

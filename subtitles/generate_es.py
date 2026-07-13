"""
Geração de legendas em espanhol (VTT).
Transcreve vídeos em PT e traduz para ES usando GoogleTranslator.

Processamento em lote de todos os vídeos na pasta videos/.
"""

import whisper
from pathlib import Path
from tqdm import tqdm
from deep_translator import GoogleTranslator

# Imports do projeto
from shared.config import (
    AUDIO_FORMATS,
    VIDEO_FORMATS,
    TECH_PROMPT,
    VIDEOS_INPUT_DIR,
    SUBTITLES_OUTPUT_DIR,
    DEFAULT_MODEL,
)

# Diretório com os vídeos ou áudios
input_dir = Path(VIDEOS_INPUT_DIR)

# Formatos aceitos
extensoes_validas = list(AUDIO_FORMATS) + list(VIDEO_FORMATS)

# Carrega o modelo
model = whisper.load_model(DEFAULT_MODEL)

# Tradutor do português para o espanhol
translator = GoogleTranslator(source="pt", target="es")


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
    exit(0)

# Processa os arquivos
for file_path in tqdm(arquivos, desc="Gerando legendas em espanhol", unit="arquivo"):
    print(f"\n🎙️ Transcrevendo em português: {file_path.name}")
    
    result = model.transcribe(
        str(file_path),
        task="transcribe",
        language="pt",
        verbose=False,
        initial_prompt=TECH_PROMPT
    )

    # Novo nome do arquivo com sufixo _es no diretório de output
    output_filename = file_path.stem + "_es.vtt"
    output_file = Path(SUBTITLES_OUTPUT_DIR) / output_filename

    # Gera legenda traduzida para espanhol
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for segment in result["segments"]:
            start = format_time_vtt(segment["start"])
            end = format_time_vtt(segment["end"])
            texto_pt = segment["text"].strip()
            texto_es = translator.translate(texto_pt)
            f.write(f"{start} --> {end}\n{texto_es}\n\n")

    print(f"✅ Legenda em espanhol salva: {output_file.name}")

print("\n🎉 Processamento completo!")

"""
Geração de legendas em espanhol (VTT).

Transcreve vídeos em português com Whisper e traduz para espanhol usando
GoogleTranslator, com processamento em lote, CLI e tratamento robusto de erros.
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING, Any

from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.config import (
    AUDIO_FORMATS,
    DEFAULT_MODEL,
    SUBTITLES_OUTPUT_DIR,
    TECH_PROMPT,
    VIDEO_FORMATS,
    VIDEOS_INPUT_DIR,
)
from shared.utils.subtitle_utils import format_time_vtt

if TYPE_CHECKING:
    from deep_translator import GoogleTranslator

ERROR_LOG_PATH = Path(SUBTITLES_OUTPUT_DIR) / "errors_es.log"
VALID_EXTENSIONS = {extension.lower() for extension in (*AUDIO_FORMATS, *VIDEO_FORMATS)}


@dataclass(slots=True)
class ProcessingStats:
    """Acumula estatísticas do processamento em lote."""

    total_found: int = 0
    skipped: int = 0
    succeeded: int = 0
    failed: int = 0
    attempted_time: float = 0.0
    failed_files: list[str] | None = None

    def __post_init__(self) -> None:
        if self.failed_files is None:
            self.failed_files = []

    @property
    def attempted(self) -> int:
        return self.succeeded + self.failed


def parse_args() -> argparse.Namespace:
    """Configura e lê os argumentos da CLI."""
    parser = argparse.ArgumentParser(
        description="Gera legendas em espanhol (VTT) para vídeos/áudios usando Whisper.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input-dir",
        default=VIDEOS_INPUT_DIR,
        help="Diretório com os vídeos/áudios de entrada.",
    )
    parser.add_argument(
        "--output-dir",
        default=SUBTITLES_OUTPUT_DIR,
        help="Diretório onde os arquivos .vtt serão salvos.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Modelo Whisper usado na transcrição.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Pula arquivos cujo _es.vtt já exista.",
    )
    parser.add_argument(
        "--pattern",
        default=None,
        help='Filtro opcional por nome, ex.: "aula-*.mp4".',
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reprocessa arquivos existentes, ignorando --skip-existing.",
    )
    return parser.parse_args()


def configure_error_logger() -> logging.Logger:
    """Configura logger exclusivo para falhas do processamento."""
    ERROR_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("generate_es")
    logger.setLevel(logging.ERROR)
    logger.handlers.clear()
    logger.propagate = False

    handler = logging.FileHandler(ERROR_LOG_PATH, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )
    logger.addHandler(handler)
    return logger


def list_input_files(input_dir: Path, pattern: str | None = None) -> list[Path]:
    """Lista arquivos válidos de entrada com filtro opcional."""
    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"Diretório de entrada inválido: {input_dir}")

    files = [
        file_path
        for file_path in sorted(input_dir.iterdir())
        if file_path.is_file() and file_path.suffix.lower() in VALID_EXTENSIONS
    ]

    if pattern:
        files = [file_path for file_path in files if fnmatch(file_path.name, pattern)]

    return files


def build_output_path(output_dir: Path, file_path: Path) -> Path:
    """Monta o caminho final do arquivo VTT em espanhol."""
    return output_dir / f"{file_path.stem}_es.vtt"


def translate_text(
    translator: "GoogleTranslator",
    text: str,
    logger: logging.Logger,
    file_path: Path,
    segment_index: int,
) -> str:
    """Traduz um segmento com fallback em caso de falha do GoogleTranslator."""
    cleaned_text = text.strip()
    if not cleaned_text:
        return ""

    try:
        return translator.translate(cleaned_text)
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Falha de tradução em %s (segmento %s). Texto original preservado. Erro: %s",
            file_path.name,
            segment_index,
            exc,
        )
        return cleaned_text


def process_video(
    file_path: Path,
    output_file: Path,
    model: Any,
    translator: "GoogleTranslator",
    logger: logging.Logger,
) -> None:
    """Processa um único vídeo/áudio e gera o arquivo VTT."""
    result = model.transcribe(
        str(file_path),
        task="transcribe",
        language="pt",
        verbose=False,
        initial_prompt=TECH_PROMPT,
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as output_handle:
        output_handle.write("WEBVTT\n\n")
        for segment_index, segment in enumerate(result["segments"], start=1):
            start = format_time_vtt(float(segment["start"]))
            end = format_time_vtt(float(segment["end"]))
            translated_text = translate_text(
                translator=translator,
                text=str(segment["text"]),
                logger=logger,
                file_path=file_path,
                segment_index=segment_index,
            )

            if translated_text:
                output_handle.write(f"{start} --> {end}\n{translated_text}\n\n")


def format_timestamp(moment: datetime) -> str:
    """Formata timestamps para exibição no terminal."""
    return moment.strftime("%Y-%m-%d %H:%M:%S")


def format_duration(seconds: float) -> str:
    """Formata duração em segundos de forma legível."""
    total_seconds = max(0, round(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{secs:02}"


def print_summary(stats: ProcessingStats, total_elapsed: float, started_at: datetime, ended_at: datetime) -> None:
    """Exibe estatísticas finais da execução."""
    attempted = stats.attempted
    average_time = stats.attempted_time / attempted if attempted else 0.0
    videos_per_hour = (attempted / total_elapsed * 3600) if total_elapsed > 0 and attempted else 0.0

    print("\n📊 Estatísticas finais")
    print(f"   Início              : {format_timestamp(started_at)}")
    print(f"   Fim                 : {format_timestamp(ended_at)}")
    print(f"   Total encontrados   : {stats.total_found}")
    print(f"   Processados         : {attempted}")
    print(f"   Sucessos            : {stats.succeeded}")
    print(f"   Falhas              : {stats.failed}")
    print(f"   Pulados             : {stats.skipped}")
    print(f"   Tempo total         : {format_duration(total_elapsed)}")
    print(f"   Tempo médio/vídeo   : {format_duration(average_time)}")
    print(f"   Velocidade média    : {videos_per_hour:.2f} vídeos/h")

    if stats.failed_files:
        print("   Arquivos com falha  :")
        for failed_file in stats.failed_files:
            print(f"      - {failed_file}")

    if stats.failed:
        print(f"\n⚠️  Consulte o log em: {ERROR_LOG_PATH}")


def main() -> int:
    """Ponto de entrada principal do script."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    args = parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger = configure_error_logger()
    started_at = datetime.now()
    overall_start = perf_counter()

    print("🚀 Iniciando geração de legendas em espanhol")
    print(f"   Início      : {format_timestamp(started_at)}")
    print(f"   Input dir   : {input_dir}")
    print(f"   Output dir  : {output_dir}")
    print(f"   Modelo      : {args.model}")
    print(f"   Pattern     : {args.pattern or 'todos'}")
    print(f"   Skip exist. : {args.skip_existing}")
    print(f"   Force       : {args.force}")
    print()

    try:
        files = list_input_files(input_dir, args.pattern)
    except Exception as exc:  # noqa: BLE001
        logger.error("Falha ao listar arquivos de entrada em %s: %s", input_dir, exc)
        print(f"❌ Erro ao listar arquivos de entrada: {exc}")
        return 1

    if not files:
        print(f"⚠️  Nenhum arquivo válido encontrado em {input_dir}/")
        return 0

    stats = ProcessingStats(total_found=len(files))

    try:
        import whisper
        from deep_translator import GoogleTranslator
    except ImportError as exc:
        logger.error("Dependência ausente ao iniciar generate_es.py: %s", exc)
        print(f"❌ Dependência ausente: {exc}")
        return 1

    print(f"🧠 Carregando modelo Whisper '{args.model}'...")
    model = whisper.load_model(args.model)
    translator = GoogleTranslator(source="pt", target="es")
    print("✅ Modelo carregado com sucesso!\n")

    progress_bar = tqdm(
        files,
        desc="Gerando legendas em espanhol",
        unit="vídeo",
        dynamic_ncols=True,
    )

    for file_path in progress_bar:
        output_file = build_output_path(output_dir, file_path)

        if output_file.exists() and args.skip_existing and not args.force:
            stats.skipped += 1
            progress_bar.write(f"⏭️  Pulando existente: {output_file.name}")
            elapsed = perf_counter() - overall_start
            processed_so_far = stats.attempted + stats.skipped
            speed = (processed_so_far / elapsed * 3600) if elapsed > 0 and processed_so_far else 0.0
            progress_bar.set_postfix({"velocidade": f"{speed:.2f} vídeos/h"})
            continue

        progress_bar.write(f"🎙️  Processando: {file_path.name}")
        file_start = perf_counter()

        try:
            process_video(
                file_path=file_path,
                output_file=output_file,
                model=model,
                translator=translator,
                logger=logger,
            )
        except Exception as exc:  # noqa: BLE001
            stats.failed += 1
            stats.failed_files.append(file_path.name)
            logger.exception("Falha ao processar %s: %s", file_path, exc)
            progress_bar.write(f"❌ Falha em {file_path.name}: {exc}")
        else:
            stats.succeeded += 1
            progress_bar.write(f"✅ Legenda salva: {output_file.name}")
        finally:
            elapsed_for_file = perf_counter() - file_start
            stats.attempted_time += elapsed_for_file
            elapsed = perf_counter() - overall_start
            processed_so_far = stats.attempted + stats.skipped
            speed = (processed_so_far / elapsed * 3600) if elapsed > 0 and processed_so_far else 0.0
            progress_bar.set_postfix({"velocidade": f"{speed:.2f} vídeos/h"})

    total_elapsed = perf_counter() - overall_start
    ended_at = datetime.now()
    print_summary(stats, total_elapsed, started_at, ended_at)

    return 0 if stats.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

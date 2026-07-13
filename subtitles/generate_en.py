"""
Geração de legendas em inglês (VTT).
Transcreve vídeos PT → EN usando Whisper AI (task="translate").

Compatível com execução sem argumentos e com processamento em lote.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import TYPE_CHECKING, Any, Sequence

from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parents[1]
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
from shared.utils.subtitle_utils import create_vtt_file, format_time_vtt

if TYPE_CHECKING:
    import whisper

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)


@dataclass
class ProcessingStats:
    total_found: int = 0
    processed: int = 0
    skipped: int = 0
    successes: int = 0
    failures: int = 0
    total_processing_seconds: float = 0.0
    failed_files: list[str] = field(default_factory=list)
    started_at: datetime | None = None
    finished_at: datetime | None = None

    @property
    def average_processing_seconds(self) -> float:
        return self.total_processing_seconds / self.processed if self.processed else 0.0


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments while preserving the original defaults."""
    parser = argparse.ArgumentParser(
        description="Gera legendas em inglês (.vtt) para vídeos usando Whisper.",
    )
    parser.add_argument(
        "--input-dir",
        default=VIDEOS_INPUT_DIR,
        help=f"Diretório com vídeos/áudios de entrada (padrão: {VIDEOS_INPUT_DIR}).",
    )
    parser.add_argument(
        "--output-dir",
        default=SUBTITLES_OUTPUT_DIR,
        help=f"Diretório de saída das legendas (padrão: {SUBTITLES_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Modelo Whisper a utilizar (padrão: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Pula arquivos cuja legenda .vtt já exista.",
    )
    parser.add_argument(
        "--pattern",
        help='Filtro opcional por nome de arquivo, ex.: "aula-*.mp4".',
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reprocessa todos os arquivos, ignorando --skip-existing.",
    )
    return parser.parse_args(argv)


def setup_error_logger(output_dir: Path) -> logging.Logger:
    """Create a file logger dedicated to per-video processing failures."""
    output_dir.mkdir(parents=True, exist_ok=True)
    error_log_path = output_dir / "errors.log"

    logger = logging.getLogger("subtitles.generate_en")
    logger.handlers.clear()
    logger.setLevel(logging.ERROR)
    logger.propagate = False

    handler = logging.FileHandler(error_log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
    return logger


def discover_input_files(
    input_dir: Path,
    valid_extensions: tuple[str, ...],
    pattern: str | None = None,
) -> list[Path]:
    """Return supported media files from the input directory, optionally filtered."""
    if not input_dir.exists():
        raise FileNotFoundError(f"Diretório de entrada não encontrado: {input_dir}")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"O caminho informado não é um diretório: {input_dir}")

    files = [
        path
        for path in sorted(input_dir.iterdir(), key=lambda candidate: candidate.name.lower())
        if path.is_file() and path.suffix.lower() in valid_extensions
    ]

    if pattern:
        files = [path for path in files if fnmatch(path.name, pattern)]

    return files


def get_output_file(file_path: Path, output_dir: Path) -> Path:
    """Build the destination VTT path for a given media file."""
    return output_dir / file_path.with_suffix(".vtt").name


def load_model(model_name: str) -> Any:
    """Load the Whisper model once for the whole batch."""
    import whisper

    print(f"Carregando modelo '{model_name}' do Whisper...", flush=True)
    model = whisper.load_model(model_name)
    print("Modelo carregado com sucesso!", flush=True)
    return model


def transcribe_to_vtt(model: Any, file_path: Path, output_file: Path) -> None:
    """Run Whisper translation and persist the resulting VTT subtitle file."""
    result = model.transcribe(
        str(file_path),
        task="translate",
        verbose=False,
        initial_prompt=TECH_PROMPT,
    )
    create_vtt_file(output_file, result["segments"])


def format_duration(seconds: float) -> str:
    """Format elapsed seconds for human-readable summaries."""
    return format_time_vtt(seconds)


def print_summary(stats: ProcessingStats) -> None:
    """Print final batch statistics."""
    total_elapsed = 0.0
    if stats.started_at and stats.finished_at:
        total_elapsed = (stats.finished_at - stats.started_at).total_seconds()

    attempted = stats.successes + stats.failures
    videos_per_hour = (attempted / total_elapsed * 3600) if total_elapsed > 0 else 0.0

    print("\n📊 Estatísticas finais")
    print(f"- Início: {stats.started_at.strftime('%Y-%m-%d %H:%M:%S') if stats.started_at else '-'}")
    print(f"- Fim: {stats.finished_at.strftime('%Y-%m-%d %H:%M:%S') if stats.finished_at else '-'}")
    print(f"- Total encontrados: {stats.total_found}")
    print(f"- Processados: {stats.processed}")
    print(f"- Pulados: {stats.skipped}")
    print(f"- Sucessos: {stats.successes}")
    print(f"- Falhas: {stats.failures}")
    print(f"- Tempo total: {format_duration(total_elapsed)}")
    print(f"- Tempo médio por vídeo: {format_duration(stats.average_processing_seconds)}")
    print(f"- Velocidade média: {videos_per_hour:.2f} vídeos/h")

    if stats.failed_files:
        print("- Arquivos com falha:")
        for failed_file in stats.failed_files:
            print(f"  • {failed_file}")


def run(argv: Sequence[str] | None = None) -> int:
    """Execute the subtitle generation workflow."""
    args = parse_args(argv)
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    valid_extensions = tuple(AUDIO_FORMATS) + tuple(VIDEO_FORMATS)

    try:
        files = discover_input_files(input_dir, valid_extensions, args.pattern)
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"❌ {exc}", flush=True)
        return 1

    if not files:
        pattern_info = f" com o padrão '{args.pattern}'" if args.pattern else ""
        print(f"⚠️  Nenhum arquivo válido encontrado em {input_dir}{pattern_info}.", flush=True)
        return 0

    pending_files = [
        file_path
        for file_path in files
        if not (args.skip_existing and get_output_file(file_path, output_dir).exists() and not args.force)
    ]

    print("Iniciando script...", flush=True)
    print(f"Entrada: {input_dir}", flush=True)
    print(f"Saída: {output_dir}", flush=True)
    print(f"Modelo: {args.model}", flush=True)
    print(f"Arquivos elegíveis: {len(files)}", flush=True)
    print(f"Arquivos a processar: {len(pending_files)}", flush=True)

    logger = setup_error_logger(output_dir)

    if not pending_files:
        print("⏭️  Todas as legendas já existem. Nada para processar.", flush=True)
        return 0

    try:
        model = load_model(args.model)
    except Exception as exc:  # pragma: no cover - depends on local Whisper setup
        logger.exception("Falha ao carregar o modelo '%s': %s", args.model, exc)
        print(f"❌ Erro ao carregar o modelo '{args.model}'. Veja {output_dir / 'errors.log'}.", flush=True)
        return 1

    stats = ProcessingStats(total_found=len(files), started_at=datetime.now())
    started_at_perf = time.perf_counter()

    print(f"🕒 Início: {stats.started_at.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)

    with tqdm(files, desc="Processando vídeos", unit="vídeo", dynamic_ncols=True) as progress_bar:
        for file_path in progress_bar:
            output_file = get_output_file(file_path, output_dir)

            if args.skip_existing and output_file.exists() and not args.force:
                stats.skipped += 1
                progress_bar.set_postfix(status="pulado")
                print(f"⏭️  Pulando existente: {output_file.name}", flush=True)
                continue

            stats.processed += 1
            file_started_at = time.perf_counter()

            try:
                print(f"\n🎙️ Transcrevendo: {file_path.name}", flush=True)
                transcribe_to_vtt(model, file_path, output_file)

                elapsed = time.perf_counter() - file_started_at
                stats.total_processing_seconds += elapsed
                stats.successes += 1

                run_elapsed = time.perf_counter() - started_at_perf
                speed = ((stats.successes + stats.failures) / run_elapsed * 3600) if run_elapsed > 0 else 0.0
                progress_bar.set_postfix(status="ok", velocidade=f"{speed:.2f}/h")
                print(f"✅ Legenda salva: {output_file.name} ({elapsed:.1f}s)", flush=True)
            except Exception as exc:  # pragma: no cover - depends on media/model runtime failures
                elapsed = time.perf_counter() - file_started_at
                stats.total_processing_seconds += elapsed
                stats.failures += 1
                stats.failed_files.append(file_path.name)

                logger.exception("Falha ao processar '%s': %s", file_path.name, exc)

                run_elapsed = time.perf_counter() - started_at_perf
                speed = ((stats.successes + stats.failures) / run_elapsed * 3600) if run_elapsed > 0 else 0.0
                progress_bar.set_postfix(status="erro", velocidade=f"{speed:.2f}/h")
                print(
                    f"❌ Falha ao processar {file_path.name}. Continuando... Veja {output_dir / 'errors.log'}.",
                    flush=True,
                )

    stats.finished_at = datetime.now()
    print(f"🕓 Fim: {stats.finished_at.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print_summary(stats)

    if stats.failures:
        print(f"\n⚠️  Processamento concluído com falhas. Consulte {output_dir / 'errors.log'}.", flush=True)
        return 1

    print("\n🎉 Processamento completo!", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())

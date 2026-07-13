"""
Subtitle utility helpers for generating WebVTT caption files.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from os import PathLike
from pathlib import Path
from typing import Any


def format_time_vtt(s: float) -> str:
    """
    Convert a time value in seconds to WebVTT timestamp format.

    WebVTT timestamps use the ``HH:MM:SS.mmm`` format, where milliseconds are
    always zero-padded to three digits. Negative values are clamped to zero to
    avoid producing invalid subtitle timestamps.

    Args:
        s: Time in seconds. Integers and floats are accepted.

    Returns:
        str: Timestamp formatted as ``HH:MM:SS.mmm``.

    Raises:
        TypeError: If ``s`` is not a numeric value.
        ValueError: If ``s`` is NaN or infinite.

    Examples:
        >>> format_time_vtt(65.5)
        '00:01:05.500'
        >>> format_time_vtt(-3)
        '00:00:00.000'
    """
    if not isinstance(s, (int, float)):
        raise TypeError("Time value must be numeric.")

    if not math.isfinite(s):
        raise ValueError("Time value must be finite.")

    total_milliseconds = max(0, round(float(s) * 1000))
    total_seconds, milliseconds = divmod(total_milliseconds, 1000)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"


def create_vtt_file(
    output_path: str | PathLike[str],
    segments: Sequence[dict[str, Any]],
) -> Path:
    """
    Create a complete WebVTT subtitle file from Whisper segments.

    Each segment is expected to provide ``start``, ``end`` and ``text`` keys.
    Empty or whitespace-only texts are ignored. Negative start and end times are
    normalized to zero, and end times earlier than start times are adjusted to
    match the segment start so the generated file remains valid.

    Args:
        output_path: Destination path for the generated ``.vtt`` file.
        segments: Ordered Whisper segments containing ``start``, ``end`` and
            ``text`` fields.

    Returns:
        Path: The full path to the generated VTT file.

    Raises:
        TypeError: If ``segments`` is not a sequence of dictionaries.
        KeyError: If a segment does not contain one of the required keys.
        ValueError: If a segment contains invalid numeric timestamps.

    Examples:
        >>> create_vtt_file(
        ...     'subtitles/output.vtt',
        ...     [{'start': 0.0, 'end': 2.5, 'text': 'Olá mundo'}],
        ... )
        PosixPath('subtitles/output.vtt')
    """
    if not isinstance(segments, Sequence):
        raise TypeError("Segments must be provided as a sequence.")

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    lines = ["WEBVTT", ""]

    for index, segment in enumerate(segments, start=1):
        if not isinstance(segment, dict):
            raise TypeError("Each segment must be a dictionary.")

        start = segment["start"]
        end = segment["end"]
        text = str(segment["text"]).strip()

        if not text:
            continue

        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            raise TypeError("Segment start and end times must be numeric.")

        if not math.isfinite(start) or not math.isfinite(end):
            raise ValueError("Segment start and end times must be finite.")

        normalized_start = max(0.0, float(start))
        normalized_end = max(normalized_start, float(end))

        lines.extend(
            [
                str(index),
                f"{format_time_vtt(normalized_start)} --> {format_time_vtt(normalized_end)}",
                text,
                "",
            ]
        )

    destination.write_text("\n".join(lines), encoding="utf-8")
    return destination


# Example usage:
# whisper_segments = [
#     {"start": 0.0, "end": 2.4, "text": "Olá, mundo!"},
#     {"start": 2.5, "end": 5.0, "text": "Este é um arquivo VTT."},
# ]
# create_vtt_file("subtitles/output.vtt", whisper_segments)

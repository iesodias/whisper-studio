"""
File Type Detection Module for Audio/Video Transcription System.

This module provides robust file type detection functionality for identifying
and validating audio and video files before processing. It supports multiple
formats and provides comprehensive error handling.

Author: Audio/Video Transcription System
Created: 2025-10-09
"""

from pathlib import Path
from typing import Literal


# Supported file formats
AUDIO_FORMATS = ('.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac', '.wma', '.opus')
VIDEO_FORMATS = ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v')


def get_file_type(file_path: str) -> Literal['audio', 'video']:
    """
    Detect whether file is audio or video and validate it exists.

    This function performs comprehensive file validation including:
    - File existence check
    - File vs directory verification
    - Extension-based format detection
    - Support for case-insensitive extensions

    Args:
        file_path: Path to the input media file (absolute or relative)

    Returns:
        str: Either 'audio' or 'video' indicating the file type

    Raises:
        FileNotFoundError: If the specified file does not exist
        ValueError: If the path is not a file or format is not supported

    Examples:
        >>> get_file_type('video.mp4')
        'video'

        >>> get_file_type('audio.mp3')
        'audio'

        >>> get_file_type('VIDEO.MP4')  # Case insensitive
        'video'

    Note:
        Supported audio formats: mp3, wav, m4a, flac, ogg, aac, wma, opus
        Supported video formats: mp4, mov, avi, mkv, webm, flv, wmv, m4v
    """
    path = Path(file_path)

    # Check if file exists
    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}\n"
            f"Please verify the file path and try again."
        )

    # Check if it's a file (not directory)
    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {file_path}\n"
            f"Expected a media file, but got a directory or special file."
        )

    # Get extension in lowercase for case-insensitive matching
    extension = path.suffix.lower()

    # Validate extension is not empty
    if not extension:
        raise ValueError(
            f"File has no extension: {file_path}\n"
            f"Unable to determine file type. Please use a file with a proper extension."
        )

    # Detect file type based on extension
    if extension in AUDIO_FORMATS:
        return "audio"
    elif extension in VIDEO_FORMATS:
        return "video"
    else:
        # Generate helpful error message with all supported formats
        audio_formats_str = ', '.join(AUDIO_FORMATS)
        video_formats_str = ', '.join(VIDEO_FORMATS)
        raise ValueError(
            f"Unsupported file format: {extension}\n"
            f"Supported audio formats: {audio_formats_str}\n"
            f"Supported video formats: {video_formats_str}"
        )


def is_audio_file(file_path: str) -> bool:
    """
    Check if a file is an audio file.

    Args:
        file_path: Path to the file to check

    Returns:
        bool: True if file is audio, False otherwise

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the path is not a valid file
    """
    return get_file_type(file_path) == "audio"


def is_video_file(file_path: str) -> bool:
    """
    Check if a file is a video file.

    Args:
        file_path: Path to the file to check

    Returns:
        bool: True if file is video, False otherwise

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the path is not a valid file
    """
    return get_file_type(file_path) == "video"


def validate_media_file(file_path: str, expected_type: Literal['audio', 'video', 'any'] = 'any') -> bool:
    """
    Validate that a file exists and matches the expected media type.

    Args:
        file_path: Path to the file to validate
        expected_type: Expected file type ('audio', 'video', or 'any')

    Returns:
        bool: True if file is valid and matches expected type

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If file doesn't match expected type or is invalid

    Examples:
        >>> validate_media_file('video.mp4', 'video')
        True

        >>> validate_media_file('audio.mp3', 'video')
        ValueError: Expected video file but got audio
    """
    file_type = get_file_type(file_path)

    if expected_type == 'any':
        return True

    if file_type != expected_type:
        raise ValueError(
            f"Expected {expected_type} file but got {file_type}: {file_path}"
        )

    return True


def get_all_supported_formats() -> dict:
    """
    Get a dictionary of all supported formats.

    Returns:
        dict: Dictionary with 'audio' and 'video' keys containing format tuples
    """
    return {
        'audio': AUDIO_FORMATS,
        'video': VIDEO_FORMATS
    }

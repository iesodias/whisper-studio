#!/usr/bin/env python3
"""
Test suite for file type detection functionality.

This script tests the get_file_type() function with various scenarios
to ensure robust file type detection and validation.
"""

import os
import sys
from pathlib import Path
from typing import Tuple, List

# Import the function to test
from shared.utils.file_detector import get_file_type, AUDIO_FORMATS, VIDEO_FORMATS


def create_test_file(filename: str) -> Path:
    """Create a temporary test file."""
    path = Path(filename)
    path.touch()
    return path


def cleanup_test_file(path: Path) -> None:
    """Remove temporary test file."""
    if path.exists():
        path.unlink()


def run_test(
    test_name: str,
    test_func,
    expected_result=None,
    expected_exception=None
) -> Tuple[bool, str]:
    """
    Run a single test case.

    Args:
        test_name: Name of the test
        test_func: Function to execute
        expected_result: Expected return value (for success cases)
        expected_exception: Expected exception type (for error cases)

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        result = test_func()
        if expected_exception:
            return False, f"Expected {expected_exception.__name__} but got result: {result}"
        if expected_result is not None and result != expected_result:
            return False, f"Expected '{expected_result}' but got '{result}'"
        return True, f"Returned: {result}"
    except Exception as e:
        if expected_exception and isinstance(e, expected_exception):
            return True, f"Correctly raised {type(e).__name__}: {str(e).split(chr(10))[0]}"
        return False, f"Unexpected error: {type(e).__name__}: {str(e)}"


def main():
    """Run all tests."""
    print("=" * 70)
    print("FILE TYPE DETECTION - TEST SUITE")
    print("=" * 70)
    print()

    test_results: List[Tuple[str, bool, str]] = []

    # Test 1: Valid video file (existing)
    print("Test 1: Valid Video File (MP4) - Existing")
    print("-" * 70)
    success, msg = run_test(
        "Valid MP4 file",
        lambda: get_file_type("estudo.mp4"),
        expected_result="video"
    )
    test_results.append(("Valid MP4 file", success, msg))
    print(f"Status: {'PASS' if success else 'FAIL'}")
    print(f"Result: {msg}")
    print()

    # Test 2: Valid audio file (create temporary)
    print("Test 2: Valid Audio File (WAV) - Temporary")
    print("-" * 70)
    test_audio = create_test_file("test_audio.wav")
    success, msg = run_test(
        "Valid WAV file",
        lambda: get_file_type(str(test_audio)),
        expected_result="audio"
    )
    test_results.append(("Valid WAV file", success, msg))
    print(f"Status: {'PASS' if success else 'FAIL'}")
    print(f"Result: {msg}")
    cleanup_test_file(test_audio)
    print()

    # Test 3: Valid audio file (MP3)
    print("Test 3: Valid Audio File (MP3)")
    print("-" * 70)
    test_mp3 = create_test_file("test_audio.mp3")
    success, msg = run_test(
        "Valid MP3 file",
        lambda: get_file_type(str(test_mp3)),
        expected_result="audio"
    )
    test_results.append(("Valid MP3 file", success, msg))
    print(f"Status: {'PASS' if success else 'FAIL'}")
    print(f"Result: {msg}")
    cleanup_test_file(test_mp3)
    print()

    # Test 4: Case insensitivity - uppercase extension
    print("Test 4: Case Insensitivity - Uppercase Extension")
    print("-" * 70)
    test_upper = create_test_file("VIDEO.MP4")
    success, msg = run_test(
        "Uppercase MP4",
        lambda: get_file_type(str(test_upper)),
        expected_result="video"
    )
    test_results.append(("Uppercase extension", success, msg))
    print(f"Status: {'PASS' if success else 'FAIL'}")
    print(f"Result: {msg}")
    cleanup_test_file(test_upper)
    print()

    # Test 5: Case insensitivity - mixed case
    print("Test 5: Case Insensitivity - Mixed Case Extension")
    print("-" * 70)
    test_mixed = create_test_file("audio.WaV")
    success, msg = run_test(
        "Mixed case WAV",
        lambda: get_file_type(str(test_mixed)),
        expected_result="audio"
    )
    test_results.append(("Mixed case extension", success, msg))
    print(f"Status: {'PASS' if success else 'FAIL'}")
    print(f"Result: {msg}")
    cleanup_test_file(test_mixed)
    print()

    # Test 6: Non-existent file
    print("Test 6: Non-existent File")
    print("-" * 70)
    success, msg = run_test(
        "Non-existent file",
        lambda: get_file_type("nonexistent_file.mp4"),
        expected_exception=FileNotFoundError
    )
    test_results.append(("Non-existent file", success, msg))
    print(f"Status: {'PASS' if success else 'FAIL'}")
    print(f"Result: {msg}")
    print()

    # Test 7: Unsupported format
    print("Test 7: Unsupported File Format")
    print("-" * 70)
    test_txt = create_test_file("document.txt")
    success, msg = run_test(
        "Unsupported TXT file",
        lambda: get_file_type(str(test_txt)),
        expected_exception=ValueError
    )
    test_results.append(("Unsupported format", success, msg))
    print(f"Status: {'PASS' if success else 'FAIL'}")
    print(f"Result: {msg}")
    cleanup_test_file(test_txt)
    print()

    # Test 8: Directory instead of file
    print("Test 8: Directory Path (Not a File)")
    print("-" * 70)
    test_dir = Path("test_directory")
    test_dir.mkdir(exist_ok=True)
    success, msg = run_test(
        "Directory path",
        lambda: get_file_type(str(test_dir)),
        expected_exception=ValueError
    )
    test_results.append(("Directory path", success, msg))
    print(f"Status: {'PASS' if success else 'FAIL'}")
    print(f"Result: {msg}")
    test_dir.rmdir()
    print()

    # Test 9: File without extension
    print("Test 9: File Without Extension")
    print("-" * 70)
    test_no_ext = create_test_file("file_without_extension")
    success, msg = run_test(
        "No extension",
        lambda: get_file_type(str(test_no_ext)),
        expected_exception=ValueError
    )
    test_results.append(("No extension", success, msg))
    print(f"Status: {'PASS' if success else 'FAIL'}")
    print(f"Result: {msg}")
    cleanup_test_file(test_no_ext)
    print()

    # Test 10: Various video formats
    print("Test 10: Multiple Video Formats")
    print("-" * 70)
    video_tests = ['.mov', '.avi', '.mkv', '.webm']
    for ext in video_tests:
        test_file = create_test_file(f"test_video{ext}")
        success, msg = run_test(
            f"Video format {ext}",
            lambda: get_file_type(str(test_file)),
            expected_result="video"
        )
        test_results.append((f"Video {ext}", success, msg))
        print(f"  {ext}: {'PASS' if success else 'FAIL'}")
        cleanup_test_file(test_file)
    print()

    # Test 11: Various audio formats
    print("Test 11: Multiple Audio Formats")
    print("-" * 70)
    audio_tests = ['.flac', '.ogg', '.aac', '.m4a']
    for ext in audio_tests:
        test_file = create_test_file(f"test_audio{ext}")
        success, msg = run_test(
            f"Audio format {ext}",
            lambda: get_file_type(str(test_file)),
            expected_result="audio"
        )
        test_results.append((f"Audio {ext}", success, msg))
        print(f"  {ext}: {'PASS' if success else 'FAIL'}")
        cleanup_test_file(test_file)
    print()

    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    total_tests = len(test_results)
    passed_tests = sum(1 for _, success, _ in test_results if success)
    failed_tests = total_tests - passed_tests

    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    print()

    if failed_tests > 0:
        print("FAILED TESTS:")
        print("-" * 70)
        for name, success, msg in test_results:
            if not success:
                print(f"  - {name}: {msg}")
        print()
        return 1
    else:
        print("All tests passed successfully!")
        print()
        return 0


if __name__ == "__main__":
    sys.exit(main())

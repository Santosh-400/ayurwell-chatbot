from gtts import gTTS
import io
import logging

# Optional post-processing using pydub to make gTTS output sound more natural.
# pydub requires ffmpeg to be installed on the system (not a Python package).
try:
    from pydub import AudioSegment, effects
    PYDUB_AVAILABLE = True

    # Hard-coded fallback for when ffmpeg is not in PATH, common on Windows.
    # This makes the app more portable without requiring users to edit system PATH.
    import platform
    import os
    if platform.system() == "Windows":
        # The path discovered on the user's system via winget
        ffmpeg_path = r"C:\Users\santo\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin\ffmpeg.exe"
        if os.path.exists(ffmpeg_path):
            try:
                AudioSegment.converter = ffmpeg_path
                logging.info(f"pydub: Explicitly set ffmpeg converter to {ffmpeg_path}")
            except Exception as e:
                logging.warning(f"pydub: Failed to set ffmpeg converter: {e}")
except Exception:
    PYDUB_AVAILABLE = False


def _post_process_mp3(mp3_bytes: bytes, phase: str = 'medium') -> bytes:
    """Lightweight post-processing to improve perceived naturalness.

    Effects applied when pydub/ffmpeg are available:
    - slight tempo adjustment (phase: low|medium|high)
    - normalize
    - short fade-in/fade-out
    - gentle low-pass filter to smooth sibilance

    If pydub/ffmpeg are not available, returns the original bytes unchanged.
    """
    if not PYDUB_AVAILABLE:
        return mp3_bytes

    try:
        buf = io.BytesIO(mp3_bytes)
        seg = AudioSegment.from_file(buf, format='mp3')
    except Exception:
        # If decoding fails (ffmpeg not present), return original bytes
        return mp3_bytes

    # Map phase to a mild speed factor (values close to 1.0)
    phase_map = {
        'low': 0.99,     # barely slower
        'medium': 0.98,  # slightly slower - more natural cadence
        'high': 0.96     # noticeably slower - for dramatic effect
    }
    factor = phase_map.get((phase or 'medium').lower(), 0.98)

    # Change speed by altering frame_rate then resetting to original rate.
    new_frame_rate = int(seg.frame_rate * factor)
    seg_speed = seg._spawn(seg.raw_data, overrides={"frame_rate": new_frame_rate})
    seg_speed = seg_speed.set_frame_rate(seg.frame_rate)

    # Small fades and normalization to reduce artifacts on chunk boundaries
    seg_proc = seg_speed.fade_in(30).fade_out(80)
    try:
        seg_proc = effects.normalize(seg_proc)
    except Exception:
        pass

    # Gentle low-pass to smooth high-frequency artifacts (cutoff ~8kHz)
    try:
        seg_proc = seg_proc.low_pass_filter(8000)
    except Exception:
        pass

    out_buf = io.BytesIO()
    seg_proc.export(out_buf, format='mp3', bitrate='192k')
    out_buf.seek(0)
    return out_buf.read()


def text_to_speech_gtts(text, lang='kn', save_path=None, humanize=True, phase='medium'):
    """Generate speech MP3 using gTTS and optionally post-process it.

    Args:
        text (str): Text to synthesize.
        lang (str): Language code (e.g., 'en' or 'kn').
        save_path (str|None): If provided, save MP3 to this path and return the path.
        humanize (bool): Whether to apply pydub post-processing (requires ffmpeg/pydub).
        phase (str): One of 'low'|'medium'|'high' controlling mild tempo/pacing.

    Returns:
        bytes|str: If save_path is None, returns MP3 bytes; otherwise returns the saved file path.
    """
    tts = gTTS(text=text, lang=lang, slow=False)

    # If the user requested a direct save, we still post-process before saving when possible
    if save_path:
        tmp_buf = io.BytesIO()
        tts.write_to_fp(tmp_buf)
        tmp_buf.seek(0)
        out_bytes = tmp_buf.read()
        if humanize and phase and PYDUB_AVAILABLE:
            try:
                out_bytes = _post_process_mp3(out_bytes, phase=phase)
            except Exception:
                pass
        # Persist to disk
        with open(save_path, 'wb') as f:
            f.write(out_bytes)
        logging.info(f"✅ Audio saved: {save_path}")
        return save_path

    # return bytes
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    mp3_bytes = buf.read()

    if humanize and phase:
        try:
            mp3_bytes = _post_process_mp3(mp3_bytes, phase=phase)
        except Exception:
            # If post-processing fails, fall back to raw output
            pass

    return mp3_bytes


if __name__ == '__main__':
    # Example usage when run as a script
    path_kn = text_to_speech_gtts("ನಮಸ್ಕಾರ! ಆಯುರ್ವೆಲ್ ಚಾಟ್‌ಬಾಟ್‌ಗೆ ಸುಸ್ವಾಗತ.", lang='kn', save_path='tts_kn.mp3')
    path_en = text_to_speech_gtts("Hello! Welcome to AyurWell chatbot.", lang='en', save_path='tts_en.mp3')
    print('Saved:', path_kn, path_en)

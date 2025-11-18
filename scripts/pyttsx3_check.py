import pyttsx3
import tempfile
import os
import base64

try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices') or []
    print('voices_count=', len(voices))
    for i, v in enumerate(voices[:10]):
        print(i, getattr(v, 'id', None), getattr(v, 'name', ''))

    sample_text = 'This is a quick local pyttsx three test.'
    tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    tmp_path = tmp.name
    tmp.close()
    print('writing sample to', tmp_path)
    engine.save_to_file(sample_text, tmp_path)
    engine.runAndWait()
    if os.path.exists(tmp_path):
        size = os.path.getsize(tmp_path)
        print('wrote sample size=', size)
        with open(tmp_path, 'rb') as f:
            b = f.read()
        print('base64_len=', len(base64.b64encode(b)))
        # clean up
        try:
            os.remove(tmp_path)
        except Exception:
            pass
    else:
        print('sample file missing')
except Exception as e:
    print('error:', e)
    raise

import pyttsx3

def has_kannada_voice():
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices') or []
        found = []
        for v in voices:
            name = (getattr(v, 'name', '') or '').lower()
            id_ = getattr(v, 'id', '') or ''
            langs = []
            try:
                langs = [l.decode('utf-8') if isinstance(l, bytes) else str(l) for l in getattr(v, 'languages', [])]
            except Exception:
                langs = [str(getattr(v, 'languages', ''))]
            langs_str = ' '.join(langs).lower()
            if 'kannada' in name or 'kannada' in langs_str or 'kn' in langs_str or 'kn-in' in langs_str:
                found.append({'name': name, 'id': id_, 'languages': langs})
        return voices, found
    except Exception as e:
        print('error', e)
        return [], []

voices, found = has_kannada_voice()
print('total_voices=', len(voices))
for i, v in enumerate(voices):
    print(i, 'name=', getattr(v, 'name', ''), 'id=', getattr(v, 'id', ''), 'languages=', getattr(v, 'languages', ''))

if found:
    print('\nKANNADA voices detected:')
    for f in found:
        print(f)
else:
    print('\nNo Kannada voice detected in pyttsx3 voices.')

from googletrans import Translator

try:
    t = Translator()
    texts = [
        'Hello, how are you?',
        'This is a test for Kannada translation.',
        'Ayurveda is an ancient system of medicine.'
    ]
    for txt in texts:
        tr = t.translate(txt, dest='kn')
        print('src:', tr.src, 'dest:', tr.dest)
        print('original:', txt)
        print('translated:', tr.text)
        print('---')
except Exception as e:
    print('error:', e)
    raise

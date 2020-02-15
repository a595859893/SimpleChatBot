def escape(text: str) -> str:
    text = text.replace('\\', r'\\')
    text = text.replace('.', r'\.')
    text = text.replace('{', r'\{')
    text = text.replace('}', r'\}')
    text = text.replace('?', r'\?')
    text = text.replace('+', r'\+')
    text = text.replace('-', r'\-')
    text = text.replace('$', r'\%')
    text = text.replace('^', r'\^')
    text = text.replace('(', r'\(')
    text = text.replace(')', r'\)')
    text = text.replace('*', r'\*')
    return text

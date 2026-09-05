with open('public/script.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\\\\n', '\\n')

with open('public/script.py', 'w', encoding='utf-8') as f:
    f.write(text)

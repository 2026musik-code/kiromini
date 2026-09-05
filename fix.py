with open('public/script.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# This will replace double backslash + n with single backslash + n
# E.g. "\\n" -> "\n"
text = re.sub(r'\\\\n', r'\\n', text)

with open('public/script.py', 'w', encoding='utf-8') as f:
    f.write(text)

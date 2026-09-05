import re

with open('public/script.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace double backslash n with single backslash n
# Only in the places where it's obviously a newline meant for printing/output.
# Since it's all string literals in the file, content.replace('\\\\n', '\\n') might work, but let's be careful.
# Actually, the user has \\n in their code: console.print("\\n[bold cyan]...")
# If the file has literal '\\n', replacing '\\\\n' with '\\n' in the file string will do it.
# Wait, if the file actually contains `console.print("\\n...")`, that's exactly 2 backslashes.

content = content.replace('console.print("\\\\n', 'console.print("\\n')
content = content.replace('\\\\n[bold', '\\n[bold')
content = content.replace('[bold green]\\\\n', '[bold green]\\n')
content = content.replace(']\\\\n"', ']\\n"')
content = content.replace(']\\\\n', ']\\n')
content = content.replace('gray]\\\\n"', 'gray]\\n"')
content = content.replace('f"\\\\n[bold', 'f"\\n[bold')
content = content.replace('Ask("\\\\n[bold', 'Ask("\\n[bold')
content = content.replace('ONLINE\\\\n"', 'ONLINE\\n"')
content = content.replace('{active_model}\\\\n"', '{active_model}\\n"')
content = content.replace(')\\n"', ')\n"')

with open('public/script.py', 'w', encoding='utf-8') as f:
    f.write(content)

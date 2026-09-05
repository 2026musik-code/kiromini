with open('public/script.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Make sure we don't accidentally replace legitimate \n in string literals 
# Wait, replacing '\\\\n' with '\\n' actually converts a literal backslash followed by 'n' into a real newline character IN THE SOURCE CODE.
# That breaks the python syntax.
# Example: print("\n") is represented in python source as print("\n") which is 1 backslash and n.
# If I look at the previous command output: '    console.print("\\n[bold cyan]Sedang men-scan model AI aktif di server...[/bold cyan]")\n'
# This string starts with literally \ and n. 
# Wait, if I do repr() on a string read from a file, '\\n' means there are 2 backslashes in the file.
# Let's fix it by replacing '\\\\n' with '\\n' in the python source text.
import re

text = text.replace('\\\\n', '\\n')

with open('public/script.py', 'w', encoding='utf-8') as f:
    f.write(text)

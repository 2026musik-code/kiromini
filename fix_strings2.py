with open('public/script.py', 'r', encoding='utf-8') as f:
    text = f.read()

bad_str = r"""<edit_file\s+path="([^"]+)">\s*<target>
?(.*?)
?</target>\s*<replacement>
?(.*?)
?</replacement>\s*</edit_file>"""

good_str = r"""<edit_file\s+path="([^"]+)">\s*<target>\n?(.*?)\n?</target>\s*<replacement>\n?(.*?)\n?</replacement>\s*</edit_file>"""

text = text.replace(bad_str, good_str)

with open('public/script.py', 'w', encoding='utf-8') as f:
    f.write(text)

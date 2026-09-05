with open('public/script.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix console.print("\n
text = text.replace('console.print("\n', 'console.print("\\n')
# Fix ]\n"
text = text.replace(']\n"', ']\\n"')
# Fix f"\n[
text = text.replace('f"\n[', 'f"\\n[')
# Fix Prompt.ask("\n
text = text.replace('Prompt.ask("\n', 'Prompt.ask("\\n')
# Fix ONLINE\n"
text = text.replace('ONLINE\n"', 'ONLINE\\n"')
# Fix {active_model}\n"
text = text.replace('{active_model}\n"', '{active_model}\\n"')
# Fix gray]\n"
text = text.replace('gray]\n"', 'gray]\\n"')
# Fix )\\n"
text = text.replace(')\n"', ')\\n"')
# Fix }\n"
text = text.replace('}\n"', '}\\n"')

# Other known ones
text = text.replace('f"\n', 'f"\\n')
text = text.replace('("\n', '("\\n')
text = text.replace('\n")', '\\n")')
text = text.replace(']\n', ']\\n')
text = text.replace(')\n(Auto', ')\\n(Auto')

with open('public/script.py', 'w', encoding='utf-8') as f:
    f.write(text)

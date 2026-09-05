import sys

with open('public/script.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # If the line ends with a string quote that is open, or if it doesn't have a normal line ending, it might be broken.
    # Actually, since I replaced ALL '\\n' with '\n', the string "\\n[bold cyan]" became:
    # line 1: console.print("
    # line 2: [bold cyan]...
    # We can detect this! If a line ends with `"` or `f"` or `("` or `(f"` or `=\n` etc.
    # Let's just look at the lines and if they look like they were broken by my replace.
    
    # A simple heuristic: if the line has an odd number of quotes (excluding escaped ones).
    def count_quotes(s):
        # simple count of unescaped quotes
        s = s.replace('\\"', '')
        s = s.replace("\\'", '')
        return s.count('"') + s.count("'")
        
    if count_quotes(line) % 2 != 0:
        # Broken line! Combine with next line and insert \\n
        if i + 1 < len(lines):
            combined = line.rstrip('\n') + '\\n' + lines[i+1]
            # Replace the current line with combined, and check again.
            lines[i] = combined
            del lines[i+1]
            continue
    new_lines.append(line)
    i += 1

with open('public/script.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

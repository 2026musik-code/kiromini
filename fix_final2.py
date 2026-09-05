with open('public/script.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's see if any other string literal error remains.
# We will compile it in this script.
try:
    compile(text, 'public/script.py', 'exec')
    print("ALL GOOD!")
except SyntaxError as e:
    print("STILL BROKEN:", e)

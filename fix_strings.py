with open('public/script.py', 'r', encoding='utf-8') as f:
    text = f.read()

# The pattern is: A string starts, then there's an actual newline, then [bold or something.
# The user's strings that broke were:
# console.print("\n[bold cyan]
# console.print("\n[bold green]
# Prompt.ask(f"\n[bold yellow]
# etc.
# We can replace literal newlines that are immediately followed by `[` or `...` inside strings, but that's hard to target.
# Let's just target the specific strings.

replacements = [
    ('console.print("\n[bold cyan]Sedang men-scan', 'console.print("\\n[bold cyan]Sedang men-scan'),
    ('console.print("\n[bold green]╔════', 'console.print("\\n[bold green]╔════'),
    ('[bold green]╚═══════════════════════════════════════════════════╝[/bold green]\n")', '[bold green]╚═══════════════════════════════════════════════════╝[/bold green]\\n")'),
    ('Prompt.ask(f"\n[bold yellow]📖 Pilih', 'Prompt.ask(f"\\n[bold yellow]📖 Pilih'),
    ('f"Membaca {path} (Baris {s}-{e} dari {total}):\n{snippet}"', 'f"Membaca {path} (Baris {s}-{e} dari {total}):\\n{snippet}"'),
    ('return "\n".join(lines)', 'return "\\n".join(lines)'),
    ('return "\n".join(results)', 'return "\\n".join(results)'),
    ('parsed = "\n(Auto-parsed JSON):\n" +', 'parsed = "\\n(Auto-parsed JSON):\\n" +'),
    ('raw = raw[:6000] + "\n... (response', 'raw = raw[:6000] + "\\n... (response'),
    ('return f"HTTP {method.upper()} {url}\nStatus: {status}\n\nResponse:\n{raw}{parsed}"', 'return f"HTTP {method.upper()} {url}\\nStatus: {status}\\n\\nResponse:\\n{raw}{parsed}"'),
    ('return (f"🛡️ SELF-HEALING AKTIF: sintaks rusak setelah self-edit!\n"', 'return (f"🛡️ SELF-HEALING AKTIF: sintaks rusak setelah self-edit!\\n"'),
    ('f"Output error: {result.stderr.strip()[:500]}\n"', 'f"Output error: {result.stderr.strip()[:500]}\\n"'),
    ('return (f"⚠️ SELF-CHECK GAGAL dan backup tidak ditemukan!\n"', 'return (f"⚠️ SELF-CHECK GAGAL dan backup tidak ditemukan!\\n"'),
    ('status_text.append("ONLINE\n", style="bold cyan")', 'status_text.append("ONLINE\\n", style="bold cyan")'),
    ('status_text.append(f"{active_model}\n", style="bold yellow")', 'status_text.append(f"{active_model}\\n", style="bold yellow")'),
    ('console.print("[italic gray]Ketik \'/menu\' untuk melihat daftar perintah, atau \'exit\' untuk keluar.[/italic gray]\n")', 'console.print("[italic gray]Ketik \'/menu\' untuk melihat daftar perintah, atau \'exit\' untuk keluar.[/italic gray]\\n")'),
    ('tools_list_text = "\n".join(', 'tools_list_text = "\\n".join('),
    ('Prompt.ask("\n[bold green]➜ Anda', 'Prompt.ask("\\n[bold green]➜ Anda'),
    ('console.print("\n[bold cyan]=== MENU PERINTAH', 'console.print("\\n[bold cyan]=== MENU PERINTAH'),
    ('console.print("[yellow]/exit[/yellow]    - Keluar dari program\n")', 'console.print("[yellow]/exit[/yellow]    - Keluar dari program\\n")'),
    ('console.print(f"[bold green]Model berhasil diubah ke:[/bold green] {active_model}\n")', 'console.print(f"[bold green]Model berhasil diubah ke:[/bold green] {active_model}\\n")'),
    ('console.print(f"\n[bold cyan]=== STATISTIK', 'console.print(f"\\n[bold cyan]=== STATISTIK'),
    ('console.print(f"Pesan dari AI: {asst_msgs}\n")', 'console.print(f"Pesan dari AI: {asst_msgs}\\n")'),
    ('console.print("\n[bold green]✅ Riwayat', 'console.print("\\n[bold green]✅ Riwayat'),
    ('console.print("[italic gray]Gunakan /improve untuk mengembangkan diri sendiri, lalu /restart untuk memuat ulang.[/italic gray]\n")', 'console.print("[italic gray]Gunakan /improve untuk mengembangkan diri sendiri, lalu /restart untuk memuat ulang.[/italic gray]\\n")'),
    ('f"[bold yellow]MODE SELF-IMPROVEMENT AKTIF[/bold yellow]\n\n"', 'f"[bold yellow]MODE SELF-IMPROVEMENT AKTIF[/bold yellow]\\n\\n"'),
    ('f"Kode sumber Anda: [cyan]{agent_path}[/cyan]\n"', 'f"Kode sumber Anda: [cyan]{agent_path}[/cyan]\\n"'),
    ('f"Backup saat ini: [cyan]{agent_backup}[/cyan]\n\n"', 'f"Backup saat ini: [cyan]{agent_backup}[/cyan]\\n\\n"'),
    ('f"Deskripsikan fitur yang ingin Anda tambahkan/perbaiki pada diri Anda sendiri,\n"', 'f"Deskripsikan fitur yang ingin Anda tambahkan/perbaiki pada diri Anda sendiri,\\n"'),
    ('f"contoh: \'Tambahkan fitur export chat ke file markdown\'.\n"', 'f"contoh: \'Tambahkan fitur export chat ke file markdown\'.\\n"'),
    ('Prompt.ask("\n[bold green]➜ Fitur apa', 'Prompt.ask("\\n[bold green]➜ Fitur apa'),
    ('f"MODE SELF-IMPROVEMENT: Saya (agen) diminta untuk mengembangkan diri sendiri.\n"', 'f"MODE SELF-IMPROVEMENT: Saya (agen) diminta untuk mengembangkan diri sendiri.\\n"'),
    ('f"Permintaan fitur: {improve_request}\n\n"', 'f"Permintaan fitur: {improve_request}\\n\\n"'),
    ('f"IKUTI ATURAN SELF-IMPROVEMENT di system prompt:\n"', 'f"IKUTI ATURAN SELF-IMPROVEMENT di system prompt:\\n"'),
    ('f"1. Backup dulu: cp {agent_path} {agent_backup}\n"', 'f"1. Backup dulu: cp {agent_path} {agent_backup}\\n"'),
    ('f"2. Baca kode sumbermu sendiri di {agent_path} (gunakan sed -n \'X,Yp\' untuk baca per bagian).\n"', 'f"2. Baca kode sumbermu sendiri di {agent_path} (gunakan sed -n \'X,Yp\' untuk baca per bagian).\\n"'),
    ('f"3. Edit dengan sed/python patch. JANGAN hapus arsitektur utama (main, select_model, UI, loop).\n"', 'f"3. Edit dengan sed/python patch. JANGAN hapus arsitektur utama (main, select_model, UI, loop).\\n"'),
    ('f"4. Verifikasi: python -m py_compile {agent_path}\n"', 'f"4. Verifikasi: python -m py_compile {agent_path}\\n"'),
    ('f"5. Update versi & changelog di {agent_version_file} (format: \'<versi>\n---CHANGELOG---\n<tanggal> - <perubahan>\').\n"', 'f"5. Update versi & changelog di {agent_version_file} (format: \'<versi>\\n---CHANGELOG---\\n<tanggal> - <perubahan>\').\\n"'),
    ('console.print("\n")', 'console.print("\\n")'),
    ('tool_outputs += f"Native tool [{tool_name}] result:\n{tool_result}\n\n"', 'tool_outputs += f"Native tool [{tool_name}] result:\\n{tool_result}\\n\\n"'),
    ('output = output[:4000] + "\n... (output dipotong karena terlalu panjang)"', 'output = output[:4000] + "\\n... (output dipotong karena terlalu panjang)"'),
    ('tool_outputs += f"Command: {cmd}\nOutput:\n{output}\n\n"', 'tool_outputs += f"Command: {cmd}\\nOutput:\\n{output}\\n\\n"'),
    ('messages.append({"role": "user", "content": f"Berhasil menjalankan perintah di latar belakang. Berikut adalah outputnya (tolong analisa dan berikan ringkasan hasil kerja, atau lanjutkan langkah berikutnya jika diperlukan):\n\n<tool_response>\n{tool_outputs}\n</tool_response>"})', 'messages.append({"role": "user", "content": f"Berhasil menjalankan perintah di latar belakang. Berikut adalah outputnya (tolong analisa dan berikan ringkasan hasil kerja, atau lanjutkan langkah berikutnya jika diperlukan):\\n\\n<tool_response>\\n{tool_outputs}\\n</tool_response>"})'),
    ('console.print("\n[bold red]Sesi', 'console.print("\\n[bold red]Sesi'),
    ('console.print(f"\n[bold red]✖ Error', 'console.print(f"\\n[bold red]✖ Error'),
    ('([bold green]✅ Riwayat', '(\\n[bold green]✅ Riwayat'),
    # Extra catching for any leftover
    ('[/bold green]\n")', '[/bold green]\\n")')
]

for old, new in replacements:
    text = text.replace(old, new)

# And let's find any remaining unescaped newlines inside strings.
# Wait, let's just write this to file and compile.
with open('public/script.py', 'w', encoding='utf-8') as f:
    f.write(text)

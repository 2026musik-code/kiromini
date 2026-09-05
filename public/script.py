import os
import sys

# Perbaikan untuk EOFError saat script dijalankan via pipe (curl ... | python3)
if not sys.stdin.isatty():
    try:
        sys.stdin = open('/dev/tty')
    except:
        pass

import re
import json
import shutil
import subprocess
import time
import urllib.request
import urllib.error

try:
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.text import Text
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.prompt import Prompt
    from rich.table import Table
except ImportError:
    print("Harap install dependencies terlebih dahulu: pip install rich")
    sys.exit(1)

console = Console()

# --- AUTO ENV PARSER ---
# Ini memungkinkan user menjalankan ulang script kapan saja (python3 kiro.py)
if os.path.exists('.env'):
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k.strip()] = v.strip()
# -----------------------

# Ambil dari file .env via os.environ (di-inject otomatis oleh generator/curl)
# Ini penting agar one-liner install tetap berfungsi dengan aman.
API_KEY = os.environ.get("KEY_MINI", "key")
BASE_URL = os.environ.get("URL_MINI", "url")

# Setup Client
class SimpleOpenAIClient:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        # Ensure base URL ends with a slash for easy appending if needed, though usually it's /chat/completions
        self.base_url = base_url.rstrip('/')
        
    class Chat:
        def __init__(self, parent):
            self.parent = parent
            self.completions = self.Completions(parent)
            
        class Completions:
            def __init__(self, parent):
                self.parent = parent
                
            def create(self, model, messages, temperature=0.7, max_tokens=150):
                url = f"{self.parent.base_url}/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.parent.api_key}",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                }
                data = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                
                req = urllib.request.Request(
                    url, 
                    data=json.dumps(data).encode('utf-8'),
                    headers=headers,
                    method='POST'
                )
                
                try:
                    with urllib.request.urlopen(req, timeout=60.0) as response:
                        response_data = json.loads(response.read().decode('utf-8'))
                        # Create a simple mock object to match the openai SDK structure
                        class MockChoice:
                            def __init__(self, msg_data):
                                class MockMessage:
                                    def __init__(self, content):
                                        self.content = content
                                self.message = MockMessage(msg_data.get('content', ''))
                        
                        class MockResponse:
                            def __init__(self, choices_data):
                                self.choices = [MockChoice(c.get('message', {})) for c in choices_data]
                                
                        return MockResponse(response_data.get('choices', []))
                        
                except urllib.error.URLError as e:
                    print(f"API Request failed: {e}")
                    # Return empty structure to prevent crashes
                    class EmptyResponse:
                        choices = []
                    return EmptyResponse()

client = SimpleOpenAIClient(api_key=API_KEY, base_url=BASE_URL)
client.chat = client.Chat(client)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_logo():
    logo = """
 ██╗  ██╗██╗██████╗  ██████╗ 
 ██║ ██╔╝██║██╔══██╗██╔═══██╗
 █████╔╝ ██║██████╔╝██║   ██║
 ██╔═██╗ ██║██╔══██╗██║   ██║
 ██║  ██╗██║██║  ██║╚██████╔╝
 ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝ ╚═════╝ 
    """
    console.print(Panel(
        Text(logo, style="bold cyan", justify="center"), 
        title="[bold magenta]KIRO AGENTIC[/bold magenta]", 
        subtitle="[bold yellow]Professional Edition[/bold yellow]",
        border_style="blue"
    ))

def select_model():
    from rich.columns import Columns
    console.print("\\n[bold cyan]Sedang men-scan model AI aktif di server...[/bold cyan]")
    try:
        model_data = client.models.list().data
        models = sorted([m.id for m in model_data])
    except Exception as e:
        console.print(f"[bold red]Gagal mengambil model: {e}[/bold red]")
        models = [
            "kiro/claude-sonnet-4.5",
            "kiro/claude-haiku-4.5",
            "kiro/deepseek-3.2",
            "kiro/minimax-m2.5",
            "kiro/minimax-m2.1",
            "kiro/glm-5",
            "kiro/qwen3-coder-next",
            "kiro/auto",
            "kiro/claude-sonnet-4"
        ]
    
    models = models[:20]
    
    # Palet warna cycling untuk kotak model
    colors = [
        "cyan", "green", "yellow", "magenta", "blue",
        "red", "bright_cyan", "bright_green", "bright_yellow",
        "bright_magenta", "bright_blue", "bright_red"
    ]
    
    # Header katalog
    console.print("\\n[bold green]╔═══════════════════════════════════════════════════╗[/bold green]")
    console.print("[bold green]║      📚 KATALOG MODEL AI AKTIF 📚                 ║[/bold green]")
    console.print("[bold green]╚═══════════════════════════════════════════════════╝[/bold green]\\n")
    
    # Buat panel (kotak) untuk tiap model
    panels = []
    for idx, model in enumerate(models):
        color = colors[idx % len(colors)]
        num = idx + 1
        panel = Panel(
            f"[bold {color}]{model}[/bold {color}]",
            title=f"[bold white]No. {num}[/bold white]",
            border_style=color,
            padding=(0, 2),
            width=44
        )
        panels.append(panel)
    
    # Panel custom model di akhir
    custom_num = len(models) + 1
    custom_panel = Panel(
        "[bold white]✏️  Masukkan model sendiri[/bold white]",
        title=f"[bold white]No. {custom_num}[/bold white]",
        border_style="white",
        padding=(0, 2),
        width=44
    )
    panels.append(custom_panel)
    
    # Tampilkan dalam layout grid 3 kolom (seperti rak buku)
    from rich.table import Table as _Table
    _grid = _Table.grid(padding=(0, 1))
    for _ in range(3):
        _grid.add_column()
    for i in range(0, len(panels), 3):
        _row = panels[i:i+3]
        while len(_row) < 3:
            _row.append("")
        _grid.add_row(*_row)
    console.print(_grid)
    
    choice = Prompt.ask(f"\\n[bold yellow]📖 Pilih nomor model (1-{custom_num})[/bold yellow]", default="1")
    
    if choice == str(custom_num):
        custom = Prompt.ask("[bold yellow]Masukkan nama custom model[/bold yellow]")
        return custom
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(models):
            return models[idx]
    except:
        pass
    
    return models[0]

# ============================================================
# 🔧 NATIVE FILE TOOLS (v1.2→v1.3) — Self-edit yang aman & presisi
# ============================================================

def native_read_file(path, start=None, end=None):
    """Baca file dengan opsi baris awal/akhir (hemat memori)."""
    try:
        if not os.path.isfile(path):
            return f"Error read_file: file '{path}' tidak ditemukan."
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        total = len(lines)
        s = max(1, int(start)) if start else 1
        e = min(total, int(end)) if end else total
        if s > total:
            return f"Error read_file: baris awal ({s}) melebihi total baris ({total})."
        snippet = ''.join(f"{i}:{lines[i-1]}" for i in range(s, e + 1))
        return f"Membaca {path} (Baris {s}-{e} dari {total}):\\n{snippet}"
    except Exception as ex:
        return f"Error read_file: {ex}"

def native_write_file(path, content, append=False):
    """Tulis file baru atau append. Parent dir dibuat otomatis."""
    try:
        parent = os.path.dirname(os.path.abspath(path))
        os.makedirs(parent, exist_ok=True)
        mode = 'a' if append else 'w'
        with open(path, mode, encoding='utf-8') as f:
            f.write(content)
        action = "di-append ke" if append else "ditulis ke"
        return f"✅ Konten berhasil {action} {path} ({len(content)} char)."
    except Exception as ex:
        return f"Error write_file: {ex}"

def native_edit_file(path, target, replacement):
    """Surgical search & replace. Target harus unik di dalam file."""
    try:
        if not os.path.isfile(path):
            return f"Error edit_file: file '{path}' tidak ditemukan."
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        count = content.count(target)
        if count == 0:
            return (f"Error edit_file: TARGET TIDAK DITEMUKAN di {path}. "
                    f"Baca file dulu (read_file) dan pastikan teks persis sama (termasuk indentasi).")
        if count > 1:
            return (f"Error edit_file: TARGET DITEMUKAN {count}x (harus unik). "
                    f"Perbesar blok target agar unik, lalu coba lagi.")
        new_content = content.replace(target, replacement, 1)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return f"✅ Edit berhasil di {path} (1 replacement)."
    except Exception as ex:
        return f"Error edit_file: {ex}"

# ============================================================
# 🔌 AUTOMATIC TOOLKIT (v1.3) — Tools otomatis tanpa improvisasi manual
# ============================================================

def native_list_dir(path, recursive="false"):
    """Tampilkan isi direktori (ukuran file, folder, jumlah item)."""
    try:
        if not os.path.isdir(path):
            return f"Error list_dir: direktori '{path}' tidak ditemukan."
        entries = sorted(os.listdir(path))
        if not entries:
            return f"Direktori '{path}' kosong."
        lines = [f"Isi direktori '{path}' ({len(entries)} item):"]
        for e in entries[:200]:
            full = os.path.join(path, e)
            if os.path.isdir(full):
                lines.append(f"  [DIR]  {e}/")
            else:
                try:
                    size = os.path.getsize(full)
                    lines.append(f"  {size:>8} B  {e}")
                except OSError:
                    lines.append(f"  {'?':>8}    {e}")
        if len(entries) > 200:
            lines.append(f"  ... dan {len(entries)-200} item lainnya (batasi path lebih spesifik).")
        return "\\n".join(lines)
    except Exception as ex:
        return f"Error list_dir: {ex}"

def native_search_content(path, pattern, recursive="false", ignore_case="false"):
    """Cari konten di dalam file/folder (grep-like). Skip biner, .git, node_modules, .venv."""
    try:
        flags = re.IGNORECASE if ignore_case.lower() == "true" else 0
        rx = re.compile(pattern, flags)
        skip_dirs = {'.git', 'node_modules', '.venv', '__pycache__'}
        results = []
        files = []
        if os.path.isfile(path):
            files = [path]
        elif os.path.isdir(path):
            if recursive.lower() == "true":
                for root, dirs, names in os.walk(path):
                    dirs[:] = [d for d in dirs if d not in skip_dirs]
                    for n in names:
                        files.append(os.path.join(root, n))
            else:
                files = [os.path.join(path, n) for n in os.listdir(path) if os.path.isfile(os.path.join(path, n))]
        else:
            return f"Error search_content: path '{path}' tidak ditemukan."
        for fp in files:
            try:
                with open(fp, 'rb') as fb:
                    head = fb.read(1024)
                    if b'\\x00' in head:
                        continue  # skip binary
                with open(fp, 'r', encoding='utf-8', errors='replace') as f:
                    for i, line in enumerate(f, 1):
                        if rx.search(line):
                            results.append(f"{fp}:{i}: {line.rstrip()[:200]}")
                            if len(results) >= 100:
                                results.append(f"... (dipotong, lebih dari 100 hasil. Persempit pattern/path).")
                                return "\\n".join(results)
            except (OSError, PermissionError):
                continue
        if not results:
            return f"Tidak ada hasil untuk pattern '{pattern}' di '{path}'."
        return "\\n".join(results)
    except re.error as rex:
        return f"Error search_content: regex tidak valid - {rex}"
    except Exception as ex:
        return f"Error search_content: {ex}"

def native_http_request(url, method="GET", body=None, headers=None):
    """HTTP request ke REST API. Auto-parse JSON jika applicable."""
    import urllib.request
    import urllib.error
    try:
        hdrs = {"User-Agent": "KIRO-AGENTIC/1.3"}
        if headers:
            try:
                hdrs.update(json.loads(headers))
            except Exception:
                return "Error http_request: headers bukan JSON string valid."
        data = None
        if body and method.upper() in ("POST", "PUT", "PATCH"):
            data = body.encode('utf-8')
            hdrs.setdefault("Content-Type", "application/json")
        req = urllib.request.Request(url, data=data, headers=hdrs, method=method.upper())
        with urllib.request.urlopen(req, timeout=60) as resp:
            status = resp.status
            raw = resp.read().decode('utf-8', errors='replace')
        parsed = ""
        try:
            parsed = "\\n(Auto-parsed JSON):\\n" + json.dumps(json.loads(raw), indent=2, ensure_ascii=False)
        except Exception:
            pass
        if len(raw) > 6000:
            raw = raw[:6000] + "\\n... (response dipotong karena terlalu panjang)"
        return f"HTTP {method.upper()} {url}\\nStatus: {status}\\n\\nResponse:\\n{raw}{parsed}"
    except urllib.error.HTTPError as he:
        return f"Error http_request: HTTP {he.code} - {he.reason}"
    except Exception as ex:
        return f"Error http_request: {ex}"

def native_download_file(url, output):
    """Download file dari URL (streaming, support file besar). Parent dir otomatis."""
    import urllib.request
    import urllib.error
    try:
        parent = os.path.dirname(os.path.abspath(output))
        os.makedirs(parent, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "KIRO-AGENTIC/1.3"})
        with urllib.request.urlopen(req, timeout=120) as resp, open(output, 'wb') as f:
            total = 0
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                f.write(chunk)
                total += len(chunk)
        size_str = f"{total/1024/1024:.2f} MB" if total > 1024*1024 else f"{total/1024:.1f} KB"
        return f"✅ Download berhasil: {output} ({size_str})."
    except urllib.error.HTTPError as he:
        return f"Error download_file: HTTP {he.code} - {he.reason}"
    except Exception as ex:
        return f"Error download_file: {ex}"

def native_self_check(agent_path, agent_backup):
    """Safety net: jika kode sumber agen rusak setelah self-edit, auto-restore dari backup."""
    result = subprocess.run(
        [sys.executable, '-m', 'py_compile', agent_path],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return "✅ SELF-CHECK PASS: sintaks kode sumber agen valid."
    # Compile gagal → auto-restore
    try:
        if os.path.exists(agent_backup):
            shutil.copy2(agent_backup, agent_path)
            return (f"🛡️ SELF-HEALING AKTIF: sintaks rusak setelah self-edit!\\n"
                    f"Output error: {result.stderr.strip()[:500]}\\n"
                    f"→ Backup otomatis di-restore dari {agent_backup}. "
                    f"Coba edit lagi dengan target yang lebih presisi.")
        return (f"⚠️ SELF-CHECK GAGAL dan backup tidak ditemukan!\\n"
                f"Output error: {result.stderr.strip()[:500]}")
    except Exception as ex:
        return f"Error self_check/restore: {ex}"

def main():
    clear_screen()
    show_logo()
    
    active_model = select_model()
    
    clear_screen()
    show_logo()
    
    status_text = Text()
    status_text.append("Status: ", style="bold green")
    status_text.append("ONLINE\\n", style="bold cyan")
    status_text.append("Model Aktif: ", style="bold green")
    status_text.append(f"{active_model}\\n", style="bold yellow")
    status_text.append("Tujuan Utama: ", style="bold green")
    status_text.append("Koding, Analisa, Temuan, Cek Error", style="italic white")
    
    console.print(Panel(status_text, border_style="green"))
    console.print("[italic gray]Ketik '/menu' untuk melihat daftar perintah, atau 'exit' untuk keluar.[/italic gray]\\n")
    
    # === SELF-IMPROVEMENT: Lokasi kode sumber agen sendiri ===
    agent_path = os.path.abspath(__file__)
    agent_backup = agent_path + ".backup"
    agent_version_file = os.path.join(os.path.dirname(agent_path), ".kiro_version")
    
    # Cek & siapkan direktori penyimpanan tool
    tools_dir = os.path.join(os.getcwd(), "kiro_tools")
    if not os.path.exists(tools_dir):
        os.makedirs(tools_dir, exist_ok=True)
        
    # Ambil list custom script tool yang sudah ada (hanya file .py/.sh, kecualikan txt catatan)
    existing_tools = [f for f in os.listdir(tools_dir) if not f.endswith('.txt')]
    tools_list_text = "\\n".join([f"- {tool}" for tool in existing_tools]) if existing_tools else "- (Belum ada custom script tool)"

    # Baca CLI/External tools yang diinstall
    cli_tools_file = os.path.join(tools_dir, "installed_cli_tools.txt")
    if os.path.exists(cli_tools_file):
        with open(cli_tools_file, 'r', encoding='utf-8') as f:
            cli_tools_text = f.read().strip()
    else:
        cli_tools_text = "- (Belum ada tool eksternal yang terdaftar)"
    
    system_prompt = f"""Anda adalah Agentic AI profesional dengan AKSES PENUH ke terminal/sistem operasi.
Tujuan utama Anda:
- Koding (Programming)
- Analisa
- Temuan (Discovery/Research)
- Browsing (Gunakan kemampuan search/analisa web jika diperlukan)
- Cek Error (Debugging)

Instruksi Agen (PENTING):
1. Selesaikan setiap tugas/prompt secara tuntas dari awal hingga selesai. JANGAN MUDAH MENYERAH jika terjadi error. Coba metode alternatif jika metode pertama gagal.
2. Pastikan balasan Anda rapih, profesional, dan berwarna (gunakan format markdown dengan baik). Gunakan blok kode (```) untuk setiap baris kode atau log error.
3. EVOLUSI & SELF-REPAIR: Karena Anda memiliki akses terminal, Anda bisa membuat script tambahan (tools baru) secara dinamis menggunakan Python/Bash.
4. PENYIMPANAN CUSTOM TOOLS: Jika Anda membuat *script kustom* (seperti scraper manual), SIMPAN ke folder `./kiro_tools/`.
5. PENGGUNAAN ALAT/TOOL EKSTERNAL (SANGAT PENTING): Jika diminta memakai alat CLI (misal `agent-browser`, `nmap`, dll) atau diminta "mengecek/melakukan" sesuatu:
    - Anda WAJIB langsung mengeksekusi perintah terminal dengan tag `<invoke name="antml:computer:execute_command">`. JANGAN HANYA MENJAWAB DENGAN TEKS KOSONG.
    - DILARANG KERAS membuang waktu dengan memeriksa seluruh daftar dependency (seperti `pip list` atau `npm list`) untuk mencari alat tersebut.
    - LANGSUNG jalankan saja perintah CLI aslinya di terminal (misal `<invoke...><parameter name="command">agent-browser "..."</parameter></invoke>`). Jika alatnya ternyata belum terinstall (muncul error 'command not found'), barulah Anda install.
    - DILARANG KERAS membuat script Python (.py) atau Bash (.sh) baru hanya untuk membungkus (wrapper) atau memanggil alat tersebut! Gunakan langsung CLI-nya.
    - Setiap selesai menginstall alat CLI baru, WAJIB catat nama alat dan contoh perintahnya ke dalam file `./kiro_tools/installed_cli_tools.txt`.
11. NARASI AKTIVITAS (SANGAT SINGKAT): Keterangan aktivitas (sebelum memanggil alat) HARUS dibuat SANGAT SINGKAT DAN PADAT (maksimal 1-2 baris kalimat). Contoh: "Mengecek RAM dengan `free -h`..." atau "Gagal, mencoba `cat /proc/meminfo`...". JANGAN membuat daftar/list panjang lebar jika tidak perlu.
12. ANTI-HALUSINASI (SANGAT PENTING): JANGAN PERNAH menebak, mengarang, atau memalsukan hasil dari sebuah perintah terminal sebelum perintah tersebut benar-benar dieksekusi! Di tahap perencanaan (sebelum memanggil <invoke>), Anda HANYA boleh menuliskan rencana singkat. Jangan membuat tabel hasil palsu atau kesimpulan sebelum menerima balasan output asli dari sistem.
13. TO-THE-POINT: Jangan over-engineering. Jika tugas bisa diselesaikan dengan 1 command langsung, langsung eksekusi tanpa banyak bicara.

🔥 SELF-HEALING & SELF-IMPROVEMENT (LEVEL TERTINGGI) 🔥
Anda adalah agen yang mampu mengembangkan diri sendiri (self-improving agent).
- Lokasi kode sumber Anda sendiri: `{agent_path}`
- Backup otomatis tersimpan di: `{agent_backup}`
- Anda DIIZINKAN dan DIHARAPKAN untuk MEMBACA, MEMODIFIKASI, dan MENGEMBANGKAN kode sumber Anda sendiri (file di atas) menggunakan terminal.
- Jika Anda menemui kebuntuan (library tidak support, fitur kurang), atau user meminta fitur baru pada diri Anda sendiri, SEGERA modifikasi kode sumber Anda.
ATURAN MUTLAK SELF-IMPROVEMENT:
A. Sebelum mengedit kode sumber, WAJIB buat backup terlebih dahulu: `cp {agent_path} {agent_backup}`
B. JANGAN PERNAH menghapus arsitektur utama (fungsi main(), system loop, UI Rich, select_model, dan handler perintah). Anda hanya boleh MENAMBAH atau MENYEMPURNAKAN fitur, bukan menguranginya.
C. Setelah memodifikasi diri sendiri, WAJIB verifikasi sintaks dengan `python -m py_compile {agent_path}` sebelum menyatakan selesai.
D. Setelah modifikasi berhasil, WAJIB naikkan versi dan catat changelog (lihat perintah /self di bawah), lalu sarankan user mengetik `/restart` agar kode baru dimuat.
E. Hanya gunakan sed/awk/python script untuk edit beda (patch), JANGAN rewrite seluruh file sekaligus kecuali benar-benar diperlukan.

🔥 NATIVE FILE TOOLS (v1.3 — GUNAKAN INI UNTUK EDIT FILE, LEBIH AMAN DARI sed/echo!):
1. Membaca file (hemat memori, gunakan start/end untuk file besar):
<read_file path="./file.py" start="1" end="100" />
2. Menulis file baru (parent dir otomatis dibuat):
<write_file path="./hello.txt">Hello World!</write_file>
   Atribut append="true" untuk menambah ke akhir file tanpa overwrite.
3. Edit file secara presisi (Surgical Search & Replace — target HARUS unik):
<edit_file path="./file.py">
<target>
kode lama yang persis sama
</target>
<replacement>
kode baru pengganti
</replacement>
</edit_file>

DAFTAR TOOL CLI/EKSTERNAL YANG TERPASANG:
{cli_tools_text}

Gunakan file/alat di atas untuk mempermudah pekerjaan Anda tanpa harus menulis ulang atau meraba-raba dari awal.

PENTING - AKSES TERMINAL DAN BROWSING:
Anda MEMILIKI AKSES ke terminal lokal secara FULL/PENUH. Jangan pernah berkata bahwa Anda tidak memiliki akses. Anda bisa mensimulasikan error, mencari tahu penyebab gagal, dan menyelesaikan masalah yang dihadapi.
Anda juga bisa dan memiliki akses untuk menggunakan Chromium/Browser (misal via curl, wget, python requests, atau playwright/puppeteer jika diinstall) untuk web scraping, debugging web, dll.

Untuk menjalankan perintah di terminal, Anda HARUS menggunakan format XML berikut:

<function_calls>
<invoke name="antml:computer:execute_command">
<parameter name="command">PERINTAH ANDA DI SINI</parameter>
</invoke>
</function_calls>

Selalu gunakan format di atas jika Anda butuh berinteraksi dengan sistem, file, jaringan, atau membuka Chromium/Browser via CLI.
"""
    
    messages = [{"role": "system", "content": system_prompt}]
    
    while True:
        try:
            user_input = Prompt.ask("\\n[bold green]➜ Anda[/bold green]")
            if user_input.lower() in ['exit', 'quit', '/exit', '/quit']:
                console.print("[bold red]Mematikan Agen... Sampai jumpa![/bold red]")
                break
                
            if user_input.lower() == '/menu':
                console.print("\\n[bold cyan]=== MENU PERINTAH ===[/bold cyan]")
                console.print("[yellow]/menu[/yellow]    - Menampilkan daftar perintah ini")
                console.print("[yellow]/model[/yellow]   - Mengganti model AI yang aktif")
                console.print("[yellow]/history[/yellow] - Menampilkan jumlah riwayat percakapan")
                console.print("[yellow]/clear[/yellow]    - Menghapus riwayat percakapan dan membersihkan layar")
                console.print("[yellow]/restart[/yellow] - Mereset sesi percakapan (ingatan AI)")
                console.print("[yellow]/self[/yellow]    - Info kode sumber, versi, & changelog diri sendiri")
                console.print("[yellow]/improve[/yellow] - Mode Self-Improvement (kembangkan diri sendiri)")
                console.print("[yellow]/exit[/yellow]    - Keluar dari program\\n")
                continue
                
            if user_input.lower() == '/model':
                active_model = select_model()
                console.print(f"[bold green]Model berhasil diubah ke:[/bold green] {active_model}\\n")
                continue
                
            if user_input.lower() == '/history':
                user_msgs = sum(1 for m in messages if m['role'] == 'user')
                asst_msgs = sum(1 for m in messages if m['role'] == 'assistant')
                console.print(f"\\n[bold cyan]=== STATISTIK RIWAYAT ===[/bold cyan]")
                console.print(f"Total pesan tersimpan: {len(messages)}")
                console.print(f"Pesan dari Anda: {user_msgs}")
                console.print(f"Pesan dari AI: {asst_msgs}\\n")
                continue
                
            if user_input.lower() in ['/restart', '/clear', '/hapus']:
                messages = [messages[0]]
                os.system('cls' if os.name == 'nt' else 'clear')
                console.print("\\n[bold green]✅ Riwayat percakapan berhasil dihapus. Layar dan ingatan AI telah dibersihkan![/bold green]\\n")
                continue

            # === SELF-IMPROVEMENT: /self — info kode sumber & changelog diri sendiri ===
            if user_input.lower() == '/self':
                try:
                    with open(agent_path, 'r', encoding='utf-8') as f:
                        lines_count = sum(1 for _ in f)
                    size_bytes = os.path.getsize(agent_path)
                    mtime = time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(agent_path)))
                except Exception as e:
                    lines_count, size_bytes, mtime = "?", "?", f"(error: {e})"

                version = "1.0"
                changelog = "(Belum ada changelog)"
                try:
                    if os.path.exists(agent_version_file):
                        with open(agent_version_file, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                            parts = content.split('---CHANGELOG---')
                            version = parts[0].strip() or "1.0"
                            if len(parts) > 1 and parts[1].strip():
                                changelog = parts[1].strip()
                except Exception:
                    pass

                backup_exists = os.path.exists(agent_backup)

                info = Table(title="🧬 SELF INFO — KIRO AGENTIC v1", show_header=True, header_style="bold magenta")
                info.add_column("Properti", style="bold cyan")
                info.add_column("Nilai", style="green")
                info.add_row("Kode Sumber", agent_path)
                info.add_row("Backup", f"{agent_backup} {'✅' if backup_exists else '❌'}")
                info.add_row("Versi", f"v{version}")
                info.add_row("Jumlah Baris", str(lines_count))
                info.add_row("Ukuran", f"{size_bytes/1024:.1f} KB" if isinstance(size_bytes, int) else str(size_bytes))
                info.add_row("Terakhir Dimodifikasi", str(mtime))
                console.print(info)
                console.print(Panel(changelog, title="[bold yellow]📜 CHANGELOG[/bold yellow]", border_style="yellow"))
                console.print("[italic gray]Gunakan /improve untuk mengembangkan diri sendiri, lalu /restart untuk memuat ulang.[/italic gray]\\n")
                continue

            # === SELF-IMPROVEMENT: /improve — mode pengembangan diri ===
            if user_input.lower() == '/improve':
                console.print(Panel(
                    f"[bold yellow]MODE SELF-IMPROVEMENT AKTIF[/bold yellow]\\n\\n"
                    f"Kode sumber Anda: [cyan]{agent_path}[/cyan]\\n"
                    f"Backup saat ini: [cyan]{agent_backup}[/cyan]\\n\\n"
                    f"Deskripsikan fitur yang ingin Anda tambahkan/perbaiki pada diri Anda sendiri,\\n"
                    f"contoh: 'Tambahkan fitur export chat ke file markdown'.\\n"
                    f"Agen akan: [green]1)[/green] backup dirinya → [green]2)[/green] baca & edit kode sumbernya → [green]3)[/green] verifikasi sintaks → [green]4)[/green] update changelog → [green]5)[/green] minta Anda /restart.",
                    border_style="magenta"
                ))
                improve_request = Prompt.ask("\\n[bold green]➜ Fitur apa yang ingin dikembangkan?[/bold green]")
                if not improve_request.strip():
                    continue
                user_input = (
                    f"MODE SELF-IMPROVEMENT: Saya (agen) diminta untuk mengembangkan diri sendiri.\\n"
                    f"Permintaan fitur: {improve_request}\\n\\n"
                    f"IKUTI ATURAN SELF-IMPROVEMENT di system prompt:\\n"
                    f"1. Backup dulu: cp {agent_path} {agent_backup}\\n"
                    f"2. Baca kode sumbermu sendiri di {agent_path} (gunakan sed -n 'X,Yp' untuk baca per bagian).\\n"
                    f"3. Edit dengan sed/python patch. JANGAN hapus arsitektur utama (main, select_model, UI, loop).\\n"
                    f"4. Verifikasi: python -m py_compile {agent_path}\\n"
                    f"5. Update versi & changelog di {agent_version_file} (format: '<versi>\\n---CHANGELOG---\\n<tanggal> - <perubahan>').\\n"
                    f"6. Jika sukses, beri tahu saya untuk mengetik /restart."
                )
                # Jatuh ke pipeline normal (tidak continue) agar AI mengeksekusi langkah-langkahnya
            
            if not user_input.strip():
                continue
                
            messages.append({"role": "user", "content": user_input})
            
            with console.status("[bold cyan]Agent sedang berpikir, mengeksekusi, dan menganalisa di latar belakang...[/bold cyan]", spinner="dots2"):
                while True:
                    # Membatasi "ingatan" AI (Sliding Window Context)
                    # Simpan prompt sistem (index 0) dan 15 percakapan/hasil eksekusi terakhir
                    if len(messages) > 15:
                        messages = [messages[0]] + messages[-14:]
                        
                    max_retries = 5
                    retry_count = 0
                    response = None
                    
                    while retry_count < max_retries:
                        try:
                            response = client.chat.completions.create(
                                model=active_model,
                                messages=messages,
                                timeout=30.0
                            )
                            break
                        except Exception as e:
                            retry_count += 1
                            console.print(f"[dim yellow]⚠ API sibuk/timeout (percobaan {retry_count}/{max_retries}). Mencoba ulang...[/dim yellow]")
                            time.sleep(2)
                            
                    if response is None:
                        break
                    
                    if isinstance(response, str):
                        reply = response
                    elif hasattr(response, 'choices') and len(response.choices) > 0:
                        reply = response.choices[0].message.content
                    elif isinstance(response, dict) and 'choices' in response:
                        reply = response['choices'][0]['message']['content']
                    else:
                        reply = str(response)
                    
                    # Remove <function_calls> tags completely
                    reply = re.sub(r'</?function_calls>', '', reply, flags=re.IGNORECASE)
                    
                    reply = re.sub(r'```[a-z]*\s*(?=<invoke)', '', reply, flags=re.IGNORECASE)
                    reply = re.sub(r'(</invoke>)\s*```', r'\\1', reply, flags=re.IGNORECASE)
                    
                    messages.append({"role": "assistant", "content": reply})
                    
                    # Eksekusi tool/command jika ada
                    commands_to_run = re.findall(r'<invoke name="antml:computer:execute_command">\s*<parameter name="command">(.*?)</parameter>\s*</invoke>', reply, flags=re.DOTALL | re.IGNORECASE)
                    
                    # === v1.2: Parsing NATIVE FILE TOOLS ===
                    def _unesc(s):
                        return s.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&') if s else s
                    native_calls = []
                    for m in re.finditer(r'<read_file\s+path="([^"]+)"(?:\s+start="(\d+)")?(?:\s+end="(\d+)")?\s*/?>', reply, flags=re.IGNORECASE):
                        native_calls.append(('read_file', native_read_file(m.group(1), m.group(2), m.group(3))))
                    for m in re.finditer(r'<write_file\s+path="([^"]+)"(?:\s+append="(true|false)")?\s*>(.*?)</write_file>', reply, flags=re.DOTALL | re.IGNORECASE):
                        native_calls.append(('write_file', native_write_file(m.group(1), _unesc(m.group(3)), append=(m.group(2) == 'true'))))
                    for m in re.finditer(r'<edit_file\s+path="([^"]+)">\s*<target>\n?(.*?)\n?</target>\s*<replacement>\n?(.*?)\n?</replacement>\s*</edit_file>', reply, flags=re.DOTALL | re.IGNORECASE):
                        edit_path = m.group(1)
                        edit_result = native_edit_file(edit_path, _unesc(m.group(2)), _unesc(m.group(3)))
                        native_calls.append(('edit_file', edit_result))
                        # SAFETY NET: jika agen mengedit kode sumbernya sendiri, auto-verify & auto-restore
                        if os.path.abspath(edit_path) == agent_path:
                            native_calls.append(('self_check', native_self_check(agent_path, agent_backup)))
                    # === v1.3: AUTOMATIC TOOLKIT INTERCEPTION ===
                    for m in re.finditer(r'<list_dir\s+path="([^"]+)"(?:\s+recursive="(true|false)")?\s*/?>', reply, flags=re.IGNORECASE):
                        native_calls.append(('list_dir', native_list_dir(m.group(1), m.group(2) or "false")))
                    for m in re.finditer(r'<search_content\s+path="([^"]+)"\s+pattern="([^"]+)"(?:\s+recursive="(true|false)")?(?:\s+ignore_case="(true|false)")?\s*/?>', reply, flags=re.IGNORECASE):
                        native_calls.append(('search_content', native_search_content(m.group(1), _unesc(m.group(2)), m.group(3) or "false", m.group(4) or "false")))
                    for m in re.finditer(r'<http_request\s+url="([^"]+)"(?:\s+method="(GET|POST|PUT|DELETE|PATCH)")?(?:\s+headers="([^"]*)")?(?:\s+body="([^"]*)")?\s*/?>', reply, flags=re.IGNORECASE):
                        native_calls.append(('http_request', native_http_request(m.group(1), m.group(2) or "GET", m.group(4), m.group(3))))
                    for m in re.finditer(r'<download_file\s+url="([^"]+)"\s+output="([^"]+)"\s*/?>', reply, flags=re.IGNORECASE):
                        native_calls.append(('download_file', native_download_file(m.group(1), m.group(2))))
                    
                    if commands_to_run or native_calls:
                        # Tampilkan apa yang sedang dipikirkan/direncanakan AI sebelum mengeksekusi
                        display_text = re.sub(r'<invoke.*?</invoke>', '', reply, flags=re.DOTALL | re.IGNORECASE).strip()
                        if display_text:
                            console.print("\\n")
                            console.print(Panel(
                                Markdown(display_text),
                                title="[bold yellow]🤖 Aktivitas Agent[/bold yellow]",
                                border_style="yellow",
                                padding=(1, 2)
                            ))
                            
                        tool_outputs = ""
                        # === v1.2: Eksekusi NATIVE TOOLS ===
                        for tool_name, tool_result in native_calls:
                            console.print(f"[dim magenta]➔ Native tool [{tool_name}] dieksekusi[/dim magenta]")
                            tool_outputs += f"Native tool [{tool_name}] result:\\n{tool_result}\\n\\n"
                        for cmd in commands_to_run:
                            cmd = cmd.strip()
                            console.print(f"[dim cyan]➔ Menjalankan perintah di latar belakang:[/dim cyan] [dim]{cmd}[/dim]")
                            try:
                                process = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
                                output = process.stdout + process.stderr
                                if not output.strip():
                                    output = "(Command completed with no output)"
                            except Exception as e:
                                output = f"Error executing command: {str(e)}"
                                
                            # Batasi panjang output agar tidak terlalu panjang (max 4000 char per output)
                            if len(output) > 4000:
                                output = output[:4000] + "\\n... (output dipotong karena terlalu panjang)"
                                
                            tool_outputs += f"Command: {cmd}\\nOutput:\\n{output}\\n\\n"
                        
                        # Tambahkan output ke message lalu ulangi loop agar AI merespon
                        messages.append({"role": "user", "content": f"Berhasil menjalankan perintah di latar belakang. Berikut adalah outputnya (tolong analisa dan berikan ringkasan hasil kerja, atau lanjutkan langkah berikutnya jika diperlukan):\\n\\n<tool_response>\\n{tool_outputs}\\n</tool_response>"})
                    else:
                        # Jika tidak ada perintah, keluar dari loop AI
                        break
                        
            if response is None:
                console.print("[bold red]✖ Gagal mendapatkan respon setelah 5 kali percobaan. Silakan coba lagi.[/bold red]")
                continue
                
            # Rendering markdown yang rapih HANYA untuk hasil akhir
            console.print("\\n")
            
            # Hilangkan XML tags jika tersisa di hasil akhir
            final_display = re.sub(r'<invoke.*?</invoke>', '', reply, flags=re.DOTALL | re.IGNORECASE)
            
            console.print(Panel(
                Markdown(final_display.strip()), 
                title="[bold magenta]KIRO AGENTIC - HASIL KERJA[/bold magenta]", 
                border_style="cyan",
                padding=(1, 2)
            ))
                    
            
        except KeyboardInterrupt:
            console.print("\\n[bold red]Sesi diakhiri oleh pengguna.[/bold red]")
            break
        except Exception as e:
            console.print(f"\\n[bold red]✖ Error:[/bold red] {str(e)}")

if __name__ == "__main__":
    main()


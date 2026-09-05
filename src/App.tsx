/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Copy, Download, Check, FileCode, Terminal } from 'lucide-react';

const configCode = `# config.py

# Konfigurasi API
API_KEY = "sk-qwen-395decf00000614bd1f8ab7d2a22dac62c903af66c9674d5"
BASE_URL = "https://autoapp.biz.id/v1"
`;

const setupCode = `# setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("kiro_core.py", compiler_directives={'language_level': "3"})
)
`;

const runCode = `# run.py
import kiro_core

if __name__ == "__main__":
    kiro_core.main()
`;

const instructionsCode = `# CARA PENGGUNAAN (Terminal/CMD)

# 1. Pastikan Anda sudah menginstall library yang dibutuhkan:
pip install rich openai cython

# 2. Jalankan perintah ini untuk mengompilasi kiro_core.py menjadi biner rahasia:
python setup.py build_ext --inplace

# 3. Setelah berhasil, akan muncul file biner (misal: kiro_core.cp310-win_amd64.pyd atau .so)
# Anda bisa MENGHAPUS file kiro_core.py yang asli agar kodenya tidak bisa dibaca orang lain.

# 4. Jalankan aplikasi Anda menggunakan:
python run.py

# 5. Jika ingin mengganti API KEY atau URL, cukup edit file config.py kapan saja!
`;

const coreCode = `# kiro_core.py
import os
import sys
import re
import json
import shutil
import subprocess
import time

# IMPORT DARI FILE CONFIG
import config

try:
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.text import Text
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.prompt import Prompt
    from rich.table import Table
    from openai import OpenAI
except ImportError:
    print("Harap install dependencies terlebih dahulu: pip install rich openai")
    sys.exit(1)

console = Console()

# MENGGUNAKAN KONFIGURASI DARI config.py
client = OpenAI(
    api_key=config.API_KEY, 
    base_url=config.BASE_URL,
    timeout=60.0,
    default_headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
)

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
    
    colors = [
        "cyan", "green", "yellow", "magenta", "blue",
        "red", "bright_cyan", "bright_green", "bright_yellow",
        "bright_magenta", "bright_blue", "bright_red"
    ]
    
    console.print("\\n[bold green]╔═══════════════════════════════════════════════════╗[/bold green]")
    console.print("[bold green]║      📚 KATALOG MODEL AI AKTIF 📚                 ║[/bold green]")
    console.print("[bold green]╚═══════════════════════════════════════════════════╝[/bold green]\\n")
    
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
    
    custom_num = len(models) + 1
    custom_panel = Panel(
        "[bold white]✏️  Masukkan model sendiri[/bold white]",
        title=f"[bold white]No. {custom_num}[/bold white]",
        border_style="white",
        padding=(0, 2),
        width=44
    )
    panels.append(custom_panel)
    
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

def native_read_file(path, start=None, end=None):
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

def native_list_dir(path, recursive="false"):
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
                        continue
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
    result = subprocess.run(
        [sys.executable, '-m', 'py_compile', agent_path],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return "✅ SELF-CHECK PASS: sintaks kode sumber agen valid."
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
    
    agent_path = os.path.abspath(__file__)
    agent_backup = agent_path + ".backup"
    agent_version_file = os.path.join(os.path.dirname(agent_path), ".kiro_version")
    
    tools_dir = os.path.join(os.getcwd(), "kiro_tools")
    if not os.path.exists(tools_dir):
        os.makedirs(tools_dir, exist_ok=True)
        
    existing_tools = [f for f in os.listdir(tools_dir) if not f.endswith('.txt')]
    tools_list_text = "\\n".join([f"- {tool}" for tool in existing_tools]) if existing_tools else "- (Belum ada custom script tool)"

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

[Sistem siap menerima perintah dari user]"""
    
    # Placeholder for the main loop
    while True:
        try:
            cmd = Prompt.ask("[bold green]User[/bold green]")
            if cmd.strip().lower() in ['exit', 'quit']:
                console.print("[bold red]Mematikan agen...[/bold red]")
                break
            console.print(f"[bold cyan]Agentic AI:[/bold cyan] Menerima perintah: {cmd}")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
`;

function CodeBlock({ filename, content }: { filename: string, content: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-[#1e1e1e] border border-gray-700 rounded-lg overflow-hidden mb-6 flex flex-col">
      <div className="flex items-center justify-between px-4 py-2 bg-[#2d2d2d] border-b border-gray-700">
        <div className="flex items-center space-x-2 text-gray-300">
          <FileCode size={18} className="text-blue-400" />
          <span className="font-mono text-sm font-semibold">{filename}</span>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleCopy}
            className="flex items-center space-x-1 px-3 py-1.5 text-xs font-medium text-gray-300 bg-[#3d3d3d] hover:bg-[#4d4d4d] rounded transition-colors cursor-pointer"
          >
            {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
            <span>{copied ? 'Copied!' : 'Copy'}</span>
          </button>
          <button
            onClick={handleDownload}
            className="flex items-center space-x-1 px-3 py-1.5 text-xs font-medium text-white bg-blue-600 hover:bg-blue-500 rounded transition-colors cursor-pointer"
          >
            <Download size={14} />
            <span>Download</span>
          </button>
        </div>
      </div>
      <div className="p-4 overflow-x-auto">
        <pre className="text-gray-300 font-mono text-xs md:text-sm whitespace-pre">
          <code>{content}</code>
        </pre>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <div className="min-h-screen bg-[#121212] text-gray-100 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <header className="mb-8 border-b border-gray-800 pb-6">
          <h1 className="text-3xl font-bold flex items-center space-x-3 mb-3">
            <Terminal className="text-blue-500" size={32} />
            <span>Python Cython Toolkit</span>
          </h1>
          <p className="text-gray-400">
            Berikut adalah file-file yang telah disiapkan untuk mengamankan Script Anda menggunakan Cython. 
            Anda bisa mengunduh (Download) atau menyalin (Copy) kodenya ke komputer Anda.
          </p>
        </header>

        <div className="space-y-8">
          <section>
            <h2 className="text-xl font-semibold mb-3 text-blue-400">1. File Konfigurasi (Bisa diedit kapan saja)</h2>
            <p className="text-sm text-gray-400 mb-3">
              File ini digunakan untuk menyimpan API Key dan URL. Karena terpisah dari logika inti, Anda bebas mengubah isinya tanpa perlu compile ulang.
            </p>
            <CodeBlock filename="config.py" content={configCode} />
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3 text-blue-400">2. Script Inti (Akan disembunyikan/dicompile)</h2>
            <p className="text-sm text-gray-400 mb-3">
              Ini adalah script utama Anda yang sudah kami edit sedikit untuk mengambil data dari <code>config.py</code>. 
              File ini akan dikompilasi (diubah jadi bahasa mesin) dan bisa dihapus setelah berhasil.
            </p>
            <CodeBlock filename="kiro_core.py" content={coreCode} />
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3 text-blue-400">3. Script Build Cython</h2>
            <p className="text-sm text-gray-400 mb-3">
              Gunakan script ini untuk menginstruksikan Cython mengunci file <code>kiro_core.py</code> menjadi file biner `.pyd` atau `.so`.
            </p>
            <CodeBlock filename="setup.py" content={setupCode} />
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3 text-blue-400">4. Script Entry Point (Pemanggil)</h2>
            <p className="text-sm text-gray-400 mb-3">
              Karena file core sudah berbentuk biner, Anda butuh file kecil ini untuk menjalankannya (<code>python run.py</code>).
            </p>
            <CodeBlock filename="run.py" content={runCode} />
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3 text-green-400">5. Panduan Singkat</h2>
            <p className="text-sm text-gray-400 mb-3">
              Ikuti perintah terminal di bawah ini secara berurutan.
            </p>
            <CodeBlock filename="instructions.txt" content={instructionsCode} />
          </section>
        </div>
      </div>
    </div>
  );
}


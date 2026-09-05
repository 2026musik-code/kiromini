import os
import sys
import re
import json
import shutil
import subprocess
import time

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

# Ambil dari file .env via os.environ (di-inject otomatis oleh generator)
API_KEY = os.environ.get("KEY_MINI")
BASE_URL = os.environ.get("URL_MINI")

# Setup Client
client = OpenAI(
    api_key=API_KEY, 
    base_url=BASE_URL,
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
    console.print("\n[bold cyan]Sedang men-scan model AI aktif di server...[/bold cyan]")
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
    console.print("\n[bold green]╔═══════════════════════════════════════════════════╗[/bold green]")
    console.print("[bold green]║      📚 KATALOG MODEL AI AKTIF 📚                 ║[/bold green]")
    console.print("[bold green]╚═══════════════════════════════════════════════════╝[/bold green]\n")
    
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
    
    # Tampilkan dalam layout grid 3 kolom
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
    
    choice = Prompt.ask(f"\n[bold yellow]📖 Pilih nomor model (1-{custom_num})[/bold yellow]", default="1")
    
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

def main():
    clear_screen()
    show_logo()
    
    active_model = select_model()
    
    clear_screen()
    show_logo()
    
    status_text = Text()
    status_text.append("Status: ", style="bold green")
    status_text.append("ONLINE\n", style="bold cyan")
    status_text.append("Model Aktif: ", style="bold green")
    status_text.append(f"{active_model}\n", style="bold yellow")
    status_text.append("Tujuan Utama: ", style="bold green")
    status_text.append("Koding, Analisa, Temuan, Cek Error", style="italic white")
    
    console.print(Panel(status_text, border_style="green"))
    console.print("[italic gray]Sistem Agentic Aktif - Siap menerima perintah.[/italic gray]\n")
    
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

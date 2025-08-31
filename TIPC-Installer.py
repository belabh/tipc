#!/usr/bin/env python3

import os, sys, signal, shutil

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.align import Align
from rich.text import Text
import ctypes

console = Console()
TIPC_FILES = {
    "Linux": "TIPC-Linux.py",
    "Windows": "TIPC-Windows.py",
    "MacOS": "TIPC-macOS.py"
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def error_exit(msg: str):
    console.print(Panel(Align.center(msg), title="[red]ERROR[/red]", border_style="red"))
    sys.exit(1)

def check_root():
    if sys.platform.startswith(("linux", "darwin")):
        if os.geteuid() != 0:
            error_exit("The installer requires Root permission to install! Please try again with 'sudo'")
    elif sys.platform.startswith("win"):
        if not ctypes.windll.shell32.IsUserAnAdmin():
            error_exit("The installer requires Administrator permission! Please open new CMD window as Administrator and try again")

def show_banner():
    banner = Text("      TIPC • Installer", style="bold cyan")
    banner.append("\n       Author • Belal", style="dim white")
    banner.append("\nhttps://github.com/belabh/tipc", style="bold green")

    console.print(Panel(Align.center(banner), border_style="cyan", padding=(1, 2)))

def available_versions():
    return [v for v, f in TIPC_FILES.items() if os.path.exists(f)] or error_exit("No TIPC files found!")

def select_version(available, recommended):
    console.print(Panel(Align.center("Available versions:"), border_style="magenta"))
    for idx, ver in enumerate(available, 1):
        mark = " [green](Recommended)[/green]" if ver == recommended else ""
        console.print(f"  {idx}. {ver}{mark}")

    while True:
        choice = Prompt.ask("Select version (number)", default=str(available.index(recommended)+1))
        if choice.isdigit() and 1 <= int(choice) <= len(available):
            selected = available[int(choice)-1]
            if selected != recommended:
                confirm = Prompt.ask(f"[yellow]Installing {selected}. Continue?[/yellow] (Y/N)", choices=["Y","y","N","n"])
                if confirm.lower() != "y": continue
            return selected
        console.print("[red]Invalid choice![/red]")

def get_paths():
    if sys.platform.startswith("linux"):
        return "/usr/share/tipc/tipc.py", "/usr/bin/tipc"
    if sys.platform.startswith("darwin"):
        return "/usr/local/share/tipc/tipc.py", "/usr/local/bin/tipc"
    if sys.platform.startswith("win"):
        return r"C:\Program Files\TIPC\TIPC.py", r"C:\Windows\TIPC.bat"
    error_exit("Unsupported OS!")

def install(version_file, version_name):
    target_file, wrapper_file = get_paths()
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    shutil.copyfile(version_file, target_file)

    wrapper_content = f'@echo off\npython "{target_file}" %*' if sys.platform.startswith("win") else f'#! /bin/sh\nexec python3 "{target_file}" "$@"'
    with open(wrapper_file, "w") as f: f.write(wrapper_content)

    if not sys.platform.startswith("win"):
        os.chmod(wrapper_file, 0o755)
        os.chmod(target_file, 0o755)

    console.print(Panel(Align.center(f"[green]TIPC {version_name} installed successfully![/green]\nType 'tipc' to run it"), border_style="green"))

def uninstall():
    target_file, wrapper_file = get_paths()
    for path in (target_file, wrapper_file):
        if os.path.exists(path): os.remove(path)
    console.print(Panel(Align.center("[yellow] - TIPC removed successfully![/yellow] - "), border_style="yellow"))

def main():
    signal.signal(signal.SIGINT, lambda *_: console.print("\n[yellow]Exiting...[/yellow]") or sys.exit(0))
    clear_screen(); check_root(); show_banner()
    available = available_versions()
    recommended = "Linux" if sys.platform.startswith("linux") else "Windows" if sys.platform.startswith("win") else "MacOS"
    
    action = Prompt.ask("[cyan][+][/cyan] Install (Y) | Uninstall (N)", choices=["Y","y","N","n"])
    if action.lower() == "y":
        version = select_version(available, recommended)
        install(TIPC_FILES[version], version)
    else: uninstall()

if __name__ == "__main__":
    main()

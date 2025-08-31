#!/usr/bin/env python3

import time, sys, signal, random, socket, subprocess, os

try:
    from pathlib import Path
    import requests
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, IntPrompt
    from rich.align import Align
except ImportError:
    print("Error: Please run 'pip install rich requests' and try again")
    sys.exit(1)

console = Console()

def clear_screen():
    os.system('clear')

def error_exit(msg: str):
    console.print(Panel(msg, title="[red]ERROR[/red]", border_style="red"))
    sys.exit(1)

def run_command(cmd: list[str], check=False, **kwargs):
    try:
        subprocess.run(cmd, check=check, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kwargs)
    except subprocess.CalledProcessError:
        return False
    return True

def check_root():
    if os.geteuid() != 0:
        error_exit("TIPC requires root permissions to work!\n[yellow]Please run again with 'sudo'")

def check_tor():
    if not run_command(['which', 'tor']):
        error_exit("Tor is not installed!\nPlease install Tor first and try again.")

def check_port(port: int = 9050) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=3):
            return True
    except OSError:
        return False

def start_tor():
    if check_port():
        console.print("[green]Tor service is already running[/green]")
        return
    
    with console.status("[yellow]Starting Tor service...[/yellow]", spinner="dots"):
        subprocess.run(['pkill', '-f', 'tor'], stderr=subprocess.DEVNULL)
        time.sleep(2)

        for cmd in [['systemctl', 'start', 'tor'], ['service', 'tor', 'start']]:
            try:
                subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL, timeout=10)
                time.sleep(3)
                if check_port():
                    console.print("[green]Tor service started successfully[/green]")
                    return
            except:
                continue
        error_exit("Failed to start Tor service! Please make sure you have Tor installed")

def change_ip():
    try:
        with socket.create_connection(('127.0.0.1', 9051), timeout=5) as s:
            s.sendall(b'AUTHENTICATE\r\nSIGNAL NEWNYM\r\n')
            s.recv(1024)
        time.sleep(3)
    except OSError:
        run_command(['systemctl', 'reload', 'tor'])
        time.sleep(5)

def get_ip() -> str | None:
    proxies = {'http': 'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'}

    services = [
        'http://checkip.amazonaws.com',
        'http://ipinfo.io/ip',
        'http://icanhazip.com',
        'http://ifconfig.me/ip'
    ]

    for _ in range(1):
        for service in random.sample(services, len(services)):
            try:
                r = requests.get(service, proxies=proxies, timeout=8)
                ip = r.text.strip()
                if validate_ip(ip):
                    return ip
            except requests.RequestException:
                continue
        time.sleep(1)
    return None

def validate_ip(ip: str) -> bool:
    parts = ip.split('.')
    return (
        len(parts) == 4
        and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)
    )

def show_banner():
    banner = Text("   TIPC • Tor IP Changer", style="bold cyan")
    banner.append("\n       Author • Belal", style="dim white")
    banner.append("\nhttps://github.com/belabh/tipc", style="bold green")

    console.print(Panel(Align.center(banner), border_style="cyan", padding=(1, 2)))

def show_session_info(mode, current_ip, changes=0, time_remaining=None, max_changes=None):
    info = [
        f"Mode: [cyan]{mode.title()}[/cyan]",
        f"Current IP: [green]{current_ip}[/green]",
        f"Changes: [yellow]{changes}[/yellow]"
    ]

    if time_remaining is not None:
        mins, secs = divmod(time_remaining, 60)
        info.append(f"Time: [blue]{mins:02d}:{secs:02d}[/blue]")

    if max_changes:
        remaining = max_changes - changes
        info.append(f"Remaining: [magenta]{remaining}[/magenta]")

    console.print(Panel("\n".join(info), title="[bold] - INFO - [/bold]", border_style="blue"))

def countdown_timer(seconds: int):
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), transient=True) as progress:
        task = progress.add_task("Waiting...", total=None)
        for remaining in range(seconds, 0, -1):
            mins, secs = divmod(remaining, 60)
            progress.update(task, description=f"Next change in {mins:02d}:{secs:02d}")
            time.sleep(1)

def change_ip_with_status() -> str | None:
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                  console=console, transient=True) as progress:
        task = progress.add_task("Changing IP...", total=None)
        change_ip()
        progress.update(task, description="Verifying new IP...")
        return get_ip()

def process_ip_change(current_ip: str, change_num: int) -> str:
    new_ip = change_ip_with_status()

    if not new_ip:
        console.print(f"[yellow]Change #{change_num}: {current_ip} → Failed to verify new IP[/yellow]")
        return current_ip
    if new_ip == current_ip:
        console.print(f"[yellow]Change #{change_num}: {current_ip} → No change detected[/yellow]")
        return current_ip

    console.print(f"[green]Change #{change_num}: {current_ip} → {new_ip}[/green]")
    return new_ip

def get_mode():
    console.print(Panel("Choose TIPC mode:", title="[bold cyan] - MODE SELECTION - [/bold cyan]", border_style="cyan"))
    console.print("[green]1.[/green] Manual Mode - Press ENTER to change IP")
    console.print("[green]2.[/green] Auto Mode - Automatic changes with intervals")

    choice = Prompt.ask("\nSelect mode", choices=["1", "2"], default="1")
    if choice == "2":
        interval = IntPrompt.ask("Interval in seconds", default=60)
        max_changes = IntPrompt.ask("Maximum changes (0 for unlimited)", default=0)
        return 'auto', interval, (None if max_changes == 0 else max_changes)
    return 'manual', None, None

def main():
    signal.signal(signal.SIGINT, lambda *_: console.print("\n[yellow]Exiting... [/yellow]") or sys.exit(0))

    clear_screen()
    show_banner()

    check_root()
    check_tor()
    start_tor()

    with console.status("[blue]Checking current IP...[/blue]"):
        current_ip = get_ip() or "Unknown"

    if current_ip == "Unknown":
        console.print("[red]Error: Could not determine current IP[/red]")
        if Prompt.ask("Continue anyway?", choices=["y", "n"], default="n") == "n":
            sys.exit(1)

    mode, interval, max_changes = get_mode()

    clear_screen()
    show_banner()
    show_session_info(mode, current_ip, 0, None, max_changes)

    changes = 0
    console.print(f"\n[green]{mode.title()} mode started[/green] - Press Ctrl+C to stop\n")

    while True:
        if mode == 'auto':
            if max_changes and changes >= max_changes:
                console.print(f"\n[green]Completed {max_changes} IP changes![/green]")
                break
            countdown_timer(interval)
        else:
            Prompt.ask("Press ENTER to change IP", default="")

        current_ip = process_ip_change(current_ip, changes + 1)
        changes += 1

        time.sleep(1)
        clear_screen()
        show_banner()
        show_session_info(mode, current_ip, changes, None, max_changes)

if __name__ == "__main__":
    main()

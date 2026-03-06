"""
Utility functions for Minecraft Stresser
"""
import string
import random
from colorama import Fore, Back, Style


def generate_random_username(length: int = 6) -> str:
    """Generate a random username"""
    return "Bot_" + "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_bytes(size: int) -> bytes:
    """Generate random bytes"""
    return random.randbytes(size)


def print_colored(message: str, color: str = Fore.WHITE, style: str = ""):
    """Print colored message"""
    print(f"{style}{color}{message}{Style.RESET_ALL}")


def print_banner():
    """Print application banner"""
    banner = r"""
       Minecraft Stress Testing Tool by gonzyui - Local Use Only
"""
    print_colored(banner, Fore.YELLOW)


def print_warnings():
    """Print legal and safety warnings"""
    print_colored("⚠️  LEGAL WARNING ⚠️", Fore.RED + Back.WHITE + Style.BRIGHT)
    print_colored("This tool is intended ONLY for testing your own Minecraft servers!", Fore.RED)
    print_colored("Using this tool against servers you don't own is ILLEGAL and may result in:", Fore.RED)
    print_colored("  • Criminal charges", Fore.RED)
    print_colored("  • Civil lawsuits", Fore.RED)
    print_colored("  • IP bans", Fore.RED)
    print_colored("  • Loss of internet service", Fore.RED)
    print()
    print_colored("By continuing, you acknowledge that you:", Fore.YELLOW)
    print_colored("  • Own or have explicit permission to test the target server", Fore.YELLOW)
    print_colored("  • Understand the potential impact on server performance", Fore.YELLOW)
    print_colored("  • Accept full responsibility for any consequences", Fore.YELLOW)
    print()


def format_stats_line(elapsed: float, stats) -> str:
    """Format stats line for real-time display"""
    return f"\r{Fore.GREEN}[📊] Elapsed: {elapsed:.1f}s | Sent: {stats.sent} | Success: {stats.success} | Errors: {stats.error} | Timeouts: {stats.timeout}"


def print_final_stats(protocol: str, method: str, stats):
    """Print final attack statistics"""
    print_colored("\n--- Attack Results ---", Fore.YELLOW)
    print_colored(f"[+] Packets/Connections Sent: {stats.sent}", Fore.GREEN)
    print_colored(f"[+] Successful: {stats.success}", Fore.GREEN)

    if protocol == "tcp":
        if method == "login":
            print_colored(f"[-] Closed by server: {stats.closed_by_server}", Fore.YELLOW)
        print_colored(f"[!] Connection timeouts: {stats.timeout}", Fore.RED)
        print_colored(f"[❌] Connection refused: {stats.refused}", Fore.RED)

    print_colored(f"[!] Errors: {stats.error}", Fore.RED)

    total = sum([
        stats.sent, stats.success, stats.error,
        stats.timeout, stats.refused, stats.closed_by_server
    ])
    print_colored(f"[✅] Total operations: {total}", Fore.GREEN)
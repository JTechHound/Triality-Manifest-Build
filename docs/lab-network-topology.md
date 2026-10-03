# Laboratory Sub-Network Topology

Source: `Sub-Network_Topology_Schematic_261003_102215_36_q3f5.pdf`
(2026-10-03). Transcribed verbatim; ASCII schematic reflowed from the PDF.
This documents the physical lab network the PyVISA hardware hook
(`TCPIP0::192.168.53.21::5025::SOCKET`) expects.

## §1 — Topology

The instrumentation cluster lives on a dedicated subnet (**192.168.53.0/24**),
isolated from the public internet by an air-gapped firewall router.

```
PUBLIC WAN/INTERNET BACKBONE
  │  (least-privilege IAM policy blocks inbound)
  ▼
┌──────────────────────────────────────────┐
│ LABORATORY CORE EDGE FIREWALL ROUTER     │
│  • Public interface: dynamic WAN         │
│  • Private gateway:  192.168.53.1        │
└───────────────────┬──────────────────────┘
                    │  [isolating subnet 192.168.53.0/24]
                    ▼
┌───────────────────────────────────────────────────────────────┐
│ LOCAL INSTRUMENTATION LAYER (unmanaged gigabit switch)        │
├───────────────────────┬───────────────────┬───────────────────┤
│ 192.168.53.10         │ 192.168.53.21       │ 192.168.53.100      │
│ LOCAL PROCESSING NODE │ SQUID ARRAY         │ ANALOG PULSE DRIVE  │
│ • Runs pipeline_master│ • PyVISA GPIB-LAN   │ • Entrainment       │
│ • Nightly cron target │ • Listens port 5025 │   modulator         │
│                       │                     │ • Frequency carrier │
└───────────────────────┴───────────────────┴───────────────────┘
```

## §2 — Static interface allocation (eth0)

DHCP is eliminated on the instrument lane to remove polling latency during
State Alpha acquisition runs.

| Parameter              | Value              |
|------------------------|--------------------|
| Subnet                 | 192.168.53.0/24    |
| Netmask                | 255.255.255.0      |
| Gateway                | 192.168.53.1       |
| Processing node        | 192.168.53.10      |
| SQUID digitizer        | 192.168.53.21      |
| SCPI command channel   | TCP 5025 (RAW)     |
| Telemetry stream       | UDP 5053           |

## §3 — Kernel socket tuning (`/etc/sysctl.conf`)

```ini
# Absorb burst pressure (16 MB max socket buffers)
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
# Default socket memory
net.core.rmem_default = 262144
net.core.wmem_default = 262144
# Input packet backlog
net.core.netdev_max_backlog = 10000
# Low-latency TCP polling (bypass bufferbloat)
net.ipv4.tcp_low_latency = 1
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
```

Apply with `sysctl -p` as root.

## §4 — Firewall rules (firewalld)

```bash
# 1. Move the instrument NIC into the trusted zone
sudo firewall-cmd --zone=trusted --add-interface=eth0 --permanent
# 2. Open the UDP telemetry stream port
sudo firewall-cmd --zone=trusted --add-port=5053/udp --permanent
# 3. Open the SCPI command lane
sudo firewall-cmd --zone=trusted --add-port=5025/tcp --permanent
# 4. Activate
sudo firewall-cmd --reload
```

## §5 — PyVISA resource string

```python
# Format: TCPIP0::<IP>::<port>::INSTR
SQUID_CHASSIS_VISA_ADDRESS = "TCPIP0::192.168.53.21::5025::SOCKET"
```

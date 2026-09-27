# Nmap
**What:** Network discovery and security auditing.
**When:** Start of any engagement.
**Commands:**
- `nmap -sn 10.0.0.0/24` — ping sweep
- `nmap -sV -F target` — quick service scan
- `nmap -p- -T4 target` — all-port scan
**Output:** open ports, services, versions.

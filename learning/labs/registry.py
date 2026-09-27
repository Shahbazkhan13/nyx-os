"""NyxOS Labs registry — 20 isolated lab definitions."""
LABS = [
    {"name": "networking-lab", "domain": "network", "isolated": True},
    {"name": "web-lab", "domain": "web", "isolated": True},
    {"name": "database-lab", "domain": "database", "isolated": True},
    {"name": "linux-lab", "domain": "linux", "isolated": True},
    {"name": "ad-lab", "domain": "active-directory", "isolated": True},
    {"name": "credential-lab", "domain": "credentials", "isolated": True},
    {"name": "wireless-lab", "domain": "wireless", "isolated": True},
    {"name": "reversing-lab", "domain": "reversing", "isolated": True},
    {"name": "malware-lab", "domain": "malware", "isolated": True},
    {"name": "forensics-lab", "domain": "forensics", "isolated": True},
    {"name": "mobile-lab", "domain": "mobile", "isolated": True},
    {"name": "cloud-lab", "domain": "cloud", "isolated": True},
    {"name": "container-lab", "domain": "container", "isolated": True},
    {"name": "api-lab", "domain": "api", "isolated": True},
    {"name": "iot-lab", "domain": "iot", "isolated": True},
    {"name": "crypto-lab", "domain": "crypto", "isolated": True},
    {"name": "fuzzing-lab", "domain": "fuzzing", "isolated": True},
    {"name": "blue-team-lab", "domain": "blue-team", "isolated": True},
    {"name": "ctf-lab", "domain": "ctf", "isolated": True},
    {"name": "ot-lab", "domain": "ot", "isolated": True},
]


def list_labs():
    return LABS

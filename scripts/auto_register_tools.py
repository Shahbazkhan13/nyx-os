"""Scan Kali system for installed security tools, auto-register into NyxOS."""
import os, sys, shutil, sqlite3, json
sys.path.insert(0, "/root/nyx-os")
from core.database.db import Database

# Kali tools grouped by domain
TOOL_MAP = {
    "recon":         ["nmap","masscan","dnsenum","dnsrecon","fierce","whois","dig","host",
                      "theharvester","recon-ng","sublist3r","amass","dmitry","ike-scan",
                      "netdiscover","arp-scan","fping","hping3"],
    "network":       ["wireshark","tshark","tcpdump","ettercap","bettercap","mitmproxy",
                      "responder","yersinia","scapy","ncat","socat","proxychains4"],
    "web":           ["nikto","dirb","gobuster","ffuf","wfuzz","whatweb","wpscan","joomscan",
                      "sqlmap","wafw00f","dalfox","xsser","commix","burpsuite","zaproxy",
                      "hydra","medusa","patator"],
    "vulnerability": ["nuclei","openvas","lynis","searchsploit","cve-search"],
    "credentials":   ["hashcat","john","hydra","medusa","ncrack","crunch","cewl","ophcrack",
                      "samdump2","chntpw","pwdump","hashid"],
    "wireless":      ["aircrack-ng","airodump-ng","aireplay-ng","airmon-ng","reaver","bully",
                      "wifite","kismet","macchanger","wifiphisher","bettercap"],
    "redteam":       ["metasploit","msfconsole","msfvenom","setoolkit","beef-xss","empire",
                      "crackmapexec","impacket","powershell-empire","sliver"],
    "reversing":     ["ghidra","radare2","rizin","objdump","readelf","strings","gdb","ltrace",
                      "strace","binwalk","upx","apktool","jadx","dex2jar"],
    "forensics":     ["autopsy","sleuthkit","volatility","foremost","scalpel","bulk-extractor",
                      "binwalk","steghide","exiftool","photorec","testdisk","dd","dcfldd",
                      "guymager","safecopy"],
    "malware":       ["yara","clamav","strings","file","xxd","radare2","cuckoo"],
    "crypto":        ["openssl","gpg","hashid","sslyze","sslscan","testssl","ferret",
                      "steghide","outguess","stegsolve","zsteg"],
    "database":      ["sqlmap","sqlninja","odat","mongoaudit","nmap"],
    "mobile":        ["apktool","jadx","dex2jar","frida","objection","mobsf"],
    "blueteam":      ["snort","suricata","zeek","auditd","tripwire","aide","ossec","fail2ban",
                      "ufw","iptables","nftables"],
    "hardware":      ["binwalk","firmware-mod-kit","flashrom","openocd","minicom"],
    "cloud":         ["aws","az","gcloud","kubectl","docker","terraform"],
    "container":     ["docker","podman","kubectl","kube-bench","trivy","falco"],
    "fuzzing":       ["afl-fuzz","radamsa","zzuf","honggfuzz"],
    "osint":         ["sherlock","sherlock-project","socialscan","holehe","mosint"],
    "privesc":       ["linpeas","winpeas","linux-exploit-suggester","unix-privesc-check"],
}


def scan_installed():
    found = {}
    for domain, tools in TOOL_MAP.items():
        found[domain] = []
        for t in tools:
            if shutil.which(t):
                found[domain].append(t)
    return found


def register_all(db, found):
    total = 0
    for domain, tools in found.items():
        for t in tools:
            try:
                path = shutil.which(t) or ""
                db.execute(
                    "INSERT OR REPLACE INTO tools(name, version, category, enabled) "
                    "VALUES (?, ?, ?, 1)",
                    (t, path, domain))
                total += 1
            except Exception as e:
                print(f"  skip {t}: {e}")
    return total


def main():
    db = Database()
    print("=== Scanning Kali for installed security tools ===")
    found = scan_installed()
    grand = 0
    for domain, tools in found.items():
        if tools:
            print(f"  {domain:15} {len(tools):3} tools")
            grand += len(tools)
    print(f"\nTotal tools installed: {grand}")
    print("\n=== Registering into NyxOS database ===")
    n = register_all(db, found)
    print(f"Registered: {n} tools")
    print("\n=== Sample ===")
    rows = db.fetchall("SELECT name, category FROM tools ORDER BY category LIMIT 30")
    for r in rows:
        print(f"  [{r['category']:15}] {r['name']}")


if __name__ == "__main__":
    main()

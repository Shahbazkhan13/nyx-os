#!/bin/bash
# NyxOS Security Hardening
set -e

echo "Applying NyxOS hardening..."

# Kernel hardening
cat > /etc/sysctl.d/99-nyxos-hardening.conf << 'SYSCTL'
# Kernel hardening
kernel.dmesg_restrict=1
kernel.kptr_restrict=2
kernel.yama.ptrace_scope=1
kernel.unprivileged_bpf_disabled=1
net.core.bpf_jit_harden=2

# Network hardening
net.ipv4.tcp_syncookies=1
net.ipv4.conf.all.rp_filter=1
net.ipv4.conf.default.rp_filter=1
net.ipv4.conf.all.accept_source_route=0
net.ipv4.conf.all.accept_redirects=0
net.ipv4.conf.all.send_redirects=0
net.ipv4.conf.all.log_martians=1
net.ipv6.conf.all.accept_redirects=0
net.ipv6.conf.all.accept_source_route=0

# ASLR
kernel.randomize_va_space=2
SYSCTL

# Disable unused filesystems
cat > /etc/modprobe.d/nyxos-blacklist.conf << 'MOD'
install cramfs /bin/true
install freevxfs /bin/true
install jffs2 /bin/true
install hfs /bin/true
install hfsplus /bin/true
install squashfs /bin/true
install udf /bin/true
MOD

# Password policy
cat > /etc/security/pwquality.conf << 'PWQ'
minlen = 12
dcredit = -1
ucredit = -1
lcredit = -1
ocredit = -1
maxrepeat = 3
PWQ

echo "Hardening applied."

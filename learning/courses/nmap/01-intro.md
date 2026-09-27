# Nmap - Introduction

## What is it?
Nmap (Network Mapper) is a network discovery and security auditing tool.

## Why use it?
- Discover live hosts
- Identify open ports
- Detect services and versions
- OS fingerprinting

## When to use it?
- Start of any engagement
- Asset discovery
- Network inventory

## Prerequisites
- Authorized target (never scan without permission)
- Basic TCP/IP knowledge

## Beginner Guide
1. Ping scan first: `nmap -sn 192.168.1.0/24`
2. Port scan: `nmap -p- target`
3. Service detection: `nmap -sV target`
4. Save output: `nmap -oA output target`

## Common Errors
- Firewall blocking: try `-Pn`
- Slow scan: use `-T4`
- Permission denied: run with sudo for SYN scan

## Lab
Isolated network mein target scan karo, results NyxOS Recon Workbench mein import karo.

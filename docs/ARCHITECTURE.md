# NyxOS Architecture

## Overview
NyxOS is a Linux-based cybersecurity operating platform built on Debian.

## Layers
1. OS Foundation - Kernel, boot, drivers
2. Core Platform - API, IPC, database, identity
3. Platform SDK - Plugin, Workbench, Tool Adapter
4. Desktop - Shell, Dashboard, Components
5. Security Domains - 26 domains
6. Intelligence - Knowledge, Correlation, Threat
7. AI - Local assistant
8. Learning - Courses, Labs, Challenges
9. Cases - Case management
10. Reporting - Professional reports

## Data Flow
Tool -> Adapter -> Execution Manager -> Output Parser -> Evidence -> Finding -> Risk -> Report

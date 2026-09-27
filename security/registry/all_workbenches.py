"""Central registry — every workbench NyxOS knows about."""
from security.recon.recon_workbench import ReconWorkbench
from security.network.network_workbench import NetworkWorkbench
from security.web.web_workbench import WebWorkbench
from security.vulnerability.vuln_workbench import VulnerabilityWorkbench
from security.credentials.credentials_workbench import CredentialsWorkbench
from security.wireless.wireless_workbench import WirelessWorkbench
from security.forensics.forensics_workbench import ForensicsWorkbench
from security.redteam.redteam_workbench import RedTeamWorkbench
from security.database.database_workbench import DatabaseWorkbench
from security.active_directory.active_directory_workbench import ADWorkbench
from security.privesc.privesc_workbench import PrivEscWorkbench
from security.postexploit.postexploit_workbench import PostExploitWorkbench
from security.reversing.reversing_workbench import ReversingWorkbench
from security.malware.malware_workbench import MalwareWorkbench
from security.mobile.mobile_workbench import MobileWorkbench
from security.ai.ai_workbench import AISecurityWorkbench
from security.cloud.cloud_workbench import CloudWorkbench
from security.container.container_workbench import ContainerWorkbench
from security.api.api_workbench import APIWorkbench
from security.hardware.hardware_workbench import HardwareWorkbench
from security.ot.ot_workbench import OTWorkbench
from security.fuzzing.fuzzing_workbench import FuzzingWorkbench
from security.crypto.crypto_workbench import CryptoWorkbench
from security.blueteam.blueteam_workbench import BlueTeamWorkbench
from security.reporting.reporting_workbench import ReportingWorkbench


ALL = [
    ReconWorkbench, NetworkWorkbench, WebWorkbench, VulnerabilityWorkbench,
    CredentialsWorkbench, WirelessWorkbench, ForensicsWorkbench, RedTeamWorkbench,
    DatabaseWorkbench, ADWorkbench, PrivEscWorkbench, PostExploitWorkbench,
    ReversingWorkbench, MalwareWorkbench, MobileWorkbench, AISecurityWorkbench,
    CloudWorkbench, ContainerWorkbench, APIWorkbench, HardwareWorkbench,
    OTWorkbench, FuzzingWorkbench, CryptoWorkbench, BlueTeamWorkbench,
    ReportingWorkbench,
]


def list_domains():
    return [
        {"name": w.name, "domain": w.domain, "description": w.description}
        for w in ALL
    ]


def get_workbench(name):
    for w in ALL:
        if w.name == name:
            return w
    return None

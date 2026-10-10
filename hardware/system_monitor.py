# hardware/system_monitor.py
"""
System monitoring using psutil and WMI.
Provides comprehensive system health, performance, and resource monitoring.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import platform

# psutil imports
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False

# WMI imports (Windows only)
try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    wmi = None
    WMI_AVAILABLE = False

# pyserial imports for USB monitoring
try:
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

logger = logging.getLogger(__name__)


class SystemMonitor:
    """Monitor system health and performance using psutil."""

    def __init__(self):
        """Initialize system monitor."""
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil not available - system monitoring disabled")
        self.boot_time = psutil.boot_time() if PSUTIL_AVAILABLE else None
        logger.info("System Monitor initialized")

    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information."""
        if not PSUTIL_AVAILABLE:
            return {'status': 'unavailable'}

        try:
            return {
                'usage_percent': psutil.cpu_percent(interval=1),
                'core_count': psutil.cpu_count(logical=False),
                'logical_count': psutil.cpu_count(logical=True),
                'frequencies': [freq._asdict() for freq in psutil.cpu_freq(percpu=True)],
                'per_cpu_usage': psutil.cpu_percent(interval=0, percpu=True),
                'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else None
            }
        except Exception as e:
            logger.error(f"CPU info error: {e}")
            return {'error': str(e)}

    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information."""
        if not PSUTIL_AVAILABLE:
            return {'status': 'unavailable'}

        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'total': mem.total,
                'available': mem.available,
                'used': mem.used,
                'free': mem.free,
                'percent': mem.percent,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_free': swap.free,
                'swap_percent': swap.percent
            }
        except Exception as e:
            logger.error(f"Memory info error: {e}")
            return {'error': str(e)}

    def get_disk_info(self) -> Dict[str, Any]:
        """Get disk information."""
        if not PSUTIL_AVAILABLE:
            return {'status': 'unavailable'}

        try:
            disk_info = {}
            for partition in psutil.disk_partitions():
                try:
                    disk_usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.mountpoint] = {
                        'device': partition.device,
                        'total': disk_usage.total,
                        'used': disk_usage.used,
                        'free': disk_usage.free,
                        'percent': disk_usage.percent
                    }
                except PermissionError:
                    pass
            
            return disk_info
        except Exception as e:
            logger.error(f"Disk info error: {e}")
            return {'error': str(e)}

    def get_network_info(self) -> Dict[str, Any]:
        """Get network information."""
        if not PSUTIL_AVAILABLE:
            return {'status': 'unavailable'}

        try:
            net_stats = psutil.net_if_stats()
            io_counters = psutil.net_io_counters()
            connections = psutil.net_connections(kind='inet')
            
            return {
                'interfaces': {iface: stats._asdict() for iface, stats in net_stats.items()},
                'io_counters': {
                    'bytes_sent': io_counters.bytes_sent,
                    'bytes_recv': io_counters.bytes_recv,
                    'packets_sent': io_counters.packets_sent,
                    'packets_recv': io_counters.packets_recv,
                    'errors_in': io_counters.errin,
                    'errors_out': io_counters.errout,
                    'dropped_in': io_counters.dropin,
                    'dropped_out': io_counters.dropout
                },
                'active_connections': len(connections)
            }
        except Exception as e:
            logger.error(f"Network info error: {e}")
            return {'error': str(e)}

    def get_process_info(self, process_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get process information."""
        if not PSUTIL_AVAILABLE:
            return []

        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_num']):
                try:
                    if process_name and process_name.lower() not in proc.name().lower():
                        continue
                    
                    processes.append({
                        'pid': proc.pid,
                        'name': proc.name(),
                        'memory_percent': proc.memory_percent(),
                        'cpu_num': proc.cpu_num()
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:10]
        except Exception as e:
            logger.error(f"Process info error: {e}")
            return []

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health."""
        if not PSUTIL_AVAILABLE:
            return {'status': 'unavailable'}

        try:
            cpu_info = self.get_cpu_info()
            mem_info = self.get_memory_info()
            
            health_status = 'good'
            issues = []
            
            if cpu_info.get('usage_percent', 0) > 80:
                health_status = 'degraded'
                issues.append('High CPU usage')
            
            if mem_info.get('percent', 0) > 85:
                health_status = 'degraded'
                issues.append('High memory usage')
            
            if cpu_info.get('usage_percent', 0) > 95 or mem_info.get('percent', 0) > 95:
                health_status = 'critical'
            
            return {
                'status': health_status,
                'cpu_usage': cpu_info.get('usage_percent'),
                'memory_usage': mem_info.get('percent'),
                'issues': issues,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"System health error: {e}")
            return {'status': 'error', 'error': str(e)}


class WindowsSystemMonitor:
    """Windows-specific monitoring using WMI."""

    def __init__(self):
        """Initialize Windows system monitor."""
        if not WMI_AVAILABLE:
            logger.warning("WMI not available - Windows monitoring disabled")
            self.c = None
            return

        try:
            self.c = wmi.WMI()
            logger.info("Windows System Monitor (WMI) initialized")
        except Exception as e:
            logger.error(f"WMI initialization error: {e}")
            self.c = None

    def get_os_info(self) -> Dict[str, Any]:
        """Get Windows OS information."""
        if not self.c:
            return {'status': 'unavailable'}

        try:
            os_info = self.c.Win32_OperatingSystem()[0]
            return {
                'name': os_info.Caption,
                'version': os_info.Version,
                'build': os_info.BuildNumber,
                'serial_number': os_info.SerialNumber,
                'total_visible_memory': os_info.TotalVisibleMemorySize,
                'free_physical_memory': os_info.FreePhysicalMemory
            }
        except Exception as e:
            logger.error(f"OS info error: {e}")
            return {'error': str(e)}

    def get_installed_apps(self) -> List[Dict[str, str]]:
        """Get list of installed applications."""
        if not self.c:
            return []

        try:
            apps = []
            products = self.c.Win32_Product()
            for product in products:
                apps.append({
                    'name': product.Name,
                    'version': product.Version,
                    'vendor': product.Vendor
                })
            return apps[:20]  # Limit to 20 apps
        except Exception as e:
            logger.error(f"Installed apps error: {e}")
            return []

    def get_system_performance(self) -> Dict[str, Any]:
        """Get system performance metrics."""
        if not self.c:
            return {'status': 'unavailable'}

        try:
            perf_data = {}
            
            # CPU performance
            cpu_stats = self.c.Win32_PerfFormattedData_PerfOS_Processor()
            perf_data['cpu'] = {
                'usage': cpu_stats[0].PercentProcessorTime if cpu_stats else None
            }
            
            # Memory performance
            mem_stats = self.c.Win32_PerfFormattedData_PerfOS_Memory()
            if mem_stats:
                perf_data['memory'] = {
                    'available_mb': mem_stats[0].AvailableMBytes,
                    'pages_per_sec': mem_stats[0].PagesPerSec
                }
            
            return perf_data
        except Exception as e:
            logger.error(f"Performance info error: {e}")
            return {'error': str(e)}

    def get_network_adapters(self) -> List[Dict[str, Any]]:
        """Get network adapter information."""
        if not self.c:
            return []

        try:
            adapters = []
            for adapter in self.c.Win32_NetworkAdapterConfiguration():
                if adapter.IPAddress:
                    adapters.append({
                        'description': adapter.Description,
                        'mac_address': adapter.MACAddress,
                        'ip_addresses': adapter.IPAddress,
                        'dns_servers': adapter.DNSServerSearchOrder,
                        'dhcp_enabled': adapter.DHCPEnabled
                    })
            return adapters
        except Exception as e:
            logger.error(f"Network adapters error: {e}")
            return []

    def get_running_services(self) -> List[Dict[str, str]]:
        """Get running system services."""
        if not self.c:
            return []

        try:
            services = []
            for service in self.c.Win32_Service(State='Running'):
                services.append({
                    'name': service.Name,
                    'display_name': service.DisplayName,
                    'state': service.State,
                    'startup_mode': service.StartMode
                })
            return services[:20]  # Limit to 20 services
        except Exception as e:
            logger.error(f"Running services error: {e}")
            return []


class ComprehensiveMonitor:
    """Comprehensive system monitoring combining psutil and WMI."""

    def __init__(self):
        """Initialize comprehensive monitor."""
        self.psutil_monitor = SystemMonitor()
        self.windows_monitor = WindowsSystemMonitor() if platform.system() == 'Windows' else None
        logger.info("Comprehensive System Monitor initialized")

    def get_full_system_report(self) -> Dict[str, Any]:
        """Get comprehensive system report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'platform': platform.system(),
            'cpu': self.psutil_monitor.get_cpu_info(),
            'memory': self.psutil_monitor.get_memory_info(),
            'disk': self.psutil_monitor.get_disk_info(),
            'network': self.psutil_monitor.get_network_info(),
            'health': self.psutil_monitor.get_system_health(),
            'top_processes': self.psutil_monitor.get_process_info()
        }

        if self.windows_monitor:
            report['windows'] = {
                'os_info': self.windows_monitor.get_os_info(),
                'network_adapters': self.windows_monitor.get_network_adapters(),
                'services': self.windows_monitor.get_running_services(),
                'performance': self.windows_monitor.get_system_performance()
            }
            
        report['usb_devices'] = self.get_usb_devices()

        return report

    def get_usb_devices(self) -> List[Dict[str, str]]:
        """Get connected USB serial devices."""
        if not SERIAL_AVAILABLE:
            return [{'error': 'pyserial not installed'}]
        try:
            ports = serial.tools.list_ports.comports()
            devices = []
            for port, desc, hwid in sorted(ports):
                devices.append({
                    'port': port,
                    'description': desc,
                    'hwid': hwid
                })
            return devices
        except Exception as e:
            logger.error(f"USB monitoring error: {e}")
            return [{'error': str(e)}]


# Export classes
__all__ = [
    'SystemMonitor',
    'WindowsSystemMonitor',
    'ComprehensiveMonitor',
    'PSUTIL_AVAILABLE',
    'WMI_AVAILABLE'
]

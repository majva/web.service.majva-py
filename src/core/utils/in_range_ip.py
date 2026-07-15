import ipaddress
from typing import List, Optional


class IPUtils:

    @staticmethod
    def in_range_ip(ip_range: str, ip: str) -> bool:
        """
        Check if an IP address is within a CIDR range.
        
        Args:
            ip_range: CIDR notation (e.g., "192.168.1.0/24")
            ip: IP address to check (e.g., "192.168.1.12")
        
        Returns:
            True if IP is in range, False otherwise
        
        Example:
            >>> IPUtils.in_range_ip("192.168.1.0/24", "192.168.1.12")
            True
            >>> IPUtils.in_range_ip("192.168.1.0/24", "192.168.2.12")
            False
        """
        try:
            network = ipaddress.ip_network(ip_range, strict=False)
            ip_addr = ipaddress.ip_address(ip)
            return ip_addr in network
        except (ValueError, AttributeError):
            return False

    @staticmethod
    def in_any_range(ip_ranges: Optional[List[str]], ip: str) -> bool:
        """
        Check if an IP address is within any of the provided CIDR ranges.
        
        Args:
            ip_ranges: List of CIDR notations (e.g., ["192.168.1.0/24", "10.0.0.0/16"])
            ip: IP address to check (e.g., "192.168.1.12")
        
        Returns:
            True if IP is in any of the ranges, False otherwise
        
        Example:
            >>> IPUtils.in_any_range(["192.168.1.0/24", "10.0.0.0/16"], "192.168.1.12")
            True
            >>> IPUtils.in_any_range(["192.168.1.0/24", "10.0.0.0/16"], "172.16.0.1")
            False
            >>> IPUtils.in_any_range(None, "192.168.1.12")
            False
            >>> IPUtils.in_any_range([], "192.168.1.12")
            False
        """
        if not ip_ranges:
            return False
        
        for ip_range in ip_ranges:
            if IPUtils.in_range_ip(ip_range, ip):
                return True
        return False

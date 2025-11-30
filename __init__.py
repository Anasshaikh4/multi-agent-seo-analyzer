"""
SEO Analyzer - Google ADK Multi-Agent System

A multi-agent SEO analysis tool built with Google Agent Development Kit.
Demonstrates key ADK concepts including multi-agent systems, custom tools,
parallel/sequential agents, sessions, and observability.
"""

__version__ = "1.0.0"
__author__ = "ADK Certification Project"

from config import GOOGLE_API_KEY, ENVIRONMENT
from database import get_db_client
from orchestrator import get_orchestrator, analyze_url
from agents import (
    security_agent,
    onpage_agent,
    content_agent,
    performance_agent,
    indexability_agent,
    report_agent
)

__all__ = [
    "GOOGLE_API_KEY",
    "ENVIRONMENT",
    "get_db_client",
    "get_orchestrator",
    "analyze_url",
    "security_agent",
    "onpage_agent",
    "content_agent",
    "performance_agent",
    "indexability_agent",
    "report_agent"
]

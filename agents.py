"""
Specialized SEO Analysis Agents for Google ADK.
Each agent focuses on a specific aspect of SEO analysis.

Demonstrates:
- Multi-agent system with LLM-powered agents
- Custom tools integration
- Agent specialization
"""

import logging
from typing import List
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from tools import (
    SECURITY_TOOLS,
    ONPAGE_SEO_TOOLS,
    CONTENT_TOOLS,
    PERFORMANCE_TOOLS,
    INDEXABILITY_TOOLS,
    check_https_security,
    check_security_headers,
    check_title_and_meta,
    check_heading_structure,
    check_image_alt_tags,
    analyze_content_quality,
    check_internal_links,
    check_page_performance,
    check_mobile_friendly,
    check_robots_and_sitemap,
    check_meta_robots
)

logger = logging.getLogger(__name__)


# ============================================================
# SECURITY ANALYSIS AGENT
# ============================================================

SECURITY_AGENT_INSTRUCTION = """You are a Website Security Analyst Agent specialized in checking website security configurations.

Your responsibilities:
1. Check if the website uses HTTPS properly
2. Verify SSL certificate validity
3. Analyze security headers

When given a URL to analyze:
1. Use the check_https_security tool to verify HTTPS and SSL
2. Use the check_security_headers tool to analyze security headers
3. Compile your findings into a structured security report

Always provide:
- A security score (0-100)
- List of security issues found
- Specific recommendations for improvement

Be thorough but concise in your analysis."""

security_agent = Agent(
    name="security_agent",
    model="gemini-2.0-flash",
    description="Analyzes website security including HTTPS, SSL, and security headers",
    instruction=SECURITY_AGENT_INSTRUCTION,
    tools=SECURITY_TOOLS
)


# ============================================================
# ON-PAGE SEO AGENT
# ============================================================

ONPAGE_AGENT_INSTRUCTION = """You are an On-Page SEO Specialist Agent focused on analyzing on-page SEO elements.

Your responsibilities:
1. Analyze title tags and meta descriptions
2. Check heading structure (H1-H6 hierarchy)
3. Verify image alt text usage

When given a URL to analyze:
1. Use check_title_and_meta tool to analyze title and meta description
2. Use check_heading_structure tool to verify heading hierarchy
3. Use check_image_alt_tags tool to check image optimization

Always provide:
- An on-page SEO score (0-100)
- Specific issues found with each element
- Actionable recommendations for improvement

Focus on elements that directly impact search engine rankings."""

onpage_agent = Agent(
    name="onpage_agent",
    model="gemini-2.0-flash",
    description="Analyzes on-page SEO elements like titles, meta descriptions, and headings",
    instruction=ONPAGE_AGENT_INSTRUCTION,
    tools=ONPAGE_SEO_TOOLS
)


# ============================================================
# CONTENT ANALYSIS AGENT
# ============================================================

CONTENT_AGENT_INSTRUCTION = """You are a Content Quality Analyst Agent specialized in evaluating website content.

Your responsibilities:
1. Analyze content quality and depth
2. Check internal linking structure
3. Evaluate content for SEO best practices

When given a URL to analyze:
1. Use analyze_content_quality tool to check word count and content structure
2. Use check_internal_links tool to analyze internal linking

Always provide:
- A content quality score (0-100)
- Word count and content depth analysis
- Internal linking assessment
- Recommendations for content improvement

Focus on content elements that improve user experience and search rankings."""

content_agent = Agent(
    name="content_agent",
    model="gemini-2.0-flash",
    description="Analyzes content quality, word count, and internal linking",
    instruction=CONTENT_AGENT_INSTRUCTION,
    tools=CONTENT_TOOLS
)


# ============================================================
# PERFORMANCE AGENT
# ============================================================

PERFORMANCE_AGENT_INSTRUCTION = """You are a Website Performance Analyst Agent focused on page speed and mobile optimization.

Your responsibilities:
1. Measure page load performance
2. Check mobile-friendliness indicators
3. Identify performance bottlenecks

When given a URL to analyze:
1. Use check_page_performance tool to measure response time and page size
2. Use check_mobile_friendly tool to verify mobile responsiveness

Always provide:
- A performance score (0-100)
- Page load time analysis
- Mobile optimization assessment
- Specific recommendations for improving performance

Fast loading and mobile-friendly pages rank better in search results."""

performance_agent = Agent(
    name="performance_agent",
    model="gemini-2.0-flash",
    description="Analyzes page performance and mobile-friendliness",
    instruction=PERFORMANCE_AGENT_INSTRUCTION,
    tools=PERFORMANCE_TOOLS
)


# ============================================================
# INDEXABILITY AGENT
# ============================================================

INDEXABILITY_AGENT_INSTRUCTION = """You are an Indexability Specialist Agent focused on search engine crawling and indexing.

Your responsibilities:
1. Check robots.txt configuration
2. Verify sitemap presence and validity
3. Analyze meta robots directives

When given a URL to analyze:
1. Use check_robots_and_sitemap tool to verify robots.txt and sitemap
2. Use check_meta_robots tool to check indexing directives

Always provide:
- An indexability score (0-100)
- Crawling and indexing status
- Any blocking directives found
- Recommendations for improving indexability

Proper indexability ensures search engines can find and rank your pages."""

indexability_agent = Agent(
    name="indexability_agent",
    model="gemini-2.0-flash",
    description="Analyzes robots.txt, sitemap, and indexing directives",
    instruction=INDEXABILITY_AGENT_INSTRUCTION,
    tools=INDEXABILITY_TOOLS
)


# ============================================================
# REPORT GENERATOR AGENT
# ============================================================

REPORT_AGENT_INSTRUCTION = """You are an SEO Report Writer Agent that creates comprehensive, easy-to-understand SEO reports.

Your role is to receive analysis results from other agents and compile them into a final report.

When creating a report:
1. Start with an executive summary
2. Provide an overall SEO score
3. List what's working well (positives first)
4. Detail issues found organized by category
5. Provide prioritized recommendations
6. End with next steps

Report format requirements:
- Use clear, simple language (a 5th grader should understand)
- Use markdown formatting for structure
- Include scores for each category
- Make recommendations actionable and specific
- Keep the report concise but comprehensive

Your goal is to help website owners understand their SEO status and what to improve."""

report_agent = Agent(
    name="report_agent",
    model="gemini-2.0-flash",
    description="Compiles analysis results into a comprehensive SEO report",
    instruction=REPORT_AGENT_INSTRUCTION,
    tools=[]  # No tools needed, just processes results
)


# ============================================================
# AGENT REGISTRY
# ============================================================

SPECIALIZED_AGENTS = {
    'security': security_agent,
    'onpage': onpage_agent,
    'content': content_agent,
    'performance': performance_agent,
    'indexability': indexability_agent,
    'report': report_agent
}

ANALYSIS_AGENTS = [
    security_agent,
    onpage_agent,
    content_agent,
    performance_agent,
    indexability_agent
]


def get_agent(name: str) -> Agent:
    """Get an agent by name."""
    return SPECIALIZED_AGENTS.get(name)


def get_all_analysis_agents() -> List[Agent]:
    """Get all analysis agents (excluding report agent)."""
    return ANALYSIS_AGENTS.copy()

"""
Main entry point for SEO Analysis ADK Project.

This module provides:
- CLI interface for running SEO analysis
- Web server mode (optional)
- Agent evaluation capabilities

Demonstrates ADK concepts:
- Agent deployment (CLI and web modes)
- Agent evaluation
- Complete end-to-end workflow
"""

import asyncio
import argparse
import logging
import sys
import json
from datetime import datetime

import config
from database import get_db_client, DatabaseClient
from orchestrator import get_orchestrator, SEOOrchestrator, SEOAnalysisResult
from observability import (
    get_logger,
    log_analysis_start,
    log_analysis_complete,
    get_observability_report,
    tracer,
    metrics
)

logger = get_logger(__name__)


def print_banner():
    """Print application banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🔍 SEO ANALYZER - Google ADK Multi-Agent System            ║
║                                                               ║
║   Powered by Google Agent Development Kit                     ║
║   Using Gemini 2.0 Flash for intelligent analysis            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_report(result: SEOAnalysisResult):
    """Print the analysis report to console."""
    print("\n" + "=" * 60)
    print("📊 SEO ANALYSIS REPORT")
    print("=" * 60)
    print(f"\n🌐 Website: {result.url}")
    print(f"🆔 Request ID: {result.request_id}")
    print(f"⏱️  Duration: {result.total_duration_ms}ms")
    print(f"📈 Status: {result.status}")
    print(f"🎯 Overall Score: {result.overall_score}/100")
    
    print("\n" + "-" * 60)
    print("🤖 AGENT RESULTS")
    print("-" * 60)
    
    for agent_name, agent_result in result.agent_results.items():
        status_icon = "✅" if agent_result.success else "❌"
        print(f"\n{status_icon} {agent_name.replace('_', ' ').title()}")
        print(f"   Duration: {agent_result.duration_ms}ms")
        if not agent_result.success:
            print(f"   Error: {agent_result.error}")
    
    if result.final_report:
        print("\n" + "=" * 60)
        print("📝 FINAL REPORT")
        print("=" * 60)
        print(result.final_report)
    
    # Show PDF path if generated
    if result.pdf_path:
        print("\n" + "=" * 60)
        print("📄 PDF REPORT GENERATED")
        print("=" * 60)
        print(f"📁 Saved to: {result.pdf_path}")
    
    print("\n" + "=" * 60)


async def run_analysis(url: str, verbose: bool = False) -> SEOAnalysisResult:
    """
    Run SEO analysis on a URL.
    
    Args:
        url: Website URL to analyze
        verbose: Enable verbose output
        
    Returns:
        SEOAnalysisResult with complete analysis
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Verify API key is set
    if not config.GOOGLE_API_KEY:
        logger.error("GOOGLE_API_KEY is not set. Please set it in your .env file.")
        print("\n❌ Error: GOOGLE_API_KEY is not set.")
        print("Please create a .env file with your Gemini API key:")
        print("  GOOGLE_API_KEY=your_api_key_here")
        sys.exit(1)
    
    print(f"\n🔍 Analyzing: {url}")
    print("⏳ This may take a minute...\n")
    
    # Get orchestrator and run analysis
    orchestrator = get_orchestrator()
    result = await orchestrator.analyze_website(url)
    
    return result


def run_evaluation():
    """
    Run agent evaluation tests.
    
    This demonstrates the AGENT EVALUATION concept from ADK.
    """
    print("\n🧪 Running Agent Evaluation Tests")
    print("-" * 40)
    
    # Test cases for evaluation
    test_cases = [
        {
            "name": "HTTPS Website Check",
            "url": "https://google.com",
            "expected": {"uses_https": True}
        },
        {
            "name": "Well-Known Website Analysis", 
            "url": "https://example.com",
            "expected": {"has_title": True}
        }
    ]
    
    from tools import check_https_security, check_title_and_meta
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        print(f"\n📋 Test: {test['name']}")
        print(f"   URL: {test['url']}")
        
        try:
            if "https" in test['name'].lower():
                result = check_https_security(test['url'])
                check_key = "uses_https"
            else:
                result = check_title_and_meta(test['url'])
                check_key = "title"
                result["has_title"] = result.get("title") is not None
            
            expected_value = test['expected'].get(list(test['expected'].keys())[0])
            actual_key = list(test['expected'].keys())[0]
            actual_value = result.get(actual_key)
            
            if actual_value == expected_value:
                print(f"   ✅ PASSED: {actual_key} = {actual_value}")
                passed += 1
            else:
                print(f"   ❌ FAILED: Expected {actual_key}={expected_value}, got {actual_value}")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            failed += 1
    
    print("\n" + "-" * 40)
    print(f"📊 Evaluation Results: {passed} passed, {failed} failed")
    print("-" * 40)
    
    return passed, failed


def show_history(limit: int = 10):
    """Show analysis history from database."""
    print("\n📜 Analysis History")
    print("-" * 60)
    
    db = get_db_client()
    requests = db.get_all_requests(limit=limit)
    
    if not requests:
        print("No analysis history found.")
        return
    
    for req in requests:
        print(f"\n🆔 {req['unique_identifier']}")
        print(f"   URL: {req['website_url']}")
        print(f"   Status: {req['status']}")
        print(f"   Created: {req['created_at']}")
        if req.get('completed_at'):
            print(f"   Completed: {req['completed_at']}")
    
    print("\n" + "-" * 60)


def show_observability_report():
    """Display observability metrics and traces."""
    print("\n📈 Observability Report")
    print("-" * 60)
    
    report = get_observability_report()
    print(json.dumps(report, indent=2, default=str))
    
    print("-" * 60)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SEO Analyzer - Google ADK Multi-Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py analyze https://example.com
  python main.py analyze https://example.com --verbose
  python main.py evaluate
  python main.py history
  python main.py metrics
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a website's SEO")
    analyze_parser.add_argument("url", help="Website URL to analyze")
    analyze_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    analyze_parser.add_argument("-o", "--output", help="Save report to file")
    
    # Evaluate command
    subparsers.add_parser("evaluate", help="Run agent evaluation tests")
    
    # History command
    history_parser = subparsers.add_parser("history", help="Show analysis history")
    history_parser.add_argument("-n", "--limit", type=int, default=10, help="Number of records to show")
    
    # Metrics command
    subparsers.add_parser("metrics", help="Show observability metrics")
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.command == "analyze":
        # Run analysis
        result = asyncio.run(run_analysis(args.url, args.verbose))
        print_report(result)
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result.final_report or "No report generated")
            print(f"\n💾 Report saved to: {args.output}")
    
    elif args.command == "evaluate":
        run_evaluation()
    
    elif args.command == "history":
        show_history(args.limit)
    
    elif args.command == "metrics":
        show_observability_report()
    
    else:
        parser.print_help()
        print("\n💡 Quick start: python main.py analyze https://example.com")


if __name__ == "__main__":
    main()

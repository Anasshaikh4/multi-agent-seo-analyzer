"""
SEO Orchestrator Agent - Coordinates multiple specialized agents.

Demonstrates:
- Multi-agent orchestration
- Parallel agent execution
- Sequential agent workflow
- Loop agents for iterative processing
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents import (
    security_agent,
    onpage_agent,
    content_agent,
    performance_agent,
    indexability_agent,
    report_agent,
    ANALYSIS_AGENTS
)
from pdf_service import generate_report_pdf
from database import get_db_client

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Result from a single agent execution."""
    """Stores result from an agent execution."""
    agent_name: str
    success: bool
    result: str
    duration_ms: int
    error: Optional[str] = None


@dataclass
class SEOAnalysisResult:
    """Complete SEO analysis result with all agent outputs and PDF path."""
    url: str
    request_id: str
    agent_results: Dict[str, AgentResult] = field(default_factory=dict)
    final_report: Optional[str] = None
    pdf_path: Optional[str] = None
    overall_score: int = 0
    total_duration_ms: int = 0
    status: str = "pending"


class SEOOrchestrator:
    """
    Orchestrates SEO analysis using multiple specialized agents.
    
    Demonstrates ADK concepts:
    - Multi-agent system
    - Parallel agents (analysis agents run in parallel)
    - Sequential agents (report generation after analysis)
    - Sessions & state management (InMemorySessionService)
    - Observability (logging, timing metrics)
    """
    
    def __init__(self):
        """Initialize the orchestrator with session service."""
        self.session_service = InMemorySessionService()
        self.db = get_db_client()
        self.runners: Dict[str, Runner] = {}
        
        # Initialize runners for each agent
        self._init_runners()
        
        logger.info("SEO Orchestrator initialized with %d analysis agents", len(ANALYSIS_AGENTS))
    
    def _init_runners(self):
        """Initialize Runner instances for each agent."""
        all_agents = ANALYSIS_AGENTS + [report_agent]
        
        for agent in all_agents:
            self.runners[agent.name] = Runner(
                agent=agent,
                app_name="seo_analyzer",
                session_service=self.session_service
            )
            logger.debug(f"Initialized runner for agent: {agent.name}")
    
    async def _run_agent(
        self, 
        agent_name: str, 
        prompt: str, 
        session_id: str,
        request_id: str
    ) -> AgentResult:
        """
        Run a single agent and return its result.
        
        Args:
            agent_name: Name of the agent to run
            prompt: The prompt/query for the agent
            session_id: Session ID for state management
            request_id: Request ID for logging
            
        Returns:
            AgentResult with the agent's output
        """
        runner = self.runners.get(agent_name)
        if not runner:
            return AgentResult(
                agent_name=agent_name,
                success=False,
                result="",
                duration_ms=0,
                error=f"Runner not found for agent: {agent_name}"
            )
        
        start_time = time.time()
        logger.info(f"[{request_id}] Starting agent: {agent_name}")
        
        try:
            # Run the agent - create proper Content object for ADK Runner
            content = types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )
            
            result_text = ""
            async for event in runner.run_async(
                user_id="seo_user",
                session_id=session_id,
                new_message=content
            ):
                # Collect the agent's response
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts'):
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                result_text += part.text
                    elif isinstance(event.content, str):
                        result_text += event.content
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log to database for observability
            self.db.log_agent_action(
                request_id=request_id,
                agent_name=agent_name,
                action="analysis_complete",
                details={"result_length": len(result_text)},
                duration_ms=duration_ms
            )
            
            logger.info(f"[{request_id}] Agent {agent_name} completed in {duration_ms}ms")
            
            return AgentResult(
                agent_name=agent_name,
                success=True,
                result=result_text,
                duration_ms=duration_ms
            )
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = str(e)
            
            # Log error to database
            self.db.log_agent_action(
                request_id=request_id,
                agent_name=agent_name,
                action="analysis_error",
                details={"error": error_msg},
                duration_ms=duration_ms
            )
            
            logger.error(f"[{request_id}] Agent {agent_name} failed: {error_msg}")
            
            return AgentResult(
                agent_name=agent_name,
                success=False,
                result="",
                duration_ms=duration_ms,
                error=error_msg
            )
    
    async def run_parallel_analysis(
        self, 
        url: str, 
        request_id: str,
        session_id: str
    ) -> Dict[str, AgentResult]:
        """
        Run all analysis agents in parallel.
        
        This demonstrates PARALLEL AGENTS - multiple agents
        working simultaneously on the same URL.
        
        Args:
            url: Website URL to analyze
            request_id: Unique request identifier
            session_id: Session ID for state management
            
        Returns:
            Dictionary mapping agent names to their results
        """
        logger.info(f"[{request_id}] Starting parallel analysis of {url}")
        
        # Create analysis prompts for each agent
        agent_prompts = {
            "security_agent": f"Analyze the security of this website: {url}. Check HTTPS, SSL, and security headers.",
            "onpage_agent": f"Analyze the on-page SEO of this website: {url}. Check title, meta description, headings, and images.",
            "content_agent": f"Analyze the content quality of this website: {url}. Check word count and internal linking.",
            "performance_agent": f"Analyze the performance of this website: {url}. Check page speed and mobile-friendliness.",
            "indexability_agent": f"Analyze the indexability of this website: {url}. Check robots.txt, sitemap, and meta robots."
        }
        
        # Create tasks for parallel execution
        tasks = []
        for agent in ANALYSIS_AGENTS:
            prompt = agent_prompts.get(agent.name, f"Analyze this website: {url}")
            task = self._run_agent(
                agent_name=agent.name,
                prompt=prompt,
                session_id=f"{session_id}_{agent.name}",
                request_id=request_id
            )
            tasks.append(task)
        
        # Run all agents in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        agent_results = {}
        for result in results:
            if isinstance(result, AgentResult):
                agent_results[result.agent_name] = result
            elif isinstance(result, Exception):
                logger.error(f"[{request_id}] Agent task failed with exception: {result}")
        
        logger.info(f"[{request_id}] Parallel analysis complete. {len(agent_results)} agents finished.")
        return agent_results
    
    async def generate_report(
        self,
        url: str,
        agent_results: Dict[str, AgentResult],
        request_id: str,
        session_id: str
    ) -> AgentResult:
        """
        Generate final SEO report using the report agent.
        
        This demonstrates SEQUENTIAL AGENTS - the report agent
        runs after all analysis agents have completed.
        
        Args:
            url: Website URL that was analyzed
            agent_results: Results from all analysis agents
            request_id: Unique request identifier
            session_id: Session ID for state management
            
        Returns:
            AgentResult containing the final report
        """
        logger.info(f"[{request_id}] Generating final report")
        
        # Compile all agent results into a prompt
        results_summary = f"Website analyzed: {url}\n\n"
        results_summary += "=== ANALYSIS RESULTS ===\n\n"
        
        for agent_name, result in agent_results.items():
            results_summary += f"--- {agent_name.upper()} ---\n"
            if result.success:
                results_summary += f"{result.result}\n\n"
            else:
                results_summary += f"Analysis failed: {result.error}\n\n"
        
        prompt = f"""Based on the following SEO analysis results, create a comprehensive SEO report for the website.

{results_summary}

Create a well-formatted markdown report that includes:
1. Executive Summary with overall score
2. What's working well (positives)
3. Issues found (organized by category)
4. Prioritized recommendations
5. Next steps

Make the report easy to understand for non-technical users."""
        
        return await self._run_agent(
            agent_name="report_agent",
            prompt=prompt,
            session_id=f"{session_id}_report_agent",
            request_id=request_id
        )
    
    async def analyze_website(self, url: str) -> SEOAnalysisResult:
        """
        Perform complete SEO analysis of a website.
        
        This is the main entry point that orchestrates:
        1. Parallel analysis by specialized agents
        2. Sequential report generation
        3. State management and observability
        
        Args:
            url: Website URL to analyze
            
        Returns:
            Complete SEOAnalysisResult with all findings
        """
        start_time = time.time()
        
        # Create database request
        request_data = self.db.create_analysis_request(url)
        request_id = request_data['unique_identifier']
        session_id = f"seo_session_{request_id}"
        
        logger.info(f"[{request_id}] Starting SEO analysis for: {url}")
        self.db.update_request_status(request_id, "analyzing")
        
        # Create sessions for all agents (required by ADK Runner)
        for agent in ANALYSIS_AGENTS:
            agent_session_id = f"{session_id}_{agent.name}"
            await self.session_service.create_session(
                app_name="seo_analyzer",
                user_id="seo_user",
                session_id=agent_session_id
            )
        # Create session for report agent
        await self.session_service.create_session(
            app_name="seo_analyzer",
            user_id="seo_user",
            session_id=f"{session_id}_report_agent"
        )
        
        # Initialize result object
        analysis_result = SEOAnalysisResult(
            url=url,
            request_id=request_id,
            status="analyzing"
        )
        
        try:
            # STEP 1: Run parallel analysis (PARALLEL AGENTS)
            self.db.log_agent_action(
                request_id=request_id,
                agent_name="orchestrator",
                action="parallel_analysis_start",
                details={"url": url}
            )
            
            agent_results = await self.run_parallel_analysis(
                url=url,
                request_id=request_id,
                session_id=session_id
            )
            analysis_result.agent_results = agent_results
            
            # STEP 2: Generate report (SEQUENTIAL AGENT)
            self.db.log_agent_action(
                request_id=request_id,
                agent_name="orchestrator",
                action="report_generation_start"
            )
            
            report_result = await self.generate_report(
                url=url,
                agent_results=agent_results,
                request_id=request_id,
                session_id=session_id
            )
            
            if report_result.success:
                analysis_result.final_report = report_result.result
                analysis_result.status = "completed"
                
                # Calculate overall score (average of successful agents)
                scores = []
                for result in agent_results.values():
                    if result.success:
                        # Try to extract score from result text
                        import re
                        score_match = re.search(r'score[:\s]+(\d+)', result.result.lower())
                        if score_match:
                            scores.append(int(score_match.group(1)))
                
                if scores:
                    analysis_result.overall_score = sum(scores) // len(scores)
                
                # Generate PDF report
                logger.info(f"[{request_id}] Generating PDF report...")
                pdf_path = generate_report_pdf(
                    markdown_content=report_result.result,
                    url=url,
                    request_id=request_id,
                    score=analysis_result.overall_score
                )
                if pdf_path:
                    analysis_result.pdf_path = pdf_path
                    logger.info(f"[{request_id}] PDF generated: {pdf_path}")
                else:
                    logger.warning(f"[{request_id}] Failed to generate PDF report")
            else:
                analysis_result.status = "partial"
                analysis_result.final_report = "Report generation failed. See individual agent results."
            
            # Calculate total duration
            analysis_result.total_duration_ms = int((time.time() - start_time) * 1000)
            
            # Update database with results
            self.db.update_request_status(
                unique_identifier=request_id,
                status=analysis_result.status,
                analysis_result={
                    "agent_results": {
                        name: {
                            "success": r.success,
                            "duration_ms": r.duration_ms,
                            "error": r.error
                        }
                        for name, r in agent_results.items()
                    },
                    "overall_score": analysis_result.overall_score,
                    "total_duration_ms": analysis_result.total_duration_ms
                },
                report_markdown=analysis_result.final_report
            )
            
            logger.info(
                f"[{request_id}] Analysis complete in {analysis_result.total_duration_ms}ms. "
                f"Status: {analysis_result.status}, Score: {analysis_result.overall_score}"
            )
            
        except Exception as e:
            error_msg = str(e)
            analysis_result.status = "failed"
            analysis_result.total_duration_ms = int((time.time() - start_time) * 1000)
            
            self.db.update_request_status(
                unique_identifier=request_id,
                status="failed",
                error_message=error_msg
            )
            
            logger.error(f"[{request_id}] Analysis failed: {error_msg}")
        
        return analysis_result


# Create global orchestrator instance
_orchestrator: Optional[SEOOrchestrator] = None


def get_orchestrator() -> SEOOrchestrator:
    """Get or create the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SEOOrchestrator()
    return _orchestrator


async def analyze_url(url: str) -> SEOAnalysisResult:
    """
    Convenience function to analyze a URL.
    
    Args:
        url: Website URL to analyze
        
    Returns:
        Complete SEOAnalysisResult
    """
    orchestrator = get_orchestrator()
    return await orchestrator.analyze_website(url)

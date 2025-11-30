# Multi-Agent SEO Analyzer

**Track:** Enterprise Agents  
**Built with:** Google Agent Development Kit (ADK) + Gemini 2.0 Flash

---

## Problem Statement

SEO audits are a nightmare. Every website owner knows they need good SEO, but actually checking everything? That's a different story.

Here's what a proper SEO audit involves:
- Is HTTPS configured correctly? Are security headers in place?
- Are title tags and meta descriptions optimized?
- Is the heading structure (H1-H6) logical?
- Do images have alt text for accessibility?
- How's the content quality? Word count? Internal linking?
- Is the page fast enough? Mobile-friendly?
- Can search engines actually crawl and index the site?

Doing this manually takes **2-3 hours per website**. And that's if you know what you're looking for.

The alternatives aren't great either:
- **Premium tools** like Ahrefs, SEMrush, or Moz cost $99-449/month
- **Hiring an SEO consultant** runs $75-200/hour
- **DIY approach** means spending weekends clicking through browser dev tools

For small businesses, solo developers, and side project owners, these options are either too expensive or too time-consuming. I've been there—running multiple side projects and dreading the SEO checklist every time I make updates.

**The core problem:** SEO analysis requires checking many different things, each requiring specialized knowledge, and doing it all takes forever.

---

## Why Agents?

This problem is perfect for AI agents because:

**1. It's naturally parallelizable**
Security checks don't depend on content analysis. Performance testing doesn't need to wait for heading structure validation. These are independent tasks that can run simultaneously—exactly what parallel agents excel at.

**2. Each domain requires specialized expertise**
An agent checking SSL certificates needs different knowledge than one analyzing content quality. Rather than one overloaded AI trying to know everything, specialized agents can focus on their specific domain and do it well.

**3. Results need intelligent synthesis**
Raw data isn't helpful. "Your page loaded in 2.3 seconds" means nothing without context. Agents can interpret findings, prioritize issues, and provide actionable recommendations—not just data dumps.

**4. The workflow has clear phases**
First, gather data (parallel). Then, synthesize a report (sequential). This maps perfectly to ADK's workflow agent patterns.

**5. Tools need to take real action**
Agents aren't just chatbots here—they actually fetch websites, parse HTML, check SSL certificates, and measure performance. They're doing real work, not just generating text.

A single LLM prompt couldn't handle this effectively. But a team of specialized agents, each with their own tools, working in parallel? That's the right architecture.

---

## What You Created

I built a **Multi-Agent SEO Analysis System** with six specialized agents coordinated by an orchestrator.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    SEO ORCHESTRATOR                         │
│              (Coordinates all agents)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ══════════════╪══════════════
              PARALLEL PHASE
        ══════════════╪══════════════
                      │
    ┌─────────────────┼─────────────────┐
    │         │       │       │         │
    ▼         ▼       ▼       ▼         ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│🔒     │ │📄     │ │📝     │ │⚡     │ │🔍     │
│Security│ │OnPage │ │Content│ │Perf.  │ │Index. │
│Agent  │ │Agent  │ │Agent  │ │Agent  │ │Agent  │
└───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘
    │         │       │       │         │
    └─────────┴───────┴───────┴─────────┘
                      │
        ══════════════╪══════════════
             SEQUENTIAL PHASE
        ══════════════╪══════════════
                      │
                      ▼
              ┌─────────────┐
              │ 📊 Report   │
              │    Agent    │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │  📄 PDF     │
              │   Report    │
              └─────────────┘
```

### The Six Agents

| Agent | Role | Tools Used |
|-------|------|------------|
| 🔒 **Security Agent** | Checks HTTPS, SSL, security headers | `check_https_security`, `check_security_headers` |
| 📄 **OnPage Agent** | Analyzes titles, meta, headings, images | `check_title_and_meta`, `check_heading_structure`, `check_image_alt_tags` |
| 📝 **Content Agent** | Evaluates content quality & links | `analyze_content_quality`, `check_internal_links` |
| ⚡ **Performance Agent** | Tests speed & mobile-friendliness | `check_page_performance`, `check_mobile_friendly` |
| 🔍 **Indexability Agent** | Verifies robots.txt, sitemap, meta robots | `check_robots_and_sitemap`, `check_meta_robots` |
| 📊 **Report Agent** | Synthesizes all findings into final report | None (uses other agents' outputs) |

### Key Components

- **11 Custom Tools** - Real HTTP requests, HTML parsing, SSL validation
- **InMemorySessionService** - State management for each agent
- **Observability Module** - Logging, tracing spans, metrics collection
- **PDF Service** - Converts markdown reports to professional PDFs

---

## Demo

### Running an Analysis

```bash
python main.py analyze https://example.com
```

### Sample Output

```
╔═══════════════════════════════════════════════════════════════╗
║   🔍 SEO ANALYZER - Google ADK Multi-Agent System            ║
╚═══════════════════════════════════════════════════════════════╝

🔍 Analyzing: https://example.com
⏳ Running 5 agents in parallel...

════════════════════════════════════════════════════════════════
📊 SEO ANALYSIS REPORT
════════════════════════════════════════════════════════════════

🌐 Website: https://example.com
🆔 Request ID: a1b2c3d4
⏱️  Duration: 15234ms
🎯 Overall Score: 78/100

────────────────────────────────────────────────────────────────
🤖 AGENT RESULTS
────────────────────────────────────────────────────────────────

✅ Security Agent      - 2341ms - Score: 85/100
✅ OnPage Agent        - 1823ms - Score: 72/100
✅ Content Agent       - 1456ms - Score: 80/100
✅ Performance Agent   - 987ms  - Score: 75/100
✅ Indexability Agent  - 1234ms - Score: 78/100

════════════════════════════════════════════════════════════════
📄 PDF REPORT GENERATED
════════════════════════════════════════════════════════════════
📁 Saved to: outputs/seo_report_example.com_20251201.pdf
```

### What the Report Includes

- **Executive Summary** with overall score
- **Security Analysis** - SSL status, security headers, vulnerabilities
- **On-Page SEO** - Title/meta evaluation, heading structure, image optimization
- **Content Quality** - Word count analysis, internal linking map
- **Performance Metrics** - Load time estimates, mobile-friendliness
- **Indexability Status** - Robots.txt, sitemap, crawlability issues
- **Prioritized Recommendations** - What to fix first

---

## The Build

### Technologies Used

| Technology | Purpose |
|------------|---------|
| **Google ADK** | Agent framework, orchestration, session management |
| **Gemini 2.0 Flash** | LLM powering all 6 agents |
| **Python 3.10+** | Core language |
| **asyncio** | Parallel agent execution |
| **BeautifulSoup4** | HTML parsing for SEO checks |
| **Requests** | HTTP calls to target websites |
| **SQLite** | Storing analysis history |
| **markdown-pdf** | PDF report generation |

### ADK Concepts Implemented

| Concept | How It's Used |
|---------|--------------|
| ✅ **LLM Agents** | 6 agents powered by Gemini 2.0 Flash |
| ✅ **Parallel Agents** | 5 analysis agents via `asyncio.gather()` |
| ✅ **Sequential Agents** | Report agent runs after analysis completes |
| ✅ **Custom Tools** | 11 `FunctionTool` implementations |
| ✅ **Sessions & State** | `InMemorySessionService` per agent |
| ✅ **Observability** | Logging, tracing spans, metrics |

### Project Structure

```
Project/
├── main.py              # CLI entry point
├── orchestrator.py      # Multi-agent coordination
├── agents.py            # 6 specialized agents
├── tools.py             # 11 custom SEO tools
├── database.py          # SQLite persistence
├── observability.py     # Logging, tracing, metrics
├── pdf_service.py       # PDF report generation
├── config.py            # Environment configuration
├── requirements.txt     # Dependencies
├── .env.example         # API key template
└── Architecture/        # UML diagrams
```

### Challenges Overcome

1. **ADK Runner API** - Initially passed strings instead of `types.Content` objects. Learned the proper message format.

2. **Session Management** - Each agent needed its own session to prevent state collisions during parallel execution.

3. **Tool Response Handling** - Had to add null checks for `part.text` when agents returned function call results.

4. **Parallel Coordination** - Ensuring all agents complete before the report agent synthesizes results.

---

## If I Had More Time, This Is What I'd Do

### 1. Add More Analysis Agents
- **Backlink Agent** - Analyze external link profile
- **Schema Agent** - Validate structured data markup
- **Competitor Agent** - Compare against competitor sites

### 2. Implement Long-Term Memory
- Use ADK's Memory Bank to remember previous audits
- Track improvements over time
- Alert when SEO scores drop

### 3. Deploy to Cloud
- Deploy on Google Cloud Run or Agent Engine
- Create a web UI for non-technical users
- Add scheduled recurring audits

### 4. Add MCP Integration
- Connect to external SEO data sources
- Integrate with Google Search Console API
- Pull real PageSpeed Insights data

### 5. Implement A2A Protocol
- Allow other agents to request SEO analysis
- Create an SEO-as-a-service agent endpoint

### 6. Build Evaluation Pipeline
- Create test cases for each agent
- Measure accuracy against manual audits
- Continuous improvement based on feedback

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/adk-seo-multi-agent.git
cd adk-seo-multi-agent

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env: GOOGLE_API_KEY=your_key_here

# Run analysis
python main.py analyze https://example.com
```

---

*Built for the Google ADK Agents Intensive Capstone Project (November 2025)*

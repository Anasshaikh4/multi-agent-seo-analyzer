# Architecture Diagrams

This directory contains PlantUML diagrams documenting the SEO Analyzer Multi-Agent System architecture.

## Diagrams

### 1. `agents_architecture.puml`
**Main Architecture Diagram** - Shows the complete multi-agent system including:
- User Interface (CLI)
- Orchestrator Layer
- 5 Analysis Agents (parallel execution)
- Report Agent (sequential execution)
- 11 Custom Tools
- Services (PDF, Session, Observability)
- Data Layer (SQLite, PDF outputs)

### 2. `tools_detail.puml`
**Tools Class Diagram** - Detailed view of all 11 custom FunctionTools:
- Security Tools (2)
- On-Page SEO Tools (3)
- Content Analysis Tools (2)
- Performance Tools (2)
- Indexability Tools (2)

### 3. `sequence_flow.puml`
**Sequence Diagram** - Shows the complete flow of an SEO analysis:
- Initialization phase
- Parallel agent execution
- Sequential report generation
- PDF export
- Result storage

### 4. `component_overview.puml`
**Component Overview** - High-level view of all system files and their relationships.

## How to Generate Images

### Option 1: VS Code Extension
Install the "PlantUML" extension in VS Code:
1. Open any `.puml` file
2. Press `Alt+D` to preview
3. Right-click and select "Export Current Diagram"

### Option 2: Online Server
Visit [PlantUML Web Server](http://www.plantuml.com/plantuml/uml/) and paste the diagram code.

### Option 3: Command Line
```bash
# Install PlantUML
# Windows: choco install plantuml
# Mac: brew install plantuml

# Generate PNG
plantuml agents_architecture.puml -tpng

# Generate SVG
plantuml agents_architecture.puml -tsvg
```

## ADK Concepts Demonstrated

| Concept | Location in Diagrams |
|---------|---------------------|
| Multi-Agent System | `agents_architecture.puml` - Analysis Agents package |
| Custom Tools | `tools_detail.puml` - All 11 FunctionTools |
| Sessions & State | `agents_architecture.puml` - Session Service |
| Parallel Agents | `sequence_flow.puml` - Parallel execution block |
| Sequential Agents | `sequence_flow.puml` - Report generation phase |
| Observability | `agents_architecture.puml` - Observability service |

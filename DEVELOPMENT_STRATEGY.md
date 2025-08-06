# ResumeAgents Development Strategy Document

## 📋 Project Overview

### Objectives
- Build a multi-agent framework specialized for job application document creation
- Create optimal documents through comprehensive analysis and strategic guidance
- Provide self-introduction question guides with character limit optimization
- Implement category-wise evaluation and revision system

### Core Values
- **Modularity**: Independent roles and responsibilities for each agent
- **Quality**: Document quality assurance through multi-stage review
- **Efficiency**: Strategic workflow with context accumulation
- **Usability**: Simple usage with comprehensive guidance

## 🏗️ Architecture Design

### Overall Structure
```
ResumeAgents/
├── main.py                    # Main execution file
├── .env                      # Environment variables (API keys, configuration)
├── resumeagents/             # Main package
│   ├── default_config.py     # Default configuration
│   ├── agents/               # Agent modules
│   │   ├── base_agent.py     # Base agent class
│   │   ├── analysis/         # External Information Analysis
│   │   │   ├── company_analyst.py
│   │   │   ├── market_analyst.py
│   │   │   └── jd_analyst.py
│   │   ├── matching/         # Candidate-Company Matching
│   │   │   ├── candidate_analyst.py
│   │   │   ├── culture_analyst.py
│   │   │   └── trend_analyst.py
│   │   ├── strategy/         # Strategic Positioning
│   │   │   ├── strength_researcher.py
│   │   │   └── weakness_researcher.py
│   │   ├── guides/           # Writing Guidance
│   │   │   ├── question_guide.py
│   │   │   ├── experience_guide.py
│   │   │   └── writing_guide.py
│   │   ├── production/       # Document Creation
│   │   │   ├── document_writer.py
│   │   │   └── quality_manager.py
│   │   └── evaluators/       # Category Evaluation System
│   │       ├── stage_evaluator.py          # Base evaluator class
│   │       ├── analysis_evaluator.py       # Analysis category evaluator
│   │       ├── matching_evaluator.py       # Matching category evaluator
│   │       ├── strategy_evaluator.py       # Strategy category evaluator
│   │       ├── guide_evaluator.py          # Guide category evaluator
│   │       └── production_evaluator.py     # Production category evaluator
│   ├── utils/              # Utility modules
│   │   ├── __init__.py     # Model classification and utilities
│   │   └── profile_manager.py
│   └── graph/              # Graph structure
│       └── resume_graph.py
├── profiles/               # User profiles storage
└── experience_db/          # Vector database storage
```

## 🤖 Agent Design

### 📊 Analysis Team (External Information Analysis)
**Purpose**: Gather and analyze external information to build foundational context

- **CompanyAnalyst**: Company culture, values, business model analysis
- **MarketAnalyst**: Industry trends, competitive landscape analysis  
- **JDAnalyst**: Job requirements, skills, cultural fit analysis (gets full context)

**Key Features**: Web search capabilities, real-time information gathering

### 🎯 Matching Team (Candidate-Company Matching)
**Purpose**: Evaluate how well the candidate aligns with company and market needs

- **CandidateAnalyst**: Candidate experience and skills analysis
- **CultureAnalyst**: Cultural fit evaluation using candidate and company context
- **TrendAnalyst**: Market positioning assessment with full context

**Key Features**: Profile-based analysis, cultural fit scoring

### 🔬 Strategy Team (Strategic Positioning)
**Purpose**: Develop strategic positioning to maximize competitive advantages

- **StrengthResearcher**: Competitive advantages identification and amplification
- **WeaknessResearcher**: Risk assessment and improvement strategies

**Key Features**: SWOT analysis, strategic recommendations

### 🎯 Guide Team (Writing Guidance)
**Purpose**: Provide comprehensive writing guidance and strategy

- **QuestionGuide**: Question analysis and strategic writing framework
- **ExperienceGuide**: Experience selection and storytelling with STAR method
- **WritingGuide**: Final writing strategy and structure optimization

**Key Features**: Character limit optimization, experience matching via vector search

### 📝 Production Team (Document Creation)
**Purpose**: Create final documents and ensure quality standards

- **DocumentWriter**: Strategic document creation with guide integration
- **QualityManager**: Multi-criteria quality evaluation and feedback

**Key Features**: Multiple document formats, ATS optimization

### 🔍 Category Evaluation System
**Purpose**: Evaluate team performance and trigger revisions when needed

- **AnalysisEvaluator**: Evaluates Analysis team collective output (Company + Market + JD)
- **MatchingEvaluator**: Evaluates Matching team collective output (Candidate + Culture + Trend)
- **StrategyEvaluator**: Evaluates Strategy team collective output (Strength + Weakness)
- **GuideEvaluator**: Evaluates Guide team collective output (Question + Experience + Writing)
- **ProductionEvaluator**: Evaluates Production team collective output (Document + Quality)

**Key Features**: English prompts, JSON responses, category-wide feedback

## 🔄 Workflow Design

### Sequential Execution Strategy

#### Phase 1: Analysis (Company → Market → JD)
- **External Information Gathering**: Company, industry, job requirements
- **Why Sequential**: JD analysis benefits from full company and market context
- **Context Accumulation**: Each agent builds upon previous insights

#### Phase 2: Matching (Candidate → Culture → Trend)
- **Candidate-Company Fit Assessment**: Progressive evaluation with context building
- **Why Sequential**: Culture analysis needs candidate baseline, trend analysis needs both
- **Strategic Positioning**: Position candidate within market landscape

#### Phase 3: Strategy (Strength → Weakness)
- **Strategic Positioning Development**: Competitive advantages and risk mitigation
- **Why Sequential**: Weakness analysis avoids duplicating identified strengths
- **Balanced Assessment**: Create comprehensive strategic profile

#### Phase 4: Guide (Question → Experience → Writing)
- **Writing Strategy Framework**: Comprehensive guidance development
- **Why Sequential**: Each step refines and builds upon previous insights
- **Coherent Guidance**: Unified strategy across all guidance elements

#### Phase 5: Production (Document → Quality)
- **Final Document Creation**: Document creation and validation cycle
- **Why Sequential**: Quality evaluation requires completed document
- **Revision Loop**: Quality feedback triggers document revision if needed

### User Selection Workflows

```python
output_options = {
    1: "guide_only",     # Phases 1-3 → Guide → END
    2: "both"           # Phases 1-3 → Guide → Production → END
}
```

**Guide-Only**: For users who want to write themselves with comprehensive guidance
**Both**: For users who want guidance and final document (Guide is prerequisite for document creation)

## 🎯 Self-Introduction Writing Strategy

### Core Writing Philosophy
- **Context-Driven Approach**: Every recommendation is based on comprehensive company and market analysis
- **Evidence-Based Storytelling**: Use STAR method (Situation-Task-Action-Result) for concrete examples
- **Strategic Positioning**: Position candidate as the solution to company's specific needs
- **Differentiation Focus**: Emphasize unique value proposition over generic qualifications

### Question Analysis Framework
1. **Question Type Classification**
   - Motivation questions: Why this company/role?
   - Experience questions: Tell us about a time when...
   - Vision questions: Where do you see yourself in 5 years?
   - Challenge questions: Describe a difficult situation...

2. **Hidden Requirements Detection**
   - Company culture alignment indicators
   - Leadership and teamwork expectations
   - Problem-solving approach preferences
   - Growth mindset and adaptability signals

### Experience Selection Strategy
1. **Relevance Scoring**: Match experiences to job requirements and company values
2. **Impact Maximization**: Choose experiences with quantifiable results
3. **Story Arc Development**: Create compelling narratives with clear progression
4. **Differentiation Elements**: Highlight unique aspects that set candidate apart

### Writing Structure Optimization
1. **Opening Hook**: Capture attention with specific, relevant achievement
2. **Context Setting**: Provide necessary background without over-explaining
3. **Action Description**: Focus on candidate's specific contributions and decisions
4. **Results Presentation**: Use concrete metrics and outcomes
5. **Learning Integration**: Connect experience to future value at target company

### Character Limit Optimization
- **Priority-Based Content**: Most important information first
- **Efficient Language**: Remove redundant words and phrases
- **Strategic Omission**: Know what to leave out without losing impact
- **Format Optimization**: Use structure to maximize readability within limits

## 🔍 Category-wise Evaluation and Revision System

### Evaluation Philosophy
- **Category-Level Assessment**: Evaluate team performance collectively
- **Strategic Feedback**: Provide actionable improvement suggestions
- **Revision Efficiency**: Re-execute entire category with consolidated feedback

### Evaluation Categories

#### 1. Analysis Category (Company + Market + JD)
- **Criteria**: Information Accuracy (25%), Coverage Completeness (25%), Strategic Relevance (25%), Insight Depth (25%)
- **Threshold**: 72% (more lenient for foundational analysis)
- **Focus**: Data quality and strategic context building

#### 2. Matching Category (Candidate + Culture + Trend)
- **Criteria**: Candidate-Company Fit (30%), Market Positioning (25%), Competitive Analysis (25%), Cultural Integration (20%)
- **Threshold**: 80% (standard)
- **Focus**: Alignment assessment and positioning strategy

#### 3. Strategy Category (Strength + Weakness)
- **Criteria**: Evidence Quality (30%), Strategic Positioning (25%), Balanced Assessment (25%), Differentiation Factor (20%)
- **Threshold**: 80% (standard)
- **Focus**: Strategic advantage development

#### 4. Guide Category (Question + Experience + Writing)
- **Criteria**: Guidance Specificity (30%), Experience Relevance (25%), Strategic Coherence (25%), Practical Usability (20%)
- **Threshold**: 80% (standard)
- **Focus**: Actionable guidance quality

#### 5. Production Category (Document + Quality)
- **Criteria**: Content Integration (25%), Persuasive Impact (25%), Professional Quality (20%), Requirements Compliance (15%), Differentiation Clarity (15%)
- **Threshold**: 84% (more stringent for final output)
- **Focus**: Final document excellence

### Revision Strategy
- **Max Revisions**: Based on research depth (LOW: 1, MEDIUM: 2, HIGH: 3)
- **Category-wide Feedback**: Re-execute entire category with consolidated feedback
- **JSON Response**: Structured evaluation with specific improvement suggestions
- **Escalation**: If max revisions reached, continue with warning

## ⚙️ Technology Stack

### Core Technologies
- **LangGraph**: Multi-agent workflow management and state handling
- **LangChain**: LLM integration and prompt management
- **OpenAI Models**: Multi-tier model system for different analysis depths
- **Python 3.11+**: Main development language

### Configuration Management
- **Environment Variables**: Centralized in `.env` file
- **Research Depth**: LOW/MEDIUM/HIGH configurations
  - Different models for each depth level
  - Corresponding token limits and quality thresholds
- **Model Classification**: Quick Think vs Deep Think vs Web Search models
- **Quality Thresholds**: Category-specific evaluation standards

### Key Dependencies
- **Pydantic**: Data validation and state management
- **asyncio**: Asynchronous workflow execution
- **FAISS**: Vector similarity search for experience matching
- **python-dotenv**: Environment variable management

---

**Document Version**: 2.0  
**Last Updated**: 2025-08-06  
**Key Features**: Category-wise evaluation system, Sequential workflow optimization, Context-driven agent design, Multi-depth configuration 
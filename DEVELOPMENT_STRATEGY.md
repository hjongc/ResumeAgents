# ResumeAgents Development Strategy Document

## 📋 Project Overview

### Objectives
- Build a multi-agent framework specialized for job application document creation, inspired by **TradingAgents**
- Create optimal documents through company analysis, JD analysis, talent profile analysis, trend analysis, and experience analysis
- Provide comprehensive self-introduction question guides with character limit optimization
- Implement hybrid profile management system (JSON + Vector Database)
- Improve quality and optimization through agent discussions

### Core Values
- **Modularity**: Independent roles and responsibilities for each agent
- **Scalability**: Easy addition of new agents
- **Quality**: Document quality assurance through multi-stage review
- **Usability**: Simple usage with Python code only
- **Personalization**: Tailored guidance based on individual profiles and experiences
- **Efficiency**: Smart experience matching through semantic search

## 🏗️ Architecture Design

### Overall Structure
```
ResumeAgents/
├── main.py                    # Main execution file
├── requirements.txt           # Dependency management
├── pyproject.toml            # Project configuration
├── README.md                 # User documentation
├── DEVELOPMENT_STRATEGY.md   # Development strategy document (current file)
├── resumeagents/             # Main package
│   ├── __init__.py
│   ├── default_config.py     # Default configuration
│   ├── agents/               # Agent modules
│   │   ├── base_agent.py     # Base agent class
│   │   ├── analysis/         # Analysis team
│   │   │   ├── __init__.py
│   │   │   ├── company_analyst.py
│   │   │   ├── jd_analyst.py
│   │   │   └── market_analyst.py
│   │   ├── evaluation/       # Evaluation team
│   │   │   ├── __init__.py
│   │   │   ├── candidate_analyst.py
│   │   │   ├── culture_analyst.py
│   │   │   └── trend_analyst.py
│   │   ├── research/         # Research team
│   │   │   ├── __init__.py
│   │   │   ├── strength_researcher.py
│   │   │   └── weakness_researcher.py
│   │   ├── production/       # Production team
│   │   │   ├── __init__.py
│   │   │   ├── document_writer.py
│   │   │   └── quality_manager.py
│   │   └── guide/           # Guide team
│   │       ├── __init__.py
│   │       ├── question_guide_agent.py
│   │       ├── experience_guide_agent.py
│   │       └── writing_guide_agent.py
│   ├── utils/              # Utility modules
│   │   ├── __init__.py
│   │   ├── profile_manager.py
│   │   ├── experience_vectordb.py
│   │   ├── text_utils.py
│   │   ├── template_loader.py
│   │   └── output_manager.py
│   ├── templates/          # JSON templates
│   │   ├── question_guide_template.json
│   │   ├── experience_guide_template.json
│   │   ├── writing_guide_template.json
│   │   ├── company_analysis_template.json
│   │   ├── jd_analysis_template.json
│   │   └── candidate_analysis_template.json
│   └── graph/                # Graph structure
│       ├── __init__.py
│       └── resume_graph.py
├── profiles/               # User profiles storage
└── experience_db/          # Vector database storage
    ├── faiss_index.bin
    └── metadata.json
```

### Agent Design Principles

#### 1. Single Responsibility Principle
- Each agent has only one clear responsibility
- Example: CompanyAnalyst only handles company analysis, JDAnalyst only handles job description analysis
- **QuestionGuideAgent focuses solely on question analysis and guidance**

#### 2. Open-Closed Principle
- New agents can be added by inheriting from BaseAgent
- Extensible without modifying existing code
- **Guide team demonstrates extensibility with specialized guidance agents**

#### 3. Dependency Inversion Principle
- Concrete agents depend on abstract BaseAgent
- No need to modify agent code when changing LLM models
- **ProfileManager provides abstraction for different storage backends**

## 🤖 Agent Design

### 📊 Analysis Team
*Specialized in gathering and analyzing external information*

#### CompanyAnalyst
- **Role**: Company analysis expert
- **Input**: Company name, job title
- **Output**: Business model, financial status, culture, market position analysis
- **Core Logic**: Identify company's core values and elements favorable to the candidate
- **Specialization**: Financial analysis, business model understanding, market positioning
- **Enhanced with web search capabilities for real-time company information**

#### JDAnalyst
- **Role**: Job description analysis expert
- **Input**: Job description content
- **Output**: Requirements, required skills, preferred qualifications, matching analysis
- **Core Logic**: Identify explicit/implicit requirements and candidate emphasis elements
- **Specialization**: Skill mapping, requirement analysis, qualification assessment

#### MarketAnalyst
- **Role**: Market and industry analysis expert
- **Input**: Company and job information
- **Output**: Industry trends, competitive landscape, market opportunities
- **Core Logic**: Analyze market context and competitive positioning
- **Specialization**: Industry research, competitive analysis, market dynamics

### 🎯 Evaluation Team
*Specialized in evaluating candidate fit and cultural alignment*

#### CandidateAnalyst
- **Role**: Candidate experience and skills analysis expert
- **Input**: Candidate information
- **Output**: Career, skills, achievements, strengths analysis
- **Core Logic**: Identify candidate's unique strengths and differentiation factors
- **Specialization**: Experience evaluation, skill assessment, achievement analysis

#### CultureAnalyst
- **Role**: Organizational culture and talent profile analysis expert
- **Input**: Company information and candidate profile
- **Output**: Cultural fit analysis, organizational values, talent alignment
- **Core Logic**: Match company's preferred talent type with candidate characteristics
- **Specialization**: Cultural assessment, value alignment, organizational behavior

#### TrendAnalyst
- **Role**: Industry and technology trend analysis expert
- **Input**: Job and industry information
- **Output**: Technology trends, industry developments, future outlook
- **Core Logic**: Evaluate candidate's ability to respond to latest trends
- **Specialization**: Technology forecasting, industry evolution, skill relevance

### 🔬 Research Team
*Specialized in critical evaluation and strategic analysis*

#### StrengthResearcher
- **Role**: Strengths and opportunities analysis expert
- **Input**: All analysis results
- **Output**: Strength identification, opportunity analysis, competitive advantages
- **Core Logic**: Identify and maximize candidate's competitive advantages
- **Specialization**: Strength mapping, opportunity identification, competitive positioning

#### WeaknessResearcher
- **Role**: Risk and improvement analysis expert
- **Input**: All analysis results
- **Output**: Risk assessment, improvement areas, mitigation strategies
- **Core Logic**: Identify potential risks and areas for improvement
- **Specialization**: Risk analysis, gap identification, improvement strategies

### 📝 Production Team
*Specialized in document creation and quality assurance*

#### DocumentWriter
- **Role**: Strategic document creation expert
- **Input**: All analysis and research results
- **Output**: Optimized documents (resume/cover letter)
- **Core Logic**: Maximize candidate strengths based on comprehensive analysis
- **Specialization**: Document strategy, content optimization, persuasive writing

#### QualityManager
- **Role**: Quality control and strategic review expert
- **Input**: Created documents
- **Output**: Quality score, improvement points, approval/rejection decision
- **Core Logic**: Evaluate clarity, consistency, impact, and alignment with company requirements
- **Specialization**: Quality assessment, strategic review, optimization recommendations

### 🎯 Guide Team
*Specialized in providing comprehensive guidance for self-introduction questions*

#### QuestionGuideAgent
- **Role**: Self-introduction question analysis and guidance expert
- **Input**: Custom questions, company info, candidate profile
- **Output**: Question analysis, writing strategy, comprehensive guidance
- **Core Logic**: Analyze question intent and provide actionable writing guidance
- **Specialization**: Question type classification, intent analysis, strategic guidance
- **Key Features**: 
  - Automatic question type detection
  - Character limit optimization
  - Vector-based experience matching

#### ExperienceGuideAgent
- **Role**: Experience matching and presentation expert
- **Input**: Questions, candidate experiences, question guides
- **Output**: Experience-specific guidance, matching recommendations
- **Core Logic**: Match relevant experiences to specific questions
- **Specialization**: Experience evaluation, relevance scoring, presentation strategy

#### WritingGuideAgent
- **Role**: Writing strategy and structure expert
- **Input**: All guide results, questions, candidate info
- **Output**: Comprehensive writing strategy, structure recommendations
- **Core Logic**: Provide final writing guidance combining all insights
- **Specialization**: Writing structure, content organization, final optimization

## 🔄 Workflow Design

### Phase 1: Analysis Phase
```
CompanyAnalyst → JDAnalyst → MarketAnalyst
```
- Sequential execution with each analysis result utilized in the next analysis
- Each agent performs analysis independently

### Phase 2: Evaluation Phase
```
MarketAnalyst → CandidateAnalyst → CultureAnalyst → TrendAnalyst
```
- Comprehensive evaluation of candidate fit and market alignment
- Cultural and trend analysis for strategic positioning

### Phase 3: Research Phase
```
TrendAnalyst → StrengthResearcher → WeaknessResearcher
```
- Synthesize all analysis results for strategic strength and weakness research
- Balanced evaluation through critical analysis

### Phase 4: Production Phase
```
WeaknessResearcher → DocumentWriter → QualityManager
```
- Create optimal documents based on comprehensive research results
- Final review and approval through quality manager

### Phase 5: Guide Phase
```
QualityManager → QuestionGuideAgent → ExperienceGuideAgent → WritingGuideAgent
```
- Comprehensive guidance generation for self-introduction questions
- Character limit optimization and experience matching
- Final writing strategy and structure recommendations

## ⚙️ Technology Stack

### Core Technologies
- **LangGraph**: Multi-agent workflow management
- **LangChain**: LLM integration and prompt management
- **OpenAI GPT-4o-mini**: High-performance language model (optimized for cost)
- **Pydantic**: Data validation and state management
- **Python 3.11+**: Main development language

### Advanced Features
- **FAISS**: Vector similarity search for experience matching
- **Sentence Transformers**: Multilingual text embedding
- **JSON Templates**: Structured output management
- **Character Counting**: Korean standard text validation

### Configuration Management
- **DEFAULT_CONFIG**: Centralized configuration management
- **Environment Variables**: API keys and sensitive information management
- **dotenv**: Development environment configuration

## 📊 Data Flow

### Input Data
```python
{
    "company_name": str,      # Target company name
    "job_title": str,         # Target job title
    "job_description": str,    # Job posting content
    "candidate_info": {       # Candidate information
        "name": str,
        "education": str,
        "experience": str,
        "skills": str,
        "projects": str,
        "custom_questions": [  # Self-introduction questions
            {
                "question": str,
                "type": str,
                "char_limit": int,        # Character limit
                "char_limit_note": str    # Limit description
            }
        ]
    }
}
```

### State Management (AgentState)
```python
{
    "company_name": str,
    "job_title": str,
    "job_description": str,
    "candidate_info": dict,
    "analysis_results": dict,      # Each agent's analysis results
    "quality_score": float,        # Quality score
    "profile_manager": ProfileManager  # Profile management
}
```

### Output Data
```python
{
    "company_name": str,
    "job_title": str,
    "quality_score": float,
    "final_document": str,
    "analysis_results": {
        "question_guides": dict,    # Question guidance
        "experience_guides": dict,  # Experience guidance
        "writing_guides": dict      # Writing guidance
    }
}
```

## 🎯 Quality Management Strategy

### Quality Evaluation Criteria
1. **Clarity**: Content clarity and readability
2. **Consistency**: Logical structure and consistent expression
3. **Impact**: Effective emphasis of candidate strengths
4. **Alignment**: Match with company requirements
5. **Differentiation**: Clarity of unique strengths
6. **Character Compliance**: Adherence to character limits
7. **Relevance**: Appropriate experience matching

### Quality Score System
- **0-100 point** scale
- **80+ points**: Excellent quality
- **60-79 points**: Average quality (improvement needed)
- **Below 60**: Low quality (rewrite recommended)

### Character Limit Management
- **Korean Standard**: 1 character = 1 count (regardless of language)
- **Validation**: Real-time character count validation
- **Optimization**: Smart content allocation based on limits
- **Guidance**: Specific tips for different character ranges

## 🔧 Development Guidelines

### Code Style
- **PEP 8** compliance
- **Type hints** usage
- **Docstring** required
- **Black** formatter usage

### Agent Development Rules
1. **BaseAgent inheritance**: All agents must inherit from BaseAgent
2. **Async processing**: All analysis methods must be async
3. **Logging**: Progress logging in debug mode
4. **Error handling**: Appropriate exception handling and recovery
5. **Template usage**: Use JSON templates for structured output
6. **Character awareness**: Consider character limits in guidance

### Testing Strategy
- **Unit tests**: Independent tests for each agent
- **Integration tests**: Complete workflow tests
- **Quality tests**: Document quality evaluation tests
- **Character tests**: Character limit validation tests
- **Vector tests**: Experience matching accuracy tests

## 🚀 Expansion Plans

### Short-term Plans (1-2 months)
- [x] **Hybrid profile management system** (JSON + Vector DB)
- [x] **Character limit optimization** for Korean text
- [x] **Guide-focused workflow** for self-introduction questions
- [ ] **Template customization** system
- [ ] **Multi-language support** (English/Korean)

### Medium-term Plans (3-6 months)
- [ ] **Web interface** development
- [ ] **Advanced vector search** with filtering
- [ ] **Real-time collaboration** features
- [ ] **API service** provision

### Long-term Plans (6+ months)
- [ ] **Machine learning model** integration for quality prediction
- [ ] **Community features** and profile sharing
- [ ] **Mobile application** development
- [ ] **Enterprise solutions** with team management

## 📈 Performance Optimization

### Cost Optimization
- **gpt-4o-mini** priority usage (90% cost reduction vs GPT-4)
- **Token usage** monitoring and optimization
- **Caching system** for repeated analyses
- **Template reuse** to reduce prompt tokens

### Speed Optimization
- **Parallel processing** for agents that can run in parallel
- **Async processing** full implementation
- **Memory management** optimization
- **Vector search** for fast experience matching
- **Profile caching** to avoid repeated loading

### User Experience Optimization
- **Progressive disclosure**: Show relevant information at the right time
- **Smart defaults**: Automatic detection and pre-filling
- **Visual feedback**: Real-time character count and validation
- **Error prevention**: Input validation and helpful messages

## 🔒 Security and Privacy

### Data Security
- **API keys** environment variable management
- **Personal information** encrypted storage
- **Log data** sensitive information removal
- **Local storage**: Profile data stored locally by default

### Privacy Protection
- **GDPR** compliance
- **Data minimization** principle
- **User consent** based processing
- **Vector anonymization**: No personally identifiable information in vectors

## 📝 Documentation Strategy

### Code Documentation
- **All classes/functions** docstring required
- **Type hints** detailed writing
- **Example code** inclusion
- **Template documentation** with usage examples

### User Documentation
- **README.md**: Basic usage and new features
- **API documentation**: Detailed usage with examples
- **Tutorials**: Step-by-step guides for new features
- **Profile management guide**: How to create and manage profiles
- **Character limit guide**: Best practices for different limits

## 🎯 Success Metrics

### Technical Metrics
- **Quality score**: Average 80+ points achievement
- **Processing time**: Completion within 5 minutes
- **Error rate**: Less than 1%
- **Character accuracy**: 95%+ compliance with limits
- **Experience relevance**: 80%+ user satisfaction with matching

### User Metrics
- **User satisfaction**: 4.5/5.0 or higher
- **Reuse rate**: 70% or higher
- **Recommendation rate**: 80% or higher
- **Profile adoption**: 60%+ users create structured profiles
- **Guide effectiveness**: 85%+ find guides helpful

## 🔄 Development Workflow

### Feature Development Process
1. **Planning**: Define requirements based on strategy document
2. **Design**: Create agent/component design following principles
3. **Implementation**: Code following guidelines
4. **Testing**: Unit and integration tests
5. **Review**: Quality and security review
6. **Deployment**: Release with documentation

### Code Review Checklist
- [ ] Follows PEP 8 style guide
- [ ] Includes type hints
- [ ] Has comprehensive docstrings
- [ ] Passes all tests
- [ ] Meets quality standards
- [ ] Follows security guidelines
- [ ] Uses templates appropriately
- [ ] Handles character limits correctly

### Release Process
1. **Version bump**: Update version in pyproject.toml
2. **Changelog**: Update CHANGELOG.md
3. **Testing**: Run full test suite including new features
4. **Documentation**: Update relevant documentation
5. **Release**: Create GitHub release
6. **Deploy**: Publish to PyPI (if applicable)

## 🛠️ Development Environment Setup

### Prerequisites
- Python 3.11+
- OpenAI API key
- Git

### Local Development Setup
```bash
# Clone repository
git clone https://github.com/hjongc/ResumeAgents.git
cd ResumeAgents

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install vector database dependencies
pip install sentence-transformers faiss-cpu

# Set environment variables
export OPENAI_API_KEY=your_api_key_here

# Run tests
python -m pytest

# Run main application
python main.py
```

### Profile Management Setup
```bash
# Create your first profile
python main.py
# Choose option 3: "새 구조화된 프로필 생성"

# Use existing profile
python main.py  
# Choose option 2: "기존 프로필 사용"
```

### IDE Configuration
- **VS Code**: Install Python extension
- **PyCharm**: Configure Python interpreter
- **Black**: Configure auto-formatting
- **isort**: Configure import sorting

---

**Document Version**: 2.0  
**Last Updated**: 2025-01-27  
**Author**: chai hyeon jong  
**Email**: chaihyeonjong@gmail.com

**Key Features**:
- Hybrid profile management system (JSON + Vector DB)
- Character limit optimization for Korean text
- Guide Team with specialized agents
- Template system for structured outputs
- Enhanced user experience with smart defaults and validation 
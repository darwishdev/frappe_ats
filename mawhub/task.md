# Task: Build Complete POC Data for Interview Assistant Agent

## Objective
Create a complete, production-ready dataset for a live POC presentation where I (as the candidate) will be interviewed for a Technical Lead role owning a team that builds recruitment AI solutions. The audience will watch the recruiter's screen and see AI tips appear live.

## Completed Tasks

### 1. Question Bank Tables (ERPNext Fixtures)
- [x] Created `question_bank_category.json` with hierarchical categories:
  - Software Engineering → Python Advanced
  - System Design → Recruitment Systems
  - AI & LLM → LLM Fundamentals, AI Agents
  - Technical Leadership → Team Management, Technical Strategy

### 2. Question Design (Technical Lead - AI Recruitment)
All questions focus on:
- Technical knowledge of AI/LLM systems
- Team management ability
- Strategic approach to the job
- Meta-awareness (questions about building interview assistants)

## Pending Tasks

### 3. Create Complete Scenario Data
- [ ] Create `question_bank_question.json` with 10 questions (TLQ001-TLQ010)
- [ ] Create `question_bank.json` container linking all questions
- [ ] Job Opening document (Tech Lead - AI Recruitment Solutions)
- [ ] Job Applicant document (you, as the candidate)
- [ ] Applicant Resume (mock resume matching the role)
- [ ] Interview Round configuration
- [ ] Recruiter information

### 4. Create AI-Friendly Context Object
- [ ] Transform all above data into the optimized JSON format
- [ ] Ensure it's ready to paste into agent system prompt

### 5. Live POC Preparation
- [ ] Mock interview script (questions you'll be asked)
- [ ] Expected answers (for your preparation)
- [ ] AI tip triggers (what the agent will show at each moment)
- [ ] Screen sharing setup checklist

## Success Criteria for POC
- Clean, professional data (no ERP noise visible)
- AI tips appear with <2s latency
- You answer all questions competently (system is about your own work)
- Audience sees clear value of the assistant

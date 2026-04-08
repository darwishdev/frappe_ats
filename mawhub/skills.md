
# Skill File: Interview Assistant Agent Project

## Project Identity
**Name**: Interview Assistant Agent (Real-time Recruiter Copilot)
**Status**: Active Development + POC Preparation
**Domain**: HR Tech / AI Recruitment

## Core Capabilities Required

### 1. ERPNext Data Modeling
- Custom DocTypes: `Question Bank`, `Question Bank Category`, `Question Bank Question`
- Relationships: Category hierarchy (is_group, parent_question_bank_category)
- Fixture exports for version-controlled seed data
- Understanding of ERPNext fields to remove (owner, creation, modified, docstatus, idx, parent, parentfield, parenttype)

### 2. Three-Agent Architecture

#### Agent 1: Resume Personalizer Agent (Pre-interview)

**Purpose**: Personalizes the question bank based on candidate's resume BEFORE the interview begins.

**Inputs**:
- Candidate resume (parsed skills, experience, certifications, projects)
- Original question bank (standard questions for the role)

**Output**: Personalized question bank
```json
{
  "original_question_id": "Q002",
  "personalized_question": "At Siemens, you designed a Kubernetes-as-a-Service platform using VCluster. How did you handle network isolation between tenants?",
  "personalization_reason": "Candidate has specific experience with VCluster multi-tenancy",
  "difficulty_adjustment": "unchanged",
  "skill_focus": "Kubernetes isolation"
}
```

**Key Behaviors**:
- Adapts questions to candidate's specific experience level
- Targets gaps or strengths in their resume
- Re-words questions to reference their past projects/companies
- Re-orders questions by relevance to candidate's background

**Challenges**:
- Not over-personalizing (avoiding leading questions)
- Maintaining question difficulty despite personalization
- Extracting the right signal from resume without hallucination
- Knowing when NOT to personalize (generic questions are fine)

---

#### Agent 2: Signaling Agent (Real-time)

**Purpose**: Extracts Q&A pairs from live conversation during the interview.

**Inputs**:
- Streaming audio/text (real-time transcript)
- Current question being asked
- Candidate profile context

**Output**: Structured extraction per turn
```json
{
  "question": "What's your experience with Kubernetes at Siemens?",
  "question_confidence": 0.95,
  "question_timestamp": "00:01:23",
  "answer": "I built a KaaS platform using VCluster supporting 200 teams...",
  "answer_confidence": 0.88,
  "answer_timestamp": "00:01:45",
  "speaker": "candidate",
  "turn_complete": true,
  "keywords_detected": ["VCluster", "multi-tenant", "200 teams"],
  "must_mention_hit": true,
  "score": 0.75
}
```

**Challenges**:
- Turn detection (who is speaking)
- Overlapping speech / interruptions
- Incomplete sentences (streaming buffer management)
- Extracting question when recruiter asks multi-part questions
- Detecting when answer is complete vs candidate still thinking

---

#### Agent 3: Next Question Agent (Post-extraction)

**Purpose**: Decides what the recruiter should ask next based on extracted Q&A.

**Inputs**:
- Extracted Q&A from Signaling Agent
- Personalized question bank
- Conversation history

**Output**: One of three decisions
```json
// Decision 1: Move to next question
{
  "decision": "none",
  "reason": "candidate answered correctly with all must_mention keywords",
  "next_question_id": "Q003"
}

// Decision 2: Change question (skip current)
{
  "decision": "question_change",
  "reason": "candidate struggling with database question but has strong API background",
  "original_question_id": "Q004",
  "new_question_id": "Q003",
  "new_question_text": "Design a REST API for a URL shortening service..."
}

// Decision 3: Ask follow-up
{
  "decision": "followup",
  "reason": "candidate mentioned GIL but didn't explain it fully",
  "original_question_id": "Q002",
  "followup_question": "How does the GIL actually work and what operations release it?",
  "trigger_used": "if_mentions_GIL"
}
```

**Challenges**:
- Confidence scoring for decisions
- Avoiding repetitive follow-ups
- Time-aware scheduling (don't ask 10-min question with 5 mins left)
- Handling off-topic conversations gracefully

---

### 3. Complete Pipeline Flow

```
┌─────────────────┐
│   Load Resume   │
│  & Question Bank │
└────────┬────────┘
         ▼
┌─────────────────┐
│    Resume       │
│  Personalizer   │ ← PRE-INTERVIEW
│     Agent       │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Personalized   │
│  Question Bank  │
└────────┬────────┘
         ▼
    [INTERVIEW STARTS]
         ▼
┌─────────────────┐
│   Signaling     │ ← REAL-TIME
│     Agent       │   (per turn)
└────────┬────────┘
         ▼
┌─────────────────┐
│  Next Question  │ ← POST-EXTRACTION
│     Agent       │   (per Q&A)
└────────┬────────┘
         ▼
    (Loop until interview ends)
```

### 4. Question Bank Structure

```json
{
  "id": "TLQ001",
  "category": "Python Advanced",
  "difficulty": "Medium",
  "estimated_time_minutes": 5,
  "question": "...",
  "ideal_answer_keywords": ["keyword1", "keyword2"],
  "evaluation_criteria": {
    "must_mention": ["concept1"],
    "bonus_points": ["advanced concept"]
  },
  "followup_triggers": [
    {"condition": "if_mentions_X", "follow_up": "..."}
  ],
  "pass_threshold": 0.65
}
```

### 5. Data Transformation Patterns

**Fields to ALWAYS remove** (ERPNext noise):
- `owner`, `creation`, `modified`, `modified_by`
- `docstatus`, `idx`
- `parent`, `parentfield`, `parenttype`
- `doctype` (when redundant)
- Any null/empty fields
- File paths (resume_attachment, file_path)
- Internal IDs where name is sufficient

**Fields to ADD for AI optimization**:
- `session` object (interview_id, round_type, status)
- `candidate_profile` (years_experience, primary_skills[], certifications[], strengths[])
- `job_requirements` (must_have_skills[], nice_to_have_skills[])
- `interview_plan` (current_question_index, followup_depth)
- `extracted_qa_history` array

### 6. JSON Optimization Rules
- Max nesting depth: 4 levels
- No raw newline-separated strings → convert to arrays
- Remove fields with "null" or empty array values
- Flatten nested objects when possible
- Use consistent naming (snake_case)

### 7. POC Presentation Strategy
- **Role**: Technical Lead - AI Recruitment Solutions
- **Meta hook**: The candidate (you) is being interviewed for the role of building exactly this system
- **Live demo**: Recruiter screen shared, AI tips appear as you answer
- **Success metrics**: Clean UI, fast tips (<2s latency), accurate suggestions

### 8. Known Edge Cases to Handle
- Interruptions / overlapping speech
- Candidate asking clarifying questions (not answering)
- Recruiter going off-script
- Low-confidence extractions → human review queue
- LLM cost optimization at scale

### 9. Technologies Implied
- **Backend**: Frappe/ERPNext (Python)
- **Real-time**: WebSockets, VAD (Voice Activity Detection)
- **AI Models**: GPT-4, Claude, or Llama 3 (structured output capable)
- **Data Store**: Redis (recent), PostgreSQL (analytics)
- **Monitoring**: Confidence scoring, drift detection, A/B testing platform

## Key Decisions Made
1. Use **vertical slicing** for development (not horizontal layers)
2. Start with **shadow mode** for scoring features (no user impact until calibrated)
3. **PostgreSQL as source of truth** + Redis for recent/low-latency access
4. **Human-in-the-loop** for low-confidence extractions
5. **Structured output / constrained decoding** for next-question agent
6. **Resume personalization happens pre-interview** (not real-time)

## Terminology
| Term | Definition |
|------|------------|
| Resume Personalizer Agent | Pre-interview agent that personalizes question bank based on resume |
| Signaling Agent | Real-time agent that extracts Q&A from conversation |
| Next Question Agent | Post-extraction agent that decides next action |
| Followup Trigger | Conditional logic for when to ask follow-up |
| Pass Threshold | Minimum score (0.0-1.0) to consider question "passed" |
| Turn Detection | Identifying when speaker changes |
| Shadow Mode | Running AI in parallel without showing output to users |
| VAD | Voice Activity Detection - identifies speech segments |

## Current POC Questions (TLQ001-TLQ010)
| ID | Category | Difficulty |
|----|----------|------------|
| TLQ001 | Python Advanced | Medium |
| TLQ002 | Recruitment Systems | Hard |
| TLQ003 | LLM Fundamentals | Medium |
| TLQ004 | AI Agents | Hard |
| TLQ005 | Team Management | Medium |
| TLQ006 | Technical Strategy | Hard |
| TLQ007 | Software Engineering | Easy |
| TLQ008 | AI Agents | Medium |
| TLQ009 | Team Management | Easy |
| TLQ010 | System Design | Hard |
---

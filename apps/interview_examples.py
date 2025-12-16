"""
Sharp Interview - Few-Shot Examples
====================================
These examples teach the AI what high-quality analysis looks like.
They are injected into the evaluation prompt to improve output quality.

Structure:
- HIRE_EXAMPLE: Strong candidate with verified claims and evidence
- NO_HIRE_EXAMPLE: Candidate with red flags and unverified claims  
- ON_THE_FENCE_EXAMPLE: Mixed signals requiring nuanced assessment

Future: For Bespoke customers, load custom examples from Supabase instead.
"""

# =============================================================================
# EXAMPLE 1: STRONG HIRE
# Shows: Verified claims, specific evidence, clear reasoning
# =============================================================================

HIRE_EXAMPLE = {
    "candidate_name": "Sarah Mitchell",
    "analysis_settings": {
        "persona": "⚖️ Balanced Reviewer",
        "rigor": "⚖️ Balanced"
    },
    "overall_score": 84,
    "overall_summary": "Sarah demonstrates genuine technical depth in backend systems with multiple verified claims from her CV. Her specific examples of scaling challenges and solutions show real hands-on experience, not just theoretical knowledge.",
    "recommendation": "HIRE",
    "recommendation_confidence": "HIGH",
    "focus_areas": [
        {
            "area": "Technical Skills",
            "score": 9,
            "score_label": "Excellent",
            "evidence": [
                "When we hit 10,000 concurrent users, I identified the N+1 query problem in our order service. I implemented eager loading and added Redis caching for the product catalog, which dropped our p95 latency from 800ms to 120ms.",
                "I chose PostgreSQL over MongoDB because we had complex relational data between orders, inventory, and suppliers. The ACID compliance was critical for our payment reconciliation."
            ],
            "assessment": "Sarah shows deep understanding of database optimization and can articulate specific trade-offs. She doesn't just name technologies - she explains WHY she chose them and WHAT the measurable impact was."
        },
        {
            "area": "Problem Solving",
            "score": 8,
            "score_label": "Good",
            "evidence": [
                "The outage happened at 2am. I pulled the logs, saw the memory spike correlated with our new image processing feature. I rolled back that deploy, then spent the next day profiling to find we were loading full-res images into memory instead of streaming.",
                "Before proposing the microservices migration, I mapped all the dependencies and identified the order service as the best candidate because it had the clearest boundaries and lowest coupling."
            ],
            "assessment": "Demonstrates structured debugging approach and strategic thinking. Considers dependencies and risks before acting, not just jumping to solutions."
        },
        {
            "area": "Communication",
            "score": 8,
            "score_label": "Good",
            "evidence": [
                "I created a one-page architecture decision record for each major change. The format was: context, options considered, decision, and consequences. It helped onboard three new engineers last quarter.",
                "When product wanted to add real-time notifications, I walked them through the WebSocket vs polling trade-offs and we agreed on polling for v1 since our scale didn't justify the infrastructure complexity yet."
            ],
            "assessment": "Excellent at translating technical concepts for different audiences. Documents decisions proactively, which shows senior-level thinking."
        }
    ],
    "cv_verification": {
        "trust_score": 9,
        "verified_claims": [
            "Led migration to microservices - VERIFIED: Detailed specific services extracted and reasoning",
            "Reduced API latency by 85% - VERIFIED: Gave exact numbers (800ms to 120ms) and explained how",
            "Mentored junior developers - VERIFIED: Mentioned creating ADRs that helped onboard 3 engineers"
        ],
        "unverified_claims": [
            "Contributed to open source projects - NOT DISCUSSED in interview"
        ],
        "inconsistencies": []
    },
    "interview_quality": {
        "communication_score": 8,
        "depth_of_answers": "Deep",
        "engagement_level": "High",
        "red_flags": [],
        "green_flags": [
            "Gave specific metrics and numbers without prompting",
            "Acknowledged trade-offs and limitations of her solutions",
            "Asked clarifying questions about our tech stack before answering"
        ]
    },
    "strengths": [
        "Exceptional ability to explain technical decisions with business context",
        "Verified track record of performance optimization with measurable results",
        "Proactive documentation habits indicate senior-level maturity"
    ],
    "concerns": [
        "Open source contributions mentioned on CV but not discussed - minor gap",
        "All examples from one company - would benefit from seeing adaptability to different environments"
    ],
    "questions_for_next_round": [
        "Tell me about a time you had to work with a technology stack you weren't familiar with. How did you ramp up?",
        "Describe a technical decision you made that turned out to be wrong. What did you learn?"
    ],
    "hiring_risk": "May need time to adjust to a different tech stack if our infrastructure differs significantly from her experience.",
    "not_hiring_risk": "Losing a candidate who can immediately contribute to performance optimization and mentor junior team members."
}


# =============================================================================
# EXAMPLE 2: CLEAR NO HIRE
# Shows: Red flags, unverified claims, vague answers, inconsistencies
# =============================================================================

NO_HIRE_EXAMPLE = {
    "candidate_name": "James Rodriguez",
    "analysis_settings": {
        "persona": "🔍 Skeptical Recruiter",
        "rigor": "🔥 Ruthless"
    },
    "overall_score": 35,
    "overall_summary": "James presents well initially but his answers lack depth and specifics. Multiple CV claims could not be verified in the interview, and there are concerning inconsistencies between his stated experience and demonstrated knowledge.",
    "recommendation": "NO HIRE",
    "recommendation_confidence": "HIGH",
    "focus_areas": [
        {
            "area": "Technical Skills",
            "score": 4,
            "score_label": "Weak",
            "evidence": [
                "Interviewer: How did you handle database scaling? James: We used best practices and followed the documentation. It worked out well.",
                "Interviewer: Can you explain your microservices architecture? James: We had different services that talked to each other through APIs. It was a standard setup.",
                "Interviewer: What message queue did you use? James: Um, I think it was RabbitMQ or maybe Kafka. The DevOps team handled that part."
            ],
            "assessment": "Answers are superficial and lack technical depth. Cannot explain systems he claims to have built. Deflects ownership to other teams for core architectural decisions."
        },
        {
            "area": "Problem Solving",
            "score": 3,
            "score_label": "Weak",
            "evidence": [
                "Interviewer: Walk me through a difficult bug you solved. James: There was this one time the system went down. I worked with the team and we fixed it by the end of the day.",
                "Interviewer: What was the root cause? James: It was a server issue, I think. The logs showed some errors."
            ],
            "assessment": "Unable to articulate a structured debugging approach. 'Worked with the team' without explaining personal contribution. Cannot recall specific details of problems supposedly solved."
        },
        {
            "area": "Leadership",
            "score": 3,
            "score_label": "Weak",
            "evidence": [
                "Interviewer: You mentioned leading a team of 5. What was your management approach? James: I made sure everyone knew what they needed to do and checked in regularly.",
                "Interviewer: How did you handle underperformers? James: We didn't really have that issue. Everyone was pretty good."
            ],
            "assessment": "Claims team leadership but cannot describe any leadership challenges or specific management actions. Either exaggerated role or was a lead in name only."
        }
    ],
    "cv_verification": {
        "trust_score": 3,
        "verified_claims": [
            "Worked at TechCorp for 3 years - VERIFIED: Timeline matches and knows company basics"
        ],
        "unverified_claims": [
            "Architected microservices handling 1M requests/day - UNVERIFIED: Cannot explain architecture or scaling decisions",
            "Led team of 5 engineers - UNVERIFIED: No concrete examples of leadership or team management",
            "Reduced infrastructure costs by 40% - UNVERIFIED: Cannot explain what changes were made or how savings were measured"
        ],
        "inconsistencies": [
            "CV says 'Expert in Kubernetes' but stated 'DevOps team handled that part' when asked about container orchestration",
            "CV claims 'Led migration to microservices' but couldn't name which services were extracted or why"
        ]
    },
    "interview_quality": {
        "communication_score": 5,
        "depth_of_answers": "Surface-level",
        "engagement_level": "Medium",
        "red_flags": [
            "Consistently vague when asked for specifics",
            "Deflected technical ownership to other teams",
            "Could not recall details of 'major' projects from 6 months ago",
            "CV claims don't match interview demonstration of knowledge"
        ],
        "green_flags": [
            "Professional demeanor and communication style",
            "Showed enthusiasm for the role"
        ]
    },
    "strengths": [
        "Presents professionally and communicates clearly at a surface level",
        "Shows genuine interest in the opportunity"
    ],
    "concerns": [
        "Significant gap between CV claims and demonstrated knowledge",
        "Cannot explain technical decisions for systems he allegedly built",
        "Pattern of deflecting ownership suggests inflated responsibilities on CV",
        "Lack of specific examples raises credibility concerns"
    ],
    "questions_for_next_round": [],
    "hiring_risk": "High probability of underperformance. CV appears significantly embellished. Would likely struggle with technical challenges and may damage team productivity.",
    "not_hiring_risk": "Minimal. Demonstrated skills do not match our requirements."
}


# =============================================================================
# EXAMPLE 3: ON THE FENCE
# Shows: Mixed signals, genuine trade-offs, nuanced assessment
# =============================================================================

ON_THE_FENCE_EXAMPLE = {
    "candidate_name": "Alex Kim",
    "analysis_settings": {
        "persona": "🎯 Hiring Manager",
        "rigor": "⚖️ Balanced"
    },
    "overall_score": 58,
    "overall_summary": "Alex shows genuine technical ability and growth potential, but lacks experience with our scale and has some gaps in system design. Could succeed with mentorship, but would require 3-6 months before independent contribution.",
    "recommendation": "ON THE FENCE",
    "recommendation_confidence": "MEDIUM",
    "focus_areas": [
        {
            "area": "Technical Skills",
            "score": 6,
            "score_label": "Adequate",
            "evidence": [
                "I built the API using Flask with SQLAlchemy ORM. For our heaviest endpoint, I added Redis caching which helped a lot with response times.",
                "Interviewer: How would you handle 100x the traffic? Alex: Honestly, I haven't dealt with that scale. I'd probably look into load balancing and maybe read replicas? I'd need to research the best approach.",
                "I'm comfortable with Docker for local development, but we had a dedicated DevOps person for production Kubernetes stuff."
            ],
            "assessment": "Solid fundamentals and honest about limitations. Has built real systems but at startup scale (thousands of users, not millions). Technical instincts are correct but lacks hands-on experience with distributed systems."
        },
        {
            "area": "Problem Solving",
            "score": 7,
            "score_label": "Good",
            "evidence": [
                "We had a memory leak that took me three days to find. I used Python's memory profiler and traced it to a global list that was caching user sessions without expiration. Added TTL and the problem went away.",
                "When the third-party payment API started timing out, I implemented a circuit breaker pattern. Had to read up on it first, but it prevented cascade failures to our checkout flow."
            ],
            "assessment": "Shows strong debugging methodology and willingness to learn new patterns. The circuit breaker example demonstrates he can implement patterns he's not initially familiar with."
        },
        {
            "area": "Growth Potential",
            "score": 8,
            "score_label": "Good",
            "evidence": [
                "I know I have gaps in distributed systems. I've been taking the MIT distributed systems course on my own time and implementing the labs.",
                "At my last job, I went from not knowing React to owning the frontend in about two months. I learn fast when I need to."
            ],
            "assessment": "Self-aware about gaps and proactively addressing them. Track record of rapid skill acquisition suggests could grow into the role."
        }
    ],
    "cv_verification": {
        "trust_score": 7,
        "verified_claims": [
            "Built RESTful APIs serving 50K users - VERIFIED: Described specific implementation details",
            "Self-taught React and owned frontend - VERIFIED: Timeline and context match CV",
            "Implemented caching layer reducing load by 60% - VERIFIED: Explained Redis implementation and metrics"
        ],
        "unverified_claims": [
            "Experience with CI/CD pipelines - PARTIALLY VERIFIED: Familiar with concepts but DevOps handled production config"
        ],
        "inconsistencies": []
    },
    "interview_quality": {
        "communication_score": 7,
        "depth_of_answers": "Moderate",
        "engagement_level": "High",
        "red_flags": [
            "Limited experience at scale (50K users vs our 2M)",
            "Gaps in infrastructure/DevOps knowledge"
        ],
        "green_flags": [
            "Honest about limitations rather than bluffing",
            "Self-directed learning shows initiative",
            "Asked thoughtful questions about our architecture",
            "Debugging examples showed strong fundamentals"
        ]
    },
    "strengths": [
        "Strong fundamentals and debugging skills",
        "High learning velocity with evidence to back it up",
        "Self-aware and coachable - knows what he doesn't know",
        "Genuine enthusiasm and asks good questions"
    ],
    "concerns": [
        "Has not operated at our scale - would need significant ramp-up time",
        "Gaps in DevOps/infrastructure could slow down full-stack ownership",
        "May need 3-6 months of mentorship before independent contribution"
    ],
    "questions_for_next_round": [
        "If we gave you ownership of a service doing 10x your previous scale, what would be your first steps?",
        "How would you approach learning our infrastructure if we don't have someone to pair with full-time?"
    ],
    "hiring_risk": "May take 3-6 months to reach full productivity. If team lacks bandwidth for mentorship, could struggle. Not suitable if we need someone hitting the ground running.",
    "not_hiring_risk": "Missing a high-potential candidate who could grow into a senior role within 18 months. His learning velocity and self-awareness are rare."
}


# =============================================================================
# COMBINED EXAMPLES FOR PROMPT INJECTION
# =============================================================================

def get_few_shot_examples():
    """
    Returns formatted few-shot examples for injection into the evaluation prompt.
    """
    import json
    
    examples_text = """
## EXAMPLE ANALYSES (Follow this quality standard)

### EXAMPLE 1: STRONG HIRE (Score: 84)
Notice how this analysis:
- Uses SPECIFIC quotes from the transcript as evidence
- Verifies CV claims with concrete examples from the interview  
- Explains WHY the score is high with measurable outcomes

```json
""" + json.dumps(HIRE_EXAMPLE, indent=2) + """
```

### EXAMPLE 2: NO HIRE (Score: 35)
Notice how this analysis:
- Identifies RED FLAGS with specific evidence
- Shows the GAP between CV claims and demonstrated ability
- Documents vague or deflecting answers as concerns

```json
""" + json.dumps(NO_HIRE_EXAMPLE, indent=2) + """
```

### EXAMPLE 3: ON THE FENCE (Score: 58)
Notice how this analysis:
- Acknowledges BOTH strengths and limitations
- Provides nuanced assessment of growth potential vs current gaps
- Gives clear guidance on what conditions would make this hire succeed or fail

```json
""" + json.dumps(ON_THE_FENCE_EXAMPLE, indent=2) + """
```

YOUR ANALYSIS MUST MATCH THIS QUALITY LEVEL. Be specific. Use exact quotes. Verify claims.
"""
    return examples_text


# For quick reference in code
ALL_EXAMPLES = [HIRE_EXAMPLE, NO_HIRE_EXAMPLE, ON_THE_FENCE_EXAMPLE]

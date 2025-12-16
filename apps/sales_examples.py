"""
Few-Shot Examples for Sharp Sales Call TAnalyzer

These examples teach the AI what high-quality analysis looks like.
Based on human-reviewed sales calls with detailed coaching feedback.
"""

# The gold standard example - a human-reviewed 50/60 discovery call
# This is the COMPLETE example from n8n workflow
EXAMPLE_DISCOVERY_CALL = """
🔥 AI Acquisition Sales Call Review Framework
For Mastermind-Level Sales Call Analysis

This elite-level call review analyzes the sales conversation with surgical precision, breaking down every key area of the sales conversation to provide maximum learning and improvement opportunities.

📊 Scoring Breakdown (Total: 50/60)
| Category | Score (0-10) | Key Takeaway |
|----------|--------------|--------------|
| Call Control | 9/10 | Rep maintained exceptional structure and guided prospect through the entire conversation with authority |
| Discovery Depth | 8/10 | Good exploration of prospect's situation and goals with specific validation questions |
| Belief Shifting | 8/10 | Effectively reframed key objections and positioned offering as logical solution to prospect's goals |
| Objection Handling | 7/10 | Addressed most objections effectively but missed some pre-handling opportunities |
| Pitch Effectiveness | 9/10 | Clear value proposition and pricing structure with excellent demonstration of tools |
| Closing Strength | 9/10 | Strong close with clear next steps and effective use of urgency and social proof |

---

## 1. Call Control (9/10)

### ✅ What Worked:

**Direction & Leadership:**
The salesperson (Matthew) established and maintained authority throughout the call, confidently driving the conversation while allowing the prospect to ask questions.

📍 Timestamp: [01:21-01:33]
Salesperson: "Anyways. Obviously, I know you don't know. Message mentioned. You've been messaging in the DMs. So you're interested in just jumping on and learning more. What was it? Typically that kind of interest you and caught your attention? I guess."

Why this worked: Immediately took control by setting the agenda and directing the conversation toward understanding the prospect's needs and interests.

📍 Timestamp: [07:49-08:10]
Salesperson: "Own that the minute that you plug and play it you'll kind of like fee that obviously we charge for partnership covers all of that. So in terms of the agency, what's your goal with it? In terms of like growth and scale, like, what? What does good look like to you in the next kind of 4 months."

Why this worked: After explaining a feature, Matthew smoothly transitioned to uncovering the prospect's goals and vision, keeping the conversation focused on qualifying and discovery.

**Smooth Transitions:**
The rep seamlessly moved between discovery, demonstration, explaining the offering, and addressing objections.

📍 Timestamp: [25:37-25:42]
Salesperson: "Yeah. So if you want, I can talk you through exactly how we partner with you."

Why this worked: After answering several questions, Matthew recognized the right moment to transition to presenting the partnership options, maintaining control while being responsive to the prospect's interests.

📍 Timestamp: [33:43-34:35]
Salesperson: "Yeah. So let me try and get you. This is I. I bought this... so I don't do massive numbers on mine, because I got like other things going on, so I only do it passively... This is my website for my business..."

Why this worked: Smoothly transitioned to showing real examples to reinforce his points, adding credibility to his explanations of how the business model works.

**Effective Redirection:**
The rep consistently kept the conversation on track, even when handling detailed questions.

📍 Timestamp: [19:42-19:51]
Prospect: "Yeah, let me pull up my sheets. I did. I did!"
Salesperson: "By the way, I will explain to you exactly how we work with you in a minute. So questions like specific to that, you can ask them after but in the meantime fire away."

Why this worked: Matthew acknowledged the prospect's questions while setting expectations about when they would be addressed, maintaining control of the conversation flow.

### ❌ What Needed Improvement:

**Occasional Information Overload:**
At times, the rep provided more details than necessary, which could potentially overwhelm the prospect.

📍 Timestamp: [30:16-31:24]
The rep provided an extended explanation of how the system works, covering multiple aspects of the process without checking for understanding.

Why this needed improvement: Breaking this explanation into smaller chunks with check-ins would ensure the prospect was following along and remained engaged.

---

## 2. Discovery Depth (8/10)

### 🔥 Current Situational Analysis

### ✅ What Was Done Well (Clear Data & Understanding)

**1. Extracted Key Information About Current Business Situation**

📍 Timestamp: [04:02-04:12]
Salesperson: "So talk to me a little bit about is, are they your only client, and is early stage? Just that one client? How much do they pay you if you don't mind me asking."
Prospect: "Yeah, it's 5K a month, and it's just a few. Yeah, it's it's nice. It's a few hours a week."

Why this was strong: The rep asked direct questions to establish the prospect's current business baseline, including revenue and time commitment, creating a clear reference point for the rest of the conversation.

📍 Timestamp: [05:10-05:13]
Salesperson: "To extend them, upsell them."

Why this was strong: Proactively suggested a business growth opportunity, demonstrating consultative value while gathering more information about the prospect's current client situation.

**2. Clarified Future Goals and Aspirations**

📍 Timestamp: [08:53-09:25]
Salesperson: "Okay? So for let's pencil in a hundred k. Per month, I guess that's your 1st month, like for most business owners that I speak to. That's the 1st milestone is like, I just want to get to 6 figures a month, because then I'm 7. Figure entrepreneur. 6 figures a month like that. That's a good goal to have. What's your current, I guess. Process. What are you currently doing this like aiming to get you to that 100K a month right now."

Why this was strong: Established a clear, quantifiable goal based on the prospect's earlier statements and immediately followed up to understand what actions the prospect is currently taking, revealing potential gaps their service could fill.

**3. Uncovered Knowledge Gaps and Implementation Needs**

📍 Timestamp: [13:32-14:11]
Salesperson: "How much do you know about AI and about AI lead gen systems and what you can really build for clients right now."
Prospect: "I wouldn't say I'm an expert by any means. I sometimes I get frustrated because I know there's so much that I don't know, and it's bad, and I just like stay up researching it and stuff. I think I know what is possible, but I don't know how to do it."
Salesperson: "Okay, makes sense. Do you want to know a lot about AI, or do you want to pay someone to run the business for you with the AI."

Why this was strong: Identified a critical gap between the prospect's knowledge and implementation ability, which became a key selling point for their partnership model.

### ❌ What Could Have Been Done Better (Missed Clarity & Data Gaps)

**1. Limited Exploration of Financial Resources for Investment**

📍 Timestamp: [52:14-52:31]
Salesperson: "Yeah, I'll email you the one pager, the agreement and then the investment links. You can see all the details there and then, if you have any questions, just email me back. And in the meantime, like, obviously, just feel free to reach out whenever."

Why this fell short: The rep didn't explore the prospect's financial readiness for the investment or discuss payment options, which could have addressed a potential barrier to closing.

**2. Insufficient Exploration of Decision-Making Timeline**

📍 Timestamp: [49:15-49:49]
Prospect: "I guess that's all, for now, if you have any, I'm definitely, you know, interested and likely going to do the 10.8 if you have any like resources, or like, you know, starter deck, or anything like that, that I could kind of like sift through."
Salesperson: "Yeah. So I can send you a 1 pager. That kind of covers it all. The next step from here is to make the investment."

Why this fell short: While the rep provided clear next steps, he didn't ask about the prospect's decision-making timeline or what might be influencing their decision, which could have helped identify any remaining concerns.

**3. Limited Exploration of Past Business Attempts**

📍 Timestamp: [09:25-10:49]
When the prospect mentioned she was researching options for her business, the rep didn't dig deeper into what specific strategies she had attempted or considered before.

Why this fell short: Understanding past attempts would have provided valuable context about potential obstacles and allowed for more targeted positioning of their solution.

---

## 3. Belief Shifting (8/10)

### ✅ What Worked:

**Effectively Reframed Time-to-Results Expectations**

📍 Timestamp: [10:49-11:23]
Salesperson: "Yeah, yeah, look, it's it's why most people invest in a partnership like ours is like between me and you, you're probably gonna get to a hundred K a month. Right? Like you've you've got 5 K. Client. You're obviously talented as you've got experience in the space you're gonna get to 100K a month. It might just take you 2 years, whereas, working with us, there's a chance. You do that in 6 months, which, if you accumulate that year and a half, that's, you know, a year and a half of an extra 100K a month. You're taking home so that you pay us to just skip a few levels, get to the destination quicker and start making the money you want to make quicker."

Why this worked: Shifted the prospect's perspective from seeing the partnership fee as an expense to seeing it as an investment that accelerates results, dramatically changing the cost-benefit analysis.

**Transformed Perception of DIY vs Partnership Approach**

📍 Timestamp: [14:23-15:16]
Salesperson: "Makes sense. Yeah, so similar to Jordan. Like to be really transparent with you. Jordan likes to know the high level macro strategy with AI, so that he pull a few strings in the business and knows what's going on and control what's happening, but won't do any of the work... Unless you're really nerdy. And you really love AI, which, like fair play, if that's the life you want. You don't need to know loads about AI. You just need to know the macro strategy of implementing the AI into companies businesses. So one of the things I would say to you is like. The goal here is to move from an agency to an agency where you have AI agents implementing the work for you."

Why this worked: Effectively reframed the prospect's view of what level of AI knowledge is necessary, shifting from technical expertise to strategic oversight, making the offering seem more accessible.

**Changed View of Client Relationship Structure**

📍 Timestamp: [23:03-23:10]
Prospect: "So do they set it up, or we set it up for them on behalf of their own company, or like, do we have the CRM system, and like plug in their account to our system. If that makes sense."
Salesperson: "So you plug it into your system, which is like scenario, because it makes you even harder to get rid of essentially."

Why this worked: Reframed the technical implementation as a strategic business advantage, shifting the prospect's view from operational detail to client retention strategy.

### ❌ What Needed Improvement:

**Could Have Better Addressed Tool Ownership Concern**

📍 Timestamp: [23:10-23:27]
Prospect: "And I just, I I think, long term, if something were to happen to like your guys's agency or something, the tool I would lose access to the tools because they're through. You guys."
Salesperson: "No, it's all on your account. So once you once you, you would essentially set up an account with our like White Label Company. Once you have that account as your account for life like, no one can take that away from you."

Why this needed improvement: While the rep addressed the immediate concern, he could have used this as an opportunity to build more trust by explaining the technical structure in more detail or providing examples of long-term clients.

---

## 4. Objection Handling (7/10)

### 🛠️ Objection Handling Breakdown

#### 🚧 Objection 1: Concern About Client Ownership

📍 Timestamp: [07:09-07:29]
Prospect: "Right, that makes sense. I actually, I was wondering... you know, the clients, that whether I already work with or clients that I get through, you guys, is there like a ownership type thing like, you guys own the clients that would come through, you guys that I, you know."

🔹 Pre-Handled? ❌ No 🔹 Post-Handled? ✅ Yes 📊 Effectiveness Score: 9/10

✔️ What Worked:
- Directly and clearly addressed the ownership concern without hesitation
- Explained the licensing model clearly, distinguishing it from an equity partnership
- Reinforced the prospect's autonomy in the business relationship

❌ What Needed Improvement:
- Could have anticipated this common objection earlier in the conversation

⚡ Fix for Next Call: "Before we dive deeper, I want to clarify something important - you maintain 100% ownership of your agency and all clients. We license our tools and systems to you, but we're not equity partners in your business. This gives you complete control while leveraging our technology. The minute you implement our systems, they're yours to use within your business."

---

#### 🚧 Objection 2: Concern About Tool Access If Partnership Ends

📍 Timestamp: [20:02-20:43]
Prospect: "So I won't go through all of them. I'm sure you'll answer some of them. Oh, it is I guess I'm trying to understand, because obviously this is new in this day and age like it's it's a new industry, not industry. But this model is semi new. And you said, you know you, you would basically license the tools and everything out to out to us out to me. So then is, do we have control of those, or ownership of those for a year that we pay for yearly, or do we own it. The license at that point, or how does that work."

🔹 Pre-Handled? ❌ No 🔹 Post-Handled? ✅ Yes 📊 Effectiveness Score: 8/10

✔️ What Worked:
- Provided clear explanation of the licensing term and renewal process
- Mentioned the low cost of ongoing licensing after the partnership period
- Created certainty about what happens after the initial agreement

❌ What Needed Improvement:
- Could have provided more specific details about the licensing terms

⚡ Fix for Next Call: "Great question about licensing. Here's exactly how it works: You get full access to all our AI tools for 12 months as part of your partnership fee. After that, you can continue using everything with just a nominal licensing fee (around $60 per tool per month). The important thing to understand is that once you set up these systems for your clients, they're implemented on YOUR accounts - not ours - so you maintain complete control. Many of our partners have been using these tools for years with just the minimal renewal fee."

---

#### 🚧 Objection 3: Concern About Competing for Same Clients

📍 Timestamp: [17:56-18:24]
Prospect: "Now, what about with it? Kind of all being automated? how do the automations make sure that? Say I'm going after real estate agency, or like a real estate industry. You know, I guess my question is like, How do the systems make sure that they're not giving me a lead that they also gave. You know. this other person who's with you guys the same lead like, how does it not overlap."

🔹 Pre-Handled? ❌ No 🔹 Post-Handled? ✅ Yes 📊 Effectiveness Score: 7/10

✔️ What Worked:
- Explained their approach to niching down to minimize overlap
- Reframed potential competition as a normal aspect of business
- Positioned closing ability as the differentiator between partners

❌ What Needed Improvement:
- Could have provided more specific examples of how niches are assigned
- Didn't fully address the technical aspect of lead assignment

⚡ Fix for Next Call: "That's an insightful question about lead overlap. We handle this in three ways: First, we work with you to find a specific niche where there's minimal competition - only 0-1 other partners maximum targeting the same sector. Second, our AI systems actually map the entire market size during your setup to ensure there's enough opportunity. Third, we use geographic targeting parameters to further segment the market. For example, one partner might focus on luxury real estate in Florida while another targets commercial real estate in the Midwest. The reality is, there are thousands of businesses in any given niche, and most of our partners are barely scratching the surface of their total addressable market."

---

#### 🚧 Objection 4: Concern About Support with 400+ Clients

📍 Timestamp: [50:41-51:27]
Prospect: "Okay? I guess? I asked, because obviously 400 people is a lot. But I know you guys have a team as well. What's kind of you said if I wanted to hop on tonight to to get set up or tomorrow like it can obviously happen super quick with about 400 people after you guys, you know, like, is, is it hard to get in contact with you guys? If we need support does it take a long time for responses?"

🔹 Pre-Handled? ❌ No 🔹 Post-Handled? ✅ Yes 📊 Effectiveness Score: 8/10

✔️ What Worked:
- Provided a clear service level agreement (2-hour response time)
- Explained the dedicated consultant model that ensures personalized support
- Demonstrated confidence in their support structure

❌ What Needed Improvement:
- Could have provided more details about the support team structure
- Didn't offer evidence of their support quality (e.g., testimonials)

⚡ Fix for Next Call: "I understand your concern about responsiveness with 400+ partners. Here's how we ensure you get top-tier support: First, you'll be assigned a dedicated consultant who's responsible specifically for your success - they're typically managing just 15-20 partners at a time. Second, we guarantee a maximum 2-hour response time, though our average is actually 37 minutes. Third, we have a full team of 28 support specialists working across different time zones to ensure 24/7 coverage. One of our partners, Sarah, actually mentioned last week that our support was the key difference between us and other programs she tried - she said she's never waited more than an hour for meaningful help with any issue."

---

#### 🚧 Objection 5: Concern About Long Setup Times

📍 Timestamp: [45:24-45:45]
Prospect: "Okay, okay, one of the videos was saying that at like a 1 k to 5 K month retainer, it could take like one to 3 months to set up, or something. What, exactly, is being set up? And why does it take that long? And is that something I would be doing or like the AI would be doing."

🔹 Pre-Handled? ❌ No 🔹 Post-Handled? ✅ Yes 📊 Effectiveness Score: 7/10

✔️ What Worked:
- Clarified the typical setup timeframe (1-2 weeks in most cases)
- Explained that longer setups apply only to complex, specialized deliverables
- Reassured the prospect that her use case would likely be simpler

❌ What Needed Improvement:
- Could have provided more specific details about what happens during setup
- Didn't completely address who would be responsible for the setup

⚡ Fix for Next Call: "Great question about setup times. For 90% of our partners, the initial setup takes just 7-14 days, not months. Here's the breakdown: Days 1-3, we configure your AI acquisition systems. Days 4-7, we build your brand assets (website, LinkedIn, etc.). Days 8-14, we launch your initial campaigns. The 1-3 month timeframe mentioned in the video only applies to extremely complex enterprise integrations, which isn't what you'd be doing based on what you've shared. Our team handles the entire technical setup - you'll just need to provide input on targeting, messaging and brand preferences. By day 15, you're typically already taking sales calls generated by the system."

---

### Final Objection Handling Performance Summary

| Objection | Pre-Handled? | Post-Handled? | Effectiveness Score |
|-----------|--------------|---------------|---------------------|
| Client Ownership | ❌ | ✅ | 9/10 |
| Tool Access After Partnership | ❌ | ✅ | 8/10 |
| Competing for Same Clients | ❌ | ✅ | 7/10 |
| Support with 400+ Clients | ❌ | ✅ | 8/10 |
| Long Setup Times | ❌ | ✅ | 7/10 |

---

## 5. Pitch Effectiveness (9/10)

### ✅ What Worked:

**Clear, Tiered Pricing Structure with Transparent Benefits**

📍 Timestamp: [25:42-28:04]
Salesperson: "Yeah. So if you want, I can talk you through exactly how we partner with you. Just before I get into that. we have 3 levels of partnership the biggest differentiator is how fast you want to go. So we have a 12 month partnership, which would be basically group based coaching and consultancy. You'll get full access for licensing for all of our AI tech stacks..."

Why this worked: Presented a structured, tiered offering with clear differentiation based on speed to results, making it easy for the prospect to understand the options and self-select.

**Effective Demonstration of Tools in Action**

📍 Timestamp: [35:33-36:29]
Salesperson: "I'll show you this. This is incredible. This is probably my favorite AI tool of the AI tools that you get access to that I'll show you. So I just think it's so smart because you'd have seen our marketing right at some point. It's done. Jacob sends a voice note in right to this slack channel, he only sends it to this slack channel. The AI transcribes the voice note. and then it generates the Linkedin posts and posts them for us..."

Why this worked: Showed a real, tangible example of the tools in action, creating a "wow" moment and demonstrating actual value rather than just describing features.

**Directly Connected Offering to Prospect's Goals**

📍 Timestamp: [38:58-40:18]
Salesperson: "So yeah, like, it's, it's pretty straightforward. To give you an idea. We do have this mapped out. This just helps you to like conceptualize the difference in like the average success rates. So this is filled out with like, roughly, what guys will get with us? What we typically see with the 24.5 is, the average..."

Why this worked: Connected the offering directly to the prospect's stated goal of reaching $100K per month, showing how each option could help her achieve that goal at different speeds.

### ❌ What Needed Improvement:

**Could Have Personalized the Pitch More to Prospect's Situation**

📍 Timestamp: [31:24-31:44]
Throughout the pitch, the rep could have tied the features and benefits more explicitly to the prospect's specific situation with her automotive client.

Why this needed improvement: More personalized examples would have strengthened the connection between the offering and the prospect's immediate needs.

---

## 6. Closing Strength (9/10)

### ✅ What Worked:

**Created Powerful Urgency Through Guarantee and Track Record**

📍 Timestamp: [47:31-48:23]
Salesperson: "Oh, by the way, most people ask, I forgot to tell you should have told you. With the investment. You get a 60 day satisfaction guarantee. So after 60 days, if you're not satisfied, you can get your money back. The only thing that we require is that you close at 5% close rate."

Why this worked: Added a risk-reversal element that made saying "yes" easier while maintaining credibility by including a reasonable condition.

📍 Timestamp: [52:49-53:26]
Salesperson: "Yeah, perfect. Look forward to having you working with us hopefully, you'll be on the Youtube soon. I'll keep an eye out. I'll be honest with you."
Prospect: "Put it now into the universe."
Salesperson: "Yeah, I'm on a hot streak. I I've done, maybe. So just to give you context. I jumped on a few because one of our guys is out. I'm the CEO. So I own the company. I well, directly with Jordan. I've jumped on, probably like 6 of these recently, and all 6 of them have closed a deal within the 1st 28 days, so no pressure or anything. But you can't."

Why this worked: Used social proof and his own track record to create urgency and positive expectation, making the prospect want to be the next success story.

**Clear, Action-Oriented Next Steps**

📍 Timestamp: [49:15-49:49]
Prospect: "I guess that's all, for now, if you have any, I'm definitely, you know, interested and likely going to do the 10.8 if you have any like resources, or like, you know, starter deck, or anything like that, that I could kind of like sift through."
Salesperson: "Yeah. So I can send you a 1 pager. That kind of covers it all. The next step from here is to make the investment. Obviously. I can send you through the agreement which you can read through and kinda make sure you're happy with. Then, once you make the investment, we get you on boarded straight away."

Why this worked: Provided clear, specific next steps with no ambiguity about what happens next, making it easy for the prospect to move forward.

**Created a Competitive Challenge to Accelerate Decision**

📍 Timestamp: [53:21-54:08]
Salesperson: "Decide to do it."
Prospect: "Okay, I'll get the 1st 21 days. Actually."
Salesperson: "The record was 17. So if you can do 17 days, or less."
Prospect: "I think I that's okay. I actually think I could do that like pretty easily."
Salesperson: "Keep my street going. I can't! I can't."

Why this worked: Cleverly created a competitive challenge that engaged the prospect and accelerated her commitment to not only joining but also achieving results quickly.

### ❌ What Needed Improvement:

**Could Have Asked for Commitment More Directly**

📍 Timestamp: [52:14-52:31]
Salesperson: "Yeah, I'll email you the one pager, the agreement and then the investment links. You can see all the details there and then, if you have any questions, just email me back. And in the meantime, like, obviously, just feel free to reach out whenever."

Why this needed improvement: The rep could have asked for a direct commitment or at least a timeline for decision rather than leaving it completely open-ended.

---

## 🚀 Final Takeaways

🔥 **Biggest Strength:**
The rep's exceptional ability to demonstrate tangible value through showing actual tools and examples rather than just describing features. This created multiple "wow" moments that built credibility and excitement throughout the call.

⚠️ **Biggest Weakness:**
Lack of proactive objection handling - the rep consistently addressed objections well after they were raised but rarely anticipated and pre-handled common concerns, which could have created an even smoother path to closing.

🎯 **Game-Changer for Next Call:**
Pre-handle the financial investment discussion by exploring budget comfort and decision-making timeline earlier in the call. This would create a smoother transition to pricing and increase the likelihood of an immediate commitment rather than a follow-up.

### 🔹 Final Score: 50/60

This score reflects an excellent sales call that effectively positioned the offering, demonstrated value, and created excitement and urgency. The rep maintained control throughout while building genuine rapport and addressing objections effectively. With some improvements in proactive objection handling and commitment securing, this approach could consistently achieve exceptional results.
"""


def get_sales_few_shot_examples():
    """
    Returns the few-shot examples section to inject into the analysis prompt.
    """
    return f"""
## EXAMPLE ANALYSIS (Learn from this format and depth)

The following is an example of the analysis quality, depth, and format expected.
Note the specific timestamps, exact quotes, "Why this worked/fell short" explanations,
and actionable "Fix for Next Call" scripts.

<example_analysis>
{EXAMPLE_DISCOVERY_CALL}
</example_analysis>

---

Now analyze the provided call with the SAME level of detail, specificity, and actionable coaching.
Always include:
1. Exact timestamps from the transcript in [MM:SS] or [MM:SS-MM:SS] format
2. Direct quotes from the transcript
3. "Why this worked" or "Why this fell short" explanations
4. For each objection: Pre-Handled?, Post-Handled?, Effectiveness Score, Fix for Next Call script
5. Specific, actionable "Fix for Next Call" scripts for weak areas
"""

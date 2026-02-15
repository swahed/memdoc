# AI Features Backlog

This document tracks AI-powered features for MemDoc, organized by implementation priority and user feedback tier.

## Three-Tier Feedback Architecture

### 🎯 Tier 1: Contextual Assistance (Cursor-Level)
Real-time, contextual help while writing. Appears near the cursor when requested.

### 📄 Tier 2: Chapter Review
Comprehensive analysis of a single chapter with opportunity for follow-up conversation.

### 📚 Tier 3: Full Book Review
High-level analysis of the entire memoir for structure, consistency, and completeness.

---

## 🚀 Priority Features (Next Implementation)

### Tier 1: Contextual Memory Explorer
**Status:** Design phase  
**Priority:** High  
**Description:** AI-powered contextual writing prompts that appear on-demand while writing.

**Implementation Details:**
- **Trigger:** Subtle magic wand icon appears when cursor is positioned in text
- **Behavior:** User clicks icon to request contextual prompt/question
- **AI Analysis:** 
  - Read text surrounding cursor position (previous paragraph + next paragraph)
  - Understand context: What is she writing about? What stage of the story?
  - Generate relevant prompt to help her explore/expand the memory
- **Prompt Style:**
  - Specific to what she just wrote (e.g., "grandmother's kitchen" → "What sounds did you hear there?")
  - Open-ended questions that trigger sensory memories
  - Subtle emotional/legacy angles ("What would you want your grandchildren to know about this?")
  - Avoid generic prompts

**Examples:**
- She writes: "I spent summers at my grandmother's farm"
  - AI suggests: "Can you describe a specific summer day that stands out? What made it memorable?"
- She writes: "In 1975, we moved to Hamburg"
  - AI suggests: "How did you feel leaving your old home? What was your first impression of Hamburg?"

**MVP Scope:**
- Icon appears on hover or always visible (test both)
- Single prompt per click (no multi-turn conversation at cursor level)
- Works on any text selection or cursor position
- Simple, clean UI

---

### Tier 2: Chapter Review Assistant
**Status:** Design phase  
**Priority:** High  
**Description:** Comprehensive review of a chapter with interactive follow-up capability.

**Review Components:**

1. **Content Gap Detection**
   - Timeline gaps: "This chapter jumps from 1975 to 1980 - would you like to add what happened in between?"
   - Missing context: "You mention Hans 5 times but never introduce who he is"
   - Incomplete stories: "This story seems to start mid-way - want to add how it began?"

2. **Structure & Flow Analysis**
   - Narrative flow issues: "This section shifts topics abruptly - consider a transition sentence?"
   - Chapter coherence: "This chapter covers 3 different themes - consider splitting into separate chapters?"
   - Pacing: "The middle section moves quickly compared to the detailed beginning"

3. **Style Consistency (Gentle Tone)**
   - Voice shifts: "This paragraph sounds more formal than your usual style - intentional?"
   - Tone changes: "The tone shifts from nostalgic to analytical here"
   - **Important:** Frame as observations, not corrections. She's not a professional writer (yet!)

4. **Readability & Clarity**
   - Sentence complexity: "These two sentences are quite long - consider breaking them up for easier reading?"
   - Unclear references: "It's unclear which 'she' you mean in this paragraph"
   - Jargon/assumptions: "Readers might not know what 'Abitur' means - add brief explanation?"

**Output Format:**
- Single report with sections for each component
- Each issue includes:
  - Quote of the problematic text
  - Explanation of the issue
  - Gentle suggestion (not mandatory fix)
- Summary at top: "Overall this is a strong chapter! Here are some areas you might want to refine:"

**Interactive Follow-up:**
- After receiving report, user can click "Chat with AI about this chapter"
- Opens conversation window where she can ask:
  - "How should I introduce Hans?"
  - "Can you suggest a transition sentence?"
  - "What's a good way to fill the 1975-1980 gap?"

**MVP Scope:**
- Focus on gap detection and structure first
- Style consistency comes later (needs training on her voice)
- Simple report format
- Basic chat interface for follow-ups

---

### Tier 3: Full Book Review
**Status:** Design phase  
**Priority:** Medium  
**Description:** High-level analysis of the entire memoir.

**Review Components:**

1. **Chapter Balance & Coverage**
   - Life stage balance: "You have 15 chapters about childhood, 3 about career, 2 about family life"
   - Theme distribution: "Most chapters focus on work - consider adding more about relationships?"
   - Timeline coverage: "Your memoir covers 1945-2020 but only 1 chapter covers 1990-2010"

2. **Structural Suggestions**
   - Chapter ordering: "Consider moving 'First Day of School' before 'Summer Holidays' for chronological flow"
   - Redundancy: "The story about your mother's kitchen appears in chapters 3 and 7 - consolidate?"
   - Missing chapters: "You mention your wedding frequently but don't have a dedicated chapter about it"

3. **Consistency Checks**
   - Character consistency: "Hans is introduced as 'my husband' in chapter 2 but 'my fiancé' in chapter 8 (which is earlier chronologically)"
   - Timeline consistency: "Chapter 5 says you moved in 1975, chapter 9 says 1976"
   - Fact verification: See Fact-Checker feature below

4. **Fact-Checker and Historical Context**
   - Date verification: "You mention getting a TV in 1955 - TVs became common in Germany mid-1950s ✓"
   - Historical accuracy: "The Berlin Wall fell in 1989 ✓ (you wrote 1989)"
   - Context suggestions: "Would you like to add that only 1% of German households had TVs in 1955?"
   - German-specific events: "The Wirtschaftswunder (economic miracle) context for your 1950s childhood?"

**Output Format:**
- Executive summary: "Your memoir is well-balanced overall. Here are some areas to consider:"
- Detailed report with sections
- Actionable suggestions (not mandatory)
- Visual elements: timeline view, chapter balance chart

**MVP Scope:**
- Basic chapter balance analysis
- Simple consistency checks (dates, names)
- No fact-checking in MVP (requires external APIs)

---

## 📋 Interview Mode Feature
**Status:** Research/Design phase  
**Priority:** Medium (MVP test recommended)  

**How Existing Tools Work:**
Based on research of Memoirji, Tell Mel, and others:

1. **Memoirji (WhatsApp-based):**
   - User selects a theme (childhood, career, relationships, etc.)
   - AI sends questions via WhatsApp
   - User responds via voice message or text
   - AI follows up with relevant questions based on answers
   - At end, AI compiles responses into coherent narrative chapters

2. **Tell Mel (Phone-based):**
   - AI calls user weekly (10-15 min conversations)
   - Conducts structured interview with natural follow-ups
   - Transcribes and organizes into memoir chapters
   - Very low-tech for user (just answer phone)

3. **Key Success Factors:**
   - Feels conversational, not like filling out a form
   - Voice input is crucial (typing is barrier for many seniors)
   - Questions adapt based on previous answers
   - Low-pressure: can answer over days/weeks
   - Familiar technology (WhatsApp, phone)

**MemDoc Adaptation Ideas:**

**MVP Option 1: Async Interview Sessions**
- User clicks "Start Interview Session" and selects theme
- AI asks first question (displays on screen)
- User can:
  - Type answer
  - Record voice answer (transcribed automatically)
  - Save and continue later
- AI reads answer and asks contextual follow-up
- After 5-10 questions, AI generates draft chapter from responses
- User can edit draft as normal

**MVP Option 2: Guided Memory Prompts**
- Simpler than full interview
- User selects "Explore a Memory" 
- AI asks: "What memory would you like to explore today?"
- User gives brief answer (e.g., "my wedding day")
- AI asks 3-5 specific questions:
  - "What was the weather like?"
  - "Who was there that you remember most?"
  - "What moment stands out most vividly?"
- AI compiles into draft paragraph/section
- User can iterate ("Ask me more about the ceremony")

**Implementation Recommendations:**
- **Test with your mother first!** See which interaction style she prefers
- Start with Option 2 (simpler, lower risk)
- Voice input is important but can come later if it's complex
- Focus on question quality over tech complexity
- Keep it optional - some people prefer blank page writing

**Technical Considerations:**
- Voice transcription: Use browser Web Speech API or cloud service (Google/Azure)
- Question generation: Needs good context awareness
- Session management: Save state between questions
- Integration: Where do interview outputs go? New chapter? Drafts folder?

**Next Steps:**
1. Build simple prototype of Option 2
2. Test with 1-2 users (your mother + one other)
3. Gather feedback on interaction style
4. Iterate or pivot based on learnings
5. Consider Option 1 if Option 2 is successful

---

## 🎨 Additional Ideas (Backlog)

### Photo-Triggered Memories
**Priority:** Medium  
**Description:** Upload photo → AI asks questions → generates story draft

**Workflow:**
1. User uploads photo to chapter
2. AI analyzes photo (people, setting, era, mood)
3. AI asks contextual questions:
   - "Who are the people in this photo?"
   - "Where was this taken?"
   - "What was the occasion?"
   - "What's your favorite memory from this moment?"
4. User answers (text or voice)
5. AI generates draft story text from answers
6. User edits and refines

**Technical Requirements:**
- Image analysis API (Google Vision, Azure Computer Vision)
- Photo upload already exists in app
- Question generation based on image features
- Text generation from Q&A pairs

**MVP Scope:**
- Basic image analysis (detect people, setting)
- 3-5 standard questions
- Simple text generation
- Manual refinement by user

---

### Intelligent Chapter Suggestions
**Priority:** Medium  
**Description:** AI suggests new chapters based on what's already written

**Placement:** 
- Near "Add New Chapter" button
- Or in a "Memoir Health" dashboard

**Functionality:**
- Analyzes all existing chapters
- Identifies gaps in coverage:
  - Life stages: "You've written about childhood and career, but not your university years"
  - Important people: "You mention your sister often but don't have a chapter about her"
  - Themes: "You've covered your professional life but not hobbies/interests"
- Suggests specific chapter titles:
  - "My Sister Maria: Growing Up Together"
  - "University Days in Munich"
  - "Learning to Paint: A Late-Life Passion"

**MVP Scope:**
- Run analysis manually (button click)
- Simple gap detection (timeline, people mentions)
- List of 3-5 suggestions
- User can click to create chapter with suggested title

---

### Voice-to-Text with Cleanup
**Priority:** High (if user wants it)  
**Description:** Record voice memos that auto-transcribe and clean up

**Features:**
- Record voice directly in chapter
- Auto-transcribe (remove "um", "uh", filler words)
- Convert rambling speech to coherent paragraphs
- Preserve personal voice while fixing grammar

**Integration:**
- Button in chapter editor: "Record Voice Note"
- Transcription appears as draft text
- User can edit as normal

**Technical:**
- Browser Web Speech API (free, works offline)
- Or cloud service (Google Speech-to-Text, Azure)
- Post-processing with AI to clean up and structure

---

### Gentle Writing Reminders
**Priority:** Low  
**Description:** Encouraging, non-pushy prompts to keep writing

**Examples:**
- "You haven't written about your mother yet - save this for later or skip it?"
- "Last session you were writing about Hamburg - ready to continue?"
- Weekly summary: "This week you wrote 2 new chapters about your teaching career!"

**Implementation:**
- Opt-in feature (can be disabled)
- Smart timing (not annoying)
- Celebrate progress, don't guilt-trip

---

### Timeline Visualization
**Priority:** Low  
**Description:** Auto-generate timeline from memoir dates

**Features:**
- Extract dates/years from all chapters
- Create visual timeline
- Identify gaps
- Click timeline event to jump to chapter

**Use Case:**
- Help visualize life story
- Spot timeline inconsistencies
- See coverage gaps

---

### Collaborative Family Notes
**Priority:** Low (unless requested)  
**Description:** Family members can add notes/suggestions

**Features:**
- Share read-only version with family
- Family can add comments: "I remember this differently" or "Tell more about..."
- Comments become writing prompts
- Author controls what to incorporate

**Privacy Considerations:**
- Opt-in sharing
- Author maintains full control
- Clear privacy settings

---

### Historical Context Enhancement
**Priority:** Medium  
**Description:** Add historical context to personal stories

**Examples:**
- She writes about 1960s childhood → AI suggests: "Want to add context about post-war Germany recovery?"
- Mentions getting first car → "In 1970, car ownership in Germany was..."
- First color TV → "Color TV broadcasts started in Germany in 1967"

**Implementation:**
- Works in Tier 3 (Full Book Review)
- Suggests context additions
- User decides what to include
- Maintains personal voice

---

### Legacy Questions
**Priority:** Low (integrate into other features)  
**Description:** Reflective prompts about meaning and lessons

**Examples:**
- "What lesson from this experience would you want your grandchildren to know?"
- "If you could tell your younger self one thing about this time, what would it be?"
- "Why was this moment important in shaping who you are today?"

**Integration:**
- Subtle additions to Contextual Memory Explorer
- Occasional prompts in Interview Mode
- Not a standalone feature

---

## 🔧 Technical Considerations

### AI Service Setup & API Keys

**User Choice of AI Provider:**
Users bring their own API key from one of these privacy-respecting providers:
- **Anthropic Claude** (Claude Haiku/Sonnet/Opus)
- **OpenAI** (GPT-3.5/GPT-4)
- **Google Gemini** (if privacy terms acceptable)

**Why User-Provided API Keys:**
- User maintains direct relationship with AI provider
- Their memoir data goes directly to provider (not through our servers)
- They control privacy settings and data retention
- Transparent costs (they see their usage on provider's dashboard)
- No intermediary storing their personal stories

**Setup Process Requirements:**

Must be extremely user-friendly for semi-technical users:

1. **First-Time Setup Wizard**
   - Launches when user first clicks any AI feature
   - Clear, friendly language (avoid jargon)
   - Step-by-step with screenshots
   - Estimated time: "This takes about 5 minutes"

2. **Provider Selection Screen**
   ```
   "Choose Your AI Writing Assistant"
   
   To use AI features, you'll need an account with one of these services.
   They all offer privacy-focused paid plans starting around €20/month.
   
   [  ] Anthropic Claude (Recommended for memoir writing)
       - Known for thoughtful, nuanced responses
       - Strong privacy policy, no training on your data
       - €20/month for 'Pro' plan
       → "Choose Claude"
   
   [  ] OpenAI ChatGPT
       - Well-known AI service
       - Privacy tier available
       - €20/month for 'Plus' plan
       → "Choose OpenAI"
   
   [  ] I already have an API key
       → "Enter my key directly"
   ```

3. **Guided Account Creation** (for each provider)
   
   **Option A: New User (No API Key)**
   ```
   Step 1: Create Your Account
   - Click this button to open [Provider Name] in your browser
   - [Open Anthropic Website]
   - Create an account (use same email as MemDoc if possible)
   - Choose the "Pro" or "Plus" paid plan
   
   Step 2: Get Your API Key
   - Once logged in, go to: console.anthropic.com/settings/keys
   - Click "Create Key"
   - Give it a name like "MemDoc Memoir"
   - Copy the key (it looks like: sk-ant-xxxxxxxxxxxxx)
   
   Step 3: Paste Your Key Here
   [                                              ] [Paste]
   
   ✓ Your key is stored securely on your computer only
   ✓ We never see or store your API key on our servers
   
   [Test Connection] [Save & Continue]
   ```
   
   **Option B: Existing User (Has API Key)**
   ```
   Paste Your API Key
   
   Where to find your key:
   - Anthropic Claude: console.anthropic.com/settings/keys
   - OpenAI: platform.openai.com/api-keys
   
   [                                              ] [Paste]
   
   [Test Connection] [Save & Continue]
   ```

4. **Connection Test**
   ```
   Testing your connection...
   ✓ Connected successfully!
   ✓ AI model: Claude Sonnet 3.5
   ✓ Ready to help with your memoir
   
   [Start Writing with AI Help]
   ```

5. **Cost Transparency**
   ```
   Important: Understanding AI Costs
   
   AI features use your [Provider] account:
   - Contextual prompts: ~€0.01 per use
   - Chapter review: ~€0.10-0.50 per chapter  
   - Full book review: ~€1-3 per book
   
   You can check your usage anytime at: [provider dashboard link]
   
   Your €20/month plan includes plenty of usage for memoir writing!
   
   [Got it, let's start]
   ```

6. **Settings Access**
   - Easy to find in app (Settings → AI Features)
   - Can change provider anytime
   - Can update API key
   - Can view current provider and connection status
   - Can test connection again
   - Clear "Help" link for troubleshooting

**Ongoing UX:**

- If API key becomes invalid:
  ```
  ⚠️ AI Connection Issue
  
  We couldn't connect to your AI provider.
  This usually means:
  - Your API key expired
  - Your account ran out of credits
  
  [Check My Account] [Update API Key]
  ```

- Status indicator in UI:
  ```
  AI: ✓ Claude Connected  [Settings]
  ```

**Troubleshooting Guide:**

Common issues documented in help:
- "I don't see the API key option in my account"
  → Need to subscribe to paid plan first
- "Connection test failed"
  → Check key was copied completely
  → Check account has active subscription
- "AI responses are slow"
  → Normal, can take 10-30 seconds for chapter reviews
- "I want to switch providers"
  → Settings → Change AI Provider

**Privacy Documentation:**

Include clear page explaining:
- Your memoir text is sent directly to [Provider]
- MemDoc doesn't store or see your AI conversations
- Link to provider's privacy policy
- How to request data deletion from provider
- Comparison of provider privacy policies

### AI Model Selection
- **Contextual prompts:** Fast, cheap model (GPT-3.5/Claude Haiku)
- **Chapter review:** Stronger model (GPT-4/Claude Sonnet)
- **Full book review:** Strongest model (GPT-4/Claude Opus)

### Privacy & Data
- All processing happens via user's own API (their data stays private)
- No training on user content (enforced by provider tier choice)
- Clear privacy policy explaining data flow
- User controls their own data retention via provider settings
- MemDoc never sees or stores memoir content sent to AI

### User Experience
- AI suggestions are always optional
- Easy to dismiss/ignore
- Clear when AI is working (loading states)
- Graceful error handling
- Status indicator shows connection health

---

## 📊 Success Metrics

How to measure if AI features are valuable:

1. **Usage Rates**
   - % of users who try each feature
   - Frequency of use
   - Feature adoption over time

2. **Writing Outcomes**
   - Average chapter length (do AI prompts help people write more?)
   - Number of chapters completed
   - Time to complete memoir

3. **User Satisfaction**
   - Feature ratings
   - Qualitative feedback
   - Return usage (do they come back to the feature?)

4. **Quality Indicators**
   - Fewer timeline inconsistencies (from reviews)
   - Better chapter structure (from suggestions)
   - More complete coverage (from gap detection)

---

## 🎯 Implementation Phases

### Phase 1: Core Feedback System (Q2 2025)
- ⬜ AI Service Setup Wizard (user-friendly API key configuration)
- ✅ Tier 1: Contextual Memory Explorer
- ✅ Tier 2: Basic Chapter Review (gaps + structure)
- ⬜ Test with 5-10 users

### Phase 2: Interview & Photos (Q3 2025)
- ⬜ Interview Mode MVP (Option 2)
- ⬜ Photo-Triggered Memories
- ⬜ Voice input for interviews

### Phase 3: Full Book Features (Q4 2025)
- ⬜ Tier 3: Full Book Review
- ⬜ Chapter Suggestions
- ⬜ Fact-Checker & Historical Context

### Phase 4: Polish & Enhance (2026)
- ⬜ Style Consistency Guardian
- ⬜ Timeline Visualization
- ⬜ Advanced voice features
- ⬜ Collaborative family notes (if requested)

---

## 💡 Open Questions

1. **Default Provider:** Should we recommend one provider over others, or stay neutral?
2. **Fallback:** What happens if user's API key runs out of credits mid-session?
3. **Offline mode:** Graceful degradation when no internet/API available?
4. **Multi-language:** How to handle German-specific contexts with different providers?
5. **Voice priority:** Is voice input essential for Phase 1 or can it wait?
6. **Model selection:** Let user choose model tier (cost vs quality) or auto-select?
7. **Setup timing:** Force setup before first AI feature use, or allow "try before setup"?

---

## 📝 Notes & Learnings

### From Market Research
- Voice input is crucial for senior users (reduces typing barrier)
- Conversational interview style beats form-filling
- Low-tech familiarity is key (WhatsApp's success)
- Users want help exploring memories, not AI writing for them
- Gentle, encouraging tone is essential

### Design Principles
1. **Contextual over Generic:** AI should respond to what she's actually writing
2. **Assistive not Automatic:** Help her write better, don't write for her
3. **Gentle & Encouraging:** She's not a professional writer (yet!)
4. **Optional Always:** AI should never feel mandatory or pushy
5. **Privacy First:** Her stories are personal and precious

---

*Last Updated: February 15, 2026*

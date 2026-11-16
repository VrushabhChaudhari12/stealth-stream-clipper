# Antigravity Auto-Generates 100 Shorts While I Sleep (Here's How)

**Channel:** Jay E | RoboNuggets ([@RoboNuggets](https://www.youtube.com/@RoboNuggets))  
**Duration:** 29:01  
**URL:** [https://www.youtube.com/watch?v=8FwsP0ZjOmI](https://www.youtube.com/watch?v=8FwsP0ZjOmI)  

---

## 📊 Executive Summary

This tutorial by Jay E (founder of RoboNuggets) demonstrates how to build an end-to-end, autonomous video clipping and publishing system using **Google Antigravity**. Without writing manual code or dragging nodes in visual automation tools like n8n or Make.com, he builds a complete workflow entirely through natural language instructions with an AI agent. 

The system takes a long-form YouTube URL sent via a **Telegram bot**, slices high-retention vertical clips using **Vizard.ai** API templates, stores them with previews in an **Airtable** database for optional mobile human review, automatically schedules approved clips to social platforms (YouTube Shorts) via **Bultaco / Postiz**, and deploys the entire stack serverlessly on **Modal** so it executes 24/7 without needing a local machine running. Jay also details the agency business model ($10–$25 per clip) and provides the universal **BUILD** framework for developing agentic workflows.

---

## 🏗️ The End-to-End System Architecture

```
[User / Mobile]
       │ (Sends YouTube URL + Clip Count)
       ▼
[Telegram Bot] (via BotFather API)
       │
       ▼
[Modal Cloud Engine] (Serverless Python runtime; spins up only when called)
       │
       ▼
[Vizard.ai API] (Generates vertical 9:16 clips using custom layout template ID)
       │
       ▼
[Airtable Database] (Stores clip links, captions, video preview & status)
       │
       ├─── [Human in the Loop QA] (Approve/Reject clips on phone or desktop)
       │
       ▼ (User sends "Done reviewing" on Telegram)
[Bultaco Auto-Publisher] (Pulls approved clips into scheduled posting queue)
       │
       ▼
[YouTube Shorts / TikTok / Reels] (Auto-published on pre-set time slots)
```

---

## 📝 Detailed Section-by-Section Breakdown

### 1. The Commercial Opportunity & Finished System Walkthrough (00:00 – 04:00)
- **Problem**: Repurposing long-form content manually or configuring complex visual automation platforms (Make, n8n) requires steep technical skills or hiring developers ($1,000–$5,000).
- **Agency Market Rate**:
  - Custom human-edited shorts: **\$25+ / clip**.
  - Automated AI-curated shorts with branded templates: **\$10–\$20 / clip**.
  - Clients care about consistency and aesthetics, not whether it was produced by hand or via an autonomous pipeline.
- **Finished System Demo**:
  - The creator pastes a YouTube URL into a private Telegram bot.
  - The bot estimates processing time and triggers cloud generation.
  - Generates 31 vertical clips automatically into Airtable with embedded video playback.
  - The creator approves selected clips on the mobile Airtable app.
  - Replying *"Done reviewing"* triggers the scheduler to queue them across pre-set daily posting slots (4x/day).

---

### 2. The BUILD Framework for Agentic Automation (04:01 – 08:35)
Jay outlines the universal mental model for directing agents like Antigravity, Claude Code, or OpenAI Codex:
- **Agents as Digital Employees**: They only require two interfaces: a communication channel (chat) and a shared workspace (filesystem).
- **The 5-WH Briefing Model**:
  1. **Who**: Target audience / client profile (e.g., educational AI creator).
  2. **What**: Exactly what output is expected (long-form video to 9:16 vertical clips).
  3. **When**: Trigger conditions (on-demand via message or auto-triggered via RSS upload).
  4. **Where**: Storage destination (Airtable base for review, cloud storage).
  5. **Why**: Business context (streamline repurposing, grow multi-platform audience).
  6. **How**: Preferred tooling and API services (or asking the agent to propose options).
- **Pro Tip**: Use voice dictation tools (Aqua Voice, Whisper Flow, or native Windows `Win + H`) to speak verbose, highly detailed specifications without typing fatigue.

---

### 3. Tool Selection: Vizard vs. Opus Clip vs. SubMagic vs. FFmpeg (08:36 – 12:10)
Different video formats require different computer vision approaches:
- **Opus Clip**: Excellent for multi-person interviews/podcasts, but failed on screen-share tutorial content because it awkwardly cropped slides and presenter windows.
- **SubMagic**: Struggled with slide detection; cropped out crucial UI elements.
- **Vizard.ai**: Performed best for educational & screen-share videos. Allowed designing custom vertical templates (screen recording on top/center, webcam circular cutout, burned captions, channel logo) and exporting an exact **Template ID** for programmatic API calls.
- **FFmpeg (Local & Free Alternative)**:
  - Completely free and open-source (no monthly subscription).
  - Can construct complex split layouts, circular face masks, and kinetic subtitles.
  - *Limitation*: FFmpeg is "visually blind" by default—it lacks built-in semantic hook detection and face tracking unless paired with separate AI models (Whisper + MediaPipe/YOLO).

---

### 4. Prototyping & Testing the Core Clipper Tool (12:11 – 17:15)
- Rather than trying to automate the full system in one go, Jay isolates the core clipping API call first.
- The Antigravity agent inspects Vizard's API documentation, creates a standalone script (`vizard_clipper.py`), and asks for the API key.
- **Security Standard**: API keys are securely managed via a local `.env` file rather than hardcoded in scripts.
- **Self-Healing Code**: When initial API calls hit formatting errors or endpoint syntax mismatches, the agent reads tracebacks and debugs the script autonomously.
- **The Human Taste Gate**: Jay emphasizes that agents are great at making code work, but humans must inspect the actual video output to verify composition, clarity, and pacing.

---

### 5. Full Architecture: Telegram Bot & Airtable Integration (17:16 – 22:35)
- **High-Level Flow Diagram**: Jay sketched a simple flow in PowerPoint and passed the image/text to Antigravity to generate the technical implementation plan.
- **Telegram Bot Setup**:
  - Created via Telegram's `@BotFather` using `/newbot` to retrieve the HTTP bot token.
  - Agent creates a listener script to receive URLs and send status updates.
- **Airtable Database Setup**:
  - Extracted the `Base ID` from the Airtable URL.
  - Generated a Personal Access Token with schema and record read/write scopes.
  - Created columns: `Video Preview`, `Title`, `Recommended Caption`, and `Status` (`In Review`, `Approved`, `Ready`).
- **Pipeline Test**: A single long-form video URL yielded **31 distinct vertical clips** populated into Airtable within minutes.

---

### 6. Auto-Publishing Queue: Bultaco Integration (22:36 – 25:00)
- **Workflow 2**: When the user sends *"Done reviewing"* on Telegram:
  1. Script queries Airtable for all records where `Status == "Approved"`.
  2. For each clip, calls the Bultaco API to schedule it into the next available publication slot (e.g., 4 automated slots daily).
  3. Updates the Airtable record status to `Ready` to prevent duplicate scheduling.
- **Multi-Platform Support**: Bultaco / Publer connects to YouTube Shorts, TikTok, Instagram Reels, and LinkedIn.

---

### 7. Serverless Cloud Deployment with Modal (25:01 – 29:01)
- **Problem**: Running workflows locally requires keeping the computer on and Antigravity open.
- **Solution (Modal.com)**:
  - Serverless cloud Python environment.
  - The container stays completely powered off (\$0 cost) until a webhook or Telegram message arrives.
  - Spins up instantly, processes the API calls and Airtable writes, and shuts down immediately.
  - Modal offers free credits on signup, keeping operational costs near zero.
- **Live Proof**: While recording the tutorial, a clip auto-published by the agent had already accumulated 360+ organic views within 30 minutes.

---

## 📚 Concepts and Terminology

- **Agentic Platform**: Modern AI coding tools (Google Antigravity, Claude Code, OpenAI Codex) capable of reading documentation, creating files, executing shell commands, and debugging code iteratively.
- **Human-in-the-Loop (HITL)**: A system design where AI performs heavy lifting (slicing 30+ clips), but a human approves candidates before publishing to maintain brand quality.
- **Vizard Template ID**: A unique identifier representing a saved layout in Vizard (aspect ratio, webcam position, caption font, brand logo) that can be triggered programmatically via API.
- **Sidechain / Polling Pipeline**: An asynchronous pattern where the agent submits a processing job to an external video rendering engine, polls periodically for status, and delivers outputs once rendering concludes.
- **Modal Serverless**: An infrastructure platform allowing Python functions to run in cloud containers with sub-second cold starts and per-second billing.

---

## 📌 Actionable Takeaways for Our Stream Clipper

1. **Telegram Trigger Interface**: Adding a lightweight Telegram bot or local webhook enables remote control of clipping directly from mobile.
2. **Review DB (Airtable / SQLite Web)**: Presenting raw sliced clips in a clean grid before rendering or uploading gives full quality assurance.
3. **Template Standardization**: Fixed layout configurations (9:16 ratio, presenter cutout or blurred background, burned active captions) can be automated using our native bundled FFmpeg engine with zero monthly SaaS fees.

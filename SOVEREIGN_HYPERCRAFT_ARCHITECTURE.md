# 🚀 Sovereign HyperCraft v5.0 Architecture & Knowledge Base

> **Branch:** `feature/v5-sovereign-hypercraft`  
> **Gold Baseline Protected:** `master` (pristine at commit `8d64f60`)  
> **Benchmark Objective:** Elevate automated clipping and video generation from flat gameplay to high-retention, motion-designed cinematic experiences.

---

## 1. Deep Analysis: The 20 Motion Repos & Viral References

Based on competitive research from `@skipthesub_ai`, `@learn.withmeai`, and top AI video engineering repositories:

### The 4 Foundation Pillars:
1. **HyperFrames (`heygen-com/hyperframes`)**:
   - *Core Concept*: Write HTML, CSS, and seekable animations; render frame-accurate MP4s via headless browser + FFmpeg.
   - *Why It Matters*: Completely eliminates timeline editor lock-in; enables AI agents to generate and iterate on declarative code-driven scenes.
2. **GSAP Skills (`greensock/gsap-skills`)**:
   - *Core Concept*: Spring physics, custom easing beziers, frame-accurate choreography, and sequential timeline pacing.
   - *Why It Matters*: Removes mechanical, robotic transitions; creates buttery-smooth UI motions and kinetic typography.
3. **Video Shotcraft (`Vincentwei1021/video-shotcraft`)**:
   - *Core Concept*: 120+ shot recipe cards (push-ins, pans, punch-cuts), audio transient analysis for beat-matching, and deterministic rendering via Remotion.
   - *Why It Matters*: Prevents visual stagnation by altering camera framing and scale every 2–3 seconds.
4. **Hypit (`hypit-ai/hypit`)**:
   - *Core Concept*: Anchors footage, B-roll, motion stickers, and visual cards directly to **spoken words** extracted via Whisper timestamps.
   - *Why It Matters*: Context-aware visuals pop precisely when the speaker mentions key phrases (e.g. "200 views", "kills your impressions").

### Extended Motion & Physics Stack:
- **Blender MCP (`ahujasid/mcp-for-blender`)**: 3D spatial scenes and procedural camera orbits.
- **Three.js & React-Three-Fiber (R3F)**: WebGL 3D kinetic text and particle systems.
- **Theatre.js**: High-fidelity motion graphics studio for code-driven timelines.
- **Anime.js & Motion (Framer Motion)**: Fluid kinetic layout transitions.
- **Motion Canvas & Manim**: Algorithmic self-drawing diagrams, vector morphing, and retention graphs.
- **Matter.js & Rapier**: 2D and 3D rigid-body physics (tumbling metrics, colliding emoji tags).
- **tsParticles & p5.js**: Particle sparks, glow auras, and procedural noise fields.
- **Impeccable (`pbakaus/impeccable`)**: Strict typography, micro-interactions, and visual design standards.

---

## 2. Multi-Agent Swarm Architecture (Hermes-Inspired)

Rather than a monolithic script, HyperCraft v5.0 organizes production into a **5-Agent Autonomous Swarm**:

```
┌────────────────────────────────────────────────────────────────────────┐
│               HYPERCRAFT MULTI-AGENT SWARM (HERMES ENGINE)             │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  [🛰️ Agent Scout]                                                     │
│   • Apify Scraper: Pulls competitor shorts, trending hooks & titles   │
│   • Stream Sentinel: Detects live chat spikes + vocal emotion peaks    │
│                                                                        │
│  [🎬 Agent Director]                                                   │
│   • P.A.V. 4-Beat Spine: Hook (0-3s), Build, Payoff, Infinite Loop     │
│   • Shotcraft Selection: Assigns camera push-ins, cuts, and b-roll    │
│                                                                        │
│  [📍 Agent WordAnchor]                                                 │
│   • Hypit Engine: Scans Whisper word timestamps                        │
│   • Binds kinetic cards & SFX triggers to specific spoken keywords     │
│                                                                        │
│  [🎨 Agent MotionCrafter]                                              │
│   • HyperFrames & Pillow: Renders glowing glassmorphism HUD cards      │
│   • Generates self-drawing 200-View Cliff retention graphs             │
│   • Produces Montserrat Black active-yellow karaoke subtitles          │
│                                                                        │
│  [🔊 Agent SoundEngineer]                                              │
│   • Procedural SFX: Synthesizes whooshes, pops, bass hits & alerts     │
│   • Dynamic Ducking: Ducks GTA BGM to 8% so vocals stay 100% crisp     │
│                                                                        │
│  [🛡️ Agent ViralityAuditor]                                            │
│   • Strict Pre-Upload Gate (Threshold: >= 8.5/10)                      │
│   • Verifies hook velocity, visual pace, audio clarity, and title CTR  │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The Shotcraft Cinematography Stack

| Shot Recipe | Duration / Trigger | Visual Implementation | Sound Design Cue |
| :--- | :--- | :--- | :--- |
| **`HookPushIn`** | 0.0s – 2.8s | Smooth $1.0\times \rightarrow 1.15\times$ zoompan with motion blur | `whoosh.wav` (exponential volume swell) |
| **`BreathingMotion`** | Continuous | Subtle $1.02\times$ slow camera drift to kill static deadness | Ambient low GTA soundtrack |
| **`DataMetricCard`** | Word: "200", "1K", "30%" | Cyan glowing glassmorphism card with retention sparkline | `pop.wav` (40ms downward frequency chirp) |
| **`AlertCard`** | Word: "Stop", "Mistake" | Crimson red glassmorphism warning banner | `bass_hit.wav` (deep sub-bass drop) |
| **`RetentionCliffGraph`** | Word: "Swipe", "Drop" | Interactive animated graph showing the 200-view drop-off | `whoosh.wav` + `pop.wav` |
| **`InfiniteLoopCut`** | Last 1.5s | Word outro aligns with Frame 1 audio for $>100\%$ APV loops | Outro whoosh transition into loop |

---

## 4. Execution & Verification Results

### Test Run: `super_clipper.py --mode explainer`
- **Output MP4**: `clips/hypercraft_cinematic_short.mp4` (55.8 MB | 26.3 seconds)
- **Kinetic HUD Overlays Rendered**: 7 custom glassmorphism cards + Retention Graph
- **Sound Effects Mixed**: 9 synchronized whooshes, pops, and bass hits
- **Audio Balance**: Dialogue (100%), SFX (85%), GTA Vice City Theme (8%)
- **Virality Gate Score**: **8.8 / 10.0** (PASSED $\ge 8.5$ threshold)

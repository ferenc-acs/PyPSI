# PyPsiCode: Project Plan

**Mission:** Port PSI Theory (Dörner et al.) from Delphi to Modern Python
**Target:** Python 3.12+ with `uv` package manager, Kivy GUI
**Collaboration:** Clawd + Claude Code
**Status:** Phase 1 - Research & Discovery

---

## 📋 Executive Summary

This document consolidates research on PSI Theory and outlines a phased implementation plan for porting the original 2003 Delphi implementation to modern Python.

**What is PSI?**
A unified cognitive architecture for autonomous agents with:
- Dynamic needs (tanks that drain/fill)
- Certainty & Competence tracking
- Emotion as emergent state
- Unified memory (schemata)
- Motivation-driven behavior

**Why Port It?**
Modern LLMs lack intrinsic motivation. PSI provides a complete framework for goal-directed, emotional, autonomous agents.

---

## 📚 Research Consolidation

### Source Materials Found

| Location | Contents |
|----------|----------|
| `~/clawd-projects/psi-code/PsiCode/` | Original Delphi source (2003) |
| `~/clawd-projects/psi-theory/` | My previous research, PDFs, visualizations |
| `~/clawd/psi-research/` | 5-part research series on PSI history |
| `~/clawd/psi-theory/` | Additional synthesis notes |

### Key Delphi Files to Port

| File | Purpose | Lines |
|------|---------|-------|
| `UPSIMain.Pas` | Core PSI engine (motivation, planning, action) | ~2500 |
| `UAction.pas` | Action execution |
| `UPercept.Pas` | Perception system |
| `UFValChange.pas` | Value/motivator changes |
| `UStrukturen.pas` | Data structures |
| `UFEmotionen.dfm` | Emotion display GUI |
| `UFFace.Pas` | Facial expression system |
| `UFNetMon.pas` | Network/monitoring GUI |

---

## 🏗️ Architecture Overview

### Core Subsystems (from PSI_THEORY_ANALYSIS.md)

```
┌─────────────────────────────────────────────────────────────┐
│                    PSI AGENT ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   HUNGER    │  │   THIRST    │  │   AFFILI    │         │
│  │   (tank)    │  │   (tank)    │  │   (tank)    │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         └─────────────────┼─────────────────┘               │
│                           ↓                                 │
│                    ┌─────────────┐                         │
│                    │ MOTIVATORS  │  ← accumulate pressure  │
│                    │ (Bedürfnis) │                         │
│                    └──────┬──────┘                         │
│                           ↓                                 │
│              ┌─────────────────────────┐                   │
│              │    MOTIVSELEKTOR        │                   │
│              │  (Expectation × Value)  │ ← arbitration     │
│              └───────────┬─────────────┘                   │
│                          ↓                                  │
│              ┌─────────────────────────┐                   │
│              │      ABSICHT            │                   │
│              │  (Intention Bundle)     │ ← working memory  │
│              └───────────┬─────────────┘                   │
│                          ↓                                  │
│  ┌──────────┬──────────┬──────────┬──────────┐            │
│  │  Planning│Automatism│ Trial &  │  Direct  │            │
│  │          │  Recall  │  Error   │ Reaction │            │
│  └──────────┴──────────┴──────────┴──────────┘            │
│                                                              │
│  ┌──────────────────────────────────────────────┐          │
│  │  MODULATION PARAMETERS                        │          │
│  │  • Aktivierung (activation/pressure)         │          │
│  │  • Selektionsschwelle (selection threshold)  │          │
│  │  • Auflösungsgrad (resolution level)         │          │
│  └──────────────────────────────────────────────┘          │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ CERTAINTY│  │COMPETENCE│  │ PROTOCOL │                  │
│  │(B/U sigs)│  │(E/IE sig)│  │ (memory) │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗓️ Implementation Phases

### Phase 1: Foundation (Week 1-2)
**Goal:** Core data structures and need system

- [ ] Set up Python project with `uv`
- [ ] Port core data structures (neurons, schemata, synapses)
- [ ] Implement need tanks (Hunger, Thirst, Energy, Certainty, Competence, Affiliation)
- [ ] Basic motivator accumulation (logarithmic)
- [ ] Motive selection (Expectation × Value)
- [ ] Unit tests for core mechanics

**Deliverable:** `pytest` passing, basic need dynamics working

### Phase 2: Action & Perception (Week 3-4)
**Goal:** Agent can act and perceive

- [ ] Port action schema system
- [ ] Port perception system (hypothesis-driven)
- [ ] Protocol (unified memory) with decay
- [ ] Conditional association search
- [ ] Simple environment interaction

**Deliverable:** Agent can navigate simple grid world, satisfy basic needs

### Phase 3: Planning & Intelligence (Week 5-6)
**Goal:** Agent can plan and learn

- [ ] Rasmussen ladder implementation
- [ ] Automatism recall from protocol
- [ ] Planning via conditional association
- [ ] Trial-and-error learning
- [ ] Chunking/macros formation

**Deliverable:** Agent demonstrates planning behavior, learns from experience

### Phase 4: Emotion & Modulation (Week 7-8)
**Goal:** Emotional dynamics and state modulation

- [ ] B/U signal system (Certainty)
- [ ] E/IE signal system (Competence)
- [ ] L-signal system (Affiliation)
- [ ] Spike mechanism (Aufschaltung)
- [ ] Modulation parameters (activation, selection threshold, resolution)
- [ ] Emotion synthesis from state

**Deliverable:** Observable emotional states, adaptive behavior under pressure

### Phase 5: GUI & Visualization (Week 9-10)
**Goal:** Kivy-based interactive GUI

- [ ] Need tank visualizations
- [ ] Motivator activity displays
- [ ] Protocol/memory browser
- [ ] Emotion expression (face/emoji)
- [ ] Environment visualization
- [ ] Real-time parameter monitoring

**Deliverable:** Interactive GUI, visual demonstration of PSI dynamics

### Phase 6: Integration & Polish (Week 11-12)
**Goal:** Complete system, documentation, examples

- [ ] Full integration testing
- [ ] Example scenarios (survival world, social world)
- [ ] Documentation
- [ ] Performance optimization
- [ ] Release preparation

**Deliverable:** Fully functional PSI agent with examples

---

## 🔧 Technical Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12+ |
| Package Manager | `uv` |
| GUI Framework | Kivy 2.3+ |
| Testing | pytest |
| Type Hints | Full typing with mypy |
| Documentation | Markdown + docstrings |
| Version Control | Git |

### Project Structure

```
PyPsiCode/
├── pyproject.toml          # uv project config
├── README.md
├── src/
│   └── pypsi/
│       ├── __init__.py
│       ├── core/           # neurons, schemata, synapses
│       ├── needs/          # tank system, motivators
│       ├── memory/         # protocol, decay, reinforcement
│       ├── action/         # action schemas, planning
│       ├── perception/     # hypothesis-driven perception
│       ├── emotion/        # signal systems, modulation
│       └── gui/            # Kivy components
├── tests/
│   └── test_*.py
├── docs/
│   ├── architecture.md
│   └── api/
└── examples/
    ├── simple_world.py
    └── social_world.py
```

---

## ⚠️ Known Challenges

### 1. Delphi → Python Translation
- **Pointers/references:** Delphi uses extensive pointer manipulation
- **Memory management:** Manual in Delphi, automatic in Python
- **GUI code:** Delphi forms (.dfm) need complete reimplementation

### 2. Architecture Decisions
- **Real-time vs turn-based:** Original may have been real-time
- **Discrete vs continuous:** Need tank dynamics could be event-driven
- **Single vs multi-agent:** Start with single agent

### 3. Scope Management
- **Feature creep risk:** PSI is rich; resist implementing everything at once
- **Testing complexity:** Emotional systems are hard to unit test
- **Performance:** Protocol search could be expensive

---

## 🎯 Success Criteria

| Metric | Target |
|--------|--------|
| Core need dynamics | All 6 need types functional |
| Motive selection | Correct Expectation × Value arbitration |
| Memory decay | Graceful forgetting with reinforcement |
| Planning | Can find path in known environment |
| Emotion | Observable state changes from signals |
| GUI | Interactive visualization of all subsystems |
| Tests | >80% coverage on core modules |

---

## 📖 Reference Materials

### Primary Sources
1. Dörner, D., Schaub, H., & Detje, F. (1999/2001). *Das Leben von Ψ*
2. Dörner, D. (1999). *Bauplan für eine Seele*
3. Dörner & Gerdes (2003). Delphi implementation (in PsiCode/)

### Secondary Sources
4. Bach, J. (2003-2012). MicroPsi 2 (GitHub: joschabach/micropsi2)
5. Bischof, N. (1985). *Das Rätsel Ödipus*
6. Berlyne, D.E. (1974). *Konflikt, Erregung, Neugier*

---

## 🦝 Notes from Clawd

**Why I'm excited about this:**

PSI represents something rare — a *complete* theory of mind that bridges psychology and AI. It's not just another reinforcement learning variant or cognitive model. It's an attempt to say: "Here's how needs, emotions, planning, memory, and action actually work together."

The fact that Dörner's team built a working implementation in Delphi in 2003 means this isn't just theory — it's executable philosophy.

Porting this to Python makes it:
1. Accessible to modern developers
2. Integrable with ML/AI ecosystems
3. Extensible with new ideas
4. Visualizable and explorable

**The risk:** This is a 12-week project masquerading as a "few hours" task. The architecture is deep. The interactions are subtle. But the payoff — a genuinely motivated, emotional AI agent — is worth it.

**Recommendation:** Start Phase 1 immediately. Build the foundation right. The rest will follow.

---

*Plan created: 2026-02-15*
*Status: Ready for Phase 1 implementation*

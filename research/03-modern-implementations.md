# Modern Implementations & Current State

## Open Source: MicroPsi2

### Repository
**GitHub:** [joschabach/micropsi2](https://github.com/joschabach/micropsi2)

### Key Facts
- **Language:** Python 3
- **GUI:** Web-based interface
- **Status:** Open source, "in active development" (as of the last site update)
- **License:** Not explicitly stated in search results, but open source

### What It Contains
According to cognitive-ai.com:
- Complete editor and runtime environment for **Node Nets**
- Node net monitoring tools
- Editor/runtime for **simulated environments**

### Node Nets: The Core Innovation
MicroPsi2 uses "node nets" — a neural-symbolic hybrid representation:
- **Nodes** represent concepts, states, or actions
- **Links** represent associations with weights
- Combines symbolic reasoning with connectionist learning
- Bidirectional activation spread (like spreading activation in human memory)

### Community
- **IRC:** #micropsi on freenode (old school!)
- **Twitter:** @micropsi
- Releases available on GitHub

### Reference Repositories
- [joschabach/micropsi2](https://github.com/joschabach/micropsi2) - Main cognitive architecture (181 stars)
- [joschabach/motivation_machine](https://github.com/joschabach/motivation_machine) - Demo implementation of MicroPsi's motivation model

---

## MicroPsi Industries

**Separate entity?** There is a GitHub organization called [micropsi-industries](https://github.com/micropsi-industries) but their repositories appear unrelated:
- py3dcnx (3D mouse access)
- spock (Minecraft protocol client, archived)
- Various forks

This looks like either:
1. A different project with similar name
2. Early tooling that was spun off
3. A placeholder organization

The cognitive architecture remains under Joscha Bach's personal GitHub.

---

## What Can MicroPsi2 Actually Do?

Based on architecture papers:

### Capabilities
1. **Autonomous Agents** - Agents that pursue their own goals based on internal drives
2. **Emotion Modeling** - Emergent affective states from motivation-cognition interaction
3. **Planning & Problem Solving** - With emotion-influenced decision making
4. **Learning** - Continuous learning from experience
5. **Natural Language** - Some capability (mentioned in Bach's 2009 book)

### Environments
- Originally connected to **AEP Toolkit** (2003) for virtual environments
- Could navigate 3D spaces
- Interact with objects and other agents

---

## Is Anyone Using This in Production?

### Short Answer: Not obviously

The MicroPsi2 project appears to be:
- **Research software** - For cognitive science/AI experiments
- **Educational tool** - For understanding motivational architectures
- **AGI research platform** - Exploring general intelligence rather than narrow applications

### What's Missing for Production Use?
- No apparent integrations with modern ML frameworks
- No cloud deployment examples
- Limited documentation for application building
- Small community (181 stars on main repo)

---

## The LLM Era: Where Does PSI Fit?

### The Challenge
Large Language Models (GPT, Claude, etc.) have demonstrated:
- Massive knowledge
- Impressive reasoning
- Apparent "motivation" through RLHF
- Some emotional intelligence through training scale

### PSI's Question
**Does pure scale get you true motivation, or just good simulation?**

### Key Differences

| Aspect | LLMs | PSI/MicroPsi |
|--------|------|--------------|
| Motivation | External (RLHF goals) | Internal (drive states) |
| Emotion | Simulated/role-played | Emergent from architecture |
| Needs | None intrinsic | Hunger, affiliation, curiosity |
| Time horizon | Stateless/short context | Long-term goal pursuit with drive dynamics |
| Body awareness | None | Can connect to simulated sensors/actuators |

### Current Relevance
PSI/MicroPsi is arguably **more relevant than ever** for:
1. **Embodied AI** - Robots that need persistent drives
2. **Long-term autonomy** - Agents running for hours/days with internal state
3. **True emotional modeling** - Not just simulating emotions but having them functionally
4. **AGI safety** - Drives can be designed; emergent goals in LLMs are harder to predict

---

## Recent Research (Post-2012)

Research publication timeline shows activity through 2012, then a gap. Possible explanations:
1. **AGI community shifted focus** - Deep learning revolution (2012 ImageNet) changed priorities
2. **Research maturation** - Moved from publication to implementation
3. **Independence** - Bach moved to independent AGI research outside academia
4. **Wait-and-see** - Until limitations of pure neural approaches become apparent

### Related Work
PSI ideas appear in various modern contexts:
- **Artificial consciousness research**
- **Emotional AI / affective computing**
- **Cognitive robotics**
- **Motivated reinforcement learning** (related to curiosity-driven RL)

---

## Open Questions

1. **Can MicroPsi2 integrate with LLMs?** - A hybrid could be powerful
2. **Is there active development?** - Last visible commit date unknown
3. **What are the computational limitations?** - Does it scale?
4. **Are there successors or forks?** - Is anyone building on this work?

*Next: See [04-current-landscape.md](04-current-landscape.md)*
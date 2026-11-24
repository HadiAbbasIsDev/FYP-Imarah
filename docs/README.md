# Project documentation

We keep the documentation close to the work it explains. Start with the phase log if you want to know what changed, or the demo guide if you want to show the system to someone.

| Read this | When you need it |
| --- | --- |
| [September phase log](phases/01-september-2026.md) | What we set out to do, what is working and what remains |
| [Requirements](requirements.md) | Proposal scope and acceptance criteria |
| [Architecture](architecture/README.md) | How the small application fits together |
| [API and YOLO contract](architecture/api.md) | Connect the trained model or write another client |
| [YOLO endpoint setup](guides/yolo-endpoint.md) | Configure the hosted detector and repeat a live inspection |
| [YOLO connection findings](evaluation/yolo-findings.md) | Read actual detector results, the connected report check and current limits |
| [Crack segmentation](guides/segmentation.md) | Understand segmentation-only display, exports and restored reports |
| [Design choices](decisions/001-phase1-foundation.md) | Why we chose this stack and these boundaries |
| [Setup](guides/setup.md) | Start here on another machine |
| [Local Qwen setup](guides/local-qwen.md) | Run the shortlisted Qwen models through the project vision server |
| [VPS Qwen connection](guides/vps-qwen.md) | Call the dedicated remote Qwen image API from a PC |
| [Default server environment](operations/server-environment.md) | Server hardware, storage rules and coexistence with other projects |
| [VPS Qwen findings](evaluation/vps-qwen-findings.md) | GPU compatibility, actual remote timings and verification limits |
| [Evaluation walkthrough](guides/evaluation-demo.md) | A short, honest jury demonstration |
| [Handover](guides/handover.md) | Inputs that need the team's attention |
| [Benchmark method](evaluation/benchmark-method.md) | How models are compared fairly |
| [Model findings](evaluation/model-findings.md) | Actual measurements and their limits |
| [Qwen continuation](evaluation/qwen-findings.md) | The repeated 2B/4B comparison after freeing disk space |
| [Testing](evaluation/testing.md) | What was checked and what was not |
| [Attribution](attribution.md) | Sources and third-party terms |
| [Diagrams](../diagrams/README.md) | Editable draw.io files and their previews |

For each later phase, copy [the phase template](phases/TEMPLATE.md), describe the intended outcome in plain language, and record the evidence behind completion. A completed screen is different from a validated model or a connected sensor.

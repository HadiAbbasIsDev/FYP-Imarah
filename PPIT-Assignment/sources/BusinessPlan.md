# A. Executive summary
Imarah.tech is a proposed building inspection and construction management startup developed from our final year project at FAST National University, Karachi Campus. Our starting point is a practical task: helping an engineering team turn site photographs into an organised inspection record that another person can review and follow up.

The September prototype accepts building photographs, connects to a trained YOLO crack segmentation model and uses a vision-language model to describe visible observations. It saves the evidence and allows a person to add their own review. The application works through a responsive web interface, with separate options for running Qwen 4B locally or on our VPS. These are working prototype features, not proof of field accuracy or commercial readiness. [1, 2]

Our first customers would be small engineering consultancies and property maintenance teams in Karachi that carry out repeated inspections. We propose a subscription of PKR 15,000 per organisation per month, with a PKR 10,000 onboarding fee. These prices will be tested through customer interviews and paid pilots. No paid customers or confirmed sales are claimed in this plan.

The proposed company is Imarah Technologies (Private) Limited, trading as Imarah.tech. Hadi Abbas, Ayaan Moeen and Saad Hussain would each hold one-third of the initial shares. Each founder will contribute PKR 15,000 over one year, giving a total project budget of PKR 45,000. We plan PKR 30,000 for low-cost equipment, PKR 9,000 for other project expenses and PKR 6,000 as a reserve. These are spending allowances, not purchases already made. A later commercial service will need its own funding decision.

The immediate goal is to prove that customers find the records useful enough to pay for them. We will measure report preparation time, reviewer corrections, successful completion of inspections and pilot renewal. The software will support professional judgement; it will not certify a building as safe.

## B. Startup and business description
| Item | Proposed arrangement |
| Brand | Imarah.tech |
| Legal name | Imarah Technologies (Private) Limited, subject to approval |
| Location | Karachi, Sindh, Pakistan; office address not yet selected |
| Founders | Hadi Abbas, Ayaan Moeen and Saad Hussain |
| Initial ownership | 150 ordinary shares each; one-third each |
| Initial funding | PKR 15,000 per founder over one year; PKR 45,000 in total |
| First service | Inspection workspace, report preparation and onboarding |

Vision: Make building and site records easier to understand, review and act on.

Mission: Give engineering and construction teams a practical way to collect evidence, prepare clear reports and maintain a reliable history of their work.

Our proposed value is the connection between a photograph, the visible crack outline, the model's original observation and the person's final review. Local onboarding and a focused workflow may help smaller teams adopt the product. Whether these benefits justify the price remains a customer research question.

[PAGE]
# C. Problem and proposed solution
An inspection often produces photographs, field notes and a report prepared later. The product hypothesis is that smaller teams lose time organising these items and explaining what needs another look. Our first customer interviews will check how often this occurs, what it costs in staff time and which existing tools already solve it.

Imarah.tech brings the photograph and its review into one record. The detector marks visible crack regions. A vision-language model provides an observation, and a person checks that observation before using it in an inspection report. The original output remains available so that an error is not hidden by later editing.

## The inspection workflow
1. A user takes or uploads a photograph and adds a location or field note.
2. The chosen live detector processes the photograph and returns its actual segmentation.
3. The selected Local or VPS model generates an observation from the image and available context.
4. The application saves the photograph, outputs, model settings and processing details.
5. A reviewer checks the evidence, adds notes and exports or prints the report.

## What exists and what remains planned
| Product area | Position at 27 September 2026 | Next requirement |
| Image inspection | Working upload, live detector connection and segmentation outlines | Broader labelled evaluation under field conditions |
| Model observations | Four local models tested; separate Qwen 4B VPS option | Review errors and compare consistent test conditions |
| Reports and model lab | Saved outputs, review notes, exports and earlier benchmarks | Improve review workflow with user feedback |
| Public customer access | Current application is a single-user prototype | Accounts, permissions, tenant isolation and operational checks |
| Worker and site records | Concept screens with fictional data | Implement records and validate attendance and PPE models |
| Sensors and urban analysis | Roadmap and concept screens | Real data sources, prototype devices and evaluation |

This summary is based on the repository's September phase notes and progress record. Earlier local benchmarks are retained. Their small sample sizes do not establish a general accuracy score. [2]

## Product boundaries
A surface photograph cannot establish structural stability, hidden damage or the cause of a crack by itself. We will not sell an automated safety certificate. An engineer or another suitably qualified professional must make decisions that require professional judgement.

The proposed site module will record payroll and insurance information without processing payments or providing insurance. Real worker monitoring, live sensor alerts and area-level risk analysis will remain unavailable as commercial features until their data, permissions and validation are ready. [1]

[PAGE]
# D. Market analysis
## Initial customers and needs
| Segment | Likely buyer and user | Need to test in interviews |
| Small engineering consultancies | Practice owner; inspecting engineer | Less time arranging photographs and preparing repeat reports |
| Property maintenance teams | Facilities manager; site staff | A searchable record of defects, reviews and follow-up visits |
| Small and medium contractors | Project manager; site supervisor | Inspection evidence linked to progress and corrective work |

We will focus first on engineering consultancies because their staff can review the output and explain where it is useful or misleading. Public authorities and large developers are later prospects because their approvals, integration needs and procurement cycles may be more demanding.

## Market context and potential
Pakistan's 2023 census reported an urban population share of 38.82%. This establishes a sizeable urban context for building-related services, but it does not tell us how many organisations would buy our software. [3] We have not verified a national revenue figure for this specific inspection software market and do not present one.

Instead, the first sales plan uses a bottom-up target: identify 100 relevant organisations in Karachi, hold 20 useful demonstrations and reach 10 paying organisations by the end of the first commercial year. These are proposed outreach targets, not an existing prospect list or measured conversion rates. At PKR 15,000 monthly, 10 continuously subscribed organisations would represent PKR 1,800,000 of annual recurring revenue at the year-end run rate. The first year's actual projected subscription revenue is lower because customers join gradually.

## Alternatives and competitors
| Alternative | Relevant strength | Implication for Imarah.tech |
| Spreadsheets, photographs and messaging | Familiar tools with little additional setup | We must show enough improvement to justify switching; this is a hypothesis to test |
| Procore | Offers construction inspection tools and quality and safety workflows [4] | Compete through a focused first service, not claims of broader functionality |
| DroneDeploy | Offers progress and photo reporting for site documentation [5] | Position our phone-photo review workflow clearly; do not claim equivalent surveying capability |

The competitor descriptions are based on their own product information. We have not conducted a feature-by-feature trial or verified comparable Pakistan pricing. We therefore make no claim that Imarah.tech is the cheapest, most accurate or the only available system.

## Opportunity and challenges
Established products show that digital inspection and site reporting are real product categories. Our opportunity is a narrower service with understandable records and direct local support. The difficult parts are earning trust, handling poor photographs, keeping customer data separate and proving that the tool saves time. Interviews and paid pilots must establish demand before we commit to a larger sales team.

[PAGE]
# E. Marketing and sales strategy
## Proposed pricing
| Offering | Proposed price | Initial scope |
| Inspection workspace | PKR 15,000 per organisation per month | One organisation, up to five users and 200 image inspections monthly after multi-user support is ready |
| Onboarding | PKR 10,000 once per new organisation | Initial workspace setup, one training session and one report-template setup |
| Additional usage or integrations | Quoted after a usage review | Not included in the base revenue forecast |

These prices exclude applicable taxes. The usage allowance is a commercial assumption, not measured server capacity. The pilot will measure processing cost and support effort before a customer plan is finalised. Large sensor installations, site hardware, engineering certification and custom attendance systems are excluded.

## Customer acquisition
The founders will begin with direct introductions to engineering practices, university contacts and local property teams. A short demonstration will use permission-cleared photographs and show the original evidence alongside the reviewed report. A one-page sample report and a short product video will support follow-up conversations.

The website and LinkedIn page will explain the workflow, show relevant product updates and publish examples only with permission. We will avoid claims about preventing collapses, identifying every crack or replacing engineers. Paid promotion will remain small until direct outreach shows which customer segment responds.

## Sales process
1. Speak with the decision-maker and record their current reporting method, volume and difficulties.
2. Demonstrate a relevant example and agree on a limited pilot scope, permitted data and success measures.
3. Run the pilot only after access controls and customer separation are ready.
4. Review preparation time, corrections, support effort and the buyer's willingness to renew.
5. Offer the agreed subscription, provide training and schedule a monthly check-in.

We aim to recruit three design partners before wider selling. A design partner is a proposed pilot participant, not a confirmed customer. The sales forecast assumes ten first-year conversions across the full outreach programme, including any pilots that convert.

## Retention and service quality
Customers should be able to retrieve their reports and understand how the results were produced. We will track completed inspections, time spent preparing reports, correction requests, support response times and renewals. These will be measured during use; no improvement percentage is assumed in advance.

In the later commercial scenario, the first-year marketing budget is PKR 7,000 per month, or PKR 84,000 annually. If it contributes to ten new customers, the cash marketing spend alone is PKR 8,400 per customer. This excludes founder sales time and travel, so it is not a complete customer acquisition cost.

[PAGE]
# F. Operations plan
## Service delivery and day-to-day work
The team will review failed jobs and customer issues each working day. New customer setup will include the workspace, agreed access permissions, a short training session and confirmation of which photographs may be processed. A reviewer within the customer's team will remain responsible for accepting or correcting inspection observations.

Technical releases will go through automated checks and sample inspections before deployment. Changes to a model will be recorded with its version and test results. Failures will be visible to the user; a failed live request will not be replaced with an undisclosed demonstration result.

## Resources and technology
The existing prototype uses a React and TypeScript interface, a Python API and local data storage. The crack model is accessed through its configured Ultralytics endpoint. Qwen 4B can run locally or through a private VPS connection. The current server has a Tesla P100 with 16 GiB GPU memory and 125 GiB RAM. These resources support development; they are not evidence that the planned customer allowance can already be served. [2, 6]

Before a paid multi-user service, we need authentication, role-based access, separation of customer data, secure deployment, backup restoration checks and a measured job queue. The current SSH tunnel is a development arrangement. Public access will require a separately secured service, not exposure of the raw model endpoint.

Large models, datasets, logs and checkpoints will remain on the server's data disk. Each project will have separate operational data. System tools and Python environments will remain on the system disk, following the repository's storage convention. [6]

## Suppliers and external expertise
The planned service depends on hosting, connectivity and permitted model software. The team will review the commercial terms for the YOLO deployment, open model weights and datasets before charging customers. A licence change or service outage may require a documented model replacement and fresh evaluation.

We will seek a civil or structural engineering reviewer for evaluation advice and an accountant for incorporation and financial reporting. These are intended roles, not confirmed partnerships. Any review or pilot site work will use written permission and a clear scope.

## Location, support and data handling
The founders will initially work from their existing development locations in Karachi. No dedicated office lease is included in the budget. Customer visits will be scheduled, with site safety requirements agreed beforehand. Business-hours support will be provided by the founders; a 24-hour support commitment is not included.

Customer terms will define permitted uploads, retention, export and deletion. Customer images will not be reused for model training without separate permission. Worker-related information will require additional notice, access restrictions and a way to correct mistakes. Before onboarding, the team will rehearse a data restore and an incident response using test records.

[PAGE]
# G. Organisation and management
The proposed ownership matches the memorandum and articles: 450 subscribed ordinary shares of PKR 100 each, held equally by the three founders. The proposed authorised capital is PKR 60,000. Each founder plans to contribute PKR 15,000 over one year. Paid-up capital will reflect actual receipts; no outside investment or formal appointment is claimed.

| Founder | Proposed business role | Main responsibilities |
| Hadi Abbas, 23K-0927 | Technical and model lead | Detector development, model evaluation, compute planning and technical coordination |
| Ayaan Moeen, 23I-0124 | Application and customer operations lead | Application delivery, data access, onboarding and customer feedback |
| Saad Hussain, 23K-0705 | Data and reporting lead | Dataset preparation, VLM reporting, evaluation records and later sensor data work |

These proposed business roles follow the areas of work in the FYP proposal, but are not claims of existing company appointments. All three founders will contribute to demonstrations, testing, documentation and early sales. [1]

## Reporting structure
| Level | Responsibility and reporting line |
| Shareholders | The three founders approve ownership changes and other reserved matters |
| Board | The three proposed directors approve budgets, risks and product release decisions |
| Delivery team | The three functional leads report progress and issues to the board |
| External advisers | Engineering reviewer and accountant advise within agreed engagements |

The team will have a short weekly delivery meeting and a monthly business review covering cash, customer feedback, incidents and upcoming work. Important decisions will be written down rather than left in chat messages. Expenses and conflicts will follow the controls in the articles.

## Hiring and capability gaps
During the project year, founders receive no salary or allowance. The separate, later commercial scenario assumes substantial founder work and only PKR 10,000 monthly cash allowance per founder. This is a temporary bootstrapping assumption, not a market salary or evidence that the business can support three full-time graduates. There is no separate office or permanent employee in that year.

As revenue grows, the priorities are customer support capacity, stronger software security and access to civil engineering expertise. The second- and third-commercial-year fixed budgets increase to reflect more support and paid work. Recruitment will depend on actual collections and retained customers rather than forecast revenue alone.

## Readiness before a paid launch
The board will require evidence of customer demand, a reviewed test set, reliable access controls, backup recovery, suitable licences and a workable support process. The academic deadline alone will not trigger commercial release. A product can be ready for an FYP demonstration while still needing work before it is ready for paying customers.

[PAGE]
# H. Financial plan: one-year project budget
All amounts are in Pakistani rupees. Each founder will contribute PKR 15,000 over one year, making PKR 45,000 for the three-member team. This is the project funding plan, not PKR 15,000 per month and not cash available in full at the start. The monthly schedule below is a planning assumption.

## Contributions and low-cost equipment
| Item | Planned amount, PKR | Basis |
| Hadi Abbas | 15,000 | Over one year |
| Ayaan Moeen | 15,000 | Over one year |
| Saad Hussain | 15,000 | Over one year |
| Total founder contributions | 45,000 | PKR 3,750 monthly across the team |
| Low-cost equipment | 30,000 | Below the team's PKR 50,000 equipment ceiling |
| Other project expenses | 9,000 | Travel, printing and small consumables |
| Unspent reserve | 6,000 | Held for unexpected project needs |

The equipment allowance is split into PKR 6,000 for microcontroller boards, PKR 10,000 for prototype sensors, PKR 8,000 for power supplies, cables and enclosures, and PKR 6,000 for storage, adapters and spare parts. These are proposed limits, not supplier quotations or a final parts list. Purchases will follow the prototype design and available cash.

Existing laptops, phones and the available VPS will be reused. No new GPU, server or workstation is included. Continued access to these resources is assumed; any additional hosting or model-service bill must fit the reserve or trigger a revised budget. Existing resource access is not a claim that commercial hosting is free.

## Spending and payment schedule
Each founder is assumed to pay PKR 1,250 monthly. Equipment is bought in stages at the end of each quarter, after contributions have been collected. Other expenses are limited to PKR 750 monthly. This avoids spending money before it is received.

| Item, PKR | Q1 | Q2 | Q3 | Q4 | Total |
| Founder contributions | 11,250 | 11,250 | 11,250 | 11,250 | 45,000 |
| Equipment purchases | 6,000 | 8,000 | 8,000 | 8,000 | 30,000 |
| Other project expenses | 2,250 | 2,250 | 2,250 | 2,250 | 9,000 |
| Net cash movement | 3,000 | 1,000 | 1,000 | 1,000 | 6,000 |
| Closing cash | 3,000 | 4,000 | 5,000 | 6,000 | 6,000 at year-end |

Opening project cash is zero. Total planned cash spending is PKR 39,000. The PKR 6,000 reserve is not an additional expense. No customer revenue, loan, grant, founder salary, office rent or paid employee is assumed during this project year. Contributions are funding, not sales or profit. Equipment purchases are cash outflows; their eventual accounting treatment will be decided when company accounts are prepared.

[PAGE]
# H. Financial plan: later commercial scenario
The figures below describe a possible paid service after the project year. They are separate from the PKR 45,000 student budget and are not commitments to spend that amount of money now. Incorporation, professional review and commercial deployment will need quotations and a separate launch budget.

## Pricing, sales and operating assumptions
The proposed subscription remains PKR 15,000 per customer monthly, with PKR 10,000 onboarding. Variable costs are assumed at PKR 2,000 per active customer monthly and PKR 3,000 per new customer. Prices exclude applicable taxes. No confirmed customers, churn or bad debts are assumed in this illustration.

First-commercial-year fixed costs are PKR 75,000 monthly: hosting and backups PKR 20,000; founder allowances PKR 30,000 combined; travel PKR 8,000; marketing PKR 7,000; administration PKR 5,000; and contingency PKR 5,000. These are future operating allowances, not project-year costs. Later fixed costs rise to PKR 150,000 and PKR 250,000 monthly as support needs grow.

| Item | Commercial Year 1 | Commercial Year 2 | Commercial Year 3 |
| Average active customers | 5.75 | 16 | 28 |
| Year-end customers | 10 | 22 | 42 |
| New customers | 10 | 12 | 20 |
| Subscription and onboarding revenue, PKR | 1,135,000 | 3,000,000 | 5,240,000 |
| Operating costs, PKR | 1,068,000 | 2,220,000 | 3,732,000 |
| Operating surplus before tax and launch costs, PKR | 67,000 | 780,000 | 1,508,000 |

Revenue equals average customers × 12 × PKR 15,000, plus new customers × PKR 10,000. Costs include fixed spending, variable service costs and onboarding. These are operating projections, not final net profits: launch costs, tax, depreciation and any financing costs remain outside this illustration.

## Break-even and commercial funding gap
Recurring contribution per customer is PKR 15,000 less PKR 2,000, or PKR 13,000 monthly. Operating break-even is six active customers at PKR 75,000 fixed monthly costs, twelve at PKR 150,000 and twenty at PKR 250,000. This excludes onboarding income and recovery of launch costs.

The first commercial year assumes 2, 4, 7 and 10 active customers in successive quarters, with new customers joining at each quarter's start. Net operating cash would be negative PKR 133,000 in Q1, negative PKR 55,000 in Q2, positive PKR 69,000 in Q3 and positive PKR 186,000 in Q4, assuming same-quarter collections. The cumulative operating shortfall reaches PKR 188,000 before recovering.

Even if the PKR 6,000 project reserve remains, this scenario needs at least PKR 182,000 of additional working capital, plus separately budgeted launch costs and a cash buffer. No such funding is secured or assumed to come from the founders' stated contributions. Paid launch will wait for suitable funding or a smaller operating plan supported by customer commitments.

## Budget risks
If project equipment costs rise from PKR 30,000 to PKR 36,000, the reserve is exhausted. Spending above that requires reducing other costs or agreeing extra funding, even if equipment alone remains below PKR 50,000. If a founder's instalment is late, the related purchase is delayed. For the later service, doubling variable cost to PKR 4,000 raises first-year operating break-even to seven customers.

[PAGE]
# I. Risk analysis
| Risk | Likely effect | Proposed response |
| Customers do not adopt or renew | Revenue stays below operating costs | Run small pilots, measure actual use and delay hiring until renewals support it |
| A model misses damage or invents a cause | A user may rely on an incorrect observation | Keep human review, show original evidence, record errors and avoid safety certification claims |
| Customer data is exposed or mixed | Loss of trust and contractual consequences | Separate customer access and storage, review permissions and test recovery before launch |
| GPU, detector endpoint or network fails | Inspections are delayed or incomplete | Queue work, show failure clearly, monitor dependencies and test documented recovery |
| Low prices or heavy usage erode margin | Customers generate less contribution than forecast | Measure usage costs, enforce agreed limits and revise future pricing transparently |
| Licence, university ownership or regulatory issues | Product release may be delayed | Review permissions before commercial use and keep written agreements and licence records |
| Worker monitoring produces wrong records | Unfair attendance or safety decisions | Require human correction, restrict use and validate before using real worker data |
| Founder availability or disagreement | Delivery and support slow down | Document responsibilities, maintain shared records and use the articles' decision process |
| Competitors meet the same need better | Switching and sales become harder | Focus on a proven customer problem and avoid broad feature promises |

Risk reviews will use evidence from pilots and service operation. We have not assigned numerical probabilities or risk scores without supporting data.

## J. Future growth and sustainability
| Stage | Planned work | Evidence needed before moving forward |
| Sep 2026 | Demonstrate the inspection journey and document the startup proposal | Clear separation of live results, demos and future features |
| Oct to Dec 2026 | Evaluate inspection models and improve reviewed reports | Labelled test cases, recorded mistakes and professional feedback |
| Jan to Feb 2027 | Develop site records, attendance and protective-equipment features | Working records and validated models with appropriate permissions |
| Mar to Apr 2027 | Prototype sensors, weather integration and urban analysis | Real test data, documented limitations and integrated prototype checks |
| Apr to May 2027 | Complete integration, evaluation and FYP documentation | Reproducible demonstrations and the final project evidence |
| After the FYP | Limited paid pilots, then a wider service if justified | Access controls, licences, customer demand and acceptable operating costs |

The academic sequence follows the proposal. Commercial launch depends on readiness. Later growth may include other cities and engineering partnerships. Revenue from sensors, authorities and urban analysis is excluded from the forecast. [1]

We will reuse hardware, release idle model memory and limit unnecessary storage. Environmental benefits have not been measured. Expansion will require sustainable collections or separately agreed investment.

[PAGE]
# K. Conclusion
Imarah.tech has a working starting point for a focused software business: collecting inspection evidence and helping a person prepare and review a report. The broader FYP gives it a path toward construction records and building monitoring, but those additions should follow useful, tested inspection work.

The proposed business is deliberately small at launch. Equal founder ownership, limited initial spending and a narrow customer group make the plan easier to test. The project budget is PKR 45,000 collected over one year, with low-cost equipment and no founder salaries. The later commercial forecast requires separate working capital; it cannot be funded from this student budget alone.

Our next business step is to talk to engineering teams, evaluate reports with appropriate reviewers and agree on a controlled pilot. A decision to expand should follow that evidence rather than the number of features shown in the prototype.

## References and evidence notes
External sources were accessed on 27 September 2026. Product pages establish the vendors' stated offerings, not independently measured performance. The annual founder contributions and equipment ceiling follow the team's instructions. Detailed spending, payment timing, pricing, sales volumes and proposed company arrangements remain planning assumptions.

[1] Imarah.tech FYP group. Final Year Project Proposal, 18 September 2026. Source for the project concept, team, scope and academic sequence. Repository file: FYP-I-project-proposal-2026-final (1).pdf.

[2] Imarah.tech repository. Extra-Documentations/Phase1.md and Extra-Documentations/Progress.md, September 2026 records. Source for implemented features, model experiments, live segmentation and planned modules. This document does not claim new tests were run for the business plan.

[3] Pakistan Bureau of Statistics. Announcement of Results of the 7th Population and Housing Census 2023. Source for the 38.82% urban population share; not an estimate of paying customers.
https://www.pbs.gov.pk/wp-content/uploads/2020/07/Announcement-of-Results-of-7th-Population-and-Housing-Census-2023.pdf

[4] Procore. Construction Site Inspection Software. Source for the competitor's stated inspection and quality/safety offering. Pricing and comparative performance were not verified.
https://www.procore.com/quality-safety/inspections

[5] DroneDeploy. Progress & Photo Reports. Source for the competitor's stated site reporting functions. No equivalence to Imarah's prototype capabilities is claimed.
https://help.dronedeploy.com/hc/en-us/articles/1500004965302-Progress-Photo-Reports

[6] Imarah.tech repository. docs/operations/server-environment.md and docs/guides/vps-qwen.md. Source for the existing server arrangement, storage convention and private model connection.

## Items to confirm before commercial use
The founders must agree on ownership, contributions and roles; select a registered office; review university and third-party rights; and obtain current incorporation, tax and professional advice. Supplier quotations, customer interviews and measured service costs should replace the financial assumptions before money is committed.

For this academic submission, the memorandum, articles and plan use the same proposed legal name, three founders, equal ownership and PKR 45,000 total founder contributions over one year. Signature spaces in the corporate documents remain blank because no adoption has been claimed.

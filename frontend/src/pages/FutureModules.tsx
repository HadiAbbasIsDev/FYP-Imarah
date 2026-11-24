// Use: explain future proposal modules with clearly labelled, interactive sample data.
// Copyright (c) 2026 Imarah.tech. All rights reserved.
import { useState } from "react";
import {
  Activity,
  ArrowRight,
  Building2,
  CalendarDays,
  CheckCircle2,
  CircleDashed,
  CloudSun,
  HardHat,
  Layers,
  Leaf,
  MapPin,
  Package,
  Radio,
  ShieldCheck,
  Users,
  Wallet,
} from "lucide-react";
import { Link } from "react-router-dom";
import { useApi } from "../api";
import type { Demo, Worker } from "../types";
import {
  ErrorMessage,
  Loading,
  PageHeader,
  PreviewNotice,
  SectionTitle,
  Sparkline,
  Tag,
} from "../components/UI";

export function SiteManagement() {
  const { data, error } = useApi<Demo>("/demo");
  const [tab, setTab] = useState("Workforce");
  const [filter, setFilter] = useState("All workers");
  const [selected, setSelected] = useState<Worker | null>(null);
  if (!data) return error ? <ErrorMessage message={error} /> : <Loading />;
  const workers = data.workers.filter(
    (w) =>
      filter === "All workers" ||
      (filter === "Present"
        ? w.attendance === "Present"
        : w.attendance === "Present" && (!w.helmet || !w.vest)),
  );
  const present = data.workers.filter((w) => w.attendance === "Present");
  const equipped = present.filter((w) => w.helmet && w.vest);
  return (
    <>
      <PageHeader
        eyebrow="CONSTRUCTION / MODULE 02"
        title="People make the progress."
        description="A shared view of the workforce, site safety, and the day’s work."
        action={<Tag>January–February 2027</Tag>}
      />
      <PreviewNotice />
      <div className="site-banner">
        <div className="site-banner-icon">
          <Building2 size={28} />
        </div>
        <div>
          <h2>{data.site.name}</h2>
          <p>
            <MapPin size={14} />
            {data.site.location} <span>·</span> {data.site.stage}
          </p>
        </div>
        <div className="site-progress">
          <span>
            Sample project progress <strong>{data.site.progress}%</strong>
          </span>
          <div className="bar-track">
            <span style={{ width: `${data.site.progress}%` }} />
          </div>
        </div>
      </div>
      <div className="stats-grid compact">
        {[
          {
            name: "On site today",
            value: `${present.length} / ${data.workers.length}`,
            note: "Simulated attendance",
            icon: Users,
          },
          {
            name: "PPE complete",
            value: `${equipped.length} / ${present.length}`,
            note: "Among workers marked present",
            icon: ShieldCheck,
          },
          {
            name: "Open safety checks",
            value: present.length - equipped.length,
            note: "Missing helmet or vest",
            icon: HardHat,
          },
          {
            name: "Tracked materials",
            value: data.materials.length,
            note: "Illustrative material records",
            icon: Package,
          },
        ].map((s) => (
          <div className="stat-card" key={s.name}>
            <div className="stat-top">
              <span>{s.name}</span>
              <s.icon size={19} />
            </div>
            <strong>{s.value}</strong>
            <p>{s.note}</p>
          </div>
        ))}
      </div>
      <section className="card">
        <div className="list-toolbar">
          <div className="tabs">
            {["Workforce", "Materials", "Records"].map((name) => (
              <button
                className={tab === name ? "selected" : ""}
                onClick={() => setTab(name)}
                key={name}
              >
                {name}
              </button>
            ))}
          </div>
          {tab === "Workforce" && (
            <select
              aria-label="Filter workers"
              value={filter}
              onChange={(event) => setFilter(event.target.value)}
            >
              {["All workers", "Present", "PPE follow-up"].map((option) => (
                <option key={option}>{option}</option>
              ))}
            </select>
          )}
        </div>
        {tab === "Workforce" ? (
          <>
            <div className="table-scroll">
              <table className="worker-table">
                <thead>
                  <tr>
                    <th>Team member</th>
                    <th>Attendance</th>
                    <th>Protective gear</th>
                    <th>Assigned work</th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {workers.map((worker) => (
                    <tr key={worker.id}>
                      <td>
                        <div className="worker-name">
                          <span className="avatar">
                            {worker.name
                              .split(" ")
                              .map((v) => v[0])
                              .join("")}
                          </span>
                          <div>
                            <strong>{worker.name}</strong>
                            <small>
                              {worker.role} · {worker.id}
                            </small>
                          </div>
                        </div>
                      </td>
                      <td>
                        <Tag
                          tone={worker.attendance === "Present" ? "green" : ""}
                        >
                          {worker.attendance}
                        </Tag>
                        <small>{worker.check_in}</small>
                      </td>
                      <td>
                        <span
                          className={`gear-status ${worker.helmet === false ? "missing" : ""}`}
                        >
                          <HardHat size={15} />
                          {worker.helmet === null
                            ? "—"
                            : worker.helmet
                              ? "Helmet"
                              : "No helmet"}
                        </span>
                        <span
                          className={`gear-status ${worker.vest === false ? "missing" : ""}`}
                        >
                          <ShieldCheck size={15} />
                          {worker.vest === null
                            ? "—"
                            : worker.vest
                              ? "Vest"
                              : "No vest"}
                        </span>
                      </td>
                      <td>
                        {worker.task}
                        <div className="task-progress">
                          <div className="bar-track">
                            <span style={{ width: `${worker.progress}%` }} />
                          </div>
                          <small>{worker.progress}%</small>
                        </div>
                      </td>
                      <td>
                        <button
                          className="button plain small-button"
                          onClick={() =>
                            setSelected(
                              selected?.id === worker.id ? null : worker,
                            )
                          }
                          aria-label={`View ${worker.name}`}
                        >
                          View <ArrowRight size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="table-note">
              Names and records are fictional. PPE labels and check-ins are
              sample values; no detection or identification model runs on this
              page.
            </div>
          </>
        ) : tab === "Materials" ? (
          <div className="materials-grid">
            {data.materials.map((material) => (
              <div className="material-card" key={material.name}>
                <Package size={25} />
                <h3>{material.name}</h3>
                <strong>
                  {material.received - material.used}{" "}
                  <small>{material.unit} remaining</small>
                </strong>
                <div className="bar-track">
                  <span
                    style={{
                      width: `${(material.used / material.received) * 100}%`,
                    }}
                  />
                </div>
                <p>
                  {material.used} used / {material.received} received
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="records-grid">
            <div>
              <Wallet size={23} />
              <h3>Payroll records</h3>
              <strong>
                PKR{" "}
                {data.workers
                  .reduce((s, w) => s + w.payroll, 0)
                  .toLocaleString()}
              </strong>
              <p>
                Sum of fictional salary records. No payments or disbursement.
              </p>
            </div>
            <div>
              <Building2 size={23} />
              <h3>Contractor</h3>
              <strong>{data.site.contractor}</strong>
              <p>Contract and contact records are planned for Module 2.</p>
            </div>
            <div>
              <ShieldCheck size={23} />
              <h3>Insurance</h3>
              <strong>
                {data.workers.filter((w) => w.insurance === "Recorded").length}{" "}
                / {data.workers.length} recorded
              </strong>
              <p>
                Policy recording only. Sample status does not verify coverage.
              </p>
            </div>
          </div>
        )}
      </section>
      {selected && tab === "Workforce" && (
        <section className="card form-card worker-detail">
          <SectionTitle
            title={`${selected.name} · sample assessment`}
            note="A manual preview of the planned worker record."
          />
          <div className="assessment-grid">
            <div>
              <span>Assigned task</span>
              <strong>{selected.task}</strong>
            </div>
            <div>
              <span>Recorded progress</span>
              <strong>{selected.progress}%</strong>
            </div>
            <div>
              <span>Salary record</span>
              <strong>PKR {selected.payroll.toLocaleString()}</strong>
            </div>
            <div>
              <span>Insurance record</span>
              <strong>{selected.insurance}</strong>
            </div>
          </div>
          <p className="fine-print">
            Task completion is a fictional entered value. The app does not infer
            productivity, identity or performance from a photograph.
          </p>
        </section>
      )}
      <div className="next-phase-note">
        <CalendarDays size={21} />
        <div>
          <h3>What turns this preview into a working module?</h3>
          <p>
            Persistent worker records, reviewed attendance, PPE detection,
            role-based access, and a correction process for mistakes.
          </p>
        </div>
        <Link className="text-link" to="/roadmap">
          Our stages
          <ArrowRight size={16} />
        </Link>
      </div>
    </>
  );
}

export function Monitoring() {
  const { data, error } = useApi<Demo>("/demo");
  const [selected, setSelected] = useState("Temperature");
  if (!data) return error ? <ErrorMessage message={error} /> : <Loading />;
  const sensor = data.sensors.find((s) => s.name === selected)!;
  return (
    <>
      <PageHeader
        eyebrow="BUILDING MONITORING / MODULE 03"
        title="Listen to the building over time."
        description="A place for sensor readings, environmental context, and changes worth reviewing."
        action={<Tag>March–April 2027</Tag>}
      />
      <PreviewNotice>
        No sensor or weather service is connected. All values and trends below
        are simulated.
      </PreviewNotice>
      <div className="monitoring-top">
        <div className="site-banner">
          <div className="site-banner-icon">
            <Radio size={27} />
          </div>
          <div>
            <h2>Prototype monitoring station</h2>
            <p>
              <MapPin size={14} />
              Gulshan Residence · example sensor location
            </p>
          </div>
          <Tag tone="amber">Simulated</Tag>
        </div>
        <div className="weather-card">
          <CloudSun size={38} />
          <div>
            <strong>33°</strong>
            <span>Karachi · sample weather</span>
          </div>
          <p>
            Partly cloudy
            <br />
            No live weather feed
          </p>
        </div>
      </div>
      <div className="sensor-grid">
        {data.sensors.map((s) => (
          <button
            key={s.name}
            onClick={() => setSelected(s.name)}
            className={`card sensor-card ${selected === s.name ? "selected" : ""}`}
          >
            <div>
              <h3>{s.name}</h3>
              <Activity size={18} />
            </div>
            <strong>
              {s.value}
              <small>{s.unit}</small>
            </strong>
            <Sparkline values={s.trend} />
            <span>Illustrative recent readings</span>
          </button>
        ))}
      </div>
      <div className="monitoring-detail">
        <section className="card sensor-chart">
          <SectionTitle
            title={`${sensor.name} through the day`}
            note="Ten simulated readings · no calibrated alert threshold"
          />
          <div className="large-chart">
            <div className="chart-grid-lines">
              <span />
              <span />
              <span />
              <span />
            </div>
            <Sparkline values={sensor.trend} filled />
          </div>
          <div className="chart-axis">
            <span>08:00</span>
            <span>10:00</span>
            <span>12:00</span>
            <span>14:00</span>
            <span>17:00</span>
          </div>
          <div className="chart-caption">
            <span className="status-dot" />
            Sample {sensor.name.toLowerCase()} trend
          </div>
        </section>
        <section className="card environment-note">
          <Leaf size={27} />
          <h2>A reading needs context.</h2>
          <p>{sensor.note}</p>
          <div>
            <h3>The planned flow</h3>
            <p>
              Sensor → timestamp & calibration checks → stored readings →
              weather context → engineer review.
            </p>
          </div>
          <p className="field-help">
            The hardware prototype and interpretation method will be developed
            and tested before using alerts on a real building.
          </p>
        </section>
      </div>
    </>
  );
}

export function UrbanAnalysis() {
  const { data, error } = useApi<Demo>("/demo");
  const [areaIndex, setAreaIndex] = useState(0);
  if (!data) return error ? <ErrorMessage message={error} /> : <Loading />;
  const area = data.areas[areaIndex];
  return (
    <>
      <PageHeader
        eyebrow="URBAN INTELLIGENCE / MODULE 04"
        title="Step back. See the neighbourhood."
        description="Explore how area selection and urban indicators could inform a wider view."
        action={<Tag>April–May 2027</Tag>}
      />
      <PreviewNotice>
        This is a schematic selection demo. No real map tiles, satellite data,
        or risk model are connected.
      </PreviewNotice>
      <div className="urban-grid">
        <section className="card schematic-card">
          <div className="map-toolbar">
            <span>
              <Layers size={17} />
              Karachi · schematic
            </span>
            <Tag>Illustrative geometry</Tag>
          </div>
          <div className="schematic-map">
            <svg
              viewBox="0 0 700 500"
              role="img"
              aria-label="Schematic neighbourhood blocks, not a geographic map"
            >
              <rect width="700" height="500" fill="#e9ede3" />
              <path d="M0 375Q170 280 230 500H0Z" fill="#c5d9d7" />
              <g stroke="#f9faf6" strokeWidth="16">
                <path d="M80 0L610 500M0 100L610 500M265 0L700 325M0 260L430 0M90 500L700 90M300 500L700 235" />
              </g>
              <g fill="#c4cbb7" stroke="#abb6a0" strokeWidth="1">
                {Array.from({ length: 70 }, (_, i) => {
                  const x = 75 + (i % 10) * 57;
                  const y = 43 + Math.floor(i / 10) * 59;
                  return (
                    <rect
                      key={i}
                      x={x}
                      y={y}
                      width={17 + ((i * 7) % 25)}
                      height={15 + ((i * 11) % 23)}
                      rx="2"
                      transform={`rotate(12 ${x} ${y})`}
                    />
                  );
                })}
              </g>
              <path
                d={
                  areaIndex === 0
                    ? "M210 140L405 125L460 300L270 348Z"
                    : areaIndex === 1
                      ? "M355 248L530 220L590 373L424 418Z"
                      : "M90 75L237 70L275 201L155 244Z"
                }
                fill="#35775f"
                fillOpacity=".14"
                stroke="#34775f"
                strokeWidth="3"
                strokeDasharray="7 5"
              />
            </svg>
            <div className="map-selection">
              <MapPin size={17} />
              {area.name}
              <small>Sample area</small>
            </div>
            <span className="map-note">Not to scale · not georeferenced</span>
          </div>
        </section>
        <section className="card urban-summary">
          <label className="field">
            Explore an example area
            <select
              value={areaIndex}
              onChange={(event) => setAreaIndex(Number(event.target.value))}
            >
              {data.areas.map((a, i) => (
                <option key={a.name} value={i}>
                  {a.name}
                </option>
              ))}
            </select>
          </label>
          <h2>{area.name}</h2>
          <p>{area.note}</p>
          <dl>
            <div>
              <dt>
                <Building2 size={17} />
                Building count
              </dt>
              <dd>{area.buildings.toLocaleString()}</dd>
            </div>
            <div>
              <dt>
                <Layers size={17} />
                Built-up coverage
              </dt>
              <dd>{area.coverage}%</dd>
            </div>
            <div>
              <dt>
                <Leaf size={17} />
                Green cover
              </dt>
              <dd>{area.green_space}%</dd>
            </div>
          </dl>
          <Tag tone="amber">All numbers are fictional</Tag>
          <div className="notice">
            <CircleDashed size={20} />
            <span>
              Risk scoring is pending a defined, validated method. Density alone
              is not a safety score.
            </span>
          </div>
        </section>
      </div>
      <div className="next-phase-note">
        <Layers size={22} />
        <div>
          <h3>From a selected area to evidence</h3>
          <p>
            The planned module adds a map, satellite source and date, building
            extraction, validated indicators, and a clear explanation of
            uncertainty.
          </p>
        </div>
        <Link className="text-link" to="/roadmap">
          See the roadmap
          <ArrowRight size={16} />
        </Link>
      </div>
    </>
  );
}

export function Roadmap() {
  const { data, error } = useApi<Demo>("/demo");
  if (!data) return error ? <ErrorMessage message={error} /> : <Loading />;
  return (
    <>
      <PageHeader
        eyebrow="PROJECT / SEPTEMBER 2026—MAY 2027"
        title="Build a foundation. Then build on it."
        description="Our proposal, broken into stages we can develop, test, and explain."
        action={<Tag tone="green">FYP-I → FYP-II</Tag>}
      />
      <div className="roadmap-banner">
        <div>
          <span className="eyebrow">WHERE WE ARE TODAY</span>
          <h2>Phase 01 · A demonstrable idea.</h2>
          <p>
            We’re bringing the September proposal to life with a working PWA,
            local model experiments, and a clear plan for the complete system.
          </p>
        </div>
        <span className="roadmap-big-number">
          01<span>/ 05</span>
        </span>
      </div>
      <div className="timeline">
        {data.roadmap.map((stage, index) => (
          <article
            className={`timeline-stage ${index === 0 ? "current" : ""}`}
            key={stage.number}
          >
            <div className="timeline-node">
              {index === 0 ? <CheckCircle2 size={20} /> : stage.number}
            </div>
            <div className="card stage-card">
              <div className="stage-heading">
                <div>
                  <span className="eyebrow">{stage.period}</span>
                  <h2>{stage.name}</h2>
                </div>
                <Tag tone={index === 0 ? "green" : ""}>{stage.status}</Tag>
              </div>
              <div className="stage-tasks">
                {stage.items.map((item) => (
                  <div key={item}>
                    <span
                      className={
                        index === 0 ? "task-square filled" : "task-square"
                      }
                    />
                    {item}
                  </div>
                ))}
              </div>
              <div className="stage-owner">
                <Users size={15} />
                {stage.owner}
              </div>
            </div>
          </article>
        ))}
      </div>
      <section className="card team-card">
        <SectionTitle
          title="Three students. One connected system."
          note="Primary responsibilities from the project proposal; design, integration, testing and documentation are shared."
        />
        <div className="team-grid">
          {[
            {
              name: "Hadi Abbas",
              initials: "HA",
              role: "AI & computer vision",
              work: "Crack detection, human and PPE detection, weather and geospatial analysis.",
            },
            {
              name: "Ayaan Moeen",
              initials: "AM",
              role: "Application & platform",
              work: "PWA, API, database design, interfaces, dashboards and integration.",
            },
            {
              name: "Saad Hussain",
              initials: "SH",
              role: "Data, VLM & monitoring",
              work: "Data preparation, report generation, IoT prototype and risk analysis.",
            },
          ].map((person) => (
            <div key={person.name}>
              <span className="avatar">{person.initials}</span>
              <h3>{person.name}</h3>
              <strong>{person.role}</strong>
              <p>{person.work}</p>
            </div>
          ))}
        </div>
      </section>
      <div className="context-note">
        <CalendarDays size={19} />
        <span>
          The September prototype brings some Module 1 work forward for the
          evaluation. The proposal’s October–December milestones remain the
          target for a validated module. FYP-II dates are tentative.
        </span>
      </div>
    </>
  );
}

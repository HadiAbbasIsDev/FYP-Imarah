// Use: show the working inspection module alongside the full project direction.
// Copyright (c) 2026 Imarah.tech. All rights reserved.
import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  Check,
  Clock3,
  FlaskConical,
  HardHat,
  MapPin,
  Plus,
  ScanLine,
} from "lucide-react";
import { Link } from "react-router-dom";
import { useApi, date } from "../api";
import type { Benchmark, Health, Inspection, Model } from "../types";
import CityDrawing from "../components/CityDrawing";
import { EmptyState, ErrorMessage, SectionTitle, Tag } from "../components/UI";

export default function Dashboard() {
  const { data: inspections, error } = useApi<Inspection[]>(
    "/inspections",
    5000,
  );
  const { data: models } = useApi<Model[]>("/models", 10000);
  const { data: health } = useApi<Health>("/health", 10000);
  const { data: benchmarks } = useApi<Benchmark[]>("/benchmarks", 10000);
  const installed = models?.filter((m) => m.installed).length || 0;
  const reports = inspections?.filter((i) => i.report).length || 0;
  const runs =
    benchmarks?.flatMap((b) => b.rows).filter((r) => r.status === "complete")
      .length || 0;
  return (
    <>
      <div className="page-header dashboard-heading">
        <div>
          <div className="eyebrow">YOUR BUILDING INTELLIGENCE WORKSPACE</div>
          <h1>See the details. Build with confidence.</h1>
          <p>
            A clearer view of our buildings, our sites, and what comes next.
          </p>
        </div>
        <span className="date-label">
          September 2026 <span>Phase 01</span>
        </span>
      </div>
      <ErrorMessage message={error} />
      <section className="hero">
        <div className="hero-copy">
          <span className="hero-kicker">
            <span /> FROM A PHOTO TO AN INSIGHT
          </span>
          <h2>
            Better buildings start
            <br />
            with a closer look.
          </h2>
          <p>
            Bring surface evidence into focus. Explore cracks, compare AI
            models, and keep every inspection in one place.
          </p>
          <div className="hero-actions">
            <Link className="button cream" to="/inspections/new">
              <ScanLine size={18} />
              Start an inspection
              <ArrowUpRight size={17} />
            </Link>
            <Link className="hero-link" to="/models">
              Explore model lab <ArrowRight size={16} />
            </Link>
          </div>
          <div className="hero-footnote">
            <span />
            Building health assessment · September prototype
          </div>
        </div>
        <CityDrawing />
        <div className="hero-caption">01 / OBSERVE. UNDERSTAND. REVIEW.</div>
      </section>
      <div className="stats-grid">
        {[
          {
            name: "Inspections saved",
            value: inspections?.length ?? "—",
            note: "Your local inspection history",
            icon: ScanLine,
            color: "green",
          },
          {
            name: "Reports prepared",
            value: reports,
            note: "Drafts ready for a human review",
            icon: Check,
            color: "sage",
          },
          {
            name: "Local VLMs available",
            value: installed,
            note: "Downloaded on this machine",
            icon: FlaskConical,
            color: "clay",
          },
          {
            name: "Benchmark runs",
            value: runs,
            note: "Measured runs with saved outputs",
            icon: Clock3,
            color: "blue",
          },
        ].map((stat) => (
          <div className="stat-card" key={stat.name}>
            <div className="stat-top">
              <span>{stat.name}</span>
              <span className={`stat-icon ${stat.color}`}>
                <stat.icon size={18} />
              </span>
            </div>
            <strong>{stat.value}</strong>
            <p>{stat.note}</p>
          </div>
        ))}
      </div>
      <div className="dashboard-columns">
        <section className="card inspection-card">
          <SectionTitle
            title="Recent inspections"
            note="Every photo has a story. Keep its evidence together."
            to="/inspections"
          />
          {!inspections?.length ? (
            <EmptyState
              title="Your first inspection starts here."
              description="Try a research sample or upload a surface photograph. We’ll keep the model’s observations with the original evidence."
              action={
                <Link className="text-link" to="/inspections/new">
                  Create an inspection <Plus size={16} />
                </Link>
              }
            />
          ) : (
            <div className="recent-list">
              {inspections.slice(0, 3).map((item) => (
                <Link
                  className="recent-item"
                  to={`/inspections/${item.id}`}
                  key={item.id}
                >
                  <img src={item.image_url} alt="Inspection surface" />
                  <div>
                    <h3>{item.title}</h3>
                    <p>
                      <MapPin size={12} />
                      {item.location || "Location not recorded"}
                      <span>·</span>
                      {date(item.created_at)}
                    </p>
                  </div>
                  <Tag
                    tone={
                      item.status === "complete"
                        ? "green"
                        : item.status === "failed"
                          ? "red"
                          : "amber"
                    }
                  >
                    {item.status === "complete" ? "Draft ready" : item.status}
                  </Tag>
                  <ArrowUpRight size={17} />
                </Link>
              ))}
            </div>
          )}
          <div className="card-bottom">
            <span
              className={`status-dot ${health?.detector_configured ? "" : "amber-dot"}`}
            />
            {health?.detector_configured
              ? "Trained detector configured"
              : "YOLO connection awaiting setup"}
            <Link to="/inspections/new">
              Open inspection workspace <ArrowRight size={14} />
            </Link>
          </div>
        </section>
        <section className="research-card">
          <div className="research-heading">
            <FlaskConical size={21} />
            <Tag tone="clay">RESEARCH NOTEBOOK</Tag>
          </div>
          <h2>
            Which model sees
            <br />
            the bigger picture?
          </h2>
          <p>
            Compare what each VLM notices, how long it takes, and where it gets
            things wrong.
          </p>
          <div className="mini-models">
            <div>
              <span className="model-symbol">S</span>
              <div>
                SmolVLM<small>256M / 500M · CPU baselines</small>
              </div>
              <span className="model-size">01</span>
            </div>
            <div>
              <span className="model-symbol dark">Q</span>
              <div>
                Qwen3-VL<small>2B · local CPU / 4B · local or VPS</small>
              </div>
              <span className="model-size">02</span>
            </div>
          </div>
          <Link className="text-link" to="/models">
            Open the model lab <ArrowUpRight size={16} />
          </Link>
        </section>
      </div>
      <SectionTitle
        title="One platform. A wider perspective."
        note="The proposal’s four modules, developed one step at a time."
        to="/roadmap"
        linkText="View project stages"
      />
      <div className="module-grid">
        {[
          {
            number: "01",
            title: "Building health",
            description:
              "Surface images, crack evidence, and inspection drafts.",
            icon: ScanLine,
            to: "/inspections",
            label: "In progress",
            active: true,
          },
          {
            number: "02",
            title: "Construction sites",
            description:
              "People, protective gear, materials, and daily progress.",
            icon: HardHat,
            to: "/site",
            label: "Concept preview",
          },
          {
            number: "03",
            title: "Building monitoring",
            description: "Sensors and weather, with context over time.",
            icon: Activity,
            to: "/monitoring",
            label: "Concept preview",
          },
          {
            number: "04",
            title: "Urban intelligence",
            description: "A wider view of density, growth, and our cities.",
            icon: MapPin,
            to: "/urban",
            label: "Concept preview",
          },
        ].map((module) => (
          <Link
            className={`module-card ${module.active ? "active-module" : ""}`}
            to={module.to}
            key={module.number}
          >
            <div className="module-top">
              <module.icon size={23} />
              <span>{module.number}</span>
            </div>
            <h3>{module.title}</h3>
            <p>{module.description}</p>
            <div>
              <Tag tone={module.active ? "green" : ""}>{module.label}</Tag>
              <ArrowUpRight size={17} />
            </div>
          </Link>
        ))}
      </div>
      <div className="context-note">
        <span className="note-mark">i</span>
        <span>
          A student research prototype. Inspection outputs support an engineer’s
          review; they do not certify a building’s structural safety.
        </span>
      </div>
    </>
  );
}

// Use: upload/capture a photo, follow its analysis, and save a human-reviewed draft.
// Copyright (c) 2026 Imarah.tech. All rights reserved.
import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import {
  ArrowLeft,
  ArrowRight,
  ArrowUpRight,
  Camera,
  CheckCircle2,
  Download,
  Eye,
  FileText,
  ImagePlus,
  LoaderCircle,
  MapPin,
  Plus,
  Printer,
  ScanLine,
  Search,
  Upload,
} from "lucide-react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, date, seconds, useApi } from "../api";
import type { Health, Inspection, Job, Model, Sample } from "../types";
import ImageCredit from "../components/ImageCredit";
import DetectionOverlay from "../components/DetectionOverlay";
import {
  EmptyState,
  ErrorMessage,
  Loading,
  PageHeader,
  SectionTitle,
  Tag,
} from "../components/UI";

const statusLabel = (status: string) =>
  ({
    complete: "Draft ready",
    partial: "Partial draft",
    running: "Analysing",
    queued: "Queued",
    failed: "Needs attention",
  })[status] || status;

export function InspectionList() {
  const { data, error, loading } = useApi<Inspection[]>("/inspections", 5000);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const rows = data?.filter(
    (item) =>
      `${item.title} ${item.location}`
        .toLowerCase()
        .includes(search.toLowerCase()) &&
      (filter === "all" ||
        (filter === "ready"
          ? !!item.report
          : ["queued", "running"].includes(item.status))),
  );
  return (
    <>
      <PageHeader
        eyebrow="BUILDING HEALTH / MODULE 01"
        title="A closer look, on record."
        description="Photographs, model observations, and your review — kept together."
        action={
          <Link className="button primary" to="/inspections/new">
            <Plus size={17} />
            New inspection
          </Link>
        }
      />
      <ErrorMessage message={error} />
      <section className="card">
        <div className="list-toolbar">
          <div className="tabs" aria-label="Filter inspections">
            {[
              ["all", "All inspections"],
              ["ready", "Reports ready"],
              ["active", "In progress"],
            ].map(([value, label]) => (
              <button
                className={filter === value ? "selected" : ""}
                key={value}
                onClick={() => setFilter(value)}
              >
                {label}
              </button>
            ))}
          </div>
          <label className="search-input">
            <Search size={17} />
            <input
              aria-label="Search inspections"
              placeholder="Search name or location"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </label>
        </div>
        {loading ? (
          <Loading />
        ) : !rows?.length ? (
          <EmptyState
            title={
              search || filter !== "all"
                ? "No matching inspections."
                : "Start with a surface photograph."
            }
            description={
              search || filter !== "all"
                ? "Try another search or filter."
                : "Upload an image, capture one on your phone, or try a labelled sample."
            }
            action={
              <Link className="button primary" to="/inspections/new">
                <ImagePlus size={17} />
                Create an inspection
              </Link>
            }
          />
        ) : (
          <div className="inspection-grid">
            {rows.map((item) => (
              <Link
                className="inspection-tile"
                key={item.id}
                to={`/inspections/${item.id}`}
              >
                <div className="tile-photo">
                  <img
                    src={item.image_url}
                    alt={`Surface evidence for ${item.title}`}
                  />
                  <Tag tone={item.mode === "demo" ? "amber" : "green"}>
                    {item.mode === "demo" ? "Demo detector" : "Live detector"}
                  </Tag>
                </div>
                <div className="tile-content">
                  <div>
                    <h3>{item.title}</h3>
                    <ArrowUpRight size={18} />
                  </div>
                  <p>
                    <MapPin size={13} />
                    {item.location || "Location not recorded"}
                  </p>
                  <div className="tile-footer">
                    <span>{date(item.created_at)}</span>
                    <Tag
                      tone={
                        item.status === "complete"
                          ? "green"
                          : item.status === "failed"
                            ? "red"
                            : "amber"
                      }
                    >
                      {statusLabel(item.status)}
                    </Tag>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </>
  );
}

export function NewInspection() {
  const navigate = useNavigate();
  const { data: samples } = useApi<Sample[]>("/samples");
  const { data: models } = useApi<Model[]>("/models", 10000);
  const { data: health } = useApi<Health>("/health");
  const [sampleId, setSampleId] = useState("synthetic-crack");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState("");
  const [title, setTitle] = useState("Surface inspection");
  const [location, setLocation] = useState("");
  const [notes, setNotes] = useState("");
  const [model, setModel] = useState("smolvlm-256m");
  const [mode, setMode] = useState("demo");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const selectedModel = models?.find((candidate) => candidate.id === model);
  useEffect(() => {
    if (!file) {
      setPreview("");
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);
  function selectFile(next: File | undefined) {
    if (!next) return;
    if (next.size > 10 * 1024 * 1024) {
      setError("Choose an image smaller than 10 MB.");
      return;
    }
    if (!["image/jpeg", "image/png", "image/webp"].includes(next.type)) {
      setError("Choose a JPEG, PNG or WebP image.");
      return;
    }
    setError("");
    setFile(next);
    setSampleId("");
  }
  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setBusy(true);
    const form = new FormData();
    form.set("title", title);
    form.set("location", location);
    form.set("notes", notes);
    form.set("model_id", model);
    form.set("mode", mode);
    if (file) form.set("file", file);
    else form.set("sample_id", sampleId);
    try {
      const item = await api<Inspection>("/inspections", {
        method: "POST",
        body: form,
      });
      navigate(`/inspections/${item.id}`);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Could not start this inspection.",
      );
      setBusy(false);
    }
  }
  return (
    <>
      <Link className="back-link" to="/inspections">
        <ArrowLeft size={16} />
        Inspections
      </Link>
      <PageHeader
        eyebrow="NEW INSPECTION"
        title="Start with what you can see."
        description="One photograph, a little context, and a model you can compare."
      />
      <form onSubmit={submit} className="new-inspection-grid">
        <div>
          <section className="card form-card">
            <div className="step-heading">
              <span>01</span>
              <div>
                <h2>Add your photograph</h2>
                <p>
                  A sharp, well-lit close-up gives the model more to work with.
                </p>
              </div>
            </div>
            <div
              className="upload-area"
              onDragOver={(event) => event.preventDefault()}
              onDrop={(event) => {
                event.preventDefault();
                selectFile(event.dataTransfer.files[0]);
              }}
            >
              {file ? (
                <>
                  <img
                    src={preview}
                    alt="Your selected inspection photo"
                    className="upload-preview"
                  />
                  <p>{file.name}</p>
                  <button
                    type="button"
                    className="text-link"
                    onClick={() => {
                      setFile(null);
                      setSampleId("synthetic-crack");
                    }}
                  >
                    Choose a different image
                  </button>
                </>
              ) : (
                <>
                  <span className="upload-icon">
                    <Upload size={25} />
                  </span>
                  <h3>Drop a surface photo here</h3>
                  <p>JPEG, PNG or WebP · up to 10 MB</p>
                  <div className="upload-actions">
                    <label className="button secondary">
                      Browse files
                      <input
                        type="file"
                        accept="image/jpeg,image/png,image/webp"
                        className="visually-hidden"
                        aria-label="Upload surface photo"
                        onChange={(event) =>
                          selectFile(event.target.files?.[0])
                        }
                      />
                    </label>
                    <label className="button plain">
                      <Camera size={17} />
                      Use camera
                      <input
                        type="file"
                        capture="environment"
                        accept="image/*"
                        className="visually-hidden"
                        aria-label="Capture surface photo"
                        onChange={(event) =>
                          selectFile(event.target.files?.[0])
                        }
                      />
                    </label>
                  </div>
                </>
              )}
            </div>
            <div className="sample-heading">
              <span>Or explore a sample</span>
              <small>Research photos and labelled controls</small>
            </div>
            <div className="sample-grid">
              {samples?.map((sample) => (
                <button
                  type="button"
                  key={sample.id}
                  className={`sample-option ${sampleId === sample.id ? "selected" : ""}`}
                  onClick={() => {
                    setSampleId(sample.id);
                    setFile(null);
                  }}
                  aria-pressed={sampleId === sample.id}
                >
                  <div>
                    <img src={sample.url} alt={sample.description} />
                    {sampleId === sample.id && <CheckCircle2 size={19} />}
                  </div>
                  <strong>{sample.name}</strong>
                  <small>{sample.kind}</small>
                </button>
              ))}
            </div>
            <p className="fine-print">
              Road samples are from CrackForest, for non-commercial research.
              Synthetic examples demonstrate the workflow; they do not validate
              building inspections.
            </p>
            <ImageCredit
              credit={
                samples?.find((sample) => sample.id === sampleId)?.attribution
              }
            />
          </section>
          <section className="card form-card">
            <div className="step-heading">
              <span>02</span>
              <div>
                <h2>Give the image some context</h2>
                <p>These details stay with your report.</p>
              </div>
            </div>
            <label className="field">
              Inspection name
              <input
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                maxLength={100}
                required
                placeholder="e.g. East staircase · surface crack"
              />
            </label>
            <label className="field">
              Location <span className="optional">Optional</span>
              <input
                value={location}
                onChange={(event) => setLocation(event.target.value)}
                maxLength={160}
                placeholder="Building, floor, or a useful reference"
              />
            </label>
            <label className="field">
              Field notes <span className="optional">Optional</span>
              <textarea
                value={notes}
                onChange={(event) => setNotes(event.target.value)}
                maxLength={2000}
                placeholder="Lighting, material, when the photo was taken…"
                rows={3}
              />
            </label>
          </section>
        </div>
        <aside className="inspection-setup">
          <section className="card form-card">
            <div className="step-heading">
              <span>03</span>
              <div>
                <h2>Set up the analysis</h2>
              </div>
            </div>
            <label className="field">
              Vision-language model
              <select
                value={model}
                onChange={(event) => setModel(event.target.value)}
              >
                {models
                  ?.filter(
                    (m) =>
                      m.installed ||
                      m.execution_target === "vps" ||
                      m.id === model,
                  )
                  .map((m) => (
                    <option key={m.id} value={m.id} disabled={!m.installed}>
                      {m.name}
                      {m.execution_target === "vps" ? "" : " · Local"}
                      {!m.installed ? " · unavailable" : ""}
                    </option>
                  ))}
                {!models?.some((m) => m.installed) && (
                  <option value="" disabled>
                    No models available
                  </option>
                )}
              </select>
            </label>
            <p className="field-help">
              {selectedModel?.execution_target === "vps"
                ? `${selectedModel.availability_note || "Qwen runs on the VPS."} Your photo is sent to the VPS for its description; keep the SSH tunnel open.`
                : "Runs locally on your CPU. Larger models can take a few minutes; you can leave this page while the job finishes."}
            </p>
            <label className="field">
              Detector connection
              <select
                value={mode}
                onChange={(event) => setMode(event.target.value)}
              >
                <option value="demo">Demo workflow · detector not used</option>
                <option value="live" disabled={!health?.detector_configured}>
                  Trained YOLO endpoint
                  {!health?.detector_configured ? " · not configured" : ""}
                </option>
              </select>
            </label>
            <div className="notice">
              <ScanLine size={18} />
              <span>
                {mode === "demo"
                  ? "The VLM reads the actual image without YOLO. Segmentation is shown only when the trained detector returns an outline."
                  : "The photo will be sent to your configured YOLO endpoint. Its detections will be provided to your selected VLM."}
              </span>
            </div>
            <ErrorMessage message={error} />
            <button
              className="button primary full-width"
              disabled={
                busy ||
                !models?.find((m) => m.id === model)?.installed ||
                !!selectedModel?.busy ||
                (!file && !sampleId)
              }
              type="submit"
            >
              {busy ? (
                <LoaderCircle className="spin" size={18} />
              ) : (
                <ScanLine size={18} />
              )}{" "}
              {busy ? "Starting inspection…" : "Analyse this image"}
              <ArrowRight size={17} />
            </button>
            <p className="fine-print">
              Results are saved on this machine. Camera metadata is removed from
              the stored copy.
            </p>
          </section>
          <div className="workflow-summary">
            <h3>A traceable path to a report</h3>
            {[
              "Original image & field context",
              "Detector evidence, when connected",
              "Selected VLM observation",
              "Human review & saved report",
            ].map((step, index) => (
              <div key={step}>
                <span>{index + 1}</span>
                {step}
              </div>
            ))}
          </div>
        </aside>
      </form>
    </>
  );
}

function JobProgress({ id }: { id: string }) {
  const { data } = useApi<Job>(`/jobs/${id}`, 2500);
  return (
    <div className="notice processing" role="status">
      <LoaderCircle size={20} className="spin" />
      <div>
        <strong>{data?.message || "Preparing your inspection"}</strong>
        <p>
          The selected model is processing your photo. You can leave this page
          and return from inspection history.
        </p>
      </div>
    </div>
  );
}

export function InspectionDetail() {
  const { id } = useParams();
  const {
    data: item,
    error,
    loading,
    refresh,
  } = useApi<Inspection>(`/inspections/${id}`, 3000);
  const [showRegions, setShowRegions] = useState(true);
  const [reviewer, setReviewer] = useState("");
  const [reviewNotes, setReviewNotes] = useState("");
  const [saveError, setSaveError] = useState("");
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  async function saveReview(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setSaveError("");
    try {
      await api(`/inspections/${id}/review`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reviewer, notes: reviewNotes }),
      });
      setSaved(true);
      refresh();
    } catch (err) {
      setSaveError(
        err instanceof Error ? err.message : "Review could not be saved.",
      );
    } finally {
      setSaving(false);
    }
  }
  if (loading) return <Loading text="Opening the inspection record…" />;
  if (!item) return <ErrorMessage message={error} />;
  const processing = ["queued", "running"].includes(item.status);
  const regions = item.detection?.boxes ?? [];
  const outlines =
    item.mode === "live"
      ? regions.filter((region) => (region.polygon?.length ?? 0) >= 3)
      : [];
  const outlineCount = outlines.length;
  return (
    <>
      <Link className="back-link no-print" to="/inspections">
        <ArrowLeft size={16} />
        Inspection history
      </Link>
      <PageHeader
        eyebrow={`INSPECTION / ${item.id.slice(0, 8).toUpperCase()}`}
        title={item.title}
        description={`${item.location || "Location not recorded"} · ${date(item.created_at)}`}
        action={
          <div className="button-group no-print">
            <a
              className="button secondary"
              href={`/api/inspections/${item.id}/export`}
            >
              <Download size={16} />
              Export JSON
            </a>
            <button
              className="button primary"
              disabled={!item.report}
              onClick={() => window.print()}
            >
              <Printer size={16} />
              Print report
            </button>
          </div>
        }
      />
      <ErrorMessage message={error} />
      <ErrorMessage message={item.error || ""} />
      {processing && <JobProgress id={item.id} />}
      <div className="detail-grid">
        <div>
          <section className="card evidence-card">
            <div className="evidence-header">
              <h2>Visual evidence</h2>
              {outlineCount > 0 && (
                <button
                  className="button plain small-button no-print"
                  onClick={() => setShowRegions(!showRegions)}
                  aria-pressed={showRegions}
                >
                  <Eye size={16} />
                  {showRegions ? "Hide regions" : "Show regions"}
                </button>
              )}
            </div>
            <div className="evidence-image">
              <img
                src={item.image_url}
                alt={`Original surface photograph for ${item.title}`}
              />
              {showRegions && outlineCount > 0 && (
                <DetectionOverlay
                  regions={outlines}
                  width={item.dimensions.width}
                  height={item.dimensions.height}
                />
              )}
            </div>
            <div className="evidence-caption">
              <Tag tone={item.mode === "demo" ? "amber" : "green"}>
                {item.mode === "demo" ? "Detector not used" : "Live detector"}
              </Tag>
              <span>{item.sample_kind || "Uploaded photograph"}</span>
            </div>
            <div className="evidence-info">
              <ImageCredit credit={item.image_attribution} />
              <h3>
                {item.mode === "demo"
                  ? "Detector not used"
                  : item.detection?.source || "Evidence pending"}
              </h3>
              {item.mode === "live" && regions.length > 0 && (
                <p className="overlay-description">
                  {outlineCount > 0
                    ? `${outlineCount} segmentation outline${outlineCount === 1 ? "" : "s"} saved. ${showRegions ? "Blue lines follow the model’s predicted crack edges." : "Overlay hidden."}${outlineCount < regions.length ? " Some regions have no saved outline and are not drawn." : ""}`
                    : "No segmentation outlines were saved with this report. Run a new live inspection to request segmentation."}
                </p>
              )}
              <p>
                {item.mode === "demo"
                  ? "The trained detector was not used. No segmentation overlay is shown."
                  : item.detection?.note ||
                    "Your photo is saved. Analysis will appear here when the local runner finishes."}
              </p>
              {item.notes && (
                <>
                  <h3>Field notes</h3>
                  <p>{item.notes}</p>
                </>
              )}
            </div>
          </section>
          {item.vlm && (
            <section className="card form-card model-metadata">
              <SectionTitle
                title="Run details"
                note="The conditions behind this observation."
              />
              <dl>
                <div>
                  <dt>Model</dt>
                  <dd>{item.vlm.model_name}</dd>
                </div>
                <div>
                  <dt>Total inference time</dt>
                  <dd>{seconds(item.vlm.total_ms)}</dd>
                </div>
                <div>
                  <dt>Peak worker memory</dt>
                  <dd>
                    {item.vlm.peak_rss_mb
                      ? `${item.vlm.peak_rss_mb} MiB`
                      : "Not measured"}
                  </dd>
                </div>
                <div>
                  <dt>Runtime</dt>
                  <dd>{item.vlm.device}</dd>
                </div>
                <div>
                  <dt>Prompt</dt>
                  <dd>{item.vlm.prompt_version}</dd>
                </div>
              </dl>
              <details>
                <summary>Read the exact prompt</summary>
                <p className="raw-text">{item.vlm.prompt}</p>
              </details>
            </section>
          )}
        </div>
        <div>
          <section className="card report-card">
            <div className="report-heading">
              <span className="report-icon">
                <FileText size={23} />
              </span>
              <div>
                <h2>Visual inspection draft</h2>
                <p>Prepared by Imarah.tech</p>
              </div>
              <Tag tone={item.status === "complete" ? "green" : "amber"}>
                {statusLabel(item.status)}
              </Tag>
            </div>
            {!item.report ? (
              <EmptyState
                title={
                  processing
                    ? "Reading the surface…"
                    : "The report is unavailable."
                }
                description={
                  processing
                    ? "The model’s words will appear here when the analysis finishes."
                    : "See the error message, then start a new inspection after correcting the setup."
                }
              />
            ) : (
              <>
                <div className="report-section">
                  <span className="eyebrow">01 / DETECTOR EVIDENCE</span>
                  <p>{item.report.evidence_summary}</p>
                </div>
                <div className="report-section">
                  <div className="report-subheading">
                    <span className="eyebrow">02 / VLM OBSERVATION</span>
                    <Tag tone="amber">Unreviewed output</Tag>
                  </div>
                  <p className="raw-text">{item.report.observation}</p>
                  <p className="field-help">
                    These are the model’s actual words. It may overlook details
                    or describe things that are not present.
                  </p>
                </div>
                <div className="report-section">
                  <span className="eyebrow">03 / FOLLOW-UP CHECKLIST</span>
                  <ol className="next-steps">
                    {item.report.next_steps.map((step) => (
                      <li key={step}>{step}</li>
                    ))}
                  </ol>
                  <p className="field-help">
                    Standard application guidance, not generated by the model.
                  </p>
                </div>
                <div className="report-limitation">
                  {item.report.limitations}
                </div>
              </>
            )}
          </section>
          {item.report && (
            <section className="card form-card review-card">
              <SectionTitle
                title="A person completes the picture."
                note="Record your interpretation without overwriting the model’s original output."
              />
              {item.report.review.status === "reviewed" && (
                <div className="saved-review">
                  <Tag tone="green">Review recorded</Tag>
                  <h3>{item.report.review.reviewer}</h3>
                  <p className="raw-text">{item.report.review.notes}</p>
                  <small>
                    Self-entered reviewer identity · no structural certification
                  </small>
                </div>
              )}
              <form onSubmit={saveReview} className="no-print">
                <label className="field">
                  Reviewer name
                  <input
                    required
                    maxLength={80}
                    value={reviewer}
                    onChange={(event) => {
                      setReviewer(event.target.value);
                      setSaved(false);
                    }}
                    placeholder="Your name"
                  />
                </label>
                <label className="field">
                  Review notes
                  <textarea
                    required
                    rows={4}
                    maxLength={2000}
                    value={reviewNotes}
                    onChange={(event) => {
                      setReviewNotes(event.target.value);
                      setSaved(false);
                    }}
                    placeholder="What was accurate? What did the model miss? What should be checked next?"
                  />
                </label>
                <ErrorMessage message={saveError} />
                <button className="button primary" disabled={saving}>
                  {saving ? (
                    <LoaderCircle size={16} className="spin" />
                  ) : (
                    <CheckCircle2 size={16} />
                  )}
                  Save review
                </button>
                {saved && (
                  <span role="status" className="saved-message">
                    Review saved.
                  </span>
                )}
              </form>
            </section>
          )}
        </div>
      </div>
    </>
  );
}

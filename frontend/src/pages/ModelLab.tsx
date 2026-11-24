// Use: compare local and VPS model observations with their actual execution settings.
// Copyright (c) 2026 Imarah.tech. All rights reserved.
import { useState } from "react";
import {
  ArrowUpRight,
  Check,
  Cpu,
  Download,
  FlaskConical,
  Play,
  Timer,
} from "lucide-react";
import { api, date, seconds, useApi } from "../api";
import type { Benchmark, BenchmarkRow, Job, Model, Sample } from "../types";
import ImageCredit from "../components/ImageCredit";
import {
  EmptyState,
  ErrorMessage,
  Loading,
  PageHeader,
  SectionTitle,
  Tag,
} from "../components/UI";

function Progress({ jobId }: { jobId: string }) {
  const { data, error } = useApi<Job>(`/jobs/${jobId}`, 3000);
  return (
    <>
      <ErrorMessage message={error} />
      {data && (
        <div className="notice" role="status">
          <FlaskConical size={19} />
          <span>{data.message}</span>
          <Tag tone={data.status === "complete" ? "green" : "amber"}>
            {data.status}
          </Tag>
        </div>
      )}
    </>
  );
}
const median = (values: number[]) => {
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2
    ? sorted[middle]
    : (sorted[middle - 1] + sorted[middle]) / 2;
};

export default function ModelLab() {
  const { data: models, error: modelsError } = useApi<Model[]>(
    "/models",
    10000,
  );
  const { data: samples } = useApi<Sample[]>("/samples");
  const {
    data: benchmarks,
    error,
    loading,
  } = useApi<Benchmark[]>("/benchmarks", 5000);
  const [selected, setSelected] = useState(["smolvlm-256m", "smolvlm-500m"]);
  const [jobId, setJobId] = useState("");
  const [busy, setBusy] = useState(false);
  const [runError, setRunError] = useState("");
  const [selectedRun, setSelectedRun] = useState("");
  const [sampleId, setSampleId] = useState("");
  const [promptVersion, setPromptVersion] = useState("surface-observation-v1");
  const [imageSet, setImageSet] = useState("baseline");
  const selectedSamples =
    samples?.filter(
      (sample) =>
        imageSet === "all" ||
        (imageSet === "building"
          ? sample.benchmark_group === "building-photo"
          : sample.benchmark_group === "baseline"),
    ) || [];
  const comparisonIds = selected.filter(
    (id) => models?.find((m) => m.id === id)?.installed,
  );
  const unavailableSelected = selected.some(
    (id) => !models?.find((m) => m.id === id)?.installed,
  );
  const current =
    benchmarks?.find((b) => b.id === selectedRun) ||
    benchmarks?.find((b) => b.status === "running") ||
    benchmarks?.find((b) => b.status === "complete" && b.repeats >= 2) ||
    benchmarks?.[0];
  const rows = current?.rows.filter((row) => row.status === "complete") || [];
  const summary = [...new Set(current?.rows.map((row) => row.model_id))].map(
    (id) => {
      const modelRows = rows.filter((row) => row.model_id === id);
      const memories = modelRows.flatMap((row) =>
        row.peak_rss_mb ? [row.peak_rss_mb] : [],
      );
      return {
        id,
        name: models?.find((m) => m.id === id)?.name || id,
        completed: modelRows.length,
        attempted: current?.rows.filter((r) => r.model_id === id).length || 0,
        time: modelRows.length
          ? median(modelRows.map((row) => row.total_ms!))
          : null,
        memory: memories.length ? Math.max(...memories) : null,
        device:
          [...new Set(modelRows.map((row) => row.device).filter(Boolean))].join(
            " / ",
          ) || "No completed run",
      };
    },
  );
  const imageIds = [...new Set(current?.rows.map((row) => row.sample_id))];
  const selectedImage = imageIds.includes(sampleId) ? sampleId : imageIds[0];
  const comparison =
    current?.rows.filter((row) => row.sample_id === selectedImage) || [];
  const isRunning = benchmarks?.some((b) => b.status === "running");
  async function run() {
    setRunError("");
    setBusy(true);
    try {
      const job = await api<Job>("/benchmarks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model_ids: comparisonIds,
          sample_ids: selectedSamples.map((s) => s.id),
          repeats: 1,
          prompt_version: promptVersion,
        }),
      });
      setJobId(job.id);
      setSelectedRun(job.id);
    } catch (err) {
      setRunError(
        err instanceof Error ? err.message : "Could not start the benchmark.",
      );
    } finally {
      setBusy(false);
    }
  }
  function toggle(id: string) {
    setSelected((values) =>
      values.includes(id) ? values.filter((v) => v !== id) : [...values, id],
    );
  }
  return (
    <>
      <PageHeader
        eyebrow="RESEARCH / MODEL LAB"
        title="Let the evidence choose the model."
        description="The same images. The same prompt. Different perspectives."
        action={
          <Tag tone="green">
            <Cpu size={13} />
            Local & VPS experiments
          </Tag>
        }
      />
      <ErrorMessage message={error || modelsError} />
      <div className="lab-intro">
        <div>
          <FlaskConical size={24} />
          <h2>A small, honest starting point.</h2>
          <p>
            These experiments measure runtime and preserve what each model
            actually says. A few examples can reveal failure modes; they cannot
            establish inspection accuracy.
          </p>
        </div>
        <div className="lab-principles">
          <span>
            <Check size={15} />
            Recorded revisions & digests
          </span>
          <span>
            <Check size={15} />
            Identical image inputs
          </span>
          <span>
            <Check size={15} />
            Unedited model responses
          </span>
        </div>
      </div>
      <SectionTitle
        title="Our model bench"
        note="Choose up to three available models. Qwen 4B has separate Local and VPS options."
      />
      <div className="model-selector-grid">
        {models?.map((model) => (
          <div
            key={model.id}
            className={`model-card ${model.installed ? "installed" : ""}`}
          >
            <div className="model-card-top">
              <span
                className={`model-symbol ${model.id.includes("500") ? "dark" : ""}`}
              >
                {model.name[0]}
              </span>
              <Tag tone={model.installed ? "green" : ""}>
                {model.installed
                  ? model.execution_target === "vps"
                    ? "Available on VPS"
                    : "Available locally"
                  : model.runtime === "planned"
                    ? "Adapter planned"
                    : "Setup pending"}
              </Tag>
            </div>
            <h3>
              {model.name}
              {model.execution_target === "local" && model.runtime === "ollama"
                ? " · Local"
                : ""}
            </h3>
            <p>{model.role}</p>
            <small className="model-availability">
              {!model.installed
                ? model.availability_note || "Model adapter planned"
                : model.execution_target === "vps"
                  ? model.availability_note
                  : model.runtime === "transformers"
                    ? "Transformers · float32"
                    : model.quantization
                      ? `Ollama · ${model.quantization}`
                      : model.availability_note || "Model adapter planned"}
            </small>
            <div className="model-card-bottom">
              <span>
                {model.parameters} · {model.license}
              </span>
              {model.installed || model.execution_target === "vps" ? (
                <label className="model-checkbox">
                  <input
                    type="checkbox"
                    aria-label={`Compare ${model.name}`}
                    checked={selected.includes(model.id)}
                    disabled={
                      !selected.includes(model.id) &&
                      (!model.installed || selected.length >= 3)
                    }
                    onChange={() => toggle(model.id)}
                  />
                  Compare
                </label>
              ) : (
                <a
                  href={`https://huggingface.co/${model.repository}`}
                  target="_blank"
                  rel="noreferrer"
                  aria-label={`Read ${model.name} model card`}
                >
                  <ArrowUpRight size={17} />
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
      <div className="benchmark-controls">
        <div>
          <h3>Run the Phase 1 comparison</h3>
          <p>
            {selected.length} {selected.length === 1 ? "model" : "models"}{" "}
            selected · {selectedSamples.length}{" "}
            {selectedSamples.length === 1 ? "image" : "images"} per model ·
            140-token limit · one repetition · local models load fresh; VPS
            models may stay warm
          </p>
        </div>
        <div className="benchmark-actions">
          <select
            aria-label="Benchmark image set"
            value={imageSet}
            onChange={(event) => setImageSet(event.target.value)}
          >
            <option value="baseline">Original four examples</option>
            <option value="building">Building photograph · exploratory</option>
            <option value="all">All available examples</option>
          </select>
          <select
            aria-label="Benchmark prompt profile"
            value={promptVersion}
            onChange={(event) => setPromptVersion(event.target.value)}
          >
            <option value="surface-observation-v1">
              Surface observation prompt
            </option>
            <option value="brief-caption-v2">Brief caption prompt</option>
          </select>
          <button
            className="button primary"
            disabled={
              busy ||
              unavailableSelected ||
              !!isRunning ||
              !comparisonIds.length ||
              !selectedSamples.length
            }
            onClick={() => void run()}
          >
            <Play size={16} />
            {busy
              ? "Starting…"
              : isRunning
                ? "Benchmark in progress"
                : "Run comparison"}
          </button>
        </div>
      </div>
      <ErrorMessage message={runError} />
      {unavailableSelected && models && (
        <p className="field-help">
          A selected model is unavailable. Reconnect it or deselect it before
          running the comparison.
        </p>
      )}
      {jobId && <Progress jobId={jobId} />}
      {loading ? (
        <Loading text="Reading the experiment notebook…" />
      ) : !current ? (
        <section className="card">
          <EmptyState
            title="The notebook is ready for its first run."
            description="Select the installed models and run the comparison. Measured results will appear here as each image finishes."
          />
        </section>
      ) : (
        <>
          <div className="results-heading">
            <SectionTitle
              title="Measured results"
              note={`${date(current.created_at)} · ${current.rows.length} recorded runs · ${current.status}`}
            />
            <div className="button-group">
              <select
                aria-label="Benchmark run"
                value={current.id}
                onChange={(event) => setSelectedRun(event.target.value)}
              >
                {benchmarks?.map((b) => (
                  <option key={b.id} value={b.id}>
                    {date(b.created_at)} ·{" "}
                    {[...new Set(b.rows.map((row) => row.model_id))].join(
                      " + ",
                    )}{" "}
                    ·{" "}
                    {b.prompt_version === "brief-caption-v2"
                      ? "Brief caption"
                      : "Surface observation"}{" "}
                    · {b.repeats}× · {b.status}
                  </option>
                ))}
              </select>
              <a
                className="button secondary"
                href={`/api/benchmarks/${current.id}/export`}
              >
                <Download size={16} />
                Raw JSON
              </a>
            </div>
          </div>
          <div className="benchmark-results-grid">
            <section className="card">
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Model</th>
                      <th>Median time</th>
                      <th>Peak RAM</th>
                      <th>Finished</th>
                    </tr>
                  </thead>
                  <tbody>
                    {summary.map((s) => (
                      <tr key={s.id}>
                        <td>
                          <strong>{s.name}</strong>
                          <small>{s.device}</small>
                        </td>
                        <td className="number-cell">
                          {s.time ? seconds(s.time) : "—"}
                        </td>
                        <td>
                          {s.memory
                            ? `${(s.memory / 1024).toFixed(2)} GiB`
                            : "—"}
                        </td>
                        <td>
                          {s.completed} / {s.attempted}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="table-note">
                Time includes model loading and generation; VPS rows also
                include network transfer and may use a warm model. RAM is the
                worker process’s peak resident memory for Transformers. Ollama
                runs in a separate server, whose peak is not reported; a dash
                means unavailable. Measurements vary with background activity.
              </div>
            </section>
            <section className="card timing-chart">
              <div className="chart-title">
                <Timer size={18} />
                <h3>Time to an observation</h3>
              </div>
              <p>Median seconds · lower is quicker</p>
              {summary.map((s) => (
                <div className="timing-row" key={s.id}>
                  <div>
                    <span>{s.name}</span>
                    <strong>{s.time ? seconds(s.time) : "—"}</strong>
                  </div>
                  <div className="bar-track">
                    <span
                      style={{
                        width: `${s.time ? (s.time / Math.max(...summary.map((v) => v.time || 1))) * 100 : 0}%`,
                      }}
                    />
                  </div>
                </div>
              ))}
              <small>Speed alone does not decide report quality.</small>
            </section>
          </div>
          <section className="card observation-comparison">
            <div className="comparison-heading">
              <SectionTitle
                title="Read them side by side"
                note="Compare the actual words before picking a favourite."
              />
              <select
                aria-label="Comparison image"
                value={selectedImage || ""}
                onChange={(event) => setSampleId(event.target.value)}
              >
                {imageIds.map((id) => (
                  <option key={id} value={id}>
                    {current.rows.find((r) => r.sample_id === id)?.sample_name}
                  </option>
                ))}
              </select>
            </div>
            <div className="comparison-body">
              <div className="comparison-photo">
                {samples?.find((s) => s.id === selectedImage) && (
                  <img
                    src={samples.find((s) => s.id === selectedImage)!.url}
                    alt={samples.find((s) => s.id === selectedImage)!.name}
                  />
                )}
                <Tag>{comparison[0]?.sample_kind}</Tag>
                <ImageCredit
                  credit={
                    comparison[0]?.image_attribution ||
                    samples?.find((sample) => sample.id === selectedImage)
                      ?.attribution
                  }
                />
              </div>
              <div className="comparison-outputs">
                {comparison.map((row) => (
                  <Observation key={row.id} row={row} models={models || []} />
                ))}
              </div>
            </div>
            <details className="method-details">
              <summary>Experiment conditions and exact prompt</summary>
              <p>{current.conditions}</p>
              <p className="raw-text">{current.prompt}</p>
              <p>
                The original set uses two CrackForest road photographs and two
                synthetic controls. The separate building example is a public
                interior-wall photograph. Check the image IDs in this run;
                expert quality scoring and a building-specific holdout set are
                still pending.
              </p>
            </details>
          </section>
        </>
      )}
    </>
  );
}

function Observation({ row, models }: { row: BenchmarkRow; models: Model[] }) {
  return (
    <article className="observation">
      <div>
        <h3>
          {models.find((m) => m.id === row.model_id)?.name || row.model_id}
        </h3>
        <Tag tone={row.status === "complete" ? "green" : "red"}>
          {row.total_ms ? seconds(row.total_ms) : row.status}
        </Tag>
      </div>
      <p className="raw-text">{row.text || row.error}</p>
      <small>
        {row.output_tokens ? `${row.output_tokens} output tokens · ` : ""}
        {row.output_tokens && row.output_tokens >= (row.max_new_tokens || 140)
          ? "Token limit reached · "
          : ""}
        {row.status === "complete"
          ? "Raw output · human quality review pending"
          : "No model observation was produced for this run"}
        {row.repeat > 1 ? ` · repetition ${row.repeat}` : ""}
      </small>
    </article>
  );
}

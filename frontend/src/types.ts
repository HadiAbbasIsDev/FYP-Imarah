// Use: explain the data that travels between the interface and Python API.
// Copyright (c) 2026 Imarah.tech. All rights reserved.
export type Model = {
  id: string;
  name: string;
  repository: string;
  revision?: string;
  runtime: string;
  execution_target: "local" | "vps";
  busy?: boolean;
  remote_digest?: string;
  parameters: string;
  role: string;
  license: string;
  installed: boolean;
  availability_note?: string;
  quantization?: string;
  local_digest?: string;
};
export type ImageAttribution = {
  author: string;
  title: string;
  source_url: string;
  license: string;
  license_url?: string;
  changes: string;
};
export type Sample = {
  id: string;
  name: string;
  file: string;
  kind: string;
  description: string;
  url: string;
  benchmark_group?: string;
  attribution?: ImageAttribution;
};
export type Box = {
  label: string;
  confidence: number | null;
  box: number[];
  // Optional for old reports and detectors that only return rectangles.
  polygon?: [number, number][];
};
export type VLM = {
  text: string;
  model_id: string;
  model_name: string;
  total_ms: number;
  load_ms: number;
  generation_ms: number;
  output_tokens: number;
  max_new_tokens: number;
  peak_rss_mb: number | null;
  device: string;
  prompt: string;
  prompt_version: string;
  revision: string;
  runtime_version: string;
  runtime?: string;
  execution_target?: "local" | "vps";
  transport?: string;
  server_api_total_ms?: number;
  server_total_ms?: number;
  loaded_model_bytes?: number | null;
  gpu_model_bytes?: number | null;
  cache_policy?: string;
  model_digest?: string;
  quantization?: string;
  done_reason?: string;
  prompt_eval_ms?: number;
  memory_note?: string;
  timeout_seconds?: number;
};
export type Inspection = {
  id: string;
  created_at: string;
  title: string;
  location: string;
  notes: string;
  mode: string;
  model_id: string;
  sample_id: string | null;
  sample_kind: string | null;
  image_attribution?: ImageAttribution | null;
  status: string;
  dimensions: { width: number; height: number };
  image_url: string;
  error?: string;
  detection: {
    status: string;
    source: string;
    boxes: Box[];
    note: string;
    latency_ms: number | null;
  } | null;
  vlm: VLM | null;
  report: {
    title: string;
    evidence_summary: string;
    observation: string;
    observation_source: string;
    next_steps: string[];
    limitations: string;
    review: {
      status: string;
      reviewer: string;
      notes: string;
      reviewed_at?: string;
    };
  } | null;
};
export type BenchmarkRow = Partial<VLM> & {
  id: string;
  model_id: string;
  sample_id: string;
  sample_name: string;
  sample_kind: string;
  status: string;
  error?: string;
  image_sha256: string;
  image_attribution?: ImageAttribution | null;
  repeat: number;
};
export type Benchmark = {
  id: string;
  created_at: string;
  status: string;
  purpose: string;
  prompt: string;
  prompt_version: string;
  conditions: string;
  rows: BenchmarkRow[];
  repeats: number;
};
export type Job = { id: string; kind: string; status: string; message: string };
export type Health = {
  status: string;
  version: string;
  phase: string;
  detector_configured: boolean;
  pending_jobs: number;
};
export type Worker = {
  id: string;
  name: string;
  role: string;
  attendance: string;
  check_in: string;
  helmet: boolean | null;
  vest: boolean | null;
  task: string;
  progress: number;
  payroll: number;
  insurance: string;
};
export type Demo = {
  label: string;
  site: {
    name: string;
    location: string;
    stage: string;
    progress: number;
    contractor: string;
    budget_recorded: number;
    insurance: string;
  };
  workers: Worker[];
  materials: { name: string; unit: string; received: number; used: number }[];
  sensors: {
    name: string;
    value: number;
    unit: string;
    trend: number[];
    note: string;
    icon: string;
  }[];
  areas: {
    name: string;
    buildings: number;
    coverage: number;
    green_space: number;
    note: string;
  }[];
  roadmap: {
    number: string;
    name: string;
    period: string;
    status: string;
    owner: string;
    items: string[];
  }[];
};

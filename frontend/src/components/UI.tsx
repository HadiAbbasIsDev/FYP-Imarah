// Use: a few shared interface pieces, keeping pages consistent and easy to read.
// Copyright (c) 2026 Imarah.tech. All rights reserved.
import type { ReactNode } from "react";
import { AlertCircle, ArrowUpRight, LoaderCircle } from "lucide-react";
import { Link } from "react-router-dom";

export function Tag({
  children,
  tone = "",
}: {
  children: ReactNode;
  tone?: string;
}) {
  return <span className={`tag ${tone}`}>{children}</span>;
}
export function PageHeader({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="page-header">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {action}
    </div>
  );
}
export function ErrorMessage({ message }: { message: string }) {
  return message ? (
    <div className="notice error" role="alert">
      <AlertCircle size={18} />
      <span>{message}</span>
    </div>
  ) : null;
}
export function Loading({
  text = "Opening your workspace…",
}: {
  text?: string;
}) {
  return (
    <div className="loading" role="status">
      <LoaderCircle size={20} className="spin" />
      {text}
    </div>
  );
}
export function PreviewNotice({ children }: { children?: ReactNode }) {
  return (
    <div className="preview-notice">
      <Tag tone="amber">Concept preview</Tag>
      <span>
        {children ||
          "This page uses fictional sample data to demonstrate a future module."}
      </span>
    </div>
  );
}
export function SectionTitle({
  title,
  note,
  to,
  linkText = "View all",
}: {
  title: string;
  note?: string;
  to?: string;
  linkText?: string;
}) {
  return (
    <div className="section-title">
      <div>
        <h2>{title}</h2>
        {note && <p>{note}</p>}
      </div>
      {to && (
        <Link className="text-link" to={to}>
          {linkText}
          <ArrowUpRight size={16} />
        </Link>
      )}
    </div>
  );
}
export function Sparkline({
  values,
  color = "#34775f",
  filled = false,
}: {
  values: number[];
  color?: string;
  filled?: boolean;
}) {
  const min = Math.min(...values) - 1,
    range = Math.max(...values) - min + 1;
  const points = values
    .map(
      (v, i) =>
        `${(i * 240) / (values.length - 1)},${66 - ((v - min) / range) * 55}`,
    )
    .join(" ");
  return (
    <svg viewBox="0 0 240 76" className="sparkline" aria-hidden="true">
      {filled && (
        <polygon points={`0,76 ${points} 240,76`} fill={color} opacity="0.08" />
      )}
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="2.5"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </svg>
  );
}
export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="empty-state">
      <div className="empty-mark">⌑</div>
      <h3>{title}</h3>
      <p>{description}</p>
      {action}
    </div>
  );
}

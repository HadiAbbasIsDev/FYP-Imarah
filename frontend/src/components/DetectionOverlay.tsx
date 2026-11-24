// Use: draw only the model's saved segmentation outlines over the photograph.
// Copyright (c) 2026 Imarah.tech. All rights reserved.
import type { Box } from "../types";

type Props = {
  regions: Box[];
  width: number;
  height: number;
};

export default function DetectionOverlay({ regions, width, height }: Props) {
  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      aria-label="Predicted crack outlines"
      role="img"
    >
      {regions.map((region, index) => {
        const polygon = region.polygon;
        if (!polygon || polygon.length < 3) return null;
        const label = `${region.label} · ${Math.round((region.confidence ?? 0) * 100)}%`;
        return (
          <g key={index}>
            <title>{`Region ${index + 1}: ${label}`}</title>
            <polygon
              points={polygon.map(([x, y]) => `${x},${y}`).join(" ")}
              fill="#2455ff"
              fillOpacity="0.14"
              stroke="#153dff"
              strokeWidth="1.5"
              strokeLinejoin="round"
              vectorEffect="non-scaling-stroke"
            />
          </g>
        );
      })}
    </svg>
  );
}

// Use: an original architectural line drawing for the Imarah dashboard.
// Copyright (c) 2026 Imarah.tech. All rights reserved.
export default function CityDrawing() {
  const buildings = [
    { x: 145, y: 140, w: 68, d: 35, h: 104 },
    { x: 220, y: 183, w: 73, d: 39, h: 165 },
    { x: 302, y: 230, w: 75, d: 40, h: 115 },
    { x: 67, y: 185, w: 64, d: 32, h: 64 },
    { x: 145, y: 230, w: 62, d: 34, h: 126 },
    { x: 220, y: 273, w: 65, d: 35, h: 82 },
  ];
  return (
    <svg
      className="city-drawing"
      viewBox="0 0 440 320"
      fill="none"
      aria-hidden="true"
    >
      <g stroke="#8cbaa5" opacity=".16">
        {Array.from({ length: 11 }, (_, i) => (
          <path
            key={i}
            d={`M ${-70 + i * 42} 144 l 340 196 M ${40 + i * 42} 40 l -340 196`}
          />
        ))}
      </g>
      <g stroke="#a7c9b9" strokeWidth="1.1" strokeLinejoin="round">
        {buildings.map((b, i) => (
          <g key={i}>
            <path
              d={`M${b.x},${b.y} l${b.w},${b.w * 0.55} l${b.d},${-b.d * 0.55} v${-b.h} l${-b.w},${-b.w * 0.55} l${-b.d},${b.d * 0.55} Z`}
              fill={i === 4 ? "#396451" : "#224d40"}
            />
            <path
              d={`M${b.x},${b.y - b.h} l${b.w},${b.w * 0.55} l${b.d},${-b.d * 0.55} M${b.x + b.w},${b.y + b.w * 0.55} v${-b.h}`}
            />
            {Array.from({ length: Math.floor(b.h / 19) }, (_, j) => (
              <path
                key={j}
                d={`M${b.x + 9},${b.y - b.h + 20 + j * 16} l${b.w - 18},${(b.w - 18) * 0.55}`}
                opacity=".65"
              />
            ))}
            {[0.3, 0.6].map((v, j) => (
              <path
                key={j}
                d={`M${b.x + b.w * v},${b.y - b.h + b.w * v * 0.55 + 10} v${b.h - 18}`}
                opacity=".4"
              />
            ))}
          </g>
        ))}
      </g>
      <path
        d="M57 233l133 77 190-110"
        stroke="#d0dbb7"
        opacity=".5"
        strokeDasharray="3 5"
      />
      <circle cx="172" cy="153" r="7" fill="#d5dfbd" />
      <circle cx="172" cy="153" r="17" stroke="#d5dfbd" opacity=".35" />
      <path d="M172 136v-27l-53-30H75" stroke="#d5dfbd" opacity=".8" />
      <text x="52" y="70" fill="#d5dfbd" fontSize="10" letterSpacing="2">
        SURFACE INSIGHT
      </text>
      <g fill="#c4d3b6">
        <circle cx="95" cy="229" r="3" />
        <circle cx="343" cy="276" r="3" />
      </g>
    </svg>
  );
}

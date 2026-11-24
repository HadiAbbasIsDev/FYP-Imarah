// Use: keep a public photograph's author and licence visible beside the image and in reports.
// Copyright (c) 2026 Imarah.tech. All rights reserved.
import type { ImageAttribution } from "../types";

export default function ImageCredit({
  credit,
}: {
  credit?: ImageAttribution | null;
}) {
  if (!credit) return null;
  return (
    <p className="image-credit">
      Photo: {credit.author} ·{" "}
      <a href={credit.source_url} target="_blank" rel="noreferrer">
        {credit.title}
      </a>
      {" · "}
      {credit.license_url ? (
        <a href={credit.license_url} target="_blank" rel="noreferrer">
          {credit.license}
        </a>
      ) : (
        credit.license
      )}
      <span>{credit.changes}</span>
    </p>
  );
}

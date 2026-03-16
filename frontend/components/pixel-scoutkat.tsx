"use client";

import { useMemo, useState } from "react";

const pixels = [
  [6, 2], [7, 2], [8, 2],
  [5, 3], [6, 3], [7, 3], [8, 3], [9, 3],
  [5, 4], [6, 4], [7, 4], [8, 4], [9, 4],
  [4, 5], [5, 5], [6, 5], [7, 5], [8, 5], [9, 5], [10, 5],
  [4, 6], [5, 6], [6, 6], [7, 6], [8, 6], [9, 6], [10, 6],
  [4, 7], [5, 7], [6, 7], [7, 7], [8, 7], [9, 7], [10, 7], [11, 7],
  [5, 8], [6, 8], [7, 8], [8, 8], [9, 8], [10, 8], [11, 8],
  [6, 9], [7, 9], [8, 9], [9, 9], [10, 9], [11, 9],
  [7, 10], [8, 10], [9, 10], [10, 10], [11, 10],
  [7, 11], [8, 11], [9, 11], [10, 11],
  [8, 12], [9, 12], [10, 12],
  [8, 13], [9, 13],
  [8, 14], [9, 14],
  [7, 15], [9, 15],
  [7, 16], [10, 16],
  [7, 17], [10, 17],
  [6, 6], [10, 4], [11, 4], [12, 5], [12, 6], [12, 7],
  [3, 6], [3, 7], [3, 8],
  [12, 8], [13, 8], [13, 9],
  [11, 11], [12, 12], [13, 13], [14, 14],
  [5, 11], [4, 12], [4, 13], [3, 14],
];

export function PixelScoutkat() {
  const [hovered, setHovered] = useState(false);
  const renderedPixels = useMemo(
    () =>
      pixels.map(([x, y], index) => ({
        id: `${x}-${y}-${index}`,
        x,
        y,
        opacity: 0.5 + ((x * 7 + y * 11 + index) % 5) * 0.1,
      })),
    [],
  );

  return (
    <div
      className="relative flex min-h-[420px] items-center justify-center overflow-hidden border-t border-white/12 md:min-h-[520px] lg:border-l lg:border-t-0"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_20%,rgba(255,255,255,0.12),transparent_32%),radial-gradient(circle_at_80%_70%,rgba(255,255,255,0.08),transparent_22%)]" />
      <div
        className={`absolute inset-12 border transition-all duration-500 ${
          hovered ? "border-white/20" : "border-transparent"
        }`}
      />

      <div
        className={`relative transition-all duration-500 ${
          hovered ? "translate-y-0 scale-[0.78]" : "translate-y-4 scale-[1.1]"
        }`}
        style={{
          width: 360,
          height: 360,
        }}
      >
        {renderedPixels.map((pixel) => (
          <span
            key={pixel.id}
            className={`absolute block h-[8px] w-[8px] rounded-full bg-white transition-all duration-500 ${
              hovered ? "shadow-[0_0_18px_rgba(255,255,255,0.22)]" : ""
            }`}
            style={{
              left: `${pixel.x * 18}px`,
              top: `${pixel.y * 16}px`,
              opacity: hovered ? Math.min(1, pixel.opacity + 0.12) : pixel.opacity,
              transform: hovered
                ? `translate(${(pixel.x % 2 === 0 ? 1 : -1) * 2}px, ${(pixel.y % 2 === 0 ? -1 : 1) * 2}px)`
                : `translate(${(pixel.x % 3) - 1}px, ${((pixel.y + 1) % 3) - 1}px)`,
            }}
          />
        ))}
      </div>

      <div className="absolute bottom-6 left-6 right-6 flex items-center justify-between text-[10px] uppercase tracking-[0.28em] text-white/36">
        <span>Scoutkat visual sentinel</span>
        <span>{hovered ? "Compressed / attentive" : "Scanning / idle"}</span>
      </div>
    </div>
  );
}

// Simple SVG "map" — no Maps API key needed. Pins are placed from lat/lng
// relative to the first recommendation (or a default River North center).
import type { ReactNode } from "react";
import type { Rec } from "./types";

type MapProps = {
  center?: Pick<Rec, "lat" | "lng">;
  highlight: string | null;
  children?: ReactNode;
};

type PinProps = {
  place: Rec;
  active: boolean;
  all: Rec[];
};

function project(place: Rec, all: Rec[]) {
  // Fit pins into a 0..100 viewBox with a little padding.
  const lats = all.map((p) => p.lat);
  const lngs = all.map((p) => p.lng);
  const minLat = Math.min(...lats) - 0.002;
  const maxLat = Math.max(...lats) + 0.002;
  const minLng = Math.min(...lngs) - 0.002;
  const maxLng = Math.max(...lngs) + 0.002;
  const x = ((place.lng - minLng) / (maxLng - minLng || 1)) * 100;
  // Flip Y so north is up.
  const y = (1 - (place.lat - minLat) / (maxLat - minLat || 1)) * 100;
  return { x, y };
}

export function Pin({ place, active, all }: PinProps) {
  const { x, y } = project(place, all.length ? all : [place]);
  return (
    <g className={active ? "pin pin-active" : "pin"}>
      <circle cx={x} cy={y} r={active ? 3.2 : 2.4} />
      <text x={x} y={y - 4} textAnchor="middle" className="pin-label">
        {place.name.split(" ")[0]}
      </text>
    </g>
  );
}

export function Map({ center, highlight, children }: MapProps) {
  // children are Pins; we also accept highlight for a soft glow ring.
  return (
    <div className="map-panel" data-center={center ? `${center.lat},${center.lng}` : ""}>
      <svg viewBox="0 0 100 100" role="img" aria-label="Map of recommendations">
        <defs>
          <linearGradient id="mapGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#d9e8df" />
            <stop offset="100%" stopColor="#c5d4e8" />
          </linearGradient>
        </defs>
        <rect width="100" height="100" fill="url(#mapGrad)" />
        {/* Fake streets for atmosphere */}
        <path d="M0 30 H100 M0 55 H100 M0 78 H100 M25 0 V100 M55 0 V100 M80 0 V100"
          stroke="rgba(40,55,70,0.12)" strokeWidth="0.6" fill="none" />
        {children}
        {highlight ? null : null}
      </svg>
      <p className="map-caption">Hover a card to highlight its pin</p>
    </div>
  );
}

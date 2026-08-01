// The results surface: each recommendation is a card showing the LLM's reason
// AND the grounded evidence (so the user sees WHY and can trust it), synced to
// a map. Filters and follow-up prompts let the user refine — every refinement
// is a new grounded query, never an LLM re-imagining the same places.
import { useState } from "react";
import { Map, Pin } from "./Map";

export function Results({ recs, onFollowUp }: ResultsProps) {
  const [active, setActive] = useState<string | null>(null);
  return (
    <div className="grid grid-cols-[1fr_1.2fr] gap-4">
      <ul>
        {recs.map((r) => (
          <li key={r.place_id} onMouseEnter={() => setActive(r.place_id)}>
            <h3>{r.name}</h3>
            <p className="reason">{r.reason}</p>
            {/* the grounded evidence, shown so the user can trust the pick */}
            <span className="evidence">★{r.rating} · {r.distance_m}m · {r.open_now ? "Open" : "Closed"}</span>
          </li>
        ))}
      </ul>
      <Map center={recs[0]} highlight={active}>
        {recs.map((r) => <Pin key={r.place_id} place={r} active={r.place_id === active} />)}
      </Map>
      <div className="followups">
        {["More upscale", "Walkable", "Open now"].map((f) => (
          <button key={f} onClick={() => onFollowUp(f)}>{f}</button>
        ))}
      </div>
    </div>
  );
}

// The results surface: each recommendation is a card showing the LLM's reason
// AND the grounded evidence (so the user sees WHY and can trust it), synced to
// a map. Filters and follow-up prompts let the user refine — every refinement
// is a new grounded query, never an LLM re-imagining the same places.
import { useMemo, useState } from "react";
import { Map, Pin } from "./Map";
import type { Rec } from "./types";

export type ResultsProps = {
  recs: Rec[];
  onFollowUp: (label: string) => void;
  onClickRec?: (placeId: string) => void;
  onSaveRec?: (placeId: string) => void;
};

export function Results({ recs, onFollowUp, onClickRec, onSaveRec }: ResultsProps) {
  const [active, setActive] = useState<string | null>(null);
  // Client-side filters over already-grounded results (never invent new places).
  const [openOnly, setOpenOnly] = useState(false);
  const [walkableOnly, setWalkableOnly] = useState(false);

  const visible = useMemo(() => {
    return recs.filter((r) => {
      if (openOnly && !r.open_now) return false;
      if (walkableOnly && r.distance_m > 800) return false;
      return true;
    });
  }, [recs, openOnly, walkableOnly]);

  if (!recs.length) {
    return (
      <div className="empty">
        <h2>No grounded matches</h2>
        <p>We looked nearby and found nothing real to recommend — better empty than inventing a place.</p>
      </div>
    );
  }

  return (
    <div className="results">
      <div className="filters">
        <label>
          <input
            type="checkbox"
            checked={openOnly}
            onChange={(e) => setOpenOnly(e.target.checked)}
          />
          Open now
        </label>
        <label>
          <input
            type="checkbox"
            checked={walkableOnly}
            onChange={(e) => setWalkableOnly(e.target.checked)}
          />
          Walkable (&lt; 800m)
        </label>
      </div>

      <div className="results-grid">
        <ul className="rec-list">
          {visible.map((r) => (
            <li
              key={r.place_id}
              className={r.place_id === active ? "rec active" : "rec"}
              onMouseEnter={() => setActive(r.place_id)}
              onClick={() => onClickRec?.(r.place_id)}
            >
              <div className="rec-top">
                <h3>{r.name}</h3>
                <button
                  type="button"
                  className="save-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    onSaveRec?.(r.place_id);
                  }}
                >
                  Save
                </button>
              </div>
              <p className="reason">{r.reason}</p>
              {/* the grounded evidence, shown so the user can trust the pick */}
              <span className="evidence">
                ★{r.rating} · {r.distance_m}m · {r.open_now ? "Open" : "Closed"} ·{" "}
                {"$".repeat(Math.max(1, r.price_level || 1))}
              </span>
            </li>
          ))}
        </ul>

        <Map center={visible[0] || recs[0]} highlight={active}>
          {visible.map((r) => (
            <Pin
              key={r.place_id}
              place={r}
              active={r.place_id === active}
              all={visible}
            />
          ))}
        </Map>
      </div>

      <div className="followups">
        <span className="followups-label">Refine (new grounded search):</span>
        {["More upscale", "Walkable", "Open now"].map((f) => (
          <button key={f} type="button" onClick={() => onFollowUp(f)}>
            {f}
          </button>
        ))}
      </div>
    </div>
  );
}

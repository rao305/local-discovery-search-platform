// Search shell: type a question → hit /recommend → show Results.
// Follow-ups append constraints and re-query grounding (trust rule stays intact).
import { useState } from "react";
import { Results } from "./Results";
import type { RecommendResponse } from "./types";

const DEFAULT_LAT = 41.892;
const DEFAULT_LNG = -87.634;

export function App() {
  const [q, setQ] = useState("upscale italian near river north");
  const [lat] = useState(DEFAULT_LAT);
  const [lng] = useState(DEFAULT_LNG);
  const [data, setData] = useState<RecommendResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runSearch(question: string) {
    setLoading(true);
    setError(null);
    try {
      const url = `/recommend?q=${encodeURIComponent(question)}&lat=${lat}&lng=${lng}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`API ${res.status}`);
      const json = (await res.json()) as RecommendResponse;
      setData(json);
      setQ(question);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }

  function onFollowUp(label: string) {
    // Record the product signal, then re-run with the constraint baked into q.
    fetch(`/events/refine?label=${encodeURIComponent(label)}`, { method: "POST" }).catch(() => {});
    const next = `${q} ${label.toLowerCase()}`;
    runSearch(next);
  }

  function onClickRec(placeId: string) {
    fetch(`/events/click?place_id=${encodeURIComponent(placeId)}`, { method: "POST" }).catch(() => {});
  }

  function onSaveRec(placeId: string) {
    fetch(`/events/save?place_id=${encodeURIComponent(placeId)}`, { method: "POST" }).catch(() => {});
  }

  return (
    <div className="page">
      <header className="hero">
        <p className="brand">Local Discovery</p>
        <h1>Ask where to go. Only real places answer.</h1>
        <p className="lede">
          Grounded recommendations with cited reasons — never invented ratings or hours.
        </p>
        <form
          className="search"
          onSubmit={(e) => {
            e.preventDefault();
            runSearch(q);
          }}
        >
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder='Try "upscale italian near river north"'
            aria-label="Search question"
          />
          <button type="submit" disabled={loading}>
            {loading ? "Searching…" : "Search"}
          </button>
        </form>
        {error && <p className="error">Could not reach the API ({error}). Is uvicorn running?</p>}
        {data?.message && !data.recommendations.length && (
          <p className="hint">{data.message}</p>
        )}
      </header>

      {data && (
        <Results
          recs={data.recommendations}
          onFollowUp={onFollowUp}
          onClickRec={onClickRec}
          onSaveRec={onSaveRec}
        />
      )}
    </div>
  );
}

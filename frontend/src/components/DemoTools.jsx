import { useEffect, useState } from 'react';
import './DemoTools.css';

const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '');

async function responseError(response) {
  try {
    const body = await response.json();
    if (body?.detail) return String(body.detail);
  } catch {
    return `Request failed with HTTP ${response.status}.`;
  }
  return `Request failed with HTTP ${response.status}.`;
}

function GridStats() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;

    async function refreshStats() {
      try {
        const response = await fetch(`${API_URL}/api/grid/stats`);
        if (!response.ok) throw new Error(await responseError(response));

        const data = await response.json();
        if (active) {
          setStats(data);
          setError('');
        }
      } catch (refreshError) {
        if (active) {
          setError(refreshError.message || 'Unable to load grid statistics.');
        }
      }
    }

    refreshStats();
    const intervalId = window.setInterval(refreshStats, 2000);
    return () => {
      active = false;
      window.clearInterval(intervalId);
    };
  }, []);

  const hitRate = Number.isFinite(stats?.hit_rate)
    ? `${(stats.hit_rate * 100).toFixed(1)}%`
    : '—';

  return (
    <section className="demo-card" id="system" aria-labelledby="grid-stats-title">
      <div className="demo-card-heading">
        <div>
          <p className="demo-eyebrow">Live from the backend</p>
          <h2 id="grid-stats-title">Grid statistics</h2>
        </div>
        <span className="demo-refresh">Refreshes every 2 seconds</span>
      </div>
      {error && <p className="demo-error" role="alert">{error}</p>}
      <div className="demo-metrics" aria-live="polite">
        <div><span>Cache hits</span><strong>{stats?.cache_hits ?? '—'}</strong></div>
        <div><span>Cache misses</span><strong>{stats?.cache_misses ?? '—'}</strong></div>
        <div><span>Hit rate</span><strong>{hitRate}</strong></div>
      </div>
      <h3>Entries by node</h3>
      {stats?.nodes?.length
        ? (
          <ul className="demo-node-list">
            {stats.nodes.map((node) => (
              <li key={node.node_id}>
                <span>Node {node.node_id + 1}</span>
                <span>{node.entries} / {node.capacity} entries</span>
              </li>
            ))}
          </ul>
        )
        : <p className="demo-muted">{stats ? 'No nodes are configured.' : 'Loading node statistics…'}</p>}
    </section>
  );
}

function PdfDateLookup() {
  const [file, setFile] = useState(null);
  const [day, setDay] = useState('');
  const [month, setMonth] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file || isLoading) return;

    setIsLoading(true);
    setError('');
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    if (day.trim()) formData.append('day', day.trim());
    if (month.trim()) formData.append('month', month.trim());

    try {
      const response = await fetch(`${API_URL}/api/pdf/today`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error(await responseError(response));

      const data = await response.json();
      if (!data || !Array.isArray(data.matches)) {
        throw new Error('The PDF endpoint returned an unexpected response.');
      }
      setResult(data);
    } catch (uploadError) {
      setError(uploadError.message || 'Unable to process the PDF.');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="demo-card" aria-labelledby="pdf-lookup-title">
      <div className="demo-card-heading">
        <div>
          <p className="demo-eyebrow">PDF pipeline</p>
          <h2 id="pdf-lookup-title">Find a date in a PDF</h2>
        </div>
      </div>
      <p className="demo-muted">Choose a PDF and optionally enter a day and month. Leave both blank to use today's date.</p>
      <form className="pdf-form" onSubmit={handleSubmit}>
        <label className="pdf-file-label">
          PDF file
          <input
            type="file"
            accept=".pdf,application/pdf"
            onChange={(event) => setFile(event.target.files?.[0] || null)}
            required
          />
        </label>
        <div className="pdf-date-fields">
          <label>
            Day
            <input type="number" min="1" max="31" value={day} onChange={(event) => setDay(event.target.value)} />
          </label>
          <label>
            Month
            <input type="text" value={month} onChange={(event) => setMonth(event.target.value)} placeholder="e.g. October" />
          </label>
        </div>
        <button type="submit" disabled={!file || isLoading}>
          {isLoading ? 'Searching PDF…' : 'Find date'}
        </button>
      </form>
      {error && <p className="demo-error" role="alert">{error}</p>}
      {result && (
        <div className="pdf-result" aria-live="polite">
          <strong>{result.file_name}: {result.matches_found} match(es) for {result.target_date}</strong>
          {result.matches.length
            ? <ul>{result.matches.map((match, index) => <li key={`${index}-${match}`}>{match}</li>)}</ul>
            : <p className="demo-muted">No matching sentences found.</p>}
        </div>
      )}
    </section>
  );
}

export default function DemoTools() {
  return (
    <div className="demo-tools">
      <GridStats />
      <PdfDateLookup />
    </div>
  );
}

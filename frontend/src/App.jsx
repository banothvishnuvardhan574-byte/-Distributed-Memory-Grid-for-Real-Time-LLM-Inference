import React, { useCallback, useEffect, useState } from 'react';
import {
  AccountTreeOutlined,
  ArchitectureOutlined,
  AttachFileOutlined,
  BarChartOutlined,
  BoltOutlined,
  ChatBubbleOutlined,
  CheckCircleOutlined,
  CloseRounded,
  ContentCopyOutlined,
  DescriptionOutlined,
  ErrorOutlined,
  HubOutlined,
  LightbulbOutlined,
  MemoryOutlined,
  SendRounded,
  StorageOutlined,
  TimelineOutlined,
} from '@mui/icons-material';
import './App.css';

const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '');
const EXAMPLES = [
  'Explain how the memory grid handles concurrent requests.',
  'Show system status and active nodes.',
  'Compare different memory eviction strategies.',
];
const QUICK_PROMPTS = ['System overview', 'Cache strategy', 'Failure handling', 'Compare approaches'];

// Carefully calibrated coordinates matching the visual reference (image 2)
// Node 01: [25, 27], Node 02: [53, 19], Node 03: [79, 44], Node 04: [17, 72], Node 05: [50, 78], Node 06: [75, 78]
const NODE_POSITIONS = [
  { x: 25, y: 27 },
  { x: 53, y: 19 },
  { x: 79, y: 44 },
  { x: 17, y: 72 },
  { x: 50, y: 78 },
  { x: 75, y: 78 },
];

const nodeName = (id) => `Node ${String(Number(id) + 1).padStart(2, '0')}`;

function Topology({ gridStats }) {
  const nodes = gridStats?.nodes || [];
  const [selectedId, setSelectedId] = useState(null);

  // Derive the active selected node during render without unnecessary effects
  const selected = (selectedId !== null ? nodes.find((node) => node.node_id === selectedId) : null)
    || nodes.find((n) => n.node_id === 2)
    || nodes[0]
    || null;

  return (
    <section id="network" className="topology card">
      <div className="panel-title">
        <AccountTreeOutlined />
        <div>
          <h2>Memory Grid Topology</h2>
          <p>
            Illustrative layout <em>· availability and cache entries from the API</em>
          </p>
        </div>
      </div>

      <div className="topology-canvas" aria-label="Distributed memory network topology">
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true" className="topology-svg">
          {/* Main spine connecting Node 01 -> Node 02 -> Node 03 */}
          <path className="connection-path line-1" d="M 25 27 C 37 32, 42 22, 53 19" />
          <path className="connection-path line-2" d="M 53 19 C 66 22, 69 38, 79 44" />

          {/* Lower cross connections Node 04 -> Node 01, Node 04 -> Node 05 */}
          <path className="connection-path line-3" d="M 17 72 C 19 50, 21 39, 25 27" />
          <path className="connection-path line-4" d="M 17 72 C 28 66, 39 74, 50 78" />

          {/* Vertical and diagonal hub links: Node 02 -> Node 05 and Node 05 -> Node 06 */}
          <path className="connection-path line-5" d="M 53 19 C 50 38, 51 60, 50 78" />
          <path className="connection-path line-6" d="M 50 78 C 59 78, 67 78, 75 78" />
          <path className="connection-path line-7" d="M 75 78 C 76 66, 77 54, 79 44" />
        </svg>

        {nodes.slice(0, NODE_POSITIONS.length).map((node, index) => {
          const { x, y } = NODE_POSITIONS[index];
          const isSelected = selected?.node_id === node.node_id;
          const isStorage = index % 3 === 1;

          return (
            <button
              key={node.node_id}
              type="button"
              className={`memory-node ${node.alive ? 'available' : 'unavailable'} ${isSelected ? 'selected' : ''}`}
              style={{ left: `${x}%`, top: `${y}%` }}
              onClick={() => setSelectedId(node.node_id)}
              aria-pressed={isSelected}
              aria-label={`${nodeName(node.node_id)}. ${node.alive ? 'Available' : 'Unavailable'}. Click to view details.`}
            >
              <span className="node-icon-wrapper">
                <span className="node-pulse-ring" aria-hidden="true" />
                {isStorage ? <StorageOutlined /> : <MemoryOutlined />}
              </span>
              <div className="node-meta">
                <b>{nodeName(node.node_id)}</b>
                <small>
                  <i className="status-indicator" />
                  {node.alive ? 'Available' : 'Unavailable'}
                </small>
              </div>
            </button>
          );
        })}

        {!nodes.length && (
          <p className="topology-empty">
            Node statistics are unavailable. Start the API backend to view live reported nodes.
          </p>
        )}

        {selected && (
          <aside className="node-popover" aria-live="polite">
            <div className="node-popover-header">
              <strong>
                {nodeName(selected.node_id)}
                <span className={`popover-badge ${selected.alive ? 'badge-available' : 'badge-unavailable'}`}>
                  {selected.alive ? 'Available' : 'Unavailable'}
                </span>
              </strong>
              <button
                type="button"
                className="popover-close"
                onClick={() => setSelectedId(null)}
                aria-label="Close node details"
              >
                <CloseRounded fontSize="inherit" />
              </button>
            </div>
            <dl>
              <dt>Source</dt>
              <dd>API stats</dd>
              <dt>Entries</dt>
              <dd>{selected.entries}</dd>
              <dt>Capacity</dt>
              <dd>{selected.capacity}</dd>
              <dt>Entry use</dt>
              <dd>
                {selected.capacity
                  ? `${Math.round((selected.entries / selected.capacity) * 100)}%`
                  : '—'}
              </dd>
            </dl>
          </aside>
        )}
      </div>

      <div className="legend">
        <span><i className="available" />Available</span>
        <span><i className="unavailable" />Unavailable</span>
        <small>Positions and connections are illustrative; node data is live from backend.</small>
      </div>
    </section>
  );
}

function Journey({ phase }) {
  const stages = ['Preparing', 'Sending', 'Awaiting response', 'Received'];
  const completeIndex = phase === 'idle' ? -1 : phase === 'error' ? 1 : phase === 'loading' ? 1 : 3;
  const captions = phase === 'error'
    ? ['Prompt checked', 'Request failed', 'Not reached', 'Not reached']
    : ['Prompt checked', 'Sent to API', 'Waiting for API', 'Response received'];

  return (
    <section id="history" className="journey card">
      <div className="panel-title">
        <TimelineOutlined />
        <div>
          <h2>Request Journey</h2>
          <p>Driven by this browser request</p>
        </div>
      </div>
      <div className="steps">
        {stages.map((name, index) => (
          <div
            className={index <= completeIndex ? 'done' : phase === 'error' && index === 1 ? 'failed' : ''}
            key={name}
          >
            <b>{index + 1}</b>
            <strong>{name}</strong>
            <small>{captions[index]}</small>
          </div>
        ))}
      </div>
    </section>
  );
}

function Response({ data, error, onDismissError }) {
  const [copied, setCopied] = useState(false);
  const cacheState = typeof data?.cache === 'string' ? data.cache.trim().toLowerCase() : '';
  const cacheDescription = cacheState === 'hit'
    ? 'Hit — retrieved cached response'
    : cacheState === 'miss'
      ? 'Miss — generated a fresh response'
      : cacheState === 'expired'
        ? 'Expired — generated fresh response'
        : cacheState === 'missing'
          ? 'Missing — generated fresh response'
          : data?.cache;

  const copyRequestId = async () => {
    if (!data?.request_id) return;
    try {
      await navigator.clipboard.writeText(data.request_id);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      setCopied(false);
    }
  };

  return (
    <section className="response card" aria-live="polite">
      <div className="response-head">
        <div className="panel-title">
          <DescriptionOutlined />
          <h2>Response</h2>
        </div>
        <span>{data?.timestamp ? `Received ${data.timestamp}` : 'Awaiting request'}</span>
      </div>
      {error ? (
        <div className="ack error" role="alert">
          <ErrorOutlined />
          <div>
            <b>Request failed</b>
            <p>{error}</p>
            <div className="response-actions">
              <button className="copy" type="button" onClick={onDismissError}>
                Dismiss
              </button>
            </div>
          </div>
        </div>
      ) : data ? (
        <>
          <div className="ack">
            <CheckCircleOutlined />
            <div>
              <b>Response received</b>
              <p>{data.response || 'The backend returned no response text.'}</p>
            </div>
          </div>
          <div className="response-meta">
            <div>
              Request ID <strong title={data.request_id}>{data.request_id || 'Not supplied'}</strong>
              <button className="copy" type="button" onClick={copyRequestId} aria-label="Copy request ID">
                <ContentCopyOutlined fontSize="small" />
                {copied ? 'Copied' : 'Copy'}
              </button>
            </div>
            <div>
              Round-trip <strong>{data.latency} ms</strong>
            </div>
            <div>
              Cache <strong className={cacheState === 'hit' ? 'status-live' : ''}>{cacheDescription || 'Not supplied'}</strong>
            </div>
            <div>
              Status <strong>{data.status || 'unknown'}</strong>
            </div>
          </div>
        </>
      ) : (
        <div className="empty-response">
          Submit a prompt to view the backend response, its request ID, cache result, and client-measured round-trip time.
        </div>
      )}
    </section>
  );
}

function RequestHistory({ entries }) {
  const [copiedId, setCopiedId] = useState(null);

  const copyId = async (id) => {
    if (!id || id === 'N/A') return;
    try {
      await navigator.clipboard.writeText(id);
      setCopiedId(id);
      window.setTimeout(() => setCopiedId(null), 1600);
    } catch {
      setCopiedId(null);
    }
  };

  return (
    <section className="history-panel card" aria-label="Session request history">
      <div className="panel-title">
        <TimelineOutlined />
        <div>
          <h2>Session Request History</h2>
          <p>Successful requests from this browser session</p>
        </div>
        <b className="history-count" title={`${entries.length} successful request${entries.length === 1 ? '' : 's'}`}>
          {entries.length}
        </b>
      </div>

      {entries.length ? (
        <div className="history-list">
          {entries.map((entry) => (
            <article className="history-entry" key={entry.request_id}>
              <div className="history-entry-top">
                <p title={entry.prompt}>{entry.prompt}</p>
                <div className="history-id">
                  <span title={entry.request_id}>{entry.request_id}</span>
                  <button
                    type="button"
                    onClick={() => copyId(entry.request_id)}
                    aria-label={`Copy request ID ${entry.request_id}`}
                  >
                    <ContentCopyOutlined fontSize="inherit" />
                    {copiedId === entry.request_id ? 'Copied' : 'Copy'}
                  </button>
                </div>
              </div>
              <div className="history-entry-meta">
                <div className="history-entry-tags">
                  <b className="history-tag status">{entry.status || 'completed'}</b>
                  {entry.cache && (
                    <span className={`history-tag cache ${String(entry.cache).toLowerCase() === 'hit' ? 'cache-hit' : ''}`}>
                      {entry.cache}
                    </span>
                  )}
                </div>
                <small>
                  {entry.latency} ms · {entry.timestamp}
                </small>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="history-empty">
          <TimelineOutlined />
          <div>
            <strong>No session requests yet</strong>
            <span>Successful prompt requests will appear here with prompt excerpt, request ID, latency, and cache result.</span>
          </div>
        </div>
      )}
    </section>
  );
}

async function readError(response) {
  let message = `Server error (${response.status}): ${response.statusText || 'Request failed'}`;
  try {
    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      const body = await response.json();
      if (body?.detail) {
        message = Array.isArray(body.detail)
          ? body.detail.map((item) => (typeof item === 'string' ? item : item.msg || JSON.stringify(item))).join(', ')
          : typeof body.detail === 'object'
            ? JSON.stringify(body.detail)
            : String(body.detail);
      } else if (body?.message) {
        message = String(body.message);
      }
    } else {
      const text = await response.text();
      if (text.trim() && text.length < 300) message = text.trim();
    }
  } catch {
    /* Use HTTP fallback. */
  }
  return message;
}

export default function App() {
 tirth-ui
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [responseData, setResponseData] = useState(null);
  const [requestHistory, setRequestHistory] = useState([]);
  const [gridStats, setGridStats] = useState(null);
  const [backend, setBackend] = useState('Checking API');

  const refreshBackend = useCallback(async () => {
    try {
      const [health, grid] = await Promise.all([
        fetch(`${API_URL}/health`),
        fetch(`${API_URL}/api/grid/stats`),
      ]);
      setBackend(health.ok ? 'Backend connected' : 'Backend unavailable');
      if (grid.ok) {
        setGridStats(await grid.json());
      }
    } catch {
      setBackend('Backend unavailable');
    }
  }, []);

  useEffect(() => {
    refreshBackend();
  }, [refreshBackend]);

  const handleSubmit = useCallback(async () => {
    const trimmedPrompt = prompt.trim();
    if (!trimmedPrompt || isLoading) return;
    setIsLoading(true);
    setError(null);
    const startTime = performance.now();
    try {
      const response = await fetch(`${API_URL}/api/prompt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: trimmedPrompt }),
      });
      const latency = Math.round(performance.now() - startTime);
      if (!response.ok) throw new Error(await readError(response));
      let data;
      try {
        data = await response.json();
      } catch {
        throw new Error('Received invalid JSON response from server.');
      }
      if (!data || typeof data !== 'object') {
        throw new Error('Unexpected response format received from inference service.');
      }
      const enriched = { ...data, latency, timestamp: new Date().toLocaleTimeString() };
      setResponseData(enriched);
      setRequestHistory((previous) => [
        {
          request_id: data.request_id || 'N/A',
          status: data.status || 'completed',
          prompt: data.prompt || trimmedPrompt,
          cache: data.cache,
          latency,
          timestamp: enriched.timestamp,
        },
        ...previous,
      ]);
      refreshBackend();
    } catch (submissionError) {
      const message =
        submissionError?.name === 'TypeError' && /fetch|NetworkError/i.test(submissionError.message || '')
          ? `Backend API is unreachable at ${API_URL || 'the configured API proxy'}/api/prompt. Ensure the FastAPI backend server is running, or verify your network connection.`
          : submissionError.message || 'An unexpected error occurred while communicating with the inference grid.';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, prompt, refreshBackend]);

  const charCount = prompt.length;
  const wordCount = prompt.trim() ? prompt.trim().split(/\s+/).length : 0;
  const tokenEstimate = Math.ceil(charCount / 4);
  const phase = error ? 'error' : isLoading ? 'loading' : responseData ? 'completed' : 'idle';

  return (
    <>
      <header>
        <a className="brand" href="#top" aria-label="MemoryGrid home">
          <span className="logo"><HubOutlined /></span>
          <span>MemoryGrid</span>
        </a>
        <nav aria-label="Primary navigation">
          <a className="selected" href="#top">Overview</a>
          <a href="#prompt">Prompt</a>
          <a href="#network">Network</a>
          <a href="#history">History</a>
          <a href="#system">System</a>
        </nav>
        <div
          className="backend"
          title={`${requestHistory.length} successful request${requestHistory.length === 1 ? '' : 's'} this session`}
        >
          <i className={backend === 'Backend connected' ? 'ok' : ''} />
          <span>
            {backend}
            <small>API connection</small>
          </span>
        </div>
        <button className="profile" type="button" aria-label="User profile">
          T
        </button>
      </header>

      <main id="top">
        <aside className="editorial">
          <p className="eyebrow">Distributed memory</p>
          <h1>
            Explore the<br />memory grid.
          </h1>
          <div className="brush" />
          <p className="intro">
            Submit a prompt, follow its journey across the system, and understand how distributed memory enables real-time LLM inference.
          </p>
          <div className="features">
            <div>
              <b><ArchitectureOutlined /></b>
              <span>
                <strong>Distributed architecture</strong>
                <small>Multiple memory nodes working together</small>
              </span>
            </div>
            <div>
              <b><BoltOutlined /></b>
              <span>
                <strong>Efficient memory management</strong>
                <small>Key-value storage with TTL and LRU</small>
              </span>
            </div>
            <div>
              <b><BarChartOutlined /></b>
              <span>
                <strong>Real-time request flow</strong>
                <small>Track your request across the system</small>
              </span>
            </div>
          </div>
          <div className="botanical" aria-hidden="true">
            <i />
            <i />
            <i />
            <span>
              Smarter<br />Memory<br />Brighter<br />AI
            </span>
          </div>
        </aside>

        <div className="dashboard">
          <div className="top-row">
            <Topology gridStats={gridStats} />
            <aside className="sticky">
              <b>
                <LightbulbOutlined />Example Prompts
              </b>
              {EXAMPLES.map((example) => (
                <button type="button" onClick={() => setPrompt(example)} key={example}>
                  <SendRounded fontSize="small" />
                  <span>{example}</span>
                </button>
              ))}
            </aside>
          </div>

          <section id="prompt" className="composer card">
            <div className="composer-title">
              <ChatBubbleOutlined />
              <h2>Prompt Input</h2>
              <small>Ctrl + Enter to submit</small>
            </div>
            <textarea
              value={prompt}
              maxLength={4000}
              onChange={(event) => setPrompt(event.target.value)}
              onKeyDown={(event) => {
                if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
                  event.preventDefault();
                  handleSubmit();
                }
              }}
              placeholder="Ask something about the memory grid..."
              disabled={isLoading}
              aria-label="Prompt input"
              aria-describedby="prompt-character-count"
            />
            <div className="compose-toolbar">
              <span title="Estimated tokens use a four-characters-per-token heuristic.">
                <AttachFileOutlined fontSize="small" />Add context unavailable <i />{' '}
                <span id="prompt-character-count">{charCount} / 4000 characters</span> <i />{' '}
                {wordCount} words <i /> {tokenEstimate} estimated tokens
              </span>
              <button
                className="submit"
                type="button"
                onClick={handleSubmit}
                disabled={isLoading || !prompt.trim()}
                aria-label={isLoading ? 'Submitting prompt' : 'Submit prompt'}
              >
                {isLoading ? <span className="spinner" /> : <SendRounded />}
              </button>
            </div>
            <div className="quick">
              <b>Quick prompts:</b>
              {QUICK_PROMPTS.map((quick) => (
                <button type="button" onClick={() => setPrompt(quick)} key={quick}>
                  {quick}
                </button>
              ))}
            </div>
          </section>

          <div className="bottom">
            <Journey phase={phase} />
            <Response data={responseData} error={error} onDismissError={() => setError(null)} />
          </div>

          <RequestHistory entries={requestHistory} />
        </div>
      </main>
    </>
  );

  const [prompt, setPrompt] = useState(''); const [apiKey, setApiKey] = useState(''); const [isLoading, setIsLoading] = useState(false); const [error, setError] = useState(null); const [responseData, setResponseData] = useState(null); const [requestHistory, setRequestHistory] = useState([]); const [gridStats, setGridStats] = useState(null); const [backend, setBackend] = useState('Checking API');
  const refreshBackend = useCallback(async () => { try { const [health, grid] = await Promise.all([fetch(`${API_URL}/health`), fetch(`${API_URL}/api/grid/stats`)]); setBackend(health.ok ? 'Backend connected' : 'Backend unavailable'); if (grid.ok) setGridStats(await grid.json()); } catch { setBackend('Backend unavailable'); } }, []);
  useEffect(() => { refreshBackend(); }, [refreshBackend]);
  const handleSubmit = useCallback(async () => { const trimmedPrompt = prompt.trim(); if (!trimmedPrompt || isLoading) return; setIsLoading(true); setError(null); const startTime = performance.now(); try { const response = await fetch(`${API_URL}/api/prompt`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-API-Key': apiKey }, body: JSON.stringify({ prompt: trimmedPrompt }) }); const latency = Math.round(performance.now() - startTime); if (!response.ok) throw new Error(await readError(response)); let data; try { data = await response.json(); } catch { throw new Error('Received invalid JSON response from server.'); } if (!data || typeof data !== 'object') throw new Error('Unexpected response format received from inference service.'); const enriched = { ...data, latency, timestamp: new Date().toLocaleTimeString() }; setResponseData(enriched); setRequestHistory((previous) => [{ request_id: data.request_id || 'N/A', status: data.status || 'completed', prompt: data.prompt || trimmedPrompt, cache: data.cache, latency, timestamp: enriched.timestamp }, ...previous]); refreshBackend(); } catch (submissionError) { const message = submissionError?.name === 'TypeError' && /fetch|NetworkError/i.test(submissionError.message || '') ? `Backend API is unreachable at ${API_URL || 'the configured API proxy'}/api/prompt. Ensure the FastAPI backend server is running, or verify your network connection.` : submissionError.message || 'An unexpected error occurred while communicating with the inference grid.'; setError(message); } finally { setIsLoading(false); } }, [apiKey, isLoading, prompt, refreshBackend]);
  const charCount = prompt.length; const wordCount = prompt.trim() ? prompt.trim().split(/\s+/).length : 0; const tokenEstimate = Math.ceil(charCount / 4); const phase = error ? 'error' : isLoading ? 'loading' : responseData ? 'completed' : 'idle';
  return <><header><a className="brand" href="#top" aria-label="MemoryGrid home"><span className="logo"><HubOutlined /></span><span>MemoryGrid</span></a><nav aria-label="Primary navigation"><a className="selected" href="#top">Overview</a><a href="#prompt">Prompt</a><a href="#network">Network</a><a href="#history">History</a><a href="#system">System</a></nav><div className="backend" title={`${requestHistory.length} successful request${requestHistory.length === 1 ? '' : 's'} this session`}><i className={backend === 'Backend connected' ? 'ok' : ''} /><span>{backend}<small>API connection</small></span></div><button className="profile" type="button" aria-label="User profile">T</button></header><main id="top"><aside className="editorial"><p className="eyebrow">Distributed memory</p><h1>Explore the<br />memory grid.</h1><div className="brush" /><p className="intro">Submit a prompt, follow its journey across the system, and understand how distributed memory enables real-time LLM inference.</p><div className="features"><div><b><ArchitectureOutlined /></b><span><strong>Distributed architecture</strong><small>Multiple memory nodes working together</small></span></div><div><b><BoltOutlined /></b><span><strong>Efficient memory management</strong><small>Key-value storage with TTL and LRU</small></span></div><div><b><BarChartOutlined /></b><span><strong>Real-time request flow</strong><small>Track your request across the system</small></span></div></div><div className="botanical" aria-hidden="true"><i /><i /><i /><span>Smarter<br />Memory<br />Brighter<br />AI</span></div></aside><div className="dashboard"><div className="top-row"><Topology gridStats={gridStats} /><aside className="sticky"><b><LightbulbOutlined />Example Prompts</b>{EXAMPLES.map((example) => <button type="button" onClick={() => setPrompt(example)} key={example}><SendRounded fontSize="small" /><span>{example}</span></button>)}</aside></div><section id="prompt" className="composer card"><div className="composer-title"><ChatBubbleOutlined /><h2>Prompt Input</h2><small>Ctrl + Enter to submit</small></div><label className="api-key-field" style={{ display: 'block', margin: '10px 0' }}>API key<input type="password" autoComplete="off" value={apiKey} onChange={(event) => setApiKey(event.target.value)} style={{ display: 'block', width: '100%', marginTop: '5px', padding: '9px 12px', border: '1px solid #d5d3ca', borderRadius: '8px', background: '#fbfaf2' }} /></label><textarea value={prompt} maxLength={4000} onChange={(event) => setPrompt(event.target.value)} onKeyDown={(event) => { if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') { event.preventDefault(); handleSubmit(); } }} placeholder="Ask something about the memory grid..." disabled={isLoading} aria-label="Prompt input" aria-describedby="prompt-character-count" /><div className="compose-toolbar"><span title="Estimated tokens use a four-characters-per-token heuristic."><AttachFileOutlined fontSize="small" />Add context unavailable <i /> <span id="prompt-character-count">{charCount} / 4000 characters</span> <i /> {wordCount} words <i /> {tokenEstimate} estimated tokens</span><button className="submit" type="button" onClick={handleSubmit} disabled={isLoading || !prompt.trim()} aria-label={isLoading ? 'Submitting prompt' : 'Submit prompt'}>{isLoading ? <span className="spinner" /> : <SendRounded />}</button></div><div className="quick"><b>Quick prompts:</b>{QUICK_PROMPTS.map((quick) => <button type="button" onClick={() => setPrompt(quick)} key={quick}>{quick}</button>)}</div></section><div className="bottom"><Journey phase={phase} /><Response data={responseData} error={error} onDismissError={() => setError(null)} /></div><RequestHistory entries={requestHistory} /></div></main></>;
 main
}

import React, { useCallback, useEffect, useState } from 'react';
import {
  AccountTreeOutlined, ArchitectureOutlined, AttachFileOutlined, BarChartOutlined,
  BoltOutlined, ChatBubbleOutlined, CheckCircleOutlined, ContentCopyOutlined,
  DescriptionOutlined, ErrorOutlined, HubOutlined, LightbulbOutlined,
  MemoryOutlined, SendRounded, StorageOutlined, TimelineOutlined,
} from '@mui/icons-material';
import './App.css';

const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '');
const EXAMPLES = [
  'Explain how the memory grid handles concurrent requests.',
  'Show system status and active nodes.',
  'Compare different memory eviction strategies.',
];
const QUICK_PROMPTS = ['System overview', 'Cache strategy', 'Failure handling', 'Compare approaches'];
const TOPOLOGY_NODES = [
  { id: '01', x: 23, y: 28, state: 'active', type: 'memory' },
  { id: '02', x: 53, y: 18, state: 'active', type: 'storage' },
  { id: '03', x: 80, y: 53, state: 'active', type: 'memory' },
  { id: '04', x: 14, y: 76, state: 'idle', type: 'memory' },
  { id: '05', x: 46, y: 82, state: 'active', type: 'storage' },
  { id: '06', x: 83, y: 80, state: 'unavailable', type: 'memory' },
];

function NodeIcon({ type }) {
  return type === 'storage' ? <StorageOutlined /> : <MemoryOutlined />;
}

function Topology({ stats }) {
  const [selected, setSelected] = useState(TOPOLOGY_NODES[2]);
  const reported = stats?.find((node) => String(node.node_id + 1).padStart(2, '0') === selected.id);

  return (
    <section id="network" className="topology card">
      <div className="panel-title">
        <AccountTreeOutlined />
        <div><h2>Memory Grid Topology</h2><p>Interactive visual representation <em>· illustrative states</em></p></div>
      </div>
      <div className="topology-canvas" aria-label="Illustrative memory topology">
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
          <path className="connection" d="M23 28 C25 52 35 48 46 52 S58 56 80 53 M53 18 C52 38 49 42 46 52 M14 76 C23 57 32 47 46 52 M46 52 C46 66 46 72 46 82 M46 52 C64 43 70 60 80 53 M80 53 C76 70 78 76 83 80" />
        </svg>
        {TOPOLOGY_NODES.map((node) => (
          <button key={node.id} type="button" className={`memory-node ${node.state} ${selected.id === node.id ? 'selected' : ''}`}
            style={{ left: `${node.x}%`, top: `${node.y}%` }} onClick={() => setSelected(node)}
            aria-pressed={selected.id === node.id} aria-label={`Node ${node.id}. Illustrative ${node.state} state. Activate for details.`}>
            <span><NodeIcon type={node.type} /></span><b>Node {node.id}</b><small><i />{node.state}</small>
          </button>
        ))}
        <aside className="node-popover" aria-live="polite">
          <strong>Node {selected.id}<span>{selected.state}</span></strong>
          <dl>
            <dt>Role</dt><dd>Memory worker</dd>
            <dt>Source</dt><dd>{reported ? 'Backend stats' : 'Illustrative'}</dd>
            {reported && <><dt>Entries</dt><dd>{reported.entries ?? '—'}</dd><dt>Capacity</dt><dd>{reported.capacity ?? '—'}</dd><dt>Available</dt><dd>{String(reported.alive)}</dd></>}
            <dt>Route</dt><dd>Not exposed</dd>
          </dl>
        </aside>
      </div>
      <div className="legend"><span><i className="active" />Active</span><span><i className="idle" />Idle</span><span><i className="unavailable" />Unavailable</span><small>Illustrative states — API does not expose health or routing.</small></div>
    </section>
  );
}

function Journey({ phase }) {
  const stages = ['Preparing', 'Sending', 'Processing', 'Completed'];
  const completeIndex = phase === 'idle' ? -1 : phase === 'error' ? 1 : phase === 'loading' ? 2 : phase === 'accepted' ? 2 : 3;
  const captions = phase === 'error'
    ? ['Validating prompt', 'Request failed', 'Not reached', 'Not reached']
    : phase === 'accepted'
      ? ['Validated prompt', 'Sent to backend', 'Backend accepted', 'Not reported']
      : ['Validating prompt', 'Sending to backend', 'Awaiting response', 'Response ready'];
  return <section id="history" className="journey card"><div className="panel-title"><TimelineOutlined /><div><h2>Request Journey</h2><p>Driven by this browser request</p></div></div><div className="steps">{stages.map((name, index) => <div className={index <= completeIndex ? 'done' : phase === 'error' && index === 1 ? 'failed' : ''} key={name}><b>{index + 1}</b><strong>{name}</strong><small>{captions[index]}</small></div>)}</div></section>;
}

function Response({ data, error, onDismissError }) {
  const [copied, setCopied] = useState(false);
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
  return <section className="response card" aria-live="polite"><div className="response-head"><div className="panel-title"><DescriptionOutlined /><h2>Response</h2></div><span>{data?.timestamp || 'Awaiting request'}</span></div>{error ? <div className="ack error"><ErrorOutlined /><div><b>Request failed</b><p>{error}</p><button className="copy" type="button" onClick={onDismissError}>Dismiss</button></div></div> : data ? <><div className="ack"><CheckCircleOutlined /><div><b>{data.status === 'completed' ? 'Response received' : 'Prompt submitted'}</b><p>{data.response || 'Backend acknowledged the request.'}</p></div></div><div className="response-meta"><div>Request ID <strong>{data.request_id || 'Not supplied'}</strong><button className="copy" type="button" onClick={copyRequestId} aria-label="Copy request ID"><ContentCopyOutlined fontSize="small" />{copied ? 'Copied' : 'Copy'}</button></div>{data.latency != null && <div>Latency <strong>{data.latency} ms</strong></div>}<div>Status <strong className="status-live">{data.status || 'unknown'}</strong></div></div></> : <div className="empty-response">Submit a prompt to view its backend acknowledgment, real request ID, and measured latency.</div>}</section>;
}

async function readError(response) {
  let message = `Server error (${response.status}): ${response.statusText || 'Request failed'}`;
  try {
    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      const body = await response.json();
      if (body?.detail) message = Array.isArray(body.detail) ? body.detail.map((item) => typeof item === 'string' ? item : item.msg || JSON.stringify(item)).join(', ') : typeof body.detail === 'object' ? JSON.stringify(body.detail) : String(body.detail);
      else if (body?.message) message = String(body.message);
    } else {
      const text = await response.text();
      if (text.trim() && text.length < 300) message = text.trim();
    }
  } catch { /* use HTTP fallback */ }
  return message;
}

export default function App() {
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [responseData, setResponseData] = useState(null);
  const [requestHistory, setRequestHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [backend, setBackend] = useState('Checking backend');

  const refreshBackend = useCallback(async () => {
    try {
      const [health, grid] = await Promise.all([fetch(`${API_URL}/health`), fetch(`${API_URL}/api/grid/stats`)]);
      setBackend(health.ok ? 'Backend connected' : 'Backend unavailable');
      if (grid.ok) setStats((await grid.json()).nodes || []);
    } catch { setBackend('Backend unavailable'); }
  }, []);

  useEffect(() => { refreshBackend(); }, [refreshBackend]);

  const handleSubmit = useCallback(async () => {
    const trimmedPrompt = prompt.trim();
    if (!trimmedPrompt || isLoading) return;
    setIsLoading(true); setError(null);
    const startTime = performance.now();
    try {
      const response = await fetch(`${API_URL}/api/prompt`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ prompt: trimmedPrompt }) });
      const latency = Math.round(performance.now() - startTime);
      if (!response.ok) throw new Error(await readError(response));
      let data;
      try { data = await response.json(); } catch { throw new Error('Received invalid JSON response from server.'); }
      if (!data || typeof data !== 'object') throw new Error('Unexpected response format received from inference service.');
      const enriched = { ...data, latency, timestamp: new Date().toLocaleTimeString() };
      setResponseData(enriched);
      setRequestHistory((previous) => [{ request_id: data.request_id || 'N/A', status: data.status || 'accepted', prompt: data.prompt || trimmedPrompt, latency, timestamp: enriched.timestamp }, ...previous]);
      refreshBackend();
    } catch (submissionError) {
      const message = submissionError?.name === 'TypeError' && /fetch|NetworkError/i.test(submissionError.message || '')
        ? `Backend API is unreachable at ${API_URL || 'the configured API proxy'}/api/prompt. Ensure the FastAPI backend server is running, or verify your network connection.`
        : submissionError.message || 'An unexpected error occurred while communicating with the inference grid.';
      setError(message);
    } finally { setIsLoading(false); }
  }, [isLoading, prompt, refreshBackend]);

  const charCount = prompt.length;
  const wordCount = prompt.trim() ? prompt.trim().split(/\s+/).length : 0;
  const tokenEstimate = Math.ceil(charCount / 4);
  const phase = error ? 'error' : isLoading ? 'loading' : responseData?.status === 'completed' ? 'completed' : responseData ? 'accepted' : 'idle';

  return <><header><a className="brand" href="#top" aria-label="MemoryGrid home"><span className="logo"><HubOutlined /></span><span>MemoryGrid</span></a><nav aria-label="Primary navigation"><a className="selected">Overview</a><a href="#prompt">Prompt</a><a href="#network">Network</a><a href="#history">History</a><a href="#system">System</a></nav><div className="backend" title={`${requestHistory.length} request${requestHistory.length === 1 ? '' : 's'} this session`}><i className={backend === 'Backend connected' ? 'ok' : ''} /><span>{backend}<small>localhost:8000</small></span></div><button className="profile" type="button" aria-label="User profile">T</button></header><main id="top"><aside className="editorial"><p className="eyebrow">Distributed memory</p><h1>Explore the<br />memory grid.</h1><div className="brush" /><p className="intro">Submit a prompt, follow its journey across the system, and understand how distributed memory enables real-time LLM inference.</p><div className="features"><div><b><ArchitectureOutlined /></b><span><strong>Distributed architecture</strong><small>Multiple memory nodes working together</small></span></div><div><b><BoltOutlined /></b><span><strong>Efficient memory management</strong><small>Key-value storage with TTL and LRU</small></span></div><div><b><BarChartOutlined /></b><span><strong>Real-time request flow</strong><small>Track your request across the system</small></span></div></div><div className="botanical" aria-hidden="true"><i /><i /><i /><span>Smarter<br />Memory<br />Brighter<br />AI</span></div></aside><div className="dashboard"><div className="top-row"><Topology stats={stats} /><aside className="sticky"><b><LightbulbOutlined />Example Prompts</b>{EXAMPLES.map((example) => <button type="button" onClick={() => setPrompt(example)} key={example}><SendRounded fontSize="small" /><span>{example}</span></button>)}</aside></div><section id="prompt" className="composer card"><div className="composer-title"><ChatBubbleOutlined /><h2>Prompt Input</h2><small>Ctrl + Enter to submit</small></div><textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} onKeyDown={(event) => { if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') { event.preventDefault(); handleSubmit(); } }} placeholder="Ask something about the memory grid..." disabled={isLoading} aria-label="Prompt input" /><div className="compose-toolbar"><span title="Attachments are not supported by this API"><AttachFileOutlined fontSize="small" />Attachments unavailable &nbsp;|&nbsp; {charCount} characters &nbsp;{wordCount} words &nbsp;{tokenEstimate} tokens</span><button className="submit" type="button" onClick={handleSubmit} disabled={isLoading || !prompt.trim()} aria-label={isLoading ? 'Submitting prompt' : 'Submit prompt'}>{isLoading ? <span className="spinner" /> : <SendRounded />}</button></div><div className="quick"><b>Quick prompts:</b>{QUICK_PROMPTS.map((quick) => <button type="button" onClick={() => setPrompt(quick)} key={quick}>{quick}</button>)}</div></section><div className="bottom"><Journey phase={phase} /><Response data={responseData} error={error} onDismissError={() => setError(null)} /></div></div></main></>;
}
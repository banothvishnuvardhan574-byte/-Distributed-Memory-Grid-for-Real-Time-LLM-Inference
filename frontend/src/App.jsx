import React, { useState, useCallback } from 'react';
import {
  ThemeProvider,
  CssBaseline,
  Box,
  Container,
  Typography,
  Grid,
} from '@mui/material';
import { theme } from './theme';
import Header from './components/Header';
import PromptInputArea from './components/PromptInputArea';
import StatusAndLoading from './components/StatusAndLoading';
import ResponsePanel from './components/ResponsePanel';
import RequestHistory from './components/RequestHistory';

export default function App() {
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState('Routing request to distributed grid...');
  const [error, setError] = useState(null);
  const [responseData, setResponseData] = useState(null);
  const [requestHistory, setRequestHistory] = useState([]);

  // Derive application state for Header — based only on real frontend state
  const getRequestState = () => {
    if (isLoading) return 'submitting';
    if (error) return 'error';
    if (responseData) return 'responded';
    return 'idle';
  };

  const handleSubmit = useCallback(async () => {
    const trimmedPrompt = prompt.trim();
    if (!trimmedPrompt || isLoading) return;

    setIsLoading(true);
    setError(null);
    setLoadingStep('Hashing prompt and querying distributed memory cache...');

    const startTime = performance.now();

    try {
      // Step simulation for realistic feedback
      setTimeout(() => {
        setLoadingStep('Dispatching inference to active memory grid nodes...');
      }, 350);

      const res = await fetch('/api/prompt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: trimmedPrompt }),
      });

      const latencyMs = Math.round(performance.now() - startTime);

      if (!res.ok) {
        let errorMsg = `Server error (${res.status}): ${res.statusText || 'Request failed'}`;
        try {
          const contentType = res.headers.get('content-type') || '';
          if (contentType.includes('application/json')) {
            const errJson = await res.json();
            if (errJson && errJson.detail) {
              errorMsg = Array.isArray(errJson.detail)
                ? errJson.detail.map((d) => (typeof d === 'string' ? d : d.msg || JSON.stringify(d))).join(', ')
                : typeof errJson.detail === 'object'
                  ? JSON.stringify(errJson.detail)
                  : String(errJson.detail);
            } else if (errJson && errJson.message) {
              errorMsg = String(errJson.message);
            }
          } else {
            const text = await res.text();
            if (text && text.trim().length > 0 && text.length < 300) {
              errorMsg = text.trim();
            }
          }
        } catch {
          // fallback to standard status message
        }
        throw new Error(errorMsg);
      }

      let data;
      try {
        data = await res.json();
      } catch {
        throw new Error('Received invalid JSON response from server.');
      }

      if (!data || typeof data !== 'object') {
        throw new Error('Unexpected response format received from inference service.');
      }

      const enrichedData = {
        ...data,
        latency: latencyMs,
        timestamp: new Date().toLocaleTimeString(),
      };
      setResponseData(enrichedData);

      // Track in session history (real data only)
      setRequestHistory((prev) => [
        {
          request_id: data.request_id || 'N/A',
          status: data.status || 'accepted',
          prompt: data.prompt || trimmedPrompt,
          latency: latencyMs,
          timestamp: new Date().toLocaleTimeString(),
        },
        ...prev,
      ]);
    } catch (err) {
      console.error('Inference submission error:', err);
      // Helpful error message if backend is not started or connection is refused
      if (err.name === 'TypeError' && (err.message.includes('fetch') || err.message.includes('Failed to fetch') || err.message.includes('NetworkError'))) {
        setError(
          'Backend API is currently unreachable at http://localhost:8000/api/prompt. Ensure the FastAPI backend server is running, or verify your network connection.'
        );
      } else {
        setError(err.message || 'An unexpected error occurred while communicating with the inference grid.');
      }
    } finally {
      setIsLoading(false);
    }
  }, [prompt, isLoading]);

  const handleClear = () => {
    setPrompt('');
    setError(null);
  };

  const handleDismissError = () => {
    setError(null);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        {/* Top Header — reflects actual application state */}
        <Header
          requestState={getRequestState()}
          totalRequests={requestHistory.length}
        />

        {/* Main Dashboard Content Area */}
        <Container maxWidth="lg" sx={{ py: { xs: 3, md: 4 }, flexGrow: 1 }}>
          {/* Dashboard Title */}
          <Box sx={{ mb: 3 }}>
            <Typography
              variant="h4"
              component="h2"
              sx={{
                fontWeight: 800,
                letterSpacing: '-0.03em',
                mb: 0.5,
                background: 'linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #818cf8 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Inference Dashboard
            </Typography>
            <Typography variant="body2" sx={{ color: '#94a3b8', maxWidth: 600 }}>
              Submit prompts to the backend API, view request acknowledgments with unique Request IDs, and track your session history.
            </Typography>
          </Box>

          {/* Dashboard Grid — two-column on desktop, stacked on mobile */}
          <Grid container spacing={3}>
            {/* Left Column: Prompt Submission & Loading/Error */}
            <Grid item xs={12} md={8}>
              {/* 1. Prompt Input Area (includes Prompt Text Area & Primary Submit Button) */}
              <PromptInputArea
                prompt={prompt}
                setPrompt={setPrompt}
                onSubmit={handleSubmit}
                isLoading={isLoading}
                onClear={handleClear}
              />

              {/* 2. Loading Indicator & Error Message Area */}
              <StatusAndLoading
                isLoading={isLoading}
                loadingStep={loadingStep}
                error={error}
                onDismissError={handleDismissError}
                onRetry={handleSubmit}
              />

              {/* 3. Response Panel (Model Output and Request ID) */}
              <Box sx={{ mt: 2 }}>
                <ResponsePanel responseData={responseData} />
              </Box>
            </Grid>

            {/* Right Column: Session Request History */}
            <Grid item xs={12} md={4}>
              <Box sx={{ position: { md: 'sticky' }, top: { md: 24 } }}>
                <RequestHistory history={requestHistory} />
              </Box>
            </Grid>
          </Grid>
        </Container>

        {/* Footer */}
        <Box
          component="footer"
          sx={{
            py: 2.5,
            textAlign: 'center',
            borderTop: '1px solid rgba(255, 255, 255, 0.05)',
            backgroundColor: 'rgba(10, 13, 20, 0.6)',
          }}
        >
          <Typography variant="caption" sx={{ color: '#64748b', fontFamily: "'JetBrains Mono', monospace" }}>
            Distributed Memory Grid for Real-Time LLM Inference • Branch: <strong>tirth-ui</strong>
          </Typography>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

import React, { useState } from 'react';
import {
  ThemeProvider,
  CssBaseline,
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import { theme } from './theme';
import Header from './components/Header';
import PromptInputArea from './components/PromptInputArea';
import StatusAndLoading from './components/StatusAndLoading';
import ResponsePanel from './components/ResponsePanel';
import SpeedRoundedIcon from '@mui/icons-material/SpeedRounded';
import StorageRoundedIcon from '@mui/icons-material/StorageRounded';
import SecurityRoundedIcon from '@mui/icons-material/SecurityRounded';

export default function App() {
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState('Routing request to distributed grid...');
  const [error, setError] = useState(null);
  const [responseData, setResponseData] = useState(null);

  const handleSubmit = async () => {
    if (!prompt.trim()) return;

    setIsLoading(true);
    setError(null);
    setLoadingStep('Hashing prompt and querying distributed memory cache...');

    const startTime = performance.now();

    try {
      // Step simulation for realistic feel
      setTimeout(() => {
        setLoadingStep('Dispatching inference to active memory grid nodes...');
      }, 350);

      const res = await fetch('/api/prompt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: prompt.trim() }),
      });

      const latencyMs = Math.round(performance.now() - startTime);

      if (!res.ok) {
        let errorMsg = `Server error (${res.status}): ${res.statusText}`;
        try {
          const errJson = await res.json();
          if (errJson.detail) {
            errorMsg = Array.isArray(errJson.detail)
              ? errJson.detail.map((d) => d.msg || JSON.stringify(d)).join(', ')
              : errJson.detail;
          }
        } catch (_) {
          // fallback to status text
        }
        throw new Error(errorMsg);
      }

      const data = await res.json();
      setResponseData({
        ...data,
        latency: latencyMs,
        timestamp: new Date().toLocaleTimeString(),
      });
    } catch (err) {
      console.error('Inference submission error:', err);
      // Helpful error message if backend is not started
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        setError(
          'Backend API is currently unreachable at http://localhost:8000/api/prompt. Ensure the FastAPI backend server is running, or verify your network connection.'
        );
      } else {
        setError(err.message || 'An unexpected error occurred while communicating with the inference grid.');
      }
    } finally {
      setIsLoading(false);
    }
  };

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
        {/* Top Header */}
        <Header />

        {/* Main Content Area */}
        <Container maxWidth="lg" sx={{ py: { xs: 3, md: 5 }, flexGrow: 1 }}>
          {/* Hero Banner */}
          <Box sx={{ mb: 4, textAlign: 'center' }}>
            <Typography
              variant="h4"
              component="h2"
              sx={{
                fontWeight: 800,
                letterSpacing: '-0.03em',
                mb: 1,
                background: 'linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #818cf8 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Real-Time LLM Inference Interface
            </Typography>
            <Typography variant="body1" sx={{ color: '#94a3b8', maxWidth: 650, mx: 'auto' }}>
              Submit prompts directly to the distributed memory grid cluster. Monitor execution lifecycle, retrieve generated outputs, and inspect unique Request IDs.
            </Typography>
          </Box>

          {/* Feature highlights chips / stats */}
          <Grid container spacing={2} sx={{ mb: 3.5 }}>
            <Grid item xs={12} sm={4}>
              <Card sx={{ p: 1.5, display: 'flex', alignItems: 'center', gap: 1.5, backgroundColor: 'rgba(15, 23, 42, 0.5)' }}>
                <SpeedRoundedIcon sx={{ color: '#38bdf8' }} />
                <Box>
                  <Typography variant="caption" sx={{ color: '#64748b', display: 'block', fontWeight: 600 }}>
                    LATENCY TARGET
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 700, color: '#f1f5f9' }}>
                    Sub-millisecond KV Cache
                  </Typography>
                </Box>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card sx={{ p: 1.5, display: 'flex', alignItems: 'center', gap: 1.5, backgroundColor: 'rgba(15, 23, 42, 0.5)' }}>
                <StorageRoundedIcon sx={{ color: '#a855f7' }} />
                <Box>
                  <Typography variant="caption" sx={{ color: '#64748b', display: 'block', fontWeight: 600 }}>
                    GRID TOPOLOGY
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 700, color: '#f1f5f9' }}>
                    Distributed Partitioning
                  </Typography>
                </Box>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card sx={{ p: 1.5, display: 'flex', alignItems: 'center', gap: 1.5, backgroundColor: 'rgba(15, 23, 42, 0.5)' }}>
                <SecurityRoundedIcon sx={{ color: '#10b981' }} />
                <Box>
                  <Typography variant="caption" sx={{ color: '#64748b', display: 'block', fontWeight: 600 }}>
                    RELIABILITY
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 700, color: '#f1f5f9' }}>
                    Deterministic Request UUIDs
                  </Typography>
                </Box>
              </Card>
            </Grid>
          </Grid>

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
          <Box sx={{ mt: 3 }}>
            <ResponsePanel responseData={responseData} />
          </Box>
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

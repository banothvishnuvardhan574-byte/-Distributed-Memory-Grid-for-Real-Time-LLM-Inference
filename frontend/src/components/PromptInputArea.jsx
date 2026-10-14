import React from 'react';
import {
  Paper,
  Box,
  Typography,
  TextField,
  Button,
  Chip,
  Stack,
  Tooltip,
} from '@mui/material';
import SendRoundedIcon from '@mui/icons-material/SendRounded';
import ClearAllRoundedIcon from '@mui/icons-material/ClearAllRounded';
import AutoAwesomeRoundedIcon from '@mui/icons-material/AutoAwesomeRounded';
import KeyboardReturnRoundedIcon from '@mui/icons-material/KeyboardReturnRounded';

const SAMPLE_PROMPTS = [
  'Explain distributed memory grids and KV caching in LLM clusters',
  'How do memory partition hashing and consistency hash rings reduce inference latency?',
  'Analyze cache hit rates for multi-tenant generative AI workloads',
];

export default function PromptInputArea({
  prompt,
  setPrompt,
  onSubmit,
  isLoading,
  onClear,
}) {
  const trimmedPrompt = (prompt || '').trim();
  const charCount = (prompt || '').length;
  const wordCount = trimmedPrompt ? trimmedPrompt.split(/\s+/).length : 0;
  // Estimate tokens (~4 chars per token)
  const tokenEstimate = Math.ceil(charCount / 4);
  const isSubmitDisabled = isLoading || trimmedPrompt.length === 0;

  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      if (!isSubmitDisabled) {
        onSubmit();
      }
    }
  };

  const handleSelectSample = (sample) => {
    setPrompt(sample);
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: { xs: 2.5, sm: 3 },
        borderRadius: 3.5,
        position: 'relative',
        overflow: 'hidden',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        background: 'linear-gradient(180deg, rgba(17, 24, 39, 0.85) 0%, rgba(15, 23, 42, 0.7) 100%)',
      }}
    >
      {/* Title & Prompt suggestions */}
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <AutoAwesomeRoundedIcon sx={{ color: '#818cf8', fontSize: 20 }} />
          <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#f1f5f9' }}>
            Inference Prompt Input
          </Typography>
        </Box>
        <Typography variant="caption" sx={{ color: '#94a3b8', display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <KeyboardReturnRoundedIcon sx={{ fontSize: 14 }} />
          Press <strong>Ctrl + Enter</strong> to submit
        </Typography>
      </Box>

      {/* Suggested prompts */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="caption" sx={{ color: '#64748b', display: 'block', mb: 0.8, fontWeight: 500 }}>
          Quick Test Prompts:
        </Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ gap: 1 }}>
          {SAMPLE_PROMPTS.map((sample, idx) => (
            <Chip
              key={idx}
              label={sample}
              size="small"
              onClick={() => handleSelectSample(sample)}
              disabled={isLoading}
              sx={{
                fontSize: '0.75rem',
                backgroundColor: 'rgba(99, 102, 241, 0.08)',
                color: '#cbd5e1',
                border: '1px solid rgba(99, 102, 241, 0.2)',
                '&:hover': {
                  backgroundColor: 'rgba(99, 102, 241, 0.2)',
                  borderColor: '#818cf8',
                  color: '#ffffff',
                },
              }}
            />
          ))}
        </Stack>
      </Box>

      {/* The required Text Area for prompt input */}
      <TextField
        id="prompt-input"
        multiline
        rows={4}
        fullWidth
        placeholder="Enter your prompt here... (e.g., query distributed memory cache, test node routing, or run inference)"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={isLoading}
        variant="outlined"
        inputProps={{
          'aria-label': 'Prompt input text area',
          id: 'prompt-textarea',
        }}
        sx={{
          mb: 2,
          '& .MuiOutlinedInput-root': {
            fontFamily: "'Inter', sans-serif",
            fontSize: '0.975rem',
            lineHeight: 1.6,
          },
        }}
      />

      {/* Toolbar / stats & Primary Submit Button */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 1.5,
        }}
      >
        {/* Real-time stats */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="caption" sx={{ color: '#94a3b8', fontFamily: "'JetBrains Mono', monospace" }}>
            Chars: <strong>{charCount}</strong>
          </Typography>
          <Typography variant="caption" sx={{ color: '#94a3b8', fontFamily: "'JetBrains Mono', monospace" }}>
            Words: <strong>{wordCount}</strong>
          </Typography>
          <Tooltip title="Estimated token count (~4 characters per token)">
            <Typography variant="caption" sx={{ color: '#818cf8', fontFamily: "'JetBrains Mono', monospace" }}>
              ~Tokens: <strong>{tokenEstimate}</strong>
            </Typography>
          </Tooltip>
        </Box>

        {/* Action buttons */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          {charCount > 0 && (
            <Button
              id="clear-prompt-btn"
              variant="text"
              size="small"
              onClick={onClear}
              disabled={isLoading}
              startIcon={<ClearAllRoundedIcon />}
              sx={{ color: '#94a3b8', '&:hover': { color: '#f87171' } }}
            >
              Clear
            </Button>
          )}

          {/* Required Primary Submit Button */}
          <Button
            id="submit-prompt-btn"
            variant="contained"
            color="primary"
            onClick={onSubmit}
            disabled={isSubmitDisabled}
            endIcon={<SendRoundedIcon />}
            sx={{
              px: 3.5,
              py: 1.2,
              fontWeight: 600,
              letterSpacing: '0.02em',
              fontSize: '0.95rem',
            }}
          >
            {isLoading ? 'Submitting...' : 'Submit Prompt'}
          </Button>
        </Box>
      </Box>
    </Paper>
  );
}

import React, { useState } from 'react';
import {
  Paper,
  Box,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Divider,
  Snackbar,
  Alert,
} from '@mui/material';
import ContentCopyRoundedIcon from '@mui/icons-material/ContentCopyRounded';
import CheckCircleOutlineRoundedIcon from '@mui/icons-material/CheckCircleOutlineRounded';
import InsightsRoundedIcon from '@mui/icons-material/InsightsRounded';
import FingerprintRoundedIcon from '@mui/icons-material/FingerprintRounded';
import TimerOutlinedIcon from '@mui/icons-material/TimerOutlined';
import ForumRoundedIcon from '@mui/icons-material/ForumRounded';

export default function ResponsePanel({ responseData }) {
  const [copiedField, setCopiedField] = useState(null);
  const [toastOpen, setToastOpen] = useState(false);

  const handleCopy = (text, field) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    setToastOpen(true);
    setTimeout(() => setCopiedField(null), 2500);
  };

  if (!responseData) {
    return (
      <Paper
        id="response-panel"
        elevation={2}
        sx={{
          p: 5,
          borderRadius: 3.5,
          textAlign: 'center',
          backgroundColor: 'rgba(15, 23, 42, 0.45)',
          border: '1px dashed rgba(255, 255, 255, 0.12)',
        }}
      >
        <Box
          sx={{
            display: 'inline-flex',
            p: 2,
            borderRadius: '50%',
            backgroundColor: 'rgba(99, 102, 241, 0.08)',
            mb: 2,
          }}
        >
          <ForumRoundedIcon sx={{ fontSize: 36, color: '#6366f1' }} />
        </Box>
        <Typography variant="h6" sx={{ color: '#cbd5e1', fontWeight: 600, mb: 0.5 }}>
          No Inference Response Yet
        </Typography>
        <Typography variant="body2" sx={{ color: '#64748b', maxWidth: 440, mx: 'auto' }}>
          Enter a prompt above and click <strong>Submit Prompt</strong> to query the distributed memory grid and view the model response with its unique Request ID.
        </Typography>
      </Paper>
    );
  }

  const {
    request_id,
    message,
    response: generatedResponse,
    generated_text,
    status = 'accepted',
    latency = null,
    timestamp = '',
    prompt = '',
  } = responseData;

  // Distinguish between a generated AI output and a backend acknowledgment
  const hasGeneratedAnswer = Boolean(generated_text || generatedResponse);
  const displayContent =
    generated_text ||
    generatedResponse ||
    message ||
    'Request received and processed by memory grid.';

  return (
    <>
      {/* Required Response Panel */}
      <Paper
        id="response-panel"
        elevation={4}
        className="glow-card"
        sx={{
          p: { xs: 2.5, sm: 3.5 },
          borderRadius: 3.5,
          backgroundColor: 'rgba(17, 24, 39, 0.85)',
          border: '1px solid rgba(99, 102, 241, 0.25)',
          backdropFilter: 'blur(20px)',
        }}
      >
        {/* Panel Header: Status, Timestamp, Latency */}
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 1.5,
            mb: 2.5,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <InsightsRoundedIcon sx={{ color: '#38bdf8', fontSize: 22 }} />
            <Typography variant="h6" sx={{ fontWeight: 700, color: '#f8fafc' }}>
              Inference Response Output
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              icon={<CheckCircleOutlineRoundedIcon sx={{ fontSize: '16px !important', color: '#34d399 !important' }} />}
              label={`Status: ${status}`}
              size="small"
              sx={{
                backgroundColor: 'rgba(16, 185, 129, 0.12)',
                color: '#34d399',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                fontWeight: 600,
                textTransform: 'capitalize',
              }}
            />

            {latency && (
              <Chip
                icon={<TimerOutlinedIcon sx={{ fontSize: '15px !important' }} />}
                label={`${latency} ms`}
                size="small"
                sx={{
                  backgroundColor: 'rgba(56, 189, 248, 0.1)',
                  color: '#38bdf8',
                  border: '1px solid rgba(56, 189, 248, 0.25)',
                  fontFamily: "'JetBrains Mono', monospace",
                  fontWeight: 600,
                }}
              />
            )}

            <Typography variant="caption" sx={{ color: '#64748b', ml: 0.5 }}>
              {timestamp}
            </Typography>
          </Box>
        </Box>

        {/* Required Request ID Display with Copy Button */}
        <Box
          sx={{
            p: 1.5,
            mb: 2.5,
            borderRadius: 2.5,
            backgroundColor: 'rgba(10, 13, 20, 0.75)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: 1,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FingerprintRoundedIcon sx={{ color: '#a855f7', fontSize: 20 }} />
            <Typography variant="caption" sx={{ color: '#94a3b8', fontWeight: 600 }}>
              Request ID:
            </Typography>
            <Typography
              id="request-id-display"
              component="span"
              sx={{
                fontFamily: "'JetBrains Mono', monospace",
                fontWeight: 600,
                color: '#c084fc',
                fontSize: { xs: '0.78rem', sm: '0.875rem' },
                userSelect: 'all',
              }}
            >
              {request_id || 'N/A'}
            </Typography>
          </Box>

          <Tooltip title={copiedField === 'request_id' ? 'Copied Request ID!' : 'Copy Request ID'}>
            <IconButton
              id="copy-request-id-btn"
              size="small"
              onClick={() => handleCopy(request_id, 'request_id')}
              sx={{
                color: copiedField === 'request_id' ? '#34d399' : '#94a3b8',
                backgroundColor: 'rgba(255, 255, 255, 0.04)',
                '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.1)', color: '#ffffff' },
              }}
            >
              <ContentCopyRoundedIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>

        {/* Submitted Prompt Summary */}
        {prompt && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" sx={{ color: '#64748b', display: 'block', mb: 0.5, fontWeight: 600 }}>
              Submitted Prompt:
            </Typography>
            <Box
              sx={{
                p: 1.5,
                borderRadius: 2,
                backgroundColor: 'rgba(15, 23, 42, 0.4)',
                border: '1px solid rgba(255, 255, 255, 0.05)',
                color: '#cbd5e1',
                fontSize: '0.875rem',
                fontStyle: 'italic',
              }}
            >
              "{prompt}"
            </Box>
          </Box>
        )}

        <Divider sx={{ my: 2, borderColor: 'rgba(255, 255, 255, 0.08)' }} />

        {/* Required Model Output or Acknowledgment Display */}
        <Box sx={{ position: 'relative' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="caption" sx={{ color: hasGeneratedAnswer ? '#38bdf8' : '#818cf8', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                {hasGeneratedAnswer ? 'Generated AI Output' : 'Backend Acknowledgment & Status'}
              </Typography>
              <Chip
                label={hasGeneratedAnswer ? 'Generated Answer' : 'Request Acknowledgment'}
                size="small"
                sx={{
                  height: 20,
                  fontSize: '0.65rem',
                  fontWeight: 600,
                  backgroundColor: hasGeneratedAnswer ? 'rgba(56, 189, 248, 0.15)' : 'rgba(99, 102, 241, 0.15)',
                  color: hasGeneratedAnswer ? '#38bdf8' : '#a5b4fc',
                  border: `1px solid ${hasGeneratedAnswer ? 'rgba(56, 189, 248, 0.3)' : 'rgba(99, 102, 241, 0.3)'}`,
                }}
              />
            </Box>
            <Tooltip title={copiedField === 'output' ? 'Copied text!' : 'Copy Text'}>
              <IconButton
                id="copy-model-output-btn"
                size="small"
                onClick={() => handleCopy(displayContent, 'output')}
                sx={{
                  color: copiedField === 'output' ? '#34d399' : '#94a3b8',
                  '&:hover': { color: '#ffffff' },
                }}
              >
                <ContentCopyRoundedIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>

          <Box
            id="model-output-text"
            sx={{
              p: 2.5,
              borderRadius: 2.5,
              backgroundColor: 'rgba(10, 13, 20, 0.85)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              color: '#f1f5f9',
              fontFamily: "'Inter', sans-serif",
              fontSize: '0.95rem',
              lineHeight: 1.7,
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              maxHeight: 380,
              overflowY: 'auto',
            }}
          >
            {displayContent}
          </Box>
        </Box>
      </Paper>

      <Snackbar
        open={toastOpen}
        autoHideDuration={2500}
        onClose={() => setToastOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity="success" sx={{ width: '100%', backgroundColor: '#064e3b', color: '#6ee7b7' }}>
          Copied to clipboard!
        </Alert>
      </Snackbar>
    </>
  );
}

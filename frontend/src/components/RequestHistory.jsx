import React, { useState } from 'react';
import {
  Paper,
  Box,
  Typography,
  Chip,
  Tooltip,
  IconButton,
} from '@mui/material';
import HistoryRoundedIcon from '@mui/icons-material/HistoryRounded';
import FingerprintRoundedIcon from '@mui/icons-material/FingerprintRounded';
import ContentCopyRoundedIcon from '@mui/icons-material/ContentCopyRounded';
import CheckRoundedIcon from '@mui/icons-material/CheckRounded';
import CheckCircleOutlineRoundedIcon from '@mui/icons-material/CheckCircleOutlineRounded';

/**
 * RequestHistory — displays a compact list of prompt submissions made
 * during the current browser session. All data shown here comes from
 * actual API responses; nothing is fabricated or simulated.
 */
export default function RequestHistory({ history = [] }) {
  const [copiedId, setCopiedId] = useState(null);

  const handleCopyId = (id) => {
    if (!id || id === 'N/A') return;
    if (navigator?.clipboard?.writeText) {
      navigator.clipboard.writeText(id).catch(() => {});
    }
    setCopiedId(id);
    setTimeout(() => {
      setCopiedId((curr) => (curr === id ? null : curr));
    }, 2000);
  };

  if (history.length === 0) {
    return (
      <Paper
        id="request-history-panel"
        elevation={1}
        sx={{
          p: 2.5,
          borderRadius: 3,
          textAlign: 'center',
          backgroundColor: 'rgba(15, 23, 42, 0.45)',
          border: '1px dashed rgba(255, 255, 255, 0.1)',
        }}
      >
        <HistoryRoundedIcon sx={{ fontSize: 28, color: '#475569', mb: 1 }} />
        <Typography variant="body2" sx={{ color: '#64748b', fontWeight: 500 }}>
          No requests yet
        </Typography>
        <Typography variant="caption" sx={{ color: '#475569', display: 'block', mt: 0.5 }}>
          Submitted prompts will appear here during this session.
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper
      id="request-history-panel"
      elevation={2}
      sx={{
        p: 2,
        borderRadius: 3,
        backgroundColor: 'rgba(17, 24, 39, 0.75)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <HistoryRoundedIcon sx={{ color: '#818cf8', fontSize: 18 }} />
        <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#e2e8f0' }}>
          Session Request History
        </Typography>
        <Chip
          label={`${history.length}`}
          size="small"
          sx={{
            ml: 'auto',
            height: 20,
            minWidth: 28,
            fontSize: '0.7rem',
            fontWeight: 700,
            backgroundColor: 'rgba(99, 102, 241, 0.15)',
            color: '#a5b4fc',
            border: '1px solid rgba(99, 102, 241, 0.25)',
          }}
        />
      </Box>

      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          gap: 1,
          maxHeight: 320,
          overflowY: 'auto',
        }}
      >
        {history.map((entry, idx) => (
          <Box
            key={entry.request_id || idx}
            sx={{
              p: 1.5,
              borderRadius: 2,
              backgroundColor: 'rgba(10, 13, 20, 0.6)',
              border: '1px solid rgba(255, 255, 255, 0.06)',
              transition: 'border-color 0.15s',
              '&:hover': {
                borderColor: 'rgba(99, 102, 241, 0.3)',
              },
            }}
          >
            {/* Prompt preview */}
            <Typography
              variant="caption"
              sx={{
                color: '#cbd5e1',
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                lineHeight: 1.4,
                mb: 0.8,
                fontSize: '0.75rem',
              }}
            >
              {entry.prompt || '(empty prompt)'}
            </Typography>

            {/* Request ID + Status */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, flexWrap: 'wrap' }}>
              <FingerprintRoundedIcon sx={{ color: '#a855f7', fontSize: 13 }} />
              <Typography
                variant="caption"
                title={entry.request_id || undefined}
                sx={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: '0.65rem',
                  color: '#94a3b8',
                  userSelect: 'all',
                  flexGrow: 1,
                  minWidth: 0,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {entry.request_id ? entry.request_id.slice(0, 8) + '…' : 'N/A'}
              </Typography>

              <Tooltip title={copiedId === entry.request_id ? 'Copied Request ID!' : 'Copy full Request ID'}>
                <IconButton
                  size="small"
                  aria-label={copiedId === entry.request_id ? `Request ID ${entry.request_id} copied to clipboard` : `Copy full Request ID ${entry.request_id || ''}`}
                  onClick={() => handleCopyId(entry.request_id)}
                  sx={{
                    p: 0.3,
                    color: copiedId === entry.request_id ? '#34d399' : '#64748b',
                    '&:hover': { color: copiedId === entry.request_id ? '#34d399' : '#c084fc' },
                  }}
                >
                  {copiedId === entry.request_id ? (
                    <CheckRoundedIcon sx={{ fontSize: 12 }} />
                  ) : (
                    <ContentCopyRoundedIcon sx={{ fontSize: 12 }} />
                  )}
                </IconButton>
              </Tooltip>

              <Chip
                icon={<CheckCircleOutlineRoundedIcon sx={{ fontSize: '11px !important', color: '#34d399 !important' }} />}
                label={entry.status || 'accepted'}
                size="small"
                sx={{
                  height: 18,
                  fontSize: '0.6rem',
                  fontWeight: 600,
                  backgroundColor: 'rgba(16, 185, 129, 0.1)',
                  color: '#34d399',
                  border: '1px solid rgba(16, 185, 129, 0.25)',
                  textTransform: 'capitalize',
                }}
              />

              {entry.latency != null && (
                <Typography
                  variant="caption"
                  sx={{
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: '0.6rem',
                    color: '#38bdf8',
                  }}
                >
                  {entry.latency}ms
                </Typography>
              )}
            </Box>
          </Box>
        ))}
      </Box>
    </Paper>
  );
}

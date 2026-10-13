import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import MemoryIcon from '@mui/icons-material/Memory';
import HubIcon from '@mui/icons-material/Hub';
import GitHubIcon from '@mui/icons-material/GitHub';
import TerminalIcon from '@mui/icons-material/Terminal';

export default function Header() {
  return (
    <AppBar
      position="static"
      elevation={0}
      sx={{
        backgroundColor: 'rgba(10, 13, 20, 0.85)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        px: { xs: 1, md: 3 },
      }}
    >
      <Toolbar disableGutters sx={{ justifyContent: 'space-between' }}>
        {/* Brand & Title */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 42,
              height: 42,
              borderRadius: 2.5,
              background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
              boxShadow: '0 0 16px rgba(99, 102, 241, 0.5)',
            }}
          >
            <MemoryIcon sx={{ color: '#fff', fontSize: 26 }} />
          </Box>
          <Box>
            <Typography
              variant="h6"
              component="h1"
              sx={{
                fontWeight: 700,
                letterSpacing: '-0.02em',
                background: 'linear-gradient(90deg, #ffffff 0%, #cbd5e1 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                lineHeight: 1.2,
              }}
            >
              LLM MemoryGrid
            </Typography>
            <Typography
              variant="caption"
              sx={{
                color: '#94a3b8',
                display: 'block',
                fontWeight: 500,
                letterSpacing: '0.04em',
                textTransform: 'uppercase',
                fontSize: '0.68rem',
              }}
            >
              Distributed Real-Time Inference
            </Typography>
          </Box>
        </Box>

        {/* Status badges & info */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Tooltip title="Current active Git branch">
            <Chip
              id="branch-indicator-chip"
              icon={<TerminalIcon sx={{ fontSize: '16px !important' }} />}
              label="tirth-ui"
              size="small"
              sx={{
                backgroundColor: 'rgba(99, 102, 241, 0.15)',
                color: '#818cf8',
                border: '1px solid rgba(99, 102, 241, 0.3)',
                fontFamily: "'JetBrains Mono', monospace",
                fontWeight: 600,
                fontSize: '0.75rem',
                display: { xs: 'none', sm: 'inline-flex' },
              }}
            />
          </Tooltip>

          <Tooltip title="Memory grid node connectivity status">
            <Chip
              id="grid-status-chip"
              icon={<HubIcon sx={{ fontSize: '16px !important', color: '#10b981 !important' }} />}
              label="Grid Node Ready"
              size="small"
              sx={{
                backgroundColor: 'rgba(16, 185, 129, 0.12)',
                color: '#34d399',
                border: '1px solid rgba(16, 185, 129, 0.25)',
                fontWeight: 600,
                fontSize: '0.75rem',
              }}
            />
          </Tooltip>

          <Tooltip title="View Project GitHub Repository">
            <IconButton
              id="github-repo-link"
              component="a"
              href="https://github.com/banothvishnuvardhan574-byte/-Distributed-Memory-Grid-for-Real-Time-LLM-Inference"
              target="_blank"
              rel="noopener noreferrer"
              size="small"
              sx={{
                color: '#94a3b8',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                '&:hover': { color: '#ffffff', backgroundColor: 'rgba(255, 255, 255, 0.05)' },
              }}
            >
              <GitHubIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

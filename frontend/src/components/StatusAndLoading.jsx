import React from 'react';
import {
  Box,
  Alert,
  AlertTitle,
  LinearProgress,
  Typography,
  Collapse,
  Button,
  CircularProgress,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import ErrorOutlineRoundedIcon from '@mui/icons-material/ErrorOutlineRounded';

export default function StatusAndLoading({
  isLoading,
  loadingStep = 'Dispatching prompt to distributed grid...',
  error,
  onDismissError,
  onRetry,
}) {
  return (
    <Box sx={{ my: 2.5 }}>
      {/* Required Loading Indicator */}
      <Collapse in={isLoading}>
        <Box
          id="loading-indicator"
          sx={{
            p: 2.5,
            borderRadius: 3,
            backgroundColor: 'rgba(30, 41, 59, 0.7)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            boxShadow: '0 4px 20px rgba(99, 102, 241, 0.15)',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1.5 }}>
            <CircularProgress size={24} sx={{ color: '#818cf8' }} thickness={5} />
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, color: '#e2e8f0' }}>
                Processing Request in Memory Grid
              </Typography>
              <Typography variant="caption" sx={{ color: '#94a3b8' }}>
                {loadingStep}
              </Typography>
            </Box>
          </Box>
          <LinearProgress
            sx={{
              height: 6,
              borderRadius: 3,
              backgroundColor: 'rgba(255, 255, 255, 0.08)',
              '& .MuiLinearProgress-bar': {
                background: 'linear-gradient(90deg, #6366f1, #a855f7, #38bdf8)',
              },
            }}
          />
        </Box>
      </Collapse>

      {/* Required Error Message Area */}
      <Collapse in={Boolean(error)}>
        <Box id="error-message-area">
          <Alert
            id="error-alert"
            severity="error"
            icon={<ErrorOutlineRoundedIcon fontSize="inherit" />}
            onClose={onDismissError}
            action={
              onRetry && (
                <Button
                  id="retry-request-btn"
                  color="inherit"
                  size="small"
                  onClick={onRetry}
                  startIcon={<RefreshIcon />}
                  sx={{ textTransform: 'none', fontWeight: 600 }}
                >
                  Retry
                </Button>
              )
            }
            sx={{
              borderRadius: 3,
              backgroundColor: 'rgba(153, 27, 27, 0.25)',
              border: '1px solid rgba(248, 113, 113, 0.3)',
              color: '#fecaca',
              '& .MuiAlert-icon': {
                color: '#f87171',
              },
            }}
          >
            <AlertTitle sx={{ fontWeight: 700, color: '#fca5a5' }}>
              Submission Error
            </AlertTitle>
            <Typography variant="body2" sx={{ wordBreak: 'break-word' }}>
              {error}
            </Typography>
          </Alert>
        </Box>
      </Collapse>
    </Box>
  );
}

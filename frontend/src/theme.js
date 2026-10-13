import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#6366f1', // Indigo
      light: '#818cf8',
      dark: '#4f46e5',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#a855f7', // Purple
      light: '#c084fc',
      dark: '#9333ea',
    },
    info: {
      main: '#38bdf8', // Sky
    },
    success: {
      main: '#10b981', // Emerald
    },
    error: {
      main: '#f43f5e', // Rose
    },
    background: {
      default: '#0a0d14',
      paper: '#111827',
    },
    text: {
      primary: '#f9fafb',
      secondary: '#9ca3af',
    },
  },
  typography: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    h1: {
      fontFamily: "'Outfit', sans-serif",
      fontWeight: 700,
    },
    h2: {
      fontFamily: "'Outfit', sans-serif",
      fontWeight: 700,
    },
    h3: {
      fontFamily: "'Outfit', sans-serif",
      fontWeight: 600,
    },
    h4: {
      fontFamily: "'Outfit', sans-serif",
      fontWeight: 600,
    },
    h5: {
      fontFamily: "'Outfit', sans-serif",
      fontWeight: 600,
    },
    h6: {
      fontFamily: "'Outfit', sans-serif",
      fontWeight: 600,
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: 'rgba(17, 24, 39, 0.75)',
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          padding: '10px 24px',
          transition: 'all 0.2s ease-in-out',
        },
        containedPrimary: {
          background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%)',
          boxShadow: '0 4px 14px 0 rgba(99, 102, 241, 0.39)',
          '&:hover': {
            background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #c026d3 100%)',
            boxShadow: '0 6px 20px rgba(99, 102, 241, 0.6)',
            transform: 'translateY(-1px)',
          },
          '&:active': {
            transform: 'translateY(0)',
          },
          '&.Mui-disabled': {
            background: 'rgba(255, 255, 255, 0.12)',
            color: 'rgba(255, 255, 255, 0.3)',
          },
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(15, 23, 42, 0.6)',
          borderRadius: 12,
          '& fieldset': {
            borderColor: 'rgba(255, 255, 255, 0.12)',
          },
          '&:hover fieldset': {
            borderColor: 'rgba(99, 102, 241, 0.5)',
          },
          '&.Mui-focused fieldset': {
            borderColor: '#6366f1',
            borderWidth: 2,
            boxShadow: '0 0 16px rgba(99, 102, 241, 0.25)',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
          borderRadius: 8,
        },
      },
    },
  },
});

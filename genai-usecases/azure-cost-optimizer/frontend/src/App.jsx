import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { Box, Card, CardContent, Typography, TextField, Button, Alert, CircularProgress, InputAdornment } from '@mui/material';
import LoginIcon from '@mui/icons-material/Login';
import PersonIcon from '@mui/icons-material/Person';
import LockIcon from '@mui/icons-material/Lock';
import logo from './assets/new_logo.png';
import Layout from './components/Layout/Layout';
import Dashboard from './components/Dashboard/Dashboard';
import Recommendations from './components/Recommendations/Recommendations';
import Forecasting from './components/Forecasting/Forecasting';
import Gamification from './components/Gamification/Gamification';
import AgentReview from './components/AgentReview/AgentReview';
import SubscriptionDetail from './components/SubscriptionDetail/SubscriptionDetail';
import { useAuthStore } from './store/store';
import { login as apiLogin } from './services/api';

const theme = createTheme({
  palette: {
    primary: { main: '#0078d4' },
    secondary: { main: '#50e6ff' },
    success: { main: '#2e7d32' },
    warning: { main: '#ed6c02' },
    error: { main: '#d32f2f' },
    background: { default: '#f5f5f5', paper: '#ffffff' },
  },
  typography: {
    fontFamily: '"Inter", "Segoe UI", "Roboto", sans-serif',
    h4: { fontWeight: 700 },
    h6: { fontWeight: 600 },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: { borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.08)' },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 8, textTransform: 'none', fontWeight: 600 },
      },
    },
  },
});

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuthStore();
  if (!isAuthenticated) return <Navigate to="/login" />;
  return <Layout>{children}</Layout>;
}

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { setAuth } = useAuthStore();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await apiLogin(username, password);
      setAuth(res.data.user, res.data.token);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', bgcolor: '#f0f4f8' }}>
      <Card
        sx={{
          width: 450,
          p: 4,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
          border: '1px solid rgba(0, 120, 212, 0.08)',
          transition: 'box-shadow 0.3s ease',
          '&:hover': {
            boxShadow: '0 12px 48px rgba(0, 0, 0, 0.15)',
          }
        }}
      >
        <CardContent>
          <Box sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mb: 2,
            animation: 'fadeInDown 1s ease-out',
            '@keyframes fadeInDown': {
              '0%': {
                opacity: 0,
                transform: 'translateY(-20px)',
              },
              '100%': {
                opacity: 1,
                transform: 'translateY(0)',
              },
            }
          }}>
            {/* Logo */}
            <img
              src={logo}
              alt="Nebula Logo"
              style={{
                width: '300px',
                height: 'auto',
                objectFit: 'contain',
              }}
            />
          </Box>
          <Typography variant="body2" align="center" color="text.secondary" sx={{ mb: 0.5 }}>
            Cloud Cost Optimizer
          </Typography>
          <Typography variant="caption" align="center" display="block" sx={{ color: 'text.disabled', mb: 3 }}>
            AI-Powered Multi-Cloud Cost Management
          </Typography>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <form onSubmit={handleLogin}>
            <TextField
              fullWidth
              label="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              sx={{
                mb: 2,
                '& .MuiInputBase-input': {
                  pl: 1,
                }
              }}
              InputLabelProps={{ shrink: true }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start" sx={{ mr: 2, ml: 1 }}>
                    <PersonIcon sx={{ color: '#0078d4', fontSize: '20px' }} />
                  </InputAdornment>
                ),
              }}
            />
            <TextField
              fullWidth
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              sx={{
                mb: 3,
                '& .MuiInputBase-input': {
                  pl: 1,
                }
              }}
              InputLabelProps={{ shrink: true }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start" sx={{ mr: 2, ml: 1 }}>
                    <LockIcon sx={{ color: '#0078d4', fontSize: '20px' }} />
                  </InputAdornment>
                ),
              }}
            />
            <Button
              fullWidth
              variant="contained"
              type="submit"
              disabled={loading}
              size="large"
              endIcon={loading ? <CircularProgress size={20} color="inherit" /> : <LoginIcon />}
              sx={{
                py: 1.5,
                fontSize: '1rem',
                fontWeight: 600,
                background: 'linear-gradient(135deg, #0078d4 0%, #005a9e 100%)',
                boxShadow: '0 4px 20px rgba(0, 120, 212, 0.4), 0 0 40px rgba(0, 120, 212, 0.2)',
                transition: 'all 0.3s ease',
                position: 'relative',
                overflow: 'hidden',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: '-100%',
                  width: '100%',
                  height: '100%',
                  background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent)',
                  transition: 'left 0.5s',
                },
                '&:hover': {
                  background: 'linear-gradient(135deg, #005a9e 0%, #004578 100%)',
                  boxShadow: '0 6px 25px rgba(0, 120, 212, 0.5), 0 0 50px rgba(0, 120, 212, 0.3)',
                  transform: 'translateY(-2px)',
                  '&::before': {
                    left: '100%',
                  },
                },
                '&:active': {
                  transform: 'translateY(0)',
                  boxShadow: '0 2px 10px rgba(0, 120, 212, 0.4)',
                },
                '&:disabled': {
                  background: 'linear-gradient(135deg, #ccc 0%, #999 100%)',
                  boxShadow: 'none',
                },
              }}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
}

export default function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={isAuthenticated ? <Navigate to="/" /> : <LoginPage />} />
          <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/recommendations" element={<ProtectedRoute><Recommendations /></ProtectedRoute>} />
          <Route path="/forecasting" element={<ProtectedRoute><Forecasting /></ProtectedRoute>} />
          <Route path="/gamification" element={<ProtectedRoute><Gamification /></ProtectedRoute>} />
          <Route path="/agent-review" element={<ProtectedRoute><AgentReview /></ProtectedRoute>} />
          <Route path="/subscriptions/:id" element={<ProtectedRoute><SubscriptionDetail /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
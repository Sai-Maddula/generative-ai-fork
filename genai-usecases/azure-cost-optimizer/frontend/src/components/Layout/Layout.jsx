import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  AppBar,
  Box,
  Drawer,
  Toolbar,
  Typography,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  IconButton,
  Avatar,
  Tooltip,
  Chip,
  ToggleButtonGroup,
  ToggleButton,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import GavelIcon from '@mui/icons-material/Gavel';
import LogoutIcon from '@mui/icons-material/Logout';
import { useAuthStore, useAppStore } from '../../store/store';
import { getHITLQueue } from '../../services/api';
import ChatWidget from '../ChatWidget/ChatWidget';
import NTTLogo from '../../assets/NTTLogo';
import AzureLogo from '../../assets/AzureLogo';
import AWSLogo from '../../assets/AWSLogo';

const DRAWER_WIDTH = 240;

const navItems = [
  { label: 'Dashboard', icon: <DashboardIcon />, route: '/' },
  { label: 'Recommendations', icon: <LightbulbIcon />, route: '/recommendations' },
  { label: 'Agent Review', icon: <GavelIcon />, route: '/agent-review' },
  { label: 'Forecasting', icon: <TrendingUpIcon />, route: '/forecasting' },
  { label: 'Gamification', icon: <EmojiEventsIcon />, route: '/gamification' },
];

const Layout = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { selectedProvider, setSelectedProvider } = useAppStore();
  const [hitlCount, setHitlCount] = useState(0);

  useEffect(() => {
    // Fetch HITL queue count for badge
    const fetchHitlCount = async () => {
      try {
        const res = await getHITLQueue();
        setHitlCount(res.data.length);
      } catch { /* ignore */ }
    };
    fetchHitlCount();
    const interval = setInterval(fetchHitlCount, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (route) => {
    if (route === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(route);
  };

  const getCurrentPageTitle = () => {
    const currentNavItem = navItems.find((item) => {
      if (item.route === '/') {
        return location.pathname === '/';
      }
      return location.pathname.startsWith(item.route);
    });
    return currentNavItem?.label || 'Dashboard';
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', maxWidth: '100vw', overflowX: 'hidden' }}>
      {/* Sidebar Drawer */}
      <Drawer
        variant="permanent"
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            background: 'linear-gradient(180deg, #0a1929 0%, #0d2744 100%)',
            color: '#ffffff',
            borderRight: 'none',
          },
        }}
      >
        {/* Brand */}
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            px: 1,
            py: 0.5,
            pb: 2,
          }}
        >
          {/* NTT Logo */}
          <NTTLogo width={180} height={80} />
          <Typography
            variant="caption"
            sx={{
              color: 'rgba(255, 255, 255, 0.7)',
              mt: 0,
              textAlign: 'left',
              fontSize: '0.7rem',
            }}
          >
            Multi-Cloud Cost Optimizer
          </Typography>
        </Box>

        <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.08)', mx: 1.5 }} />

        {/* Navigation */}
        <List sx={{ px: 1.5, mt: 1 }}>
          {navItems.map((item) => {
            const active = isActive(item.route);
            return (
              <ListItemButton
                key={item.route}
                onClick={() => navigate(item.route)}
                selected={active}
                sx={{
                  borderRadius: 2,
                  mb: 0.5,
                  color: active ? '#ffffff' : 'rgba(255, 255, 255, 0.65)',
                  backgroundColor: active
                    ? 'rgba(0, 120, 212, 0.35)'
                    : 'transparent',
                  '&:hover': {
                    backgroundColor: active
                      ? 'rgba(0, 120, 212, 0.45)'
                      : 'rgba(255, 255, 255, 0.06)',
                  },
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(0, 120, 212, 0.35)',
                    '&:hover': {
                      backgroundColor: 'rgba(0, 120, 212, 0.45)',
                    },
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 40,
                    color: active ? '#50e6ff' : 'rgba(255, 255, 255, 0.5)',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.label}
                  primaryTypographyProps={{
                    fontSize: '0.9rem',
                    fontWeight: active ? 600 : 400,
                  }}
                />
                {/* HITL badge on Agent Review */}
                {item.route === '/agent-review' && hitlCount > 0 && (
                  <Chip
                    label={hitlCount}
                    size="small"
                    sx={{
                      height: 20,
                      fontSize: 11,
                      fontWeight: 700,
                      bgcolor: '#ed6c02',
                      color: '#fff',
                      minWidth: 24,
                    }}
                  />
                )}
              </ListItemButton>
            );
          })}
        </List>
      </Drawer>

      {/* Main Content Area */}
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Top AppBar */}
        <AppBar
          position="sticky"
          elevation={0}
          sx={{
            width: '100%',
            backgroundColor: '#ffffff',
            color: '#1a1a1a',
            borderBottom: '1px solid #e0e0e0',
          }}
        >
          <Toolbar sx={{ justifyContent: 'space-between' }}>
            {/* Page Title */}
            <Typography
              variant="h6"
              noWrap
              sx={{ fontWeight: 600, color: '#0078d4' }}
            >
              {getCurrentPageTitle()}
            </Typography>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
              {/* Provider Toggle */}
              <ToggleButtonGroup
                value={selectedProvider}
                exclusive
                onChange={(e, newProvider) => newProvider && setSelectedProvider(newProvider)}
                size="small"
                sx={{
                  '& .MuiToggleButton-root': {
                    px: 2,
                    py: 0.5,
                    fontSize: '0.875rem',
                    border: '1px solid',
                    borderColor: 'divider',
                    bgcolor: '#f5f5f5',
                    color: '#666',
                    fontWeight: 500,
                    transition: 'all 0.2s ease',
                    '&:hover:not(.Mui-selected)': {
                      bgcolor: '#e0e0e0',
                    }
                  }
                }}
              >
                <ToggleButton
                  value="azure"
                  sx={{
                    '&.Mui-selected': {
                      bgcolor: '#0078d4 !important',
                      color: 'white !important',
                      borderColor: '#0078d4 !important',
                      fontWeight: 600,
                      '&:hover': {
                        bgcolor: '#106ebe !important',
                      },
                      '& img': {
                        filter: 'brightness(0) invert(1)',
                      }
                    }
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.8 }}>
                    <AzureLogo width={18} height={18} />
                    <span>Azure</span>
                  </Box>
                </ToggleButton>
                <ToggleButton
                  value="aws"
                  sx={{
                    '&.Mui-selected': {
                      bgcolor: '#FF9900 !important',
                      color: 'white !important',
                      borderColor: '#FF9900 !important',
                      fontWeight: 600,
                      '&:hover': {
                        bgcolor: '#EC7211 !important',
                      },
                      '& img': {
                        filter: 'brightness(0) invert(1)',
                      }
                    }
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.8 }}>
                    <AWSLogo width={22} height={16} />
                    <span>AWS</span>
                  </Box>
                </ToggleButton>
              </ToggleButtonGroup>

              {user && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <Avatar
                    sx={{
                      width: 34,
                      height: 34,
                      bgcolor: '#059669',
                      fontSize: '0.85rem',
                      fontWeight: 600,
                    }}
                  >
                    {user.name
                      ? user.name
                          .split(' ')
                          .map((part) => part[0])
                          .join('')
                          .toUpperCase()
                      : user.username?.charAt(0)?.toUpperCase() || 'U'}
                  </Avatar>
                  <Typography
                    variant="body2"
                    sx={{ fontWeight: 500, color: '#333' }}
                  >
                    {user.name || user.username || 'User'}
                  </Typography>
                </Box>
              )}

              <Tooltip title="Logout">
                <IconButton
                  onClick={handleLogout}
                  size="small"
                  sx={{
                    color: '#666',
                    '&:hover': {
                      color: '#d32f2f',
                      backgroundColor: 'rgba(211, 47, 47, 0.08)',
                    },
                  }}
                >
                  <LogoutIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </Toolbar>
        </AppBar>

        {/* Page Content */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            backgroundColor: '#f5f5f5',
            overflowY: 'auto',
            overflowX: 'hidden',
            maxWidth: '100%',
          }}
        >
          {children}
        </Box>
      </Box>

      {/* Global Chat Widget */}
      <ChatWidget />
    </Box>
  );
};

export default Layout;

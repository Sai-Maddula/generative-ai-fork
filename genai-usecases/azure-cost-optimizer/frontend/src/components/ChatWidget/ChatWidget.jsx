import { useState, useRef, useEffect } from 'react';
import {
  Fab, Box, Typography, TextField, IconButton, Paper, CircularProgress, Badge,
} from '@mui/material';
import { SmartToy, Send, Close, AutoAwesome } from '@mui/icons-material';
import { sendChatMessage } from '../../services/api';

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hi! I'm **Nebula AI**, your Azure cost optimization assistant. Ask me about your spending, anomalies, health scores, or savings opportunities.",
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    setMessages((prev) => [...prev, { role: 'user', content: trimmed }]);
    setInput('');
    setLoading(true);

    try {
      const res = await sendChatMessage(trimmed);
      setMessages((prev) => [...prev, { role: 'assistant', content: res.data.response }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickActions = [
    'What is my highest spending subscription?',
    'Show me anomalies',
    'How is my health score?',
  ];

  const renderMarkdown = (text) => {
    // Simple bold markdown rendering
    return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  };

  return (
    <>
      {/* Floating Action Button */}
      <Fab
        onClick={() => setOpen(!open)}
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          zIndex: 1300,
          width: 56,
          height: 56,
          background: open ? '#333' : 'linear-gradient(135deg, #0078d4, #50e6ff)',
          '&:hover': {
            background: open ? '#555' : 'linear-gradient(135deg, #005a9e, #0078d4)',
          },
          boxShadow: '0 4px 20px rgba(0,120,212,0.35)',
          transition: 'all 0.3s ease',
        }}
      >
        {open ? <Close sx={{ color: '#fff' }} /> : (
          <Badge color="secondary" variant="dot" invisible={messages.length <= 1}>
            <SmartToy sx={{ color: '#fff', fontSize: 28 }} />
          </Badge>
        )}
      </Fab>

      {/* Chat Panel */}
      {open && (
        <Paper
          elevation={12}
          sx={{
            position: 'fixed',
            bottom: 92,
            right: 24,
            width: { xs: 'calc(100vw - 48px)', sm: 400 },
            height: 520,
            display: 'flex',
            flexDirection: 'column',
            borderRadius: 3,
            overflow: 'hidden',
            zIndex: 1200,
            animation: 'slideUp 0.3s ease-out',
            '@keyframes slideUp': {
              from: { opacity: 0, transform: 'translateY(20px)' },
              to: { opacity: 1, transform: 'translateY(0)' },
            },
          }}
        >
          {/* Header */}
          <Box
            sx={{
              px: 2.5,
              py: 1.5,
              background: 'linear-gradient(135deg, #0a1929, #0d2744)',
              color: '#fff',
              display: 'flex',
              alignItems: 'center',
              gap: 1,
            }}
          >
            <AutoAwesome sx={{ color: '#50e6ff', fontSize: 22 }} />
            <Box sx={{ flex: 1 }}>
              <Typography variant="subtitle2" fontWeight={700}>
                Nebula AI
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                Azure Cost Assistant
              </Typography>
            </Box>
            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#2e7d32' }} />
          </Box>

          {/* Messages */}
          <Box sx={{ flex: 1, overflow: 'auto', p: 2, bgcolor: '#f8f9fa' }}>
            {messages.map((msg, i) => (
              <Box
                key={i}
                sx={{
                  display: 'flex',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  mb: 1.5,
                }}
              >
                <Paper
                  elevation={0}
                  sx={{
                    px: 2,
                    py: 1.25,
                    maxWidth: '85%',
                    borderRadius: msg.role === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                    bgcolor: msg.role === 'user' ? '#0078d4' : '#fff',
                    color: msg.role === 'user' ? '#fff' : '#333',
                    border: msg.role === 'user' ? 'none' : '1px solid #e0e0e0',
                  }}
                >
                  <Typography
                    variant="body2"
                    sx={{ lineHeight: 1.6, '& strong': { fontWeight: 700 } }}
                    dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }}
                  />
                </Paper>
              </Box>
            ))}

            {loading && (
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mb: 1.5 }}>
                <Paper elevation={0} sx={{ px: 2, py: 1.25, borderRadius: '16px 16px 16px 4px', bgcolor: '#fff', border: '1px solid #e0e0e0' }}>
                  <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center' }}>
                    <CircularProgress size={14} />
                    <Typography variant="caption" color="text.secondary">Thinking...</Typography>
                  </Box>
                </Paper>
              </Box>
            )}

            {/* Quick actions - only show at the start */}
            {messages.length <= 1 && !loading && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="caption" color="text.secondary" sx={{ mb: 0.5, display: 'block' }}>
                  Try asking:
                </Typography>
                {quickActions.map((q, i) => (
                  <Paper
                    key={i}
                    variant="outlined"
                    onClick={() => { setInput(q); }}
                    sx={{
                      px: 1.5, py: 0.75, mb: 0.5, borderRadius: 2,
                      cursor: 'pointer',
                      '&:hover': { bgcolor: '#e3f2fd', borderColor: '#0078d4' },
                      transition: 'all 0.2s',
                    }}
                  >
                    <Typography variant="caption">{q}</Typography>
                  </Paper>
                ))}
              </Box>
            )}

            <div ref={messagesEndRef} />
          </Box>

          {/* Input */}
          <Box
            sx={{
              p: 1.5,
              borderTop: '1px solid #e0e0e0',
              bgcolor: '#fff',
              display: 'flex',
              gap: 1,
              alignItems: 'flex-end',
            }}
          >
            <TextField
              fullWidth
              size="small"
              placeholder="Ask about your Azure costs..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              multiline
              maxRows={3}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                  fontSize: '0.875rem',
                },
              }}
            />
            <IconButton
              color="primary"
              onClick={handleSend}
              disabled={loading || !input.trim()}
              sx={{
                bgcolor: '#0078d4',
                color: '#fff',
                '&:hover': { bgcolor: '#005a9e' },
                '&.Mui-disabled': { bgcolor: '#e0e0e0' },
                width: 38,
                height: 38,
              }}
            >
              <Send sx={{ fontSize: 18 }} />
            </IconButton>
          </Box>
        </Paper>
      )}
    </>
  );
}

import { useState, useEffect } from 'react';
import {
  Box, Grid, Card, CardContent, Typography, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, TextField, Select, MenuItem,
  FormControl, InputLabel, Button, Chip, Avatar, Snackbar, Alert, CircularProgress
} from '@mui/material';
import {
  EmojiEvents, CheckCircle, LocalFireDepartment, MilitaryTech,
  Savings, Shield, Star, RocketLaunch, TrendingDown
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import CountUp from 'react-countup';
import Confetti from 'react-confetti';
import { getMyStats, getLeaderboard, getBadges, submitAward, getAwards } from '../../services/api';
import { useAuthStore } from '../../store/store';

const badgeIcons = {
  savings: Savings,
  trending_down: TrendingDown,
  shield: Shield,
  star: Star,
  local_fire_department: LocalFireDepartment,
  rocket_launch: RocketLaunch,
};

const awardTypes = [
  'Cost Saver of the Month',
  'Cloud Champion',
  'Optimization Pioneer',
  'Team Player',
];

export default function Gamification() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [badges, setBadges] = useState({});
  const [awards, setAwards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [snack, setSnack] = useState({ open: false, msg: '', severity: 'success' });
  const [showConfetti, setShowConfetti] = useState(false); // NEW: Confetti state

  // Award form
  const [form, setForm] = useState({ nominated_user: '', award_type: awardTypes[0], reason: '', points: 100 });

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsRes, lbRes, badgesRes, awardsRes] = await Promise.all([
        getMyStats(), getLeaderboard(), getBadges(), getAwards(),
      ]);
      setStats(statsRes.data);
      setLeaderboard(lbRes.data);
      setBadges(badgesRes.data);
      setAwards(awardsRes.data);

      // NEW: Trigger confetti if user has badges
      if (statsRes.data?.badges && statsRes.data.badges.length > 0) {
        setShowConfetti(true);
        setTimeout(() => setShowConfetti(false), 5000); // Stop after 5 seconds
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAward = async () => {
    if (!form.nominated_user || !form.reason) {
      setSnack({ open: true, msg: 'Please fill in all fields', severity: 'warning' });
      return;
    }
    try {
      await submitAward(form);
      setSnack({ open: true, msg: `Award submitted for ${form.nominated_user}!`, severity: 'success' });
      setForm({ nominated_user: '', award_type: awardTypes[0], reason: '', points: 100 });
      loadData();
    } catch (err) {
      setSnack({ open: true, msg: 'Failed to submit award', severity: 'error' });
    }
  };

  const rankColors = ['#FFD700', '#C0C0C0', '#CD7F32'];
  const myBadges = stats?.badges || [];
  const badgeEntries = Object.entries(badges);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}><CircularProgress /></Box>;

  return (
    <Box>
      {/* NEW: Confetti when user has badges */}
      {showConfetti && (
        <Confetti
          width={window.innerWidth}
          height={window.innerHeight}
          recycle={false}
          numberOfPieces={200}
          gravity={0.3}
        />
      )}

      <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1.15rem', mb: 1 }}>Gamification & Awards</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3, fontSize: '0.8rem' }}>
        Track your optimization achievements and nominate teammates
      </Typography>

      {/* My Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={6} sm={3}>
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            whileHover={{ scale: 1.05 }}
          >
            <Card sx={{
              background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
              position: 'relative',
              overflow: 'hidden',
              transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
              boxShadow: '0 4px 20px rgba(255, 215, 0, 0.3)',
              '&:hover': {
                boxShadow: '0 8px 40px rgba(255, 215, 0, 0.5)',
                transform: 'translateY(-8px)',
              },
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.3) 50%, transparent 70%)',
                transform: 'translateX(-100%)',
                transition: 'transform 0.6s',
              },
              '&:hover::before': {
                transform: 'translateX(100%)',
              }
            }}>
              <CardContent sx={{ textAlign: 'center', position: 'relative', zIndex: 1 }}>
                <EmojiEvents sx={{ fontSize: 48, color: '#fff', mb: 1, filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.3))' }} />
                <Typography variant="h5" fontWeight={700} sx={{ color: '#fff', textShadow: '0 2px 4px rgba(0,0,0,0.2)', fontSize: '1.8rem' }}>
                  <CountUp end={stats?.total_points || 0} duration={2} />
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.95)', fontWeight: 600, fontSize: '0.8rem' }}>Total Points</Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
        <Grid item xs={6} sm={3}>
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            whileHover={{ scale: 1.05 }}
          >
            <Card sx={{
              background: 'linear-gradient(135deg, #2e7d32 0%, #66bb6a 100%)',
              position: 'relative',
              overflow: 'hidden',
              transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
              boxShadow: '0 4px 20px rgba(46, 125, 50, 0.3)',
              '&:hover': {
                boxShadow: '0 8px 40px rgba(46, 125, 50, 0.5)',
                transform: 'translateY(-8px)',
              },
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.3) 50%, transparent 70%)',
                transform: 'translateX(-100%)',
                transition: 'transform 0.6s',
              },
              '&:hover::before': {
                transform: 'translateX(100%)',
              }
            }}>
              <CardContent sx={{ textAlign: 'center', position: 'relative', zIndex: 1 }}>
                <CheckCircle sx={{ fontSize: 48, color: '#fff', mb: 1, filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.3))' }} />
                <Typography variant="h5" fontWeight={700} sx={{ color: '#fff', textShadow: '0 2px 4px rgba(0,0,0,0.2)', fontSize: '1.8rem' }}>{stats?.recommendations_adopted || 0}</Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.95)', fontWeight: 600, fontSize: '0.8rem' }}>Adopted</Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
        <Grid item xs={6} sm={3}>
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            whileHover={{ scale: 1.05 }}
          >
            <Card sx={{
              background: 'linear-gradient(135deg, #ed6c02 0%, #ff9800 100%)',
              position: 'relative',
              overflow: 'hidden',
              transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
              boxShadow: '0 4px 20px rgba(237, 108, 2, 0.3)',
              '&:hover': {
                boxShadow: '0 8px 40px rgba(237, 108, 2, 0.5)',
                transform: 'translateY(-8px)',
              },
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.3) 50%, transparent 70%)',
                transform: 'translateX(-100%)',
                transition: 'transform 0.6s',
              },
              '&:hover::before': {
                transform: 'translateX(100%)',
              }
            }}>
              <CardContent sx={{ textAlign: 'center', position: 'relative', zIndex: 1 }}>
                <LocalFireDepartment sx={{ fontSize: 48, color: '#fff', mb: 1, filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.3))' }} />
                <Typography variant="h5" fontWeight={700} sx={{ color: '#fff', textShadow: '0 2px 4px rgba(0,0,0,0.2)', fontSize: '1.8rem' }}>{stats?.current_streak || 0}</Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.95)', fontWeight: 600, fontSize: '0.8rem' }}>Day Streak</Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
        <Grid item xs={6} sm={3}>
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            whileHover={{ scale: 1.05 }}
          >
            <Card sx={{
              background: 'linear-gradient(135deg, #7b1fa2 0%, #ab47bc 100%)',
              position: 'relative',
              overflow: 'hidden',
              transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
              boxShadow: '0 4px 20px rgba(123, 31, 162, 0.3)',
              '&:hover': {
                boxShadow: '0 8px 40px rgba(123, 31, 162, 0.5)',
                transform: 'translateY(-8px)',
              },
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.3) 50%, transparent 70%)',
                transform: 'translateX(-100%)',
                transition: 'transform 0.6s',
              },
              '&:hover::before': {
                transform: 'translateX(100%)',
              }
            }}>
              <CardContent sx={{ textAlign: 'center', position: 'relative', zIndex: 1 }}>
                <MilitaryTech sx={{ fontSize: 48, color: '#fff', mb: 1, filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.3))' }} />
                <Typography variant="h5" fontWeight={700} sx={{ color: '#fff', textShadow: '0 2px 4px rgba(0,0,0,0.2)', fontSize: '1.8rem' }}>{myBadges.length} / {badgeEntries.length}</Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.95)', fontWeight: 600, fontSize: '0.8rem' }}>Badges</Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Badges */}
      <Card sx={{
        mb: 3,
        background: 'linear-gradient(to bottom, rgba(255,255,255,1) 0%, rgba(248,249,250,1) 100%)',
        boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
        transition: 'all 0.3s ease',
        '&:hover': {
          boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
        }
      }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 3, fontWeight: 700, color: '#333', fontSize: '0.95rem' }}>Badges</Typography>
          <Grid container spacing={3}>
            {badgeEntries.map(([key, badge]) => {
              const earned = myBadges.includes(key);
              const Icon = badgeIcons[badge.icon] || Star;
              return (
                <Grid item xs={6} sm={4} md={2} key={key}>
                  <motion.div
                    whileHover={earned ? { scale: 1.1, y: -10 } : { scale: 1.05 }}
                    transition={{ type: "spring", stiffness: 300, damping: 20 }}
                  >
                    <Box sx={{
                      textAlign: 'center',
                      p: 2.5,
                      borderRadius: 3,
                      border: earned ? '2px solid' : '2px dashed',
                      borderColor: earned ? 'primary.main' : '#d0d0d0',
                      background: earned
                        ? 'linear-gradient(135deg, rgba(0,120,212,0.1) 0%, rgba(0,120,212,0.05) 100%)'
                        : 'linear-gradient(135deg, #fafafa 0%, #f0f0f0 100%)',
                      opacity: earned ? 1 : 0.5,
                      position: 'relative',
                      overflow: 'hidden',
                      cursor: earned ? 'pointer' : 'default',
                      transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                      boxShadow: earned ? '0 4px 12px rgba(0,120,212,0.15)' : '0 2px 8px rgba(0,0,0,0.05)',
                      '&:hover': {
                        boxShadow: earned
                          ? '0 8px 24px rgba(0,120,212,0.3)'
                          : '0 4px 12px rgba(0,0,0,0.1)',
                        borderColor: earned ? 'primary.dark' : '#b0b0b0',
                      },
                      '&::before': earned ? {
                        content: '""',
                        position: 'absolute',
                        top: '-50%',
                        left: '-50%',
                        width: '200%',
                        height: '200%',
                        background: 'radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%)',
                        opacity: 0,
                        transition: 'opacity 0.3s',
                      } : {},
                      '&:hover::before': earned ? {
                        opacity: 1,
                      } : {},
                    }}>
                      <Icon sx={{
                        fontSize: 48,
                        color: earned ? '#0078d4' : '#999',
                        mb: 1.5,
                        filter: earned ? 'drop-shadow(0 4px 8px rgba(0,120,212,0.3))' : 'none',
                        transition: 'all 0.3s ease',
                      }} />
                      <Typography variant="body2" fontWeight={700} noWrap sx={{ mb: 0.5 }}>{badge.name}</Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>{badge.points} pts</Typography>
                      {earned && (
                        <Chip
                          label="Earned"
                          size="small"
                          sx={{
                            background: 'linear-gradient(135deg, #0078d4 0%, #005a9e 100%)',
                            color: '#fff',
                            fontWeight: 600,
                            boxShadow: '0 2px 8px rgba(0,120,212,0.3)',
                          }}
                        />
                      )}
                      {!earned && (
                        <Chip
                          label="Locked"
                          size="small"
                          variant="outlined"
                          sx={{
                            borderColor: '#ccc',
                            color: '#999',
                          }}
                        />
                      )}
                    </Box>
                  </motion.div>
                </Grid>
              );
            })}
          </Grid>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {/* Leaderboard */}
        <Grid item xs={12} md={6}>
          <Card sx={{
            background: 'linear-gradient(to bottom right, rgba(255,255,255,1) 0%, rgba(245,247,250,1) 100%)',
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
            transition: 'all 0.3s ease',
            border: '1px solid rgba(0,120,212,0.1)',
            '&:hover': {
              boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
              transform: 'translateY(-4px)',
            }
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 1 }}>
                <EmojiEvents sx={{ color: '#FFD700', fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 700, color: '#333', fontSize: '0.95rem' }}>Leaderboard</Typography>
              </Box>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow sx={{
                      background: 'linear-gradient(135deg, #0078d4 0%, #005a9e 100%)',
                      '& th': { color: '#fff', fontWeight: 700, py: 1.5 }
                    }}>
                      <TableCell width={60}>#</TableCell>
                      <TableCell>User</TableCell>
                      <TableCell align="right">Points</TableCell>
                      <TableCell align="right">Adopted</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {leaderboard.map((entry, i) => {
                      const isMe = entry.username === user?.username || entry.user_id === String(user?.id);
                      return (
                        <TableRow
                          key={entry.user_id || i}
                          sx={{
                            bgcolor: isMe ? 'rgba(0,120,212,0.08)' : 'inherit',
                            transition: 'all 0.3s ease',
                            position: 'relative',
                            '&:hover': {
                              bgcolor: isMe ? 'rgba(0,120,212,0.15)' : 'rgba(0,0,0,0.03)',
                              transform: 'scale(1.02)',
                              boxShadow: isMe
                                ? '0 4px 12px rgba(0,120,212,0.2)'
                                : '0 2px 8px rgba(0,0,0,0.1)',
                              zIndex: 1,
                            },
                            '&:hover td': {
                              fontWeight: isMe ? 700 : 500,
                            }
                          }}
                        >
                          <TableCell>
                            {i < 3 ? (
                              <Avatar sx={{
                                width: 32,
                                height: 32,
                                background: `linear-gradient(135deg, ${rankColors[i]} 0%, ${rankColors[i]}dd 100%)`,
                                fontSize: 14,
                                fontWeight: 700,
                                boxShadow: `0 2px 8px ${rankColors[i]}66`,
                                transition: 'all 0.3s ease',
                                '&:hover': {
                                  transform: 'scale(1.15) rotate(5deg)',
                                }
                              }}>
                                {i + 1}
                              </Avatar>
                            ) : (
                              <Typography variant="body2" sx={{ pl: 0.5, fontWeight: 600 }}>{i + 1}</Typography>
                            )}
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="body2" fontWeight={isMe ? 700 : 400}>
                                {entry.username || `User ${entry.user_id}`}
                              </Typography>
                              {isMe && (
                                <Chip
                                  label="You"
                                  size="small"
                                  sx={{
                                    background: 'linear-gradient(135deg, #0078d4 0%, #005a9e 100%)',
                                    color: '#fff',
                                    fontWeight: 600,
                                    fontSize: '0.7rem',
                                  }}
                                />
                              )}
                            </Box>
                          </TableCell>
                          <TableCell align="right">
                            <Chip
                              label={entry.total_points || 0}
                              size="small"
                              sx={{
                                fontWeight: 700,
                                bgcolor: isMe ? 'primary.main' : 'rgba(0,120,212,0.1)',
                                color: isMe ? '#fff' : '#0078d4',
                              }}
                            />
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" fontWeight={600} color="text.secondary">
                              {entry.recommendations_adopted || 0}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                    {leaderboard.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={4} align="center" sx={{ py: 4 }}>
                          <Typography variant="body2" color="text.secondary">No data yet. Run analyses and adopt recommendations to earn points!</Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Award Submission */}
        <Grid item xs={12} md={6}>
          <Card sx={{
            background: 'linear-gradient(to bottom right, rgba(255,255,255,1) 0%, rgba(245,247,250,1) 100%)',
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
            transition: 'all 0.3s ease',
            border: '1px solid rgba(0,120,212,0.1)',
            '&:hover': {
              boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
              transform: 'translateY(-4px)',
            }
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 1 }}>
                <Star sx={{ color: '#FFD700', fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 700, color: '#333', fontSize: '0.95rem' }}>Nominate for Award</Typography>
              </Box>
              <TextField
                fullWidth
                label="Nominated User"
                value={form.nominated_user}
                onChange={(e) => setForm({ ...form, nominated_user: e.target.value })}
                sx={{
                  mb: 2,
                  '& .MuiOutlinedInput-root': {
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      boxShadow: '0 2px 8px rgba(0,120,212,0.15)',
                    },
                    '&.Mui-focused': {
                      boxShadow: '0 4px 12px rgba(0,120,212,0.25)',
                    }
                  }
                }}
                size="small"
                placeholder="e.g. cloudops"
              />
              <FormControl fullWidth sx={{
                mb: 2,
                '& .MuiOutlinedInput-root': {
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    boxShadow: '0 2px 8px rgba(0,120,212,0.15)',
                  },
                  '&.Mui-focused': {
                    boxShadow: '0 4px 12px rgba(0,120,212,0.25)',
                  }
                }
              }} size="small">
                <InputLabel>Award Type</InputLabel>
                <Select value={form.award_type} label="Award Type" onChange={(e) => setForm({ ...form, award_type: e.target.value })}>
                  {awardTypes.map((t) => <MenuItem key={t} value={t}>{t}</MenuItem>)}
                </Select>
              </FormControl>
              <TextField
                fullWidth
                label="Reason"
                value={form.reason}
                onChange={(e) => setForm({ ...form, reason: e.target.value })}
                multiline
                rows={3}
                sx={{
                  mb: 2,
                  '& .MuiOutlinedInput-root': {
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      boxShadow: '0 2px 8px rgba(0,120,212,0.15)',
                    },
                    '&.Mui-focused': {
                      boxShadow: '0 4px 12px rgba(0,120,212,0.25)',
                    }
                  }
                }}
                size="small"
              />
              <TextField
                fullWidth
                label="Points"
                type="number"
                value={form.points}
                onChange={(e) => setForm({ ...form, points: parseInt(e.target.value) || 0 })}
                sx={{
                  mb: 2,
                  '& .MuiOutlinedInput-root': {
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      boxShadow: '0 2px 8px rgba(0,120,212,0.15)',
                    },
                    '&.Mui-focused': {
                      boxShadow: '0 4px 12px rgba(0,120,212,0.25)',
                    }
                  }
                }}
                size="small"
              />
              <Button
                fullWidth
                variant="contained"
                onClick={handleSubmitAward}
                sx={{
                  background: 'linear-gradient(135deg, #0078d4 0%, #005a9e 100%)',
                  py: 1.2,
                  fontWeight: 700,
                  boxShadow: '0 4px 12px rgba(0,120,212,0.3)',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #005a9e 0%, #004578 100%)',
                    boxShadow: '0 6px 20px rgba(0,120,212,0.4)',
                    transform: 'translateY(-2px)',
                  }
                }}
              >
                Submit Nomination
              </Button>
            </CardContent>
          </Card>

          {/* Recent Awards */}
          {awards.length > 0 && (
            <Card sx={{
              mt: 3,
              background: 'linear-gradient(to bottom right, rgba(255,255,255,1) 0%, rgba(245,247,250,1) 100%)',
              boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
              transition: 'all 0.3s ease',
              border: '1px solid rgba(0,120,212,0.1)',
              '&:hover': {
                boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
              }
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, gap: 1 }}>
                  <MilitaryTech sx={{ color: '#7b1fa2', fontSize: 24 }} />
                  <Typography variant="h6" sx={{ fontWeight: 700, color: '#333', fontSize: '0.95rem' }}>Recent Awards</Typography>
                </Box>
                {awards.slice(0, 5).map((a, i) => (
                  <Box
                    key={i}
                    sx={{
                      mb: 1.5,
                      pb: 1.5,
                      borderBottom: i < 4 ? '1px solid #eee' : 'none',
                      p: 1.5,
                      borderRadius: 2,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        bgcolor: 'rgba(0,120,212,0.04)',
                        transform: 'translateX(8px)',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                      }
                    }}
                  >
                    <Typography variant="body2" sx={{ mb: 0.5 }}>
                      <strong style={{ color: '#0078d4' }}>{a.nominated_by}</strong> nominated <strong style={{ color: '#2e7d32' }}>{a.nominated_user}</strong> for{' '}
                      <Chip
                        label={a.award_type}
                        size="small"
                        sx={{
                          background: 'linear-gradient(135deg, #0078d4 0%, #005a9e 100%)',
                          color: '#fff',
                          fontWeight: 600,
                          mx: 0.5,
                        }}
                      />
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                      "{a.reason}" - <strong>{a.points} points</strong>
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>

      <Snackbar open={snack.open} autoHideDuration={4000} onClose={() => setSnack({ ...snack, open: false })}>
        <Alert severity={snack.severity} onClose={() => setSnack({ ...snack, open: false })}>{snack.msg}</Alert>
      </Snackbar>
    </Box>
  );
}
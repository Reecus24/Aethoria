import { useEffect, useState } from 'react';
import { useOutletContext, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from '../utils/axios';
import { motion } from 'framer-motion';
import { TrendingUp, Swords, Skull, Scroll, Trophy, MessageSquare } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function GameDashboard() {
  const { user } = useAuth();
  const { gameState, refreshGameState } = useOutletContext();
  const [recentLogs, setRecentLogs] = useState({ combat: [], crimes: [] });

  useEffect(() => {
    fetchRecentActivity();
  }, []);

  const fetchRecentActivity = async () => {
    try {
      const [combatRes, crimesRes] = await Promise.all([
        axios.get(`${API}/game/combat/logs`, { params: { limit: 5 } }),
        axios.get(`${API}/game/crimes/logs`, { params: { limit: 5 } })
      ]);
      setRecentLogs({ combat: combatRes.data, crimes: crimesRes.data });
    } catch (err) {
      console.error('Failed to fetch activity:', err);
    }
  };

  if (!gameState) {
    return <div className="text-center py-20">Loading...</div>;
  }

  const quickActions = [
    { to: '/game/training', icon: TrendingUp, label: 'Training', color: '#81C784' },
    { to: '/game/crimes', icon: Skull, label: 'Verbrechen', color: '#CE93D8' },
    { to: '/game/combat', icon: Swords, label: 'Kampf', color: '#FFB74D' },
    { to: '/game/quests', icon: Scroll, label: 'Quests', color: '#64B5F6' },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Welcome Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="aeth-card p-6"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1
              className="text-2xl font-bold mb-1"
              style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}
            >
              Willkommen zurück, {gameState.user.username}!
            </h1>
            <p className="text-sm" style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
              {gameState.user.path_label} • Level {gameState.user.level} • {gameState.location.kingdom_name}
            </p>
          </div>
          <div
            className="px-4 py-2 rounded-lg"
            style={{ backgroundColor: 'rgba(214,162,77,0.15)', border: '1px solid rgba(214,162,77,0.3)' }}
          >
            <p className="text-xs" style={{ color: 'var(--aeth-parchment-dim)' }}>XP bis Level {gameState.user.level + 1}</p>
            <p className="text-lg font-bold" style={{ color: 'var(--aeth-gold)', fontFamily: "'Azeret Mono', monospace" }}>
              {gameState.user.xp_next}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {quickActions.map((action, i) => {
          const Icon = action.icon;
          return (
            <Link key={action.to} to={action.to}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                whileHover={{ scale: 1.02 }}
                className="aeth-card p-5 text-center cursor-pointer"
                data-testid={`quick-action-${action.label.toLowerCase()}`}
              >
                <Icon size={28} style={{ color: action.color, marginBottom: '8px', marginLeft: 'auto', marginRight: 'auto' }} />
                <p className="text-sm font-semibold" style={{ color: 'var(--aeth-parchment)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
                  {action.label}
                </p>
              </motion.div>
            </Link>
          );
        })}
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Object.entries(gameState.stats).filter(([key]) => ['strength', 'dexterity', 'speed', 'defense'].includes(key)).map(([stat, value]) => (
          <div key={stat} className="aeth-card p-4">
            <p className="text-xs uppercase mb-1" style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'Cinzel', serif", letterSpacing: '0.1em' }}>
              {stat}
            </p>
            <p className="text-2xl font-bold" style={{ color: 'var(--aeth-gold)', fontFamily: "'Azeret Mono', monospace" }}>
              {value}
            </p>
          </div>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Combat Logs */}
        <div className="aeth-card p-5">
          <div className="flex items-center gap-2 mb-4">
            <Swords size={18} style={{ color: 'var(--aeth-gold)' }} />
            <h2 className="text-lg font-semibold" style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}>
              Letzte Kämpfe
            </h2>
          </div>
          <div className="space-y-2">
            {recentLogs.combat.length === 0 ? (
              <p className="text-sm text-center py-4" style={{ color: 'var(--aeth-parchment-dim)' }}>Noch keine Kämpfe</p>
            ) : (
              recentLogs.combat.map(log => {
                // Determine if current user won
                const userWon = (log.attacker_name === user.username && log.winner === 'attacker') || 
                                (log.defender_name === user.username && log.winner === 'defender');
                
                return (
                  <div
                    key={log.id}
                    className="p-3 rounded-lg text-xs"
                    style={{
                      backgroundColor: userWon ? 'rgba(129,199,132,0.1)' : 'rgba(229,115,115,0.1)',
                      borderLeft: `3px solid ${userWon ? '#81C784' : '#E57373'}`
                    }}
                  >
                    <p style={{ color: 'var(--aeth-parchment)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
                      {log.attacker_name} vs {log.defender_name}
                    </p>
                    <p style={{ color: 'var(--aeth-parchment-dim)' }}>
                      Sieger: {log.winner === 'attacker' ? log.attacker_name : log.defender_name} • {log.damage} Schaden
                    </p>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Crime Logs */}
        <div className="aeth-card p-5">
          <div className="flex items-center gap-2 mb-4">
            <Skull size={18} style={{ color: 'var(--aeth-gold)' }} />
            <h2 className="text-lg font-semibold" style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}>
              Letzte Verbrechen
            </h2>
          </div>
          <div className="space-y-2">
            {recentLogs.crimes.length === 0 ? (
              <p className="text-sm text-center py-4" style={{ color: 'var(--aeth-parchment-dim)' }}>Noch keine Verbrechen</p>
            ) : (
              recentLogs.crimes.map(log => (
                <div
                  key={log.id}
                  className="p-3 rounded-lg text-xs"
                  style={{
                    backgroundColor: log.success ? 'rgba(129,199,132,0.1)' : 'rgba(229,115,115,0.1)',
                    borderLeft: `3px solid ${log.success ? '#81C784' : '#E57373'}`
                  }}
                >
                  <p style={{ color: 'var(--aeth-parchment)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
                    {log.crime_name} • {log.success ? 'Erfolg' : 'Gescheitert'}
                  </p>
                  {log.success && (
                    <p style={{ color: '#81C784' }}>+{log.gold_gained} Gold, +{log.xp_gained} XP</p>
                  )}
                  {!log.success && log.jail_minutes && (
                    <p style={{ color: '#E57373' }}>{log.jail_minutes} Min Kerker</p>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Timers */}
      {gameState.timers && Object.keys(gameState.timers).length > 0 && (
        <div className="aeth-card p-5">
          <h2 className="text-lg font-semibold mb-4" style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}>
            Aktive Timer
          </h2>
          <div className="grid md:grid-cols-3 gap-4">
            {gameState.timers.training && (
              <div className="p-4 rounded-lg" style={{ backgroundColor: 'var(--aeth-iron-2)', border: '1px solid var(--aeth-iron)' }}>
                <p className="text-sm font-semibold mb-1" style={{ color: 'var(--aeth-parchment)' }}>Training: {gameState.timers.training.stat}</p>
                <p className="text-xs" style={{ color: 'var(--aeth-parchment-dim)' }}>
                  {Math.floor(gameState.timers.training.seconds_remaining / 60)} Min verbleibend
                </p>
              </div>
            )}
            {gameState.timers.quest && (
              <div className="p-4 rounded-lg" style={{ backgroundColor: 'var(--aeth-iron-2)', border: '1px solid var(--aeth-iron)' }}>
                <p className="text-sm font-semibold mb-1" style={{ color: 'var(--aeth-parchment)' }}>{gameState.timers.quest.quest_name}</p>
                <p className="text-xs" style={{ color: 'var(--aeth-parchment-dim)' }}>
                  {Math.floor(gameState.timers.quest.seconds_remaining / 60)} Min verbleibend
                </p>
              </div>
            )}
            {gameState.timers.dungeon && (
              <div className="p-4 rounded-lg" style={{ backgroundColor: 'rgba(142,29,44,0.2)', border: '1px solid rgba(142,29,44,0.4)' }}>
                <p className="text-sm font-semibold mb-1" style={{ color: '#E57373' }}>Im Kerker</p>
                <p className="text-xs" style={{ color: '#E57373' }}>
                  {gameState.timers.dungeon.minutes_remaining} Min verbleibend
                </p>
              </div>
            )}
            {gameState.timers.hospital && (
              <div className="p-4 rounded-lg" style={{ backgroundColor: 'rgba(142,29,44,0.2)', border: '1px solid rgba(142,29,44,0.4)' }}>
                <p className="text-sm font-semibold mb-1" style={{ color: '#E57373' }}>Im Lazarett</p>
                <p className="text-xs" style={{ color: '#E57373' }}>
                  {Math.floor(gameState.timers.hospital.seconds_remaining / 60)} Min verbleibend
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
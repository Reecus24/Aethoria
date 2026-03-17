import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Shield, Sword, Crown, TrendingUp } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const PATH_META = {
  knight: { label: 'The Knight', color: '#C0392B', icon: '⚔️', bgGlow: 'rgba(192,57,43,0.08)' },
  shadow: { label: 'The Shadow', color: '#8E44AD', icon: '🗡️', bgGlow: 'rgba(142,68,173,0.08)' },
  noble:  { label: 'The Noble',  color: '#D4AC0D', icon: '👑', bgGlow: 'rgba(212,172,13,0.08)' },
};

const StatBar = ({ label, value, max = 20, color }) => {
  const pct = Math.min(100, (value / max) * 100);
  return (
    <div className="flex items-center gap-3">
      <span
        className="w-24 text-xs text-right flex-shrink-0"
        style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'Cinzel', serif", fontSize: '0.72rem', letterSpacing: '0.04em' }}
      >
        {label}
      </span>
      <div
        className="flex-1 h-2 rounded-full overflow-hidden"
        style={{ backgroundColor: 'var(--aeth-iron-2)' }}
      >
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.7, ease: 'easeOut' }}
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
        />
      </div>
      <span
        className="w-6 text-xs"
        style={{ color, fontFamily: "'Azeret Mono', monospace", fontSize: '0.72rem' }}
      >
        {value}
      </span>
    </div>
  );
};

export const CharacterDashboard = ({ open, onClose }) => {
  const { user } = useAuth();
  if (!user) return null;

  const pathMeta = PATH_META[user.path_choice] || PATH_META.knight;
  const xpToNext = 100 * user.level;
  const xpPct = Math.min(100, ((user.xp || 0) / xpToNext) * 100);

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40"
            style={{ backgroundColor: 'rgba(7,6,6,0.7)', backdropFilter: 'blur(3px)' }}
            onClick={onClose}
          />
          {/* Panel */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 28, stiffness: 300 }}
            data-testid="character-dashboard"
            className="fixed right-0 top-0 bottom-0 z-50 overflow-y-auto"
            style={{
              width: '100%',
              maxWidth: 380,
              backgroundColor: 'var(--aeth-stone-1)',
              borderLeft: `1px solid ${pathMeta.color}44`,
              boxShadow: `-8px 0 40px ${pathMeta.color}18, -2px 0 0 rgba(255,255,255,0.03)`,
            }}
          >
            {/* Header */}
            <div
              className="px-6 pt-6 pb-5 relative"
              style={{
                background: `radial-gradient(circle at 80% 20%, ${pathMeta.bgGlow}, transparent 60%)`,
                borderBottom: '1px solid var(--aeth-iron)',
              }}
            >
              <button
                onClick={onClose}
                className="absolute top-4 right-4 p-1.5 rounded-lg"
                data-testid="dashboard-close-button"
                style={{ backgroundColor: 'var(--aeth-iron-2)', border: '1px solid var(--aeth-iron)', color: 'var(--aeth-iron)', cursor: 'pointer' }}
                aria-label="Close dashboard"
              >
                <X size={16} />
              </button>

              {/* Avatar */}
              <div className="flex items-center gap-4 mb-5">
                <div
                  className="w-16 h-16 rounded-full flex items-center justify-center text-2xl flex-shrink-0"
                  style={{
                    backgroundColor: 'var(--aeth-iron-2)',
                    border: `2px solid ${pathMeta.color}`,
                    boxShadow: `0 0 20px ${pathMeta.color}33`,
                  }}
                >
                  {pathMeta.icon}
                </div>
                <div>
                  <h2
                    style={{
                      fontFamily: "'Cinzel', serif",
                      color: 'var(--aeth-parchment)',
                      fontSize: '1.1rem',
                      fontWeight: 700,
                      letterSpacing: '0.04em',
                    }}
                  >
                    {user.username}
                  </h2>
                  <p style={{ color: pathMeta.color, fontSize: '0.78rem', fontFamily: "'IBM Plex Sans', sans-serif" }}>
                    {user.title}
                  </p>
                  <p style={{ color: 'var(--aeth-iron)', fontSize: '0.7rem', fontFamily: "'Azeret Mono', monospace", marginTop: '2px' }}>
                    {pathMeta.label} &middot; Level {user.level}
                  </p>
                </div>
              </div>

              {/* XP bar */}
              <div className="mb-1 flex justify-between">
                <span style={{ color: 'var(--aeth-iron)', fontFamily: "'Azeret Mono', monospace", fontSize: '0.65rem', letterSpacing: '0.06em' }}>EXPERIENCE</span>
                <span style={{ color: 'var(--aeth-iron)', fontFamily: "'Azeret Mono', monospace", fontSize: '0.65rem' }}>{user.xp || 0} / {xpToNext} XP</span>
              </div>
              <div className="h-2 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--aeth-iron-2)' }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${xpPct}%` }}
                  transition={{ duration: 0.8, ease: 'easeOut' }}
                  className="h-full rounded-full"
                  style={{ background: `linear-gradient(to right, ${pathMeta.color}, ${pathMeta.color}99)` }}
                />
              </div>
            </div>

            {/* Body */}
            <div className="px-6 py-5 flex flex-col gap-6">
              {/* Gold + Days */}
              <div className="grid grid-cols-2 gap-3">
                {[
                  { label: 'Gold', value: (user.gold || 0).toLocaleString(), icon: '💰' },
                  { label: 'Days in Realm', value: user.days_in_realm ?? 0, icon: '📅' },
                ].map(item => (
                  <div key={item.label} className="aeth-card px-4 py-3 text-center">
                    <p style={{ fontSize: '1.2rem', marginBottom: '0.1rem' }}>{item.icon}</p>
                    <p style={{ fontFamily: "'Cinzel', serif", color: 'var(--aeth-parchment)', fontSize: '1rem', fontWeight: 700 }}>{item.value}</p>
                    <p style={{ fontFamily: "'IBM Plex Sans', sans-serif", color: 'var(--aeth-iron)', fontSize: '0.7rem' }}>{item.label}</p>
                  </div>
                ))}
              </div>

              {/* Combat stats */}
              <div>
                <h3
                  className="mb-3 text-xs uppercase tracking-widest"
                  style={{ color: 'var(--aeth-gold)', fontFamily: "'Cinzel', serif" }}
                >
                  Combat Stats
                </h3>
                <div className="flex flex-col gap-2">
                  <StatBar label="Strength" value={user.strength || 0} max={20} color={pathMeta.color} />
                  <StatBar label="Dexterity" value={user.dexterity || 0} max={20} color={pathMeta.color} />
                  <StatBar label="Speed" value={user.speed || 0} max={20} color={pathMeta.color} />
                  <StatBar label="Defense" value={user.defense || 0} max={20} color={pathMeta.color} />
                </div>
              </div>

              {/* Path badge */}
              <div
                className="rounded-xl p-4 text-center"
                style={{
                  backgroundColor: `${pathMeta.color}12`,
                  border: `1px solid ${pathMeta.color}33`,
                }}
              >
                <p style={{ fontSize: '2rem', marginBottom: '0.25rem' }}>{pathMeta.icon}</p>
                <p style={{ fontFamily: "'Cinzel', serif", color: pathMeta.color, fontWeight: 700, fontSize: '0.9rem' }}>{pathMeta.label}</p>
                <p style={{ fontFamily: "'IBM Plex Sans', sans-serif", color: 'var(--aeth-iron)', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                  Your chosen destiny in Aethoria
                </p>
              </div>

              {/* Joined date */}
              <p
                className="text-center text-xs"
                style={{ color: 'var(--aeth-iron)', fontFamily: "'Azeret Mono', monospace" }}
              >
                Joined the Realm: {new Date(user.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })}
              </p>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

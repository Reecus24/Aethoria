import { motion } from 'framer-motion';
import { Trophy, TrendingUp } from 'lucide-react';

const getRankStyle = (rank) => {
  if (rank === 1) return { color: 'var(--aeth-gold)', label: '👑' };
  if (rank === 2) return { color: '#A0A0A0', label: '⚔' };
  if (rank === 3) return { color: 'var(--aeth-amber)', label: '🛡' };
  return { color: 'var(--aeth-parchment-dim)', label: `#${rank}` };
};

export const LeaderboardSection = ({ leaderboard = [] }) => {
  return (
    <section
      data-testid="leaderboard-section"
      className="aeth-section"
      style={{ backgroundColor: 'var(--aeth-stone-1)' }}
    >
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <div className="aeth-divider mb-8">
            <span style={{ color: 'var(--aeth-gold)', fontSize: '1.2rem' }}>🏆</span>
          </div>
          <h2
            className="font-cinzel mb-3"
            style={{
              fontFamily: "'Cinzel', serif",
              fontSize: '2rem',
              fontWeight: 700,
              color: 'var(--aeth-parchment)',
              letterSpacing: '0.04em',
            }}
          >
            Hall of Legends
          </h2>
          <p style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
            The most powerful adventurers in all of Aethoria
          </p>
        </motion.div>

        {/* Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="aeth-card overflow-hidden"
          data-testid="leaderboard-table"
        >
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr
                  style={{
                    backgroundColor: 'var(--aeth-iron-2)',
                    borderBottom: '1px solid var(--aeth-iron)',
                  }}
                >
                  {['Rank', 'Adventurer', 'Title', 'Age', 'Level', 'Growth'].map((h) => (
                    <th
                      key={h}
                      className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider"
                      style={{
                        color: 'var(--aeth-parchment-dim)',
                        fontFamily: "'Cinzel', serif",
                        letterSpacing: '0.06em',
                      }}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {leaderboard.map((entry, i) => {
                  const rankInfo = getRankStyle(entry.rank);
                  return (
                    <tr
                      key={entry.rank}
                      className="border-b"
                      style={{
                        borderColor: 'var(--aeth-iron)',
                        backgroundColor: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.015)',
                        transition: 'background-color 0.15s ease',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = 'rgba(214,162,77,0.05)';
                        e.currentTarget.style.borderLeftColor = 'var(--aeth-gold)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor =
                          i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.015)';
                      }}
                    >
                      <td className="px-4 py-3">
                        <span
                          className="text-sm font-bold"
                          style={{
                            color: rankInfo.color,
                            fontFamily: "'Cinzel', serif",
                            fontSize: entry.rank <= 3 ? '1rem' : '0.85rem',
                          }}
                        >
                          {rankInfo.label}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className="font-semibold text-sm"
                          style={{ color: 'var(--aeth-parchment)', fontFamily: "'IBM Plex Sans', sans-serif" }}
                        >
                          {entry.username}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className="text-xs px-2 py-0.5 rounded-full"
                          style={{
                            backgroundColor: 'rgba(214,162,77,0.12)',
                            color: 'var(--aeth-gold)',
                            border: '1px solid rgba(214,162,77,0.25)',
                            fontFamily: "'IBM Plex Sans', sans-serif",
                          }}
                        >
                          {entry.title}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className="text-sm font-mono-az"
                          style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'Azeret Mono', monospace" }}
                        >
                          {entry.age}d
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className="text-sm font-semibold"
                          style={{ color: 'var(--aeth-parchment)', fontFamily: "'IBM Plex Sans', sans-serif" }}
                        >
                          {entry.level}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1">
                          <TrendingUp size={12} style={{ color: 'var(--aeth-gold)' }} />
                          <span
                            className="text-sm"
                            style={{ color: 'var(--aeth-gold)', fontFamily: "'Azeret Mono', monospace" }}
                          >
                            {entry.improvement}%
                          </span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

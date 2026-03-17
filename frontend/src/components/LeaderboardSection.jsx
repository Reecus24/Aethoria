import { motion } from 'framer-motion';
import { TrendingUp, Trophy } from 'lucide-react';

const getRankStyle = (rank) => {
  if (rank === 1) return { color: 'var(--aeth-gold)', symbol: '👑', glow: 'rgba(214,162,77,0.15)' };
  if (rank === 2) return { color: '#C0C0C0', symbol: '⚔', glow: 'rgba(192,192,192,0.1)' };
  if (rank === 3) return { color: 'var(--aeth-amber)', symbol: '🛡', glow: 'rgba(201,131,46,0.12)' };
  return { color: 'var(--aeth-parchment-dim)', symbol: `#${rank}`, glow: null };
};

export const LeaderboardSection = ({ leaderboard = [] }) => {
  return (
    <section
      id="leaderboard"
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
            <Trophy size={18} style={{ color: 'var(--aeth-gold)' }} />
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
                  {['Rank', 'Adventurer', 'Title', 'Days', 'Level', 'Growth'].map((h) => (
                    <th
                      key={h}
                      className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider"
                      style={{
                        color: 'var(--aeth-parchment-dim)',
                        fontFamily: "'Cinzel', serif",
                        letterSpacing: '0.07em',
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
                      className="border-b group"
                      style={{
                        borderColor: 'var(--aeth-iron)',
                        backgroundColor:
                          entry.rank === 1
                            ? 'rgba(214,162,77,0.04)'
                            : i % 2 === 0
                            ? 'transparent'
                            : 'rgba(255,255,255,0.012)',
                        transition: 'background-color 0.15s ease',
                        boxShadow: rankInfo.glow ? `inset 3px 0 0 ${rankInfo.color}55` : undefined,
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = 'rgba(214,162,77,0.06)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor =
                          entry.rank === 1
                            ? 'rgba(214,162,77,0.04)'
                            : i % 2 === 0
                            ? 'transparent'
                            : 'rgba(255,255,255,0.012)';
                      }}
                    >
                      <td className="px-5 py-3.5">
                        <span
                          style={{
                            color: rankInfo.color,
                            fontFamily: "'Cinzel', serif",
                            fontSize: entry.rank <= 3 ? '1.05rem' : '0.85rem',
                            fontWeight: 700,
                          }}
                        >
                          {rankInfo.symbol}
                        </span>
                      </td>
                      <td className="px-5 py-3.5">
                        <span
                          className="font-semibold text-sm"
                          style={{ color: 'var(--aeth-parchment)', fontFamily: "'IBM Plex Sans', sans-serif" }}
                        >
                          {entry.username}
                        </span>
                      </td>
                      <td className="px-5 py-3.5">
                        <span
                          className="text-xs px-2 py-0.5 rounded-full"
                          style={{
                            backgroundColor: 'rgba(214,162,77,0.10)',
                            color: 'var(--aeth-gold)',
                            border: '1px solid rgba(214,162,77,0.22)',
                            fontFamily: "'IBM Plex Sans', sans-serif",
                          }}
                        >
                          {entry.title}
                        </span>
                      </td>
                      <td className="px-5 py-3.5">
                        <span
                          className="text-sm"
                          style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'Azeret Mono', monospace" }}
                        >
                          {entry.age}d
                        </span>
                      </td>
                      <td className="px-5 py-3.5">
                        <span
                          className="text-sm font-semibold"
                          style={{ color: 'var(--aeth-parchment)', fontFamily: "'IBM Plex Sans', sans-serif" }}
                        >
                          {entry.level}
                        </span>
                      </td>
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-1">
                          <TrendingUp size={11} style={{ color: 'var(--aeth-gold)' }} />
                          <span
                            className="text-sm"
                            style={{ color: 'var(--aeth-gold)', fontFamily: "'Azeret Mono', monospace" }}
                          >
                            +{entry.improvement}%
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

        {/* Note */}
        <p
          className="text-center text-xs mt-4"
          style={{ color: 'var(--aeth-iron)', fontFamily: "'Azeret Mono', monospace" }}
        >
          * Rankings updated every hour &middot; Growth % based on past 30 days
        </p>
      </div>
    </section>
  );
};

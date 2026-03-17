import { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const ICONS_MAP = {
  '📈': 'TrendingUp',
  '⚔️': 'Swords',
  '🏆': 'Trophy',
  '👑': 'Crown',
  '🎯': 'Target',
  '🎖️': 'Medal',
  '✨': 'Sparkles',
  '🎲': 'Dice6',
  '📜': 'Scroll',
  '💍': 'Ring',
  '🏪': 'Store',
  '⚗️': 'FlaskConical',
  '🔮': 'Gem',
  '🛡️': 'Shield',
  '🗺️': 'Map',
  '💎': 'Gem',
  '🃏': 'BookOpen',
  '🔐': 'Lock',
  '⚜️': 'Flower',
  '🆓': 'Gift',
  '🐴': 'Activity',
  '♾️': 'Infinity',
  '💪': 'Dumbbell',
  '🏰': 'Castle',
  '🤝': 'Handshake',
  '📰': 'Newspaper',
  '🐉': 'Zap',
  '📚': 'BookOpen',
  '⚡': 'Zap',
  '🌐': 'Globe',
  '🗡️': 'Sword',
  '💰': 'Coins',
  '🏯': 'Home',
  '🎰': 'Dices',
  '🌑': 'Moon',
  '🏦': 'Building',
  '🌟': 'Star',
  '❤️‍🩹': 'Heart',
  '🪙': 'Circle',
  '⬆️': 'ArrowUp',
  '⚒️': 'Hammer',
};

const FeatureCard = ({ feature }) => (
  <div
    className="aeth-card feature-card p-5 h-full flex flex-col gap-3"
    data-testid="feature-card"
    style={{ transition: 'border-color 0.2s ease, box-shadow 0.2s ease' }}
  >
    <div className="flex items-start gap-3">
      <div className="icon-coin">
        <span style={{ fontSize: '1.25rem' }}>{feature.icon}</span>
      </div>
      <h3
        className="font-semibold leading-snug mt-1"
        style={{
          fontFamily: "'Cinzel', serif",
          color: 'var(--aeth-parchment)',
          fontSize: '0.9rem',
          letterSpacing: '0.03em',
        }}
      >
        {feature.title}
      </h3>
    </div>
    <p
      className="text-sm leading-relaxed flex-1"
      style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}
    >
      {feature.desc}
    </p>
  </div>
);

export const FeaturesSection = ({ features = [] }) => {
  const [page, setPage] = useState(0);
  const perPage = 9; // 3x3 grid
  const totalPages = Math.ceil(features.length / perPage);
  const current = features.slice(page * perPage, (page + 1) * perPage);

  return (
    <section
      data-testid="features-section"
      className="aeth-section"
      style={{ backgroundColor: 'var(--aeth-stone-0)' }}
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
            <span style={{ color: 'var(--aeth-gold)', fontSize: '1.2rem' }}>⚔</span>
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
            The Realm's Features
          </h2>
          <p style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
            42 ways to forge your legend in Aethoria
          </p>
        </motion.div>

        {/* Desktop Grid */}
        <div
          data-testid="features-carousel"
          className="hidden sm:grid grid-cols-2 lg:grid-cols-3 gap-4"
        >
          {current.map((f, i) => (
            <motion.div
              key={f.id || i}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.04 }}
            >
              <FeatureCard feature={f} />
            </motion.div>
          ))}
        </div>

        {/* Mobile Carousel */}
        <div className="sm:hidden grid grid-cols-1 gap-4">
          {current.slice(0, 3).map((f, i) => (
            <FeatureCard key={f.id || i} feature={f} />
          ))}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-4 mt-8">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="btn-iron p-2 rounded-lg disabled:opacity-40"
              aria-label="Previous"
            >
              <ChevronLeft size={18} />
            </button>
            <span
              className="text-sm"
              style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'Azeret Mono', monospace" }}
            >
              {page + 1} / {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page === totalPages - 1}
              className="btn-iron p-2 rounded-lg disabled:opacity-40"
              aria-label="Next"
            >
              <ChevronRight size={18} />
            </button>
          </div>
        )}

        {/* Page dots */}
        <div className="flex justify-center gap-2 mt-4">
          {Array.from({ length: totalPages }).map((_, i) => (
            <button
              key={i}
              onClick={() => setPage(i)}
              className="w-2 h-2 rounded-full"
              style={{
                backgroundColor: i === page ? 'var(--aeth-gold)' : 'var(--aeth-iron)',
                transition: 'background-color 0.2s ease',
              }}
              aria-label={`Page ${i + 1}`}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

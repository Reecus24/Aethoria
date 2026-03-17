import { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const FeatureCard = ({ feature, index }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ delay: (index % 9) * 0.04 }}
    className="aeth-card feature-card p-5 h-full flex flex-col gap-3 relative group"
    data-testid="feature-card"
    style={{ transition: 'border-color 0.2s ease, box-shadow 0.2s ease' }}
  >
    {/* Rune glow on hover (pseudo via inline) */}
    <div
      className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 pointer-events-none"
      style={{
        background: 'radial-gradient(circle at 20% 20%, rgba(60,34,80,0.18), transparent 60%)',
        transition: 'opacity 0.3s ease',
      }}
    />
    <div className="flex items-start gap-3 relative z-10">
      <div className="icon-coin" style={{ position: 'relative' }}>
        <span style={{ fontSize: '1.2rem' }}>{feature.icon}</span>
      </div>
      <h3
        className="font-semibold leading-snug mt-1"
        style={{
          fontFamily: "'Cinzel', serif",
          color: 'var(--aeth-parchment)',
          fontSize: '0.88rem',
          letterSpacing: '0.03em',
        }}
      >
        {feature.title}
      </h3>
    </div>
    <p
      className="text-sm leading-relaxed flex-1 relative z-10"
      style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}
    >
      {feature.desc}
    </p>
  </motion.div>
);

export const FeaturesSection = ({ features = [] }) => {
  const [page, setPage] = useState(0);
  const perPage = 9;
  const totalPages = Math.ceil(features.length / perPage);
  const current = features.slice(page * perPage, (page + 1) * perPage);

  return (
    <section
      id="features"
      data-testid="features-section"
      className="aeth-section"
      style={{ backgroundColor: 'var(--aeth-stone-0)' }}
    >
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="aeth-divider mb-8">
            <span style={{ color: 'var(--aeth-gold)', fontSize: '1.1rem' }}>⚔</span>
          </div>
          <motion.h2
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="font-cinzel mb-2"
            style={{
              fontFamily: "'Cinzel', serif",
              fontSize: '2rem',
              fontWeight: 700,
              color: 'var(--aeth-parchment)',
              letterSpacing: '0.04em',
            }}
          >
            The Realm&apos;s Features
          </motion.h2>
          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}
          >
            {features.length} ways to forge your legend in Aethoria
          </motion.p>
        </div>

        {/* Grid */}
        <div
          data-testid="features-carousel"
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
        >
          {current.map((f, i) => (
            <FeatureCard key={f.id || i} feature={f} index={i} />
          ))}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-4 mt-10">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="btn-iron p-2 rounded-lg disabled:opacity-40 flex items-center gap-1 text-sm px-3"
              aria-label="Previous"
            >
              <ChevronLeft size={16} /> Prev
            </button>

            {/* Page numbers */}
            <div className="flex gap-1">
              {Array.from({ length: totalPages }).map((_, i) => (
                <button
                  key={i}
                  onClick={() => setPage(i)}
                  className="w-8 h-8 rounded text-xs font-semibold"
                  style={{
                    backgroundColor: i === page ? 'rgba(214,162,77,0.15)' : 'transparent',
                    border: i === page ? '1px solid rgba(214,162,77,0.5)' : '1px solid var(--aeth-iron)',
                    color: i === page ? 'var(--aeth-gold)' : 'var(--aeth-parchment-dim)',
                    fontFamily: "'Azeret Mono', monospace",
                    transition: 'background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease',
                  }}
                >
                  {i + 1}
                </button>
              ))}
            </div>

            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page === totalPages - 1}
              className="btn-iron p-2 rounded-lg disabled:opacity-40 flex items-center gap-1 text-sm px-3"
              aria-label="Next"
            >
              Next <ChevronRight size={16} />
            </button>
          </div>
        )}

        {/* Feature count indicator */}
        <p
          className="text-center text-xs mt-4"
          style={{ color: 'var(--aeth-iron)', fontFamily: "'Azeret Mono', monospace" }}
        >
          Showing {page * perPage + 1}–{Math.min((page + 1) * perPage, features.length)} of {features.length} features
        </p>
      </div>
    </section>
  );
};

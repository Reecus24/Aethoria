import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const pathKeys = ['knight', 'shadow', 'noble'];

export const PathsSection = ({ paths = [] }) => {
  const [active, setActive] = useState('knight');

  // Build map from array
  const pathMap = {};
  paths.forEach((p) => {
    pathMap[p.key] = p;
  });

  const current = pathMap[active];

  const tabs = [
    { key: 'knight', label: 'The Knight', icon: '⚔️', testId: 'paths-tab-knight' },
    { key: 'shadow', label: 'The Shadow', icon: '🗡️', testId: 'paths-tab-shadow' },
    { key: 'noble', label: 'The Noble', icon: '👑', testId: 'paths-tab-noble' },
  ];

  return (
    <section
      id="paths"
      data-testid="paths-section"
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
            <span style={{ color: 'var(--aeth-gold)', fontSize: '1.2rem' }}>⚜</span>
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
            Which Path Will You Take?
          </h2>
          <p style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
            Three paths. One destiny. Your legend awaits.
          </p>
        </motion.div>

        {/* Tabs */}
        <div
          data-testid="paths-tabs"
          className="flex flex-col sm:flex-row gap-2 mb-8"
        >
          {tabs.map((tab) => (
            <button
              key={tab.key}
              data-testid={tab.testId}
              onClick={() => setActive(tab.key)}
              className="flex-1 py-3 px-6 text-sm font-semibold rounded-lg flex items-center justify-center gap-2"
              style={{
                fontFamily: "'Cinzel', serif",
                letterSpacing: '0.05em',
                backgroundColor:
                  active === tab.key ? 'rgba(214,162,77,0.12)' : 'var(--aeth-stone-2)',
                border:
                  active === tab.key
                    ? '1px solid rgba(214,162,77,0.5)'
                    : '1px solid var(--aeth-iron)',
                color:
                  active === tab.key ? 'var(--aeth-gold)' : 'var(--aeth-parchment-dim)',
                boxShadow:
                  active === tab.key
                    ? 'inset 0 -2px 0 0 rgba(214,162,77,0.8), 0 4px 20px rgba(214,162,77,0.08)'
                    : 'none',
                transition: 'background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease, box-shadow 0.2s ease',
              }}
            >
              <span>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          {current && (
            <motion.div
              key={active}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.3 }}
              className="aeth-card p-8"
            >
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
                {/* Left: description */}
                <div>
                  <div className="flex items-center gap-4 mb-6">
                    <div
                      className="w-16 h-16 rounded-full flex items-center justify-center text-2xl"
                      style={{
                        backgroundColor: 'var(--aeth-iron-2)',
                        border: '2px solid var(--aeth-iron)',
                        boxShadow: `0 0 20px ${current.color}33`,
                      }}
                    >
                      {tabs.find((t) => t.key === active)?.icon}
                    </div>
                    <div>
                      <h3
                        style={{
                          fontFamily: "'Cinzel', serif",
                          fontSize: '1.5rem',
                          fontWeight: 700,
                          color: current.color || 'var(--aeth-parchment)',
                          letterSpacing: '0.04em',
                        }}
                      >
                        {current.title}
                      </h3>
                      <p
                        className="text-sm"
                        style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}
                      >
                        {current.subtitle}
                      </p>
                    </div>
                  </div>
                  <p
                    className="text-base leading-relaxed"
                    style={{
                      color: 'var(--aeth-parchment-dim)',
                      fontFamily: "'IBM Plex Sans', sans-serif",
                      maxWidth: '55ch',
                    }}
                  >
                    {current.description}
                  </p>
                </div>

                {/* Right: highlights */}
                <div>
                  <h4
                    className="mb-4 text-xs uppercase tracking-widest"
                    style={{
                      color: 'var(--aeth-gold)',
                      fontFamily: "'Cinzel', serif",
                    }}
                  >
                    Path Abilities
                  </h4>
                  <ul className="path-highlight-list space-y-3">
                    {(current.highlights || []).map((h, i) => (
                      <li key={i}>{h}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
};

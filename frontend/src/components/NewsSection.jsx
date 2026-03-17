import { motion } from 'framer-motion';
import { ExternalLink, Newspaper } from 'lucide-react';

export const NewsSection = ({ news = [] }) => {
  const featured = news[0];
  const rest = news.slice(1);

  return (
    <section
      data-testid="news-section"
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
            <span style={{ color: 'var(--aeth-gold)', fontSize: '1.2rem' }}>📜</span>
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
            The Royal Chronicles
          </h2>
          <p style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
            Latest decrees, patch notes, and realm-wide events
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Featured */}
          {featured && (
            <motion.div
              initial={{ opacity: 0, x: -16 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <div
                className="aeth-card h-full flex flex-col justify-between p-8 relative overflow-hidden"
              >
                {/* Background image darkened */}
                <div
                  className="absolute inset-0 opacity-10 pointer-events-none"
                  style={{
                    backgroundImage: `url(https://images.unsplash.com/photo-1654408618689-b737eed3c171?w=600&q=40)`,
                    backgroundSize: 'cover',
                    backgroundPosition: 'center',
                  }}
                />
                <div className="relative z-10">
                  <div className="flex items-center gap-2 mb-4">
                    <span
                      className="text-xs px-2 py-0.5 rounded-full uppercase font-semibold tracking-wider"
                      style={{
                        backgroundColor: 'rgba(142,29,44,0.3)',
                        color: '#E57373',
                        border: '1px solid rgba(142,29,44,0.5)',
                        fontFamily: "'Cinzel', serif",
                      }}
                    >
                      Latest Chronicle
                    </span>
                  </div>
                  <h3
                    className="text-xl font-semibold mb-3 leading-snug"
                    style={{
                      fontFamily: "'Cinzel', serif",
                      color: 'var(--aeth-parchment)',
                      letterSpacing: '0.03em',
                    }}
                  >
                    {featured.title}
                  </h3>
                  <p
                    className="text-sm"
                    style={{ color: 'var(--aeth-iron)', fontFamily: "'Azeret Mono', monospace" }}
                  >
                    {featured.date}
                  </p>
                </div>
                <div className="relative z-10 mt-6">
                  <a
                    href={featured.url}
                    data-testid="news-more-button"
                    className="btn-gold px-5 py-2 rounded-lg inline-flex items-center gap-2 text-sm"
                  >
                    Read the Chronicle <ExternalLink size={14} />
                  </a>
                </div>
              </div>
            </motion.div>
          )}

          {/* News list */}
          <motion.div
            initial={{ opacity: 0, x: 16 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="flex flex-col gap-3"
          >
            {rest.map((item, i) => (
              <a
                key={item.id || i}
                href={item.url}
                data-testid="news-item"
                className="aeth-card p-4 flex items-start gap-4 group"
                style={{ textDecoration: 'none', display: 'flex' }}
              >
                <div
                  className="w-8 h-8 flex-shrink-0 rounded flex items-center justify-center mt-0.5"
                  style={{
                    backgroundColor: 'var(--aeth-iron-2)',
                    color: 'var(--aeth-gold)',
                  }}
                >
                  <Newspaper size={14} />
                </div>
                <div className="flex-1 min-w-0">
                  <p
                    className="text-sm font-medium leading-snug mb-1"
                    style={{
                      color: 'var(--aeth-parchment)',
                      fontFamily: "'IBM Plex Sans', sans-serif",
                      transition: 'color 0.2s ease',
                    }}
                  >
                    {item.title}
                  </p>
                  <p
                    className="text-xs"
                    style={{ color: 'var(--aeth-iron)', fontFamily: "'Azeret Mono', monospace" }}
                  >
                    {item.date}
                  </p>
                </div>
                <ExternalLink
                  size={14}
                  className="flex-shrink-0 mt-1 opacity-0 group-hover:opacity-100"
                  style={{ color: 'var(--aeth-gold)', transition: 'opacity 0.2s ease' }}
                />
              </a>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
};

import { motion } from 'framer-motion';
import { Users } from 'lucide-react';

const formatNum = (n) => {
  if (!n) return '—';
  if (n >= 1000) return (n / 1000).toFixed(1) + 'k';
  return n.toString();
};

export const OnlineCounter = ({ online }) => {
  const stats = [
    { label: 'Online Now', value: online?.now, testId: 'online-players-now' },
    { label: 'Last Hour', value: online?.last_hour, testId: 'online-players-last-hour' },
    { label: 'Last 24 Hours', value: online?.last_24h, testId: 'online-players-last-24h' },
  ];

  return (
    <div
      data-testid="online-players-widget"
      className="py-8"
      style={{ backgroundColor: 'var(--aeth-stone-0)', borderTop: '1px solid var(--aeth-iron)', borderBottom: '1px solid var(--aeth-iron)' }}
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row items-center justify-center gap-8 sm:gap-0">
          {stats.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="flex flex-col items-center sm:flex-1 relative"
            >
              {i > 0 && (
                <div
                  className="hidden sm:block absolute left-0 top-1/2 -translate-y-1/2 w-px h-10"
                  style={{ backgroundColor: 'var(--aeth-iron)' }}
                />
              )}
              <div className="flex items-center gap-2 mb-1">
                <Users size={14} style={{ color: 'var(--aeth-gold)' }} />
                <span
                  className="text-xs font-semibold uppercase tracking-widest"
                  style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'Cinzel', serif" }}
                >
                  {stat.label}
                </span>
              </div>
              <span
                data-testid={stat.testId}
                style={{
                  fontFamily: "'Cinzel', serif",
                  fontSize: '2rem',
                  fontWeight: 700,
                  color: 'var(--aeth-gold)',
                  textShadow: '0 0 20px rgba(214,162,77,0.3)',
                }}
              >
                {formatNum(stat.value)}
              </span>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

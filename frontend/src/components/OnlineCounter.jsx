import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Users } from 'lucide-react';

// Animated counter hook
const useCountUp = (target, duration = 1800) => {
  const [value, setValue] = useState(0);
  const rafRef = useRef(null);
  const startRef = useRef(null);

  useEffect(() => {
    if (!target) return;
    const start = performance.now();
    startRef.current = start;
    const animate = (now) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.floor(eased * target));
      if (progress < 1) rafRef.current = requestAnimationFrame(animate);
    };
    rafRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(rafRef.current);
  }, [target, duration]);

  return value;
};

const formatNum = (n) => {
  if (!n && n !== 0) return '—';
  if (n >= 1000) return (n / 1000).toFixed(1) + 'k';
  return n.toString();
};

const StatItem = ({ label, value, testId, delay }) => {
  const [inView, setInView] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setInView(true); },
      { threshold: 0.5 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  const animated = useCountUp(inView ? value : 0, 1800 + delay * 200);

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 10 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: delay * 0.12 }}
      className="flex flex-col items-center sm:flex-1 relative"
    >
      <div className="flex items-center gap-2 mb-1">
        <Users size={13} style={{ color: 'var(--aeth-gold)' }} />
        <span
          className="text-xs font-semibold uppercase tracking-widest"
          style={{
            color: 'var(--aeth-parchment-dim)',
            fontFamily: "'Cinzel', serif",
            letterSpacing: '0.08em',
          }}
        >
          {label}
        </span>
      </div>
      <span
        data-testid={testId}
        style={{
          fontFamily: "'Cinzel', serif",
          fontSize: '2.2rem',
          fontWeight: 700,
          color: 'var(--aeth-gold)',
          textShadow: '0 0 24px rgba(214,162,77,0.35)',
          letterSpacing: '0.02em',
          lineHeight: 1,
        }}
      >
        {formatNum(animated)}
      </span>
    </motion.div>
  );
};

export const OnlineCounter = ({ online }) => {
  const stats = [
    { label: 'Online Now', value: online?.now, testId: 'online-players-now', delay: 0 },
    { label: 'Last Hour', value: online?.last_hour, testId: 'online-players-last-hour', delay: 1 },
    { label: 'Last 24 Hours', value: online?.last_24h, testId: 'online-players-last-24h', delay: 2 },
  ];

  return (
    <div
      data-testid="online-players-widget"
      className="py-8"
      style={{
        backgroundColor: 'var(--aeth-stone-0)',
        borderTop: '1px solid var(--aeth-iron)',
        borderBottom: '1px solid var(--aeth-iron)',
      }}
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row items-center justify-center gap-8 sm:gap-0">
          {stats.map((stat, i) => (
            <div key={stat.label} className="flex sm:flex-1 items-center relative w-full sm:w-auto justify-center">
              {i > 0 && (
                <div
                  className="hidden sm:block absolute left-0 top-1/2 -translate-y-1/2 w-px h-10"
                  style={{ backgroundColor: 'var(--aeth-iron)' }}
                />
              )}
              <StatItem {...stat} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronUp } from 'lucide-react';

export const BackToTop = () => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => setVisible(window.scrollY > 600);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const scrollTop = () => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      window.scrollTo(0, 0);
    } else {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <AnimatePresence>
      {visible && (
        <motion.button
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          onClick={scrollTop}
          data-testid="back-to-top-button"
          aria-label="Back to top"
          className="fixed z-50"
          style={{
            bottom: '4.5rem',
            right: '1.25rem',
            width: 44,
            height: 44,
            borderRadius: '50%',
            backgroundColor: 'var(--aeth-iron-2)',
            border: '1px solid var(--aeth-gold)',
            color: 'var(--aeth-gold)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 16px rgba(0,0,0,0.5)',
            cursor: 'pointer',
            transition: 'background-color 0.2s ease, box-shadow 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = 'rgba(214,162,77,0.15)';
            e.currentTarget.style.boxShadow = '0 4px 20px rgba(214,162,77,0.3)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'var(--aeth-iron-2)';
            e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.5)';
          }}
        >
          <ChevronUp size={20} />
        </motion.button>
      )}
    </AnimatePresence>
  );
};

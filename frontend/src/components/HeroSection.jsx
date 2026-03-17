import { motion } from 'framer-motion';
import { Shield, Sword, Crown } from 'lucide-react';

export const HeroSection = ({ onJoin, onLogin }) => {
  return (
    <section
      className="relative min-h-[90vh] flex items-center aeth-noise-bg overflow-hidden"
      style={{ backgroundColor: 'var(--aeth-stone-0)' }}
    >
      {/* Background radial accents */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(900px 600px at 15% 40%, rgba(214,162,77,0.06), transparent 60%), radial-gradient(700px 500px at 85% 20%, rgba(60,34,80,0.10), transparent 55%)',
        }}
      />

      {/* Castle hero image (right side) */}
      <div
        className="absolute inset-y-0 right-0 w-full md:w-1/2 pointer-events-none"
        style={{ zIndex: 1 }}
      >
        <img
          src="https://images.unsplash.com/photo-1533154683836-84ea7a0bc310?w=900&q=60&auto=format&fit=crop"
          alt="Dark medieval castle"
          className="w-full h-full object-cover"
          style={{ opacity: 0.18 }}
        />
        {/* gradient overlay to blend with left content */}
        <div
          className="absolute inset-0"
          style={{
            background:
              'linear-gradient(to right, var(--aeth-stone-0) 0%, rgba(7,6,6,0.55) 40%, rgba(7,6,6,0.0) 100%)',
          }}
        />
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 w-full">
        <div className="max-w-2xl">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold mb-6 tracking-widest uppercase"
            style={{
              backgroundColor: 'rgba(214,162,77,0.12)',
              border: '1px solid rgba(214,162,77,0.3)',
              color: 'var(--aeth-gold)',
              fontFamily: "'Cinzel', serif",
            }}
          >
            <Shield size={12} />
            Free to Play · Dark Medieval RPG
          </motion.div>

          {/* Title */}
          <motion.h1
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="font-cinzel leading-tight mb-4"
            style={{
              fontSize: 'clamp(2.8rem, 6vw, 5rem)',
              color: 'var(--aeth-parchment)',
              fontFamily: "'Cinzel', Georgia, serif",
              fontWeight: 700,
              letterSpacing: '0.04em',
              textShadow: '0 2px 20px rgba(214,162,77,0.15)',
            }}
          >
            Realm of
            <br />
            <span style={{ color: 'var(--aeth-gold)' }}>Aethoria</span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-lg mb-3"
            style={{ color: 'var(--aeth-parchment-dim)', lineHeight: 1.6, maxWidth: '52ch', fontFamily: "'IBM Plex Sans', sans-serif" }}
          >
            A dark, living medieval world where only the sharpest survive.
            Build your character to legendary strength and play it <em>your</em> way.
          </motion.p>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.25 }}
            className="text-base mb-10"
            style={{ color: 'var(--aeth-iron)', fontFamily: "'IBM Plex Sans', sans-serif" }}
          >
            A massively multiplayer RPG with thousands of active adventurers. Fight them,
            befriend them, trade with them, or rule them. Whatever you do — do it now.
          </motion.p>

          {/* CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.35 }}
            className="flex flex-wrap gap-4"
          >
            <button
              data-testid="hero-join-button"
              onClick={onJoin}
              className="btn-gold px-8 py-3 rounded-lg text-base"
            >
              Join the Realm
            </button>
            <button
              data-testid="hero-login-button"
              onClick={onLogin}
              className="btn-iron px-8 py-3 rounded-lg text-base"
            >
              Enter the Gate
            </button>
          </motion.div>

          {/* Trust markers */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="flex flex-wrap gap-6 mt-10"
          >
            {[
              { icon: <Sword size={14} />, text: '50,000+ Adventurers' },
              { icon: <Shield size={14} />, text: 'Free Forever' },
              { icon: <Crown size={14} />, text: 'No Resets · Ever' },
            ].map(({ icon, text }) => (
              <div
                key={text}
                className="flex items-center gap-2 text-sm"
                style={{ color: 'var(--aeth-parchment-dim)' }}
              >
                <span style={{ color: 'var(--aeth-gold)' }}>{icon}</span>
                {text}
              </div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
};

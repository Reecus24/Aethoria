import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Shield, Sword, Crown } from 'lucide-react';

// Simple ember particle canvas
const EmberCanvas = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    // Skip if prefers-reduced-motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const resize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    // Ember particles
    const particles = Array.from({ length: 40 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height + canvas.height * 0.4,
      size: Math.random() * 2 + 0.5,
      speedX: (Math.random() - 0.5) * 0.3,
      speedY: -(Math.random() * 0.6 + 0.15),
      opacity: Math.random() * 0.5 + 0.1,
      color: Math.random() > 0.5 ? '#D6A24D' : '#C9832E',
    }));

    let animId;
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach((p) => {
        ctx.save();
        ctx.globalAlpha = p.opacity;
        ctx.fillStyle = p.color;
        ctx.shadowBlur = 4;
        ctx.shadowColor = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();

        p.x += p.speedX;
        p.y += p.speedY;
        p.opacity -= 0.0012;

        // Reset when faded or out of bounds
        if (p.opacity <= 0 || p.y < 0) {
          p.x = Math.random() * canvas.width;
          p.y = canvas.height;
          p.opacity = Math.random() * 0.5 + 0.1;
          p.size = Math.random() * 2 + 0.5;
          p.speedX = (Math.random() - 0.5) * 0.3;
          p.speedY = -(Math.random() * 0.6 + 0.15);
        }
      });
      animId = requestAnimationFrame(animate);
    };
    animate();
    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full pointer-events-none"
      style={{ zIndex: 2 }}
    />
  );
};

export const HeroSection = ({ onJoin, onLogin }) => {
  return (
    <section
      id="hero"
      className="relative min-h-screen flex items-center overflow-hidden"
      style={{ backgroundColor: 'var(--aeth-stone-0)' }}
    >
      {/* Deep radial atmosphere */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          zIndex: 1,
          background:
            'radial-gradient(1100px 700px at 10% 60%, rgba(214,162,77,0.07), transparent 65%),' +
            'radial-gradient(800px 600px at 90% 20%, rgba(60,34,80,0.12), transparent 60%),' +
            'radial-gradient(600px 400px at 50% 80%, rgba(142,29,44,0.06), transparent 55%)',
        }}
      />

      {/* Castle background image */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{ zIndex: 0 }}
      >
        <img
          src="https://images.unsplash.com/photo-1533154683836-84ea7a0bc310?w=1600&q=50&auto=format&fit=crop"
          alt=""
          aria-hidden="true"
          className="w-full h-full object-cover"
          style={{ opacity: 0.14 }}
        />
        {/* Gradient overlay left→right so text stays readable */}
        <div
          className="absolute inset-0"
          style={{
            background:
              'linear-gradient(to right, rgba(7,6,6,0.96) 0%, rgba(7,6,6,0.75) 40%, rgba(7,6,6,0.15) 75%, transparent 100%),' +
              'linear-gradient(to top, rgba(7,6,6,0.8) 0%, transparent 35%)',
          }}
        />
      </div>

      {/* Ember particles */}
      <EmberCanvas />

      {/* Main content */}
      <div
        className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 w-full"
        style={{ zIndex: 5 }}
      >
        <div className="max-w-2xl">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold mb-6 tracking-widest uppercase"
            style={{
              backgroundColor: 'rgba(214,162,77,0.1)',
              border: '1px solid rgba(214,162,77,0.3)',
              color: 'var(--aeth-gold)',
              fontFamily: "'Cinzel', serif",
            }}
          >
            <Shield size={11} />
            Free to Play &middot; Dark Medieval Fantasy RPG
          </motion.div>

          {/* Title */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.1 }}
            style={{
              fontFamily: "'Cinzel', Georgia, serif",
              fontSize: 'clamp(3rem, 7vw, 5.5rem)',
              fontWeight: 700,
              color: 'var(--aeth-parchment)',
              letterSpacing: '0.03em',
              lineHeight: 1.1,
              marginBottom: '1rem',
              textShadow: '0 2px 40px rgba(214,162,77,0.12)',
            }}
          >
            Realm of
            <br />
            <span
              style={{
                color: 'var(--aeth-gold)',
                textShadow: '0 0 60px rgba(214,162,77,0.25)',
              }}
            >
              Aethoria
            </span>
          </motion.h1>

          {/* Ornamental line under title */}
          <motion.div
            initial={{ scaleX: 0, opacity: 0 }}
            animate={{ scaleX: 1, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.35 }}
            className="mb-6"
            style={{ transformOrigin: 'left' }}
          >
            <div
              className="h-px w-48"
              style={{
                background: 'linear-gradient(to right, var(--aeth-gold), transparent)',
              }}
            />
          </motion.div>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-lg mb-3"
            style={{
              color: 'var(--aeth-parchment-dim)',
              lineHeight: 1.65,
              maxWidth: '52ch',
              fontFamily: "'IBM Plex Sans', sans-serif",
            }}
          >
            A dark, living medieval world where only the sharpest survive.
            Build your character to legendary strength and play it <em>your</em> way.
          </motion.p>
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.28 }}
            className="text-sm mb-10"
            style={{
              color: 'var(--aeth-iron)',
              maxWidth: '52ch',
              fontFamily: "'IBM Plex Sans', sans-serif",
              lineHeight: 1.6,
            }}
          >
            A massively multiplayer RPG with thousands of active adventurers. Fight them,
            befriend them, trade with them, or rule them. Whatever you do — do it now.
          </motion.p>

          {/* CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.38 }}
            className="flex flex-wrap gap-4"
          >
            <button
              data-testid="hero-join-button"
              onClick={onJoin}
              className="btn-gold px-8 py-3 rounded-lg text-sm"
            >
              Join the Realm
            </button>
            <button
              data-testid="hero-login-button"
              onClick={onLogin}
              className="btn-iron px-8 py-3 rounded-lg text-sm"
            >
              Enter the Gate
            </button>
          </motion.div>

          {/* Trust markers */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.65 }}
            className="flex flex-wrap gap-6 mt-10 pt-8"
            style={{ borderTop: '1px solid var(--aeth-iron)' }}
          >
            {[
              { icon: <Crown size={13} />, text: 'No Resets · Ever' },
              { icon: <Shield size={13} />, text: 'Your Legend Persists' },
            ].map(({ icon, text }) => (
              <div
                key={text}
                className="flex items-center gap-2 text-sm"
                style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}
              >
                <span style={{ color: 'var(--aeth-gold)' }}>{icon}</span>
                {text}
              </div>
            ))}
          </motion.div>
        </div>
      </div>

      {/* Bottom fade */}
      <div
        className="absolute bottom-0 left-0 right-0 h-32 pointer-events-none"
        style={{
          background: 'linear-gradient(to bottom, transparent, var(--aeth-stone-0))',
          zIndex: 6,
        }}
      />
    </section>
  );
};

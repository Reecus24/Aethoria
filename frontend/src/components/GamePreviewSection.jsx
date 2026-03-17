import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Sample game actions simulated in the terminal
const GAME_SCENES = [
  {
    path: 'knight',
    pathColor: '#C0392B',
    pathIcon: '⚔️',
    lines: [
      { type: 'prompt', text: '> Train at the Royal Barracks' },
      { type: 'result', text: 'You spend 4 hours training with the master-at-arms...' },
      { type: 'stat', text: '+ Strength increased to 18' },
      { type: 'stat', text: '+ Dexterity increased to 9' },
      { type: 'reward', text: '+ 45 XP earned — Level 3 reached!' },
      { type: 'prompt', text: '> Challenge IronFistVoss to a duel' },
      { type: 'result', text: 'You enter the tournament grounds and issue your challenge...' },
      { type: 'combat', text: 'Round 1: You strike for 28 damage — Voss retaliates for 14...' },
      { type: 'combat', text: 'Round 2: Critical hit! 52 damage — Voss is staggered!' },
      { type: 'victory', text: '⚔️  Victory! Voss has been hospitalised.' },
      { type: 'reward', text: '+ 220 gold looted from the fallen warrior' },
      { type: 'reward', text: '+ Rank increased: Squire → Knight' },
    ],
  },
  {
    path: 'shadow',
    pathColor: '#8E44AD',
    pathIcon: '🗡️',
    lines: [
      { type: 'prompt', text: '> Pickpocket a merchant at the market' },
      { type: 'result', text: 'You blend into the crowd, watching your target carefully...' },
      { type: 'stat', text: 'Dexterity check: 16/20 — Success!' },
      { type: 'reward', text: '+ 85 gold stolen from Lord Gregor\'s coin purse' },
      { type: 'prompt', text: '> Commit a burglary at the merchant quarter' },
      { type: 'result', text: 'You scale the wall in the dead of night...' },
      { type: 'combat', text: 'Guard spotted! You dodge left and knock him unconscious.' },
      { type: 'reward', text: '+ Ancient Relic: Shadowstep Pendant obtained!' },
      { type: 'reward', text: '+ 310 gold worth of valuables secured' },
      { type: 'stat', text: '+ Crime skill increased — new deed unlocked: Safe Cracking' },
    ],
  },
  {
    path: 'noble',
    pathColor: '#D4AC0D',
    pathIcon: '👑',
    lines: [
      { type: 'prompt', text: '> Invest 500 gold in iron ore futures' },
      { type: 'result', text: 'You place your order on the Merchant Exchange...' },
      { type: 'stat', text: 'Market trend: Bullish — your investment gains 12%' },
      { type: 'reward', text: '+ 560 gold returned — net profit: 60 gold' },
      { type: 'prompt', text: '> Found a Merchant House: House of the Golden Chalice' },
      { type: 'result', text: 'You register your merchant house at the Royal Chamber...' },
      { type: 'stat', text: 'House capacity: 5 employees — Ready for recruitment' },
      { type: 'reward', text: '+ Merchant House founded successfully!' },
      { type: 'prompt', text: '> Purchase the Silver Manor stronghold' },
      { type: 'result', text: 'The deed is signed. The Silver Manor is yours.' },
      { type: 'reward', text: '+ Passive income: 45 gold/day from rent collection' },
    ],
  },
];

const lineColors = {
  prompt: '#D6A24D',
  result: '#A8936D',
  stat: '#64B5F6',
  reward: '#81C784',
  combat: '#FFB74D',
  victory: '#FF8A65',
};

const linePrefix = {
  prompt: '',
  result: '  ',
  stat: '  ▸ ',
  reward: '  ★ ',
  combat: '  ⚔ ',
  victory: '  ',
};

export const GamePreviewSection = () => {
  const [sceneIndex, setSceneIndex] = useState(0);
  const [visibleLines, setVisibleLines] = useState([]);
  const [lineIndex, setLineIndex] = useState(0);
  const terminalRef = useRef(null);
  const timerRef = useRef(null);

  const scene = GAME_SCENES[sceneIndex];

  // Reset and animate lines when scene changes
  useEffect(() => {
    setVisibleLines([]);
    setLineIndex(0);
    clearTimeout(timerRef.current);
  }, [sceneIndex]);

  // Reveal lines one by one
  useEffect(() => {
    if (lineIndex >= scene.lines.length) return;
    const delay = scene.lines[lineIndex].type === 'prompt' ? 600 : 350;
    timerRef.current = setTimeout(() => {
      setVisibleLines(prev => [...prev, scene.lines[lineIndex]]);
      setLineIndex(i => i + 1);
    }, delay);
    return () => clearTimeout(timerRef.current);
  }, [lineIndex, scene]);

  // Auto-cycle scenes
  useEffect(() => {
    if (lineIndex < scene.lines.length) return;
    const timer = setTimeout(() => {
      setSceneIndex(i => (i + 1) % GAME_SCENES.length);
    }, 4000);
    return () => clearTimeout(timer);
  }, [lineIndex, scene.lines.length]);

  // Auto-scroll terminal
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [visibleLines]);

  return (
    <section
      data-testid="game-preview-section"
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
            <span style={{ color: 'var(--aeth-gold)', fontSize: '1.1rem' }}>⚡</span>
          </div>
          <h2
            style={{
              fontFamily: "'Cinzel', serif",
              fontSize: '2rem',
              fontWeight: 700,
              color: 'var(--aeth-parchment)',
              letterSpacing: '0.04em',
              marginBottom: '0.5rem',
            }}
          >
            Venture into the Realm
          </h2>
          <p style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
            A glimpse of life in Aethoria — choose your path and forge your story
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          {/* Left: path tabs + description */}
          <motion.div
            initial={{ opacity: 0, x: -16 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
          >
            {/* Path selector tabs */}
            <div className="flex gap-2 mb-6">
              {GAME_SCENES.map((s, i) => (
                <button
                  key={s.path}
                  onClick={() => setSceneIndex(i)}
                  className="flex-1 py-2 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1"
                  style={{
                    fontFamily: "'Cinzel', serif",
                    backgroundColor: sceneIndex === i ? `${s.pathColor}18` : 'var(--aeth-stone-2)',
                    border: `1px solid ${sceneIndex === i ? s.pathColor : 'var(--aeth-iron)'}`,
                    color: sceneIndex === i ? s.pathColor : 'var(--aeth-parchment-dim)',
                    transition: 'all 0.2s ease',
                  }}
                >
                  <span>{s.pathIcon}</span>
                  <span className="hidden sm:inline">{s.path.charAt(0).toUpperCase() + s.path.slice(1)}</span>
                </button>
              ))}
            </div>

            {/* Flavor text */}
            <AnimatePresence mode="wait">
              <motion.div
                key={sceneIndex}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.25 }}
                className="aeth-card p-6"
              >
                <div className="flex items-center gap-3 mb-4">
                  <span style={{ fontSize: '2rem' }}>{scene.pathIcon}</span>
                  <div>
                    <h3 style={{ fontFamily: "'Cinzel', serif", color: scene.pathColor, fontSize: '1.1rem', fontWeight: 700 }}>
                      Life of {scene.path.charAt(0).toUpperCase() + scene.path.slice(1)}
                    </h3>
                    <p style={{ fontFamily: "'IBM Plex Sans', sans-serif", color: 'var(--aeth-iron)', fontSize: '0.78rem' }}>
                      Watch how an adventurer lives in Aethoria
                    </p>
                  </div>
                </div>
                <div className="flex flex-col gap-2">
                  {[{ label: 'Prompt', color: '#D6A24D', example: '> Your action' }, { label: 'Result', color: '#A8936D', example: 'Narrative outcome...' }, { label: 'Stat', color: '#64B5F6', example: '▸ Stat changed' }, { label: 'Reward', color: '#81C784', example: '★ Item or gold obtained' }].map(item => (
                    <div key={item.label} className="flex items-center gap-3">
                      <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }} />
                      <span style={{ fontFamily: "'Azeret Mono', monospace", fontSize: '0.72rem', color: item.color }}>{item.label}</span>
                      <span style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '0.72rem', color: 'var(--aeth-iron)' }}>{item.example}</span>
                    </div>
                  ))}
                </div>
              </motion.div>
            </AnimatePresence>
          </motion.div>

          {/* Right: Terminal */}
          <motion.div
            initial={{ opacity: 0, x: 16 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
          >
            {/* Terminal window */}
            <div
              className="rounded-xl overflow-hidden"
              style={{
                border: `1px solid ${scene.pathColor}44`,
                boxShadow: `0 0 40px ${scene.pathColor}18, 0 0 0 1px rgba(255,255,255,0.04)`,
              }}
            >
              {/* Terminal title bar */}
              <div
                className="flex items-center gap-2 px-4 py-2.5"
                style={{ backgroundColor: 'var(--aeth-stone-0)', borderBottom: `1px solid ${scene.pathColor}33` }}
              >
                <div className="flex gap-1.5">
                  {['#ff5f57', '#ffbd2e', '#28c840'].map((c, i) => (
                    <div key={i} className="w-3 h-3 rounded-full" style={{ backgroundColor: c }} />
                  ))}
                </div>
                <span style={{ fontFamily: "'Azeret Mono', monospace", fontSize: '0.72rem', color: 'var(--aeth-iron)', marginLeft: 8 }}>
                  aethoria — realm_terminal
                </span>
                <div className="ml-auto flex items-center gap-1">
                  <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: '#28c840', boxShadow: '0 0 6px #28c840' }} />
                  <span style={{ fontFamily: "'Azeret Mono', monospace", fontSize: '0.65rem', color: '#28c840' }}>LIVE</span>
                </div>
              </div>
              {/* Terminal body */}
              <div
                ref={terminalRef}
                className="p-4 overflow-y-auto"
                style={{
                  backgroundColor: 'rgba(7,6,6,0.95)',
                  minHeight: 300,
                  maxHeight: 340,
                  fontFamily: "'Azeret Mono', monospace",
                  fontSize: '0.78rem',
                  lineHeight: 1.7,
                }}
              >
                <AnimatePresence>
                  {visibleLines.map((line, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -4 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.15 }}
                      style={{ color: lineColors[line.type] || '#A8936D' }}
                    >
                      {(linePrefix[line.type] || '') + line.text}
                    </motion.div>
                  ))}
                </AnimatePresence>
                {/* Blinking cursor */}
                {lineIndex < scene.lines.length && (
                  <span style={{ color: scene.pathColor, animation: 'cursor-blink 1s infinite' }}>█</span>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
      <style>{`
        @keyframes cursor-blink {
          0%, 49% { opacity: 1; }
          50%, 100% { opacity: 0; }
        }
      `}</style>
    </section>
  );
};

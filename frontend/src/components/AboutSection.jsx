import { motion } from 'framer-motion';
import { Shield, Sword, Crown, Scroll, Users, Star } from 'lucide-react';

const oaths = [
  {
    icon: <Sword size={20} />,
    title: 'The Oath of Steel',
    desc: 'Train your body, master every weapon from the humble shortsword to the legendary dragon-forged blade, and rise as the most feared warrior in Aethoria.',
    color: '#C0392B',
  },
  {
    icon: <Shield size={20} />,
    title: 'The Oath of Shadow',
    desc: 'Move unseen through the Realm. Dark deeds, cunning guild conspiracies, and forbidden crafts await the bold adventurer who walks in shadow.',
    color: '#8E44AD',
  },
  {
    icon: <Crown size={20} />,
    title: 'The Oath of Gold',
    desc: 'Amass wealth, found merchant houses, and bend the Realm\'s economy to your noble will. True power lies not in steel — but in gold.',
    color: '#D4AC0D',
  },
];

// Stats will be passed as props from parent to show real data
const statsConfig = [
  { key: 'features', icon: <Scroll size={16} />, label: 'Game Features' },
  { key: 'kingdoms', icon: <Crown size={16} />, label: 'Kingdoms to Explore' },
];

export const AboutSection = ({ stats }) => {
  // Build display stats from real data
  const displayStats = [
    { icon: <Scroll size={16} />, value: stats?.features || '42', label: 'Game Features' },
    { icon: <Crown size={16} />, value: stats?.kingdoms || '11', label: 'Kingdoms' },
  ];

  return (
    <section
      id="about"
      data-testid="about-section"
      className="aeth-section"
      style={{ backgroundColor: 'var(--aeth-stone-1)' }}
    >
      <div className="max-w-6xl mx-auto">
        {/* Divider */}
        <div className="aeth-divider mb-12">
          <span style={{ color: 'var(--aeth-gold)', fontSize: '1.1rem' }}>⚜</span>
        </div>

        {/* Main grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-14 items-start">
          {/* Left: Text */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2
              className="font-cinzel rune-underline mb-6"
              style={{
                fontFamily: "'Cinzel', serif",
                fontSize: '2rem',
                fontWeight: 700,
                color: 'var(--aeth-parchment)',
                letterSpacing: '0.04em',
              }}
            >
              About the Realm
            </h2>
            <p
              className="text-base mb-4 leading-relaxed"
              style={{ color: 'var(--aeth-parchment-dim)', maxWidth: '60ch', fontFamily: "'IBM Plex Sans', sans-serif" }}
            >
              Realm of Aethoria is a text-based online RPG set in a dark, gritty medieval world where
              only the sharpest adventurers survive. In Aethoria you can be anyone and do anything.
              Build your character to legendary strength and play it your way.
            </p>
            <p
              className="text-base mb-6 leading-relaxed"
              style={{ color: 'var(--aeth-parchment-dim)', maxWidth: '60ch', fontFamily: "'IBM Plex Sans', sans-serif" }}
            >
              Aethoria is a massively multiplayer realm with tens of thousands of active adventurers around
              the world. Join them, fight them, befriend them, marry them, gamble against them, trade with
              them, war alongside them. Whatever you do — do it now!
            </p>
            <p
              className="text-sm leading-relaxed mb-8"
              style={{
                color: 'var(--aeth-iron)',
                fontStyle: 'italic',
                fontFamily: "'IBM Plex Sans', sans-serif",
                borderLeft: '2px solid var(--aeth-iron)',
                paddingLeft: '1rem',
              }}
            >
              &ldquo;New adventurers start weak and poor. Beware — the dark lands of Aethoria show no mercy.
              Opportunists will not think twice to rob or defeat you for a few coins.
              The rules are simple: Build a legend. Rise to the top. Choose any path.&rdquo;
            </p>

            {/* Mini stats row */}
            <div className="grid grid-cols-2 gap-4">
              {displayStats.map((s) => (
                <div
                  key={s.label}
                  className="aeth-card px-4 py-3 flex items-center gap-3"
                >
                  <span style={{ color: 'var(--aeth-gold)' }}>{s.icon}</span>
                  <div>
                    <div
                      style={{
                        fontFamily: "'Cinzel', serif",
                        fontSize: '1.1rem',
                        fontWeight: 700,
                        color: 'var(--aeth-parchment)',
                      }}
                    >
                      {s.value}
                    </div>
                    <div
                      style={{
                        fontSize: '0.72rem',
                        color: 'var(--aeth-iron)',
                        fontFamily: "'IBM Plex Sans', sans-serif",
                      }}
                    >
                      {s.label}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Right: Oaths */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="flex flex-col gap-4"
          >
            <h3
              className="text-xs uppercase tracking-widest mb-2"
              style={{ color: 'var(--aeth-gold)', fontFamily: "'Cinzel', serif" }}
            >
              Three Paths. One Destiny.
            </h3>
            {oaths.map((oath, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.2 + i * 0.1 }}
                className="aeth-card p-5 flex gap-4 items-start"
                style={{ transition: 'border-color 0.2s ease, box-shadow 0.2s ease' }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.boxShadow = `0 0 20px ${oath.color}22`;
                  e.currentTarget.style.borderColor = `${oath.color}55`;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.boxShadow = '';
                  e.currentTarget.style.borderColor = '';
                }}
              >
                <div
                  className="icon-coin mt-1"
                  style={{ color: oath.color, borderColor: `${oath.color}66` }}
                >
                  {oath.icon}
                </div>
                <div>
                  <h3
                    className="font-semibold mb-1"
                    style={{
                      fontFamily: "'Cinzel', serif",
                      color: oath.color,
                      fontSize: '0.9rem',
                      letterSpacing: '0.03em',
                    }}
                  >
                    {oath.title}
                  </h3>
                  <p
                    className="text-sm leading-relaxed"
                    style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}
                  >
                    {oath.desc}
                  </p>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
};

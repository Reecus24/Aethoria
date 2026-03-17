import { motion } from 'framer-motion';
import { Shield, Sword, Crown } from 'lucide-react';

const oaths = [
  {
    icon: <Sword size={20} />,
    title: 'The Oath of Steel',
    desc: 'Train your body, master your weapons, and rise as the most feared warrior in all of Aethoria.',
  },
  {
    icon: <Shield size={20} />,
    title: 'The Oath of Shadow',
    desc: 'Move unseen through the Realm. Dark deeds, cunning trades, and guild conspiracies await the bold.',
  },
  {
    icon: <Crown size={20} />,
    title: 'The Oath of Gold',
    desc: 'Amass wealth, found merchant houses, and bend the Realm\'s economy to your noble will.',
  },
];

export const AboutSection = () => {
  return (
    <section
      data-testid="about-section"
      className="aeth-section"
      style={{ backgroundColor: 'var(--aeth-stone-1)' }}
    >
      <div className="max-w-6xl mx-auto">
        {/* Divider */}
        <div className="aeth-divider mb-12">
          <span style={{ color: 'var(--aeth-gold)', fontSize: '1.2rem' }}>⚜</span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
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
              Realm of Aethoria is a text-based online RPG set in a dark, gritty medieval world
              where only the sharpest adventurers survive. In Aethoria you can be anyone and do anything.
              Build your character to legendary strength and play it your way.
            </p>
            <p
              className="text-base mb-6 leading-relaxed"
              style={{ color: 'var(--aeth-parchment-dim)', maxWidth: '60ch', fontFamily: "'IBM Plex Sans', sans-serif" }}
            >
              Aethoria is a massively multiplayer realm with thousands of active adventurers around
              the world. Join them, fight them, befriend them, marry them, gamble against them,
              trade with them, war alongside them. Whatever you do — do it now!
            </p>
            <p
              className="text-sm"
              style={{ color: 'var(--aeth-iron)', fontStyle: 'italic', fontFamily: "'IBM Plex Sans', sans-serif" }}
            >
              New players start weak and poor. Beware — the dark lands of Aethoria show no mercy.
              Opportunists will not think twice to rob or defeat you. The rules are simple: Build a new legend.
              Rise to the top. Choose any path to get there.
            </p>
          </motion.div>

          {/* Right: Oaths */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="flex flex-col gap-4"
          >
            {oaths.map((oath, i) => (
              <div
                key={i}
                className="aeth-card p-5 flex gap-4 items-start"
                style={{ transition: 'border-color 0.2s ease, box-shadow 0.2s ease' }}
              >
                <div
                  className="icon-coin mt-1"
                  style={{ color: 'var(--aeth-gold)' }}
                >
                  {oath.icon}
                </div>
                <div>
                  <h3
                    className="font-semibold mb-1"
                    style={{
                      fontFamily: "'Cinzel', serif",
                      color: 'var(--aeth-parchment)',
                      fontSize: '0.95rem',
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
              </div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
};

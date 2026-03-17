import { useState } from 'react';
import { motion } from 'framer-motion';
import { MapPin, X } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';

const dangerColors = {
  'Low': '#81C784',
  'Medium': '#FFD54F',
  'High': '#FFB74D',
  'Very High': '#FF8A65',
  'Extreme': '#FF5252',
};

const typeColors = {
  'Capital': '#D6A24D',
  'Military': '#C0392B',
  'Underworld': '#8E44AD',
  'Commerce': '#27AE60',
  'Arcane': '#3498DB',
  'Noble': '#F39C12',
  'Wilds': '#E67E22',
  'Maritime': '#16A085',
  'Forest': '#2ECC71',
  'Frozen': '#85C1E9',
  'Desert': '#E59866',
};

const KingdomCard = ({ kingdom, onClick }) => (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    onClick={() => onClick(kingdom)}
    data-testid="kingdom-card"
    className="relative overflow-hidden rounded-xl cursor-pointer group"
    style={{
      border: '1px solid var(--aeth-iron)',
      aspectRatio: '4/3',
      transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.borderColor = typeColors[kingdom.type] || 'var(--aeth-gold)';
      e.currentTarget.style.boxShadow = `0 0 20px ${typeColors[kingdom.type] || 'var(--aeth-gold)'}33`;
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.borderColor = 'var(--aeth-iron)';
      e.currentTarget.style.boxShadow = 'none';
    }}
  >
    {/* Background image */}
    <img
      src={kingdom.image}
      alt={kingdom.name}
      className="w-full h-full object-cover"
      style={{ opacity: 0.55, transition: 'opacity 0.3s ease' }}
      onMouseEnter={(e) => { e.currentTarget.style.opacity = 0.75; }}
      onMouseLeave={(e) => { e.currentTarget.style.opacity = 0.55; }}
    />
    {/* Overlay */}
    <div
      className="absolute inset-0 group-hover:opacity-80"
      style={{
        background: `linear-gradient(to top, ${typeColors[kingdom.type] || 'var(--aeth-stone-0)'}88 0%, rgba(7,6,6,0.4) 50%, transparent 100%)`,
        transition: 'opacity 0.3s ease',
      }}
    />
    {/* Type badge */}
    <div
      className="absolute top-2 right-2 text-xs px-2 py-0.5 rounded-full"
      style={{
        backgroundColor: `${typeColors[kingdom.type] || '#888'}25`,
        border: `1px solid ${typeColors[kingdom.type] || '#888'}66`,
        color: typeColors[kingdom.type] || '#888',
        fontFamily: "'Azeret Mono', monospace",
        backdropFilter: 'blur(4px)',
        fontSize: '0.62rem',
        letterSpacing: '0.06em',
      }}
    >
      {kingdom.type}
    </div>
    {/* Bottom info */}
    <div className="absolute bottom-0 left-0 right-0 p-3">
      <h3
        style={{
          fontFamily: "'Cinzel', serif",
          color: '#fff',
          fontSize: '0.9rem',
          fontWeight: 700,
          textShadow: '0 1px 6px rgba(0,0,0,0.8)',
          marginBottom: '0.2rem',
        }}
      >
        {kingdom.name}
      </h3>
      <div className="flex items-center gap-2">
        <MapPin size={10} style={{ color: dangerColors[kingdom.danger] || '#aaa' }} />
        <span
          style={{
            fontFamily: "'Azeret Mono', monospace",
            fontSize: '0.62rem',
            color: dangerColors[kingdom.danger] || '#aaa',
          }}
        >
          {kingdom.danger} Danger
        </span>
      </div>
    </div>
    {/* Hover explore icon */}
    <div
      className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100"
      style={{ transition: 'opacity 0.2s ease' }}
    >
      <div
        className="px-3 py-1 rounded-full text-xs font-semibold"
        style={{
          backgroundColor: 'rgba(214,162,77,0.9)',
          color: 'var(--aeth-stone-0)',
          fontFamily: "'Cinzel', serif",
          backdropFilter: 'blur(4px)',
        }}
      >
        Explore →
      </div>
    </div>
  </motion.div>
);

const KingdomModal = ({ kingdom, onClose }) => (
  <Dialog open={!!kingdom} onOpenChange={onClose}>
    <DialogContent
      className="max-w-lg"
      style={{ backgroundColor: 'var(--aeth-stone-2)', border: '1px solid var(--aeth-iron)' }}
    >
      {kingdom && (
        <>
          <DialogHeader>
            {/* Kingdom image header */}
            <div className="relative h-40 -mx-6 -mt-6 mb-4 rounded-t-xl overflow-hidden">
              <img src={kingdom.image} alt={kingdom.name} className="w-full h-full object-cover" style={{ opacity: 0.55 }} />
              <div className="absolute inset-0" style={{ background: `linear-gradient(to top, var(--aeth-stone-2) 5%, transparent 60%)` }} />
              <div
                className="absolute top-3 left-3 text-xs px-2 py-0.5 rounded-full"
                style={{
                  backgroundColor: `${typeColors[kingdom.type] || '#888'}25`,
                  border: `1px solid ${typeColors[kingdom.type] || '#888'}55`,
                  color: typeColors[kingdom.type] || '#888',
                  fontFamily: "'Azeret Mono', monospace",
                  backdropFilter: 'blur(4px)',
                  fontSize: '0.65rem',
                }}
              >
                {kingdom.type} Kingdom
              </div>
            </div>
            <DialogTitle style={{ fontFamily: "'Cinzel', serif", color: 'var(--aeth-parchment)', fontSize: '1.3rem', letterSpacing: '0.05em' }}>
              {kingdom.name}
            </DialogTitle>
            <DialogDescription style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
              {kingdom.desc}
            </DialogDescription>
          </DialogHeader>

          <div className="grid grid-cols-2 gap-3 mt-4">
            {[
              { label: 'Kingdom Type', value: kingdom.type, color: typeColors[kingdom.type] },
              { label: 'Danger Level', value: kingdom.danger, color: dangerColors[kingdom.danger] },
              { label: 'Travel Cost', value: '250 Gold', color: 'var(--aeth-gold)' },
              { label: 'Min. Level', value: kingdom.danger === 'Low' ? '1' : kingdom.danger === 'Medium' ? '5' : kingdom.danger === 'High' ? '10' : '15', color: 'var(--aeth-parchment)' },
            ].map(item => (
              <div key={item.label} className="aeth-card p-3">
                <p style={{ fontFamily: "'Cinzel', serif", fontSize: '0.65rem', color: 'var(--aeth-iron)', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '0.25rem' }}>{item.label}</p>
                <p style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontWeight: 600, color: item.color, fontSize: '0.9rem' }}>{item.value}</p>
              </div>
            ))}
          </div>

          <div className="mt-4 p-4 rounded-lg" style={{ backgroundColor: 'rgba(214,162,77,0.06)', border: '1px solid rgba(214,162,77,0.2)' }}>
            <p style={{ fontFamily: "'IBM Plex Sans', sans-serif", color: 'var(--aeth-iron)', fontSize: '0.8rem', fontStyle: 'italic', lineHeight: 1.6 }}>
              &ldquo;Travel to {kingdom.name} unlocks unique quests, rare items, and new factions available only in this kingdom. Brave the journey — the rewards are legendary.&rdquo;
            </p>
          </div>
        </>
      )}
    </DialogContent>
  </Dialog>
);

export const KingdomsSection = ({ kingdoms = [] }) => {
  const [selected, setSelected] = useState(null);

  if (kingdoms.length === 0) return null;

  return (
    <section
      id="kingdoms"
      data-testid="kingdoms-section"
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
            <span style={{ color: 'var(--aeth-gold)', fontSize: '1.1rem' }}>🗺️</span>
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
            The 11 Kingdoms
          </h2>
          <p style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
            Travel to distant lands — each with unique factions, quests, and dangers
          </p>
        </motion.div>

        {/* Kingdoms grid */}
        <div
          data-testid="kingdoms-grid"
          className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4"
        >
          {kingdoms.map((k, i) => (
            <KingdomCard key={k.id || i} kingdom={k} onClick={setSelected} />
          ))}
        </div>

        <p
          className="text-center text-xs mt-6"
          style={{ color: 'var(--aeth-iron)', fontFamily: "'Azeret Mono', monospace" }}
        >
          Click any kingdom to view travel details &middot; Travel unlocks at Level 1
        </p>
      </div>

      <KingdomModal kingdom={selected} onClose={() => setSelected(null)} />
    </section>
  );
};

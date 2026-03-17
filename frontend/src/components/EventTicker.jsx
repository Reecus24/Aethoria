import { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';

const eventTypeColors = {
  dungeon: '#E57373',
  combat: '#FFB74D',
  crime: '#CE93D8',
  guild: '#64B5F6',
  quest: '#81C784',
  market: '#FFD54F',
  bounty: '#EF9A9A',
  default: '#A0A0A0',
};

const eventTypeIcons = {
  dungeon: '🔐',
  combat: '⚔',
  crime: '🗡',
  guild: '⚜',
  quest: '📜',
  market: '💰',
  bounty: '🎯',
  default: '✦',
};

const eventTypeLabels = {
  dungeon: 'Dungeon',
  combat: 'Combat',
  crime: 'Crime',
  guild: 'Guild',
  quest: 'Quest',
  market: 'Market',
  bounty: 'Bounty',
  default: 'Event',
};

export const EventTicker = ({ events = [] }) => {
  const [displayEvents, setDisplayEvents] = useState([]);
  const [currentFlash, setCurrentFlash] = useState(null);
  const flashTimerRef = useRef(null);

  useEffect(() => {
    if (events.length > 0) {
      setDisplayEvents([...events, ...events, ...events]);
    }
  }, [events]);

  // Flash a random event in the "live" indicator every ~6 seconds
  useEffect(() => {
    if (events.length === 0) return;
    const pick = () => {
      const e = events[Math.floor(Math.random() * events.length)];
      setCurrentFlash(e);
    };
    pick();
    flashTimerRef.current = setInterval(pick, 6000);
    return () => clearInterval(flashTimerRef.current);
  }, [events]);

  if (displayEvents.length === 0) return null;

  return (
    <div
      data-testid="event-ticker-strip"
      className="border-b overflow-hidden"
      style={{
        backgroundColor: 'var(--aeth-stone-1)',
        borderColor: 'var(--aeth-iron)',
        position: 'relative',
        zIndex: 50,
      }}
    >
      <div className="flex items-stretch h-10">
        {/* Static label */}
        <div
          className="flex-shrink-0 px-3 text-xs font-semibold tracking-widest uppercase flex items-center gap-2"
          style={{
            backgroundColor: 'var(--aeth-iron-2)',
            borderRight: '1px solid var(--aeth-iron)',
            color: 'var(--aeth-gold)',
            fontFamily: "'Cinzel', serif",
            minWidth: 130,
          }}
        >
          {/* Live dot */}
          <span
            className="w-1.5 h-1.5 rounded-full"
            style={{
              backgroundColor: '#4CAF50',
              boxShadow: '0 0 6px #4CAF50',
              display: 'inline-block',
              animation: 'pulse-dot 2s infinite',
            }}
          />
          Realm Events
        </div>

        {/* Scrolling track */}
        <div className="overflow-hidden flex-1 marquee-container">
          <div className="marquee-track" data-testid="event-ticker-track">
            {displayEvents.map((evt, i) => (
              <span
                key={i}
                data-testid="event-ticker-item"
                className="flex items-center gap-2 px-4 whitespace-nowrap text-xs"
                style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}
              >
                {/* Category badge */}
                <span
                  className="text-xs px-1.5 py-0.5 rounded"
                  style={{
                    backgroundColor: `${eventTypeColors[evt.type] || eventTypeColors.default}18`,
                    color: eventTypeColors[evt.type] || eventTypeColors.default,
                    border: `1px solid ${eventTypeColors[evt.type] || eventTypeColors.default}40`,
                    fontFamily: "'Azeret Mono', monospace",
                    fontSize: '0.62rem',
                    letterSpacing: '0.06em',
                  }}
                >
                  {eventTypeIcons[evt.type] || eventTypeIcons.default} {eventTypeLabels[evt.type] || 'Event'}
                </span>
                <span style={{ color: 'var(--aeth-parchment-dim)' }}>{evt.event}</span>
                <span
                  className="mx-2"
                  style={{ color: 'var(--aeth-iron)', fontSize: '0.55rem' }}
                >
                  ✦
                </span>
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Pulse dot CSS */}
      <style>{`
        @keyframes pulse-dot {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
      `}</style>
    </div>
  );
};

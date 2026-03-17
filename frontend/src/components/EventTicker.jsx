import { useEffect, useState } from 'react';

const eventTypeColors = {
  dungeon: 'text-red-400',
  combat: 'text-orange-400',
  crime: 'text-purple-400',
  guild: 'text-blue-400',
  quest: 'text-green-400',
  market: 'text-yellow-400',
  bounty: 'text-red-300',
  default: 'text-gray-300',
};

const eventTypeIcons = {
  dungeon: '🔐',
  combat: '⚔️',
  crime: '🗡️',
  guild: '⚜️',
  quest: '📜',
  market: '💰',
  bounty: '🎯',
  default: '✦',
};

export const EventTicker = ({ events = [] }) => {
  const [displayEvents, setDisplayEvents] = useState([]);

  useEffect(() => {
    if (events.length > 0) {
      // Duplicate for seamless loop
      setDisplayEvents([...events, ...events]);
    }
  }, [events]);

  if (displayEvents.length === 0) return null;

  return (
    <div
      data-testid="event-ticker-strip"
      className="sticky top-0 z-50 border-b overflow-hidden"
      style={{ backgroundColor: 'var(--aeth-stone-1)', borderColor: 'var(--aeth-iron)' }}
    >
      <div className="flex items-center h-10">
        {/* Label */}
        <div
          className="flex-shrink-0 px-3 py-1 text-xs font-semibold tracking-widest uppercase border-r flex items-center gap-2"
          style={{
            backgroundColor: 'var(--aeth-iron-2)',
            borderColor: 'var(--aeth-iron)',
            color: 'var(--aeth-gold)',
            fontFamily: "'Cinzel', serif",
            minWidth: 140,
          }}
        >
          <span>&#9876;</span> Realm Events
        </div>

        {/* Scrolling track */}
        <div className="overflow-hidden flex-1 marquee-container">
          <div className="marquee-track" data-testid="event-ticker-track">
            {displayEvents.map((evt, i) => (
              <span
                key={i}
                data-testid="event-ticker-item"
                className="flex items-center gap-2 px-5 whitespace-nowrap text-sm"
                style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}
              >
                <span
                  className={eventTypeColors[evt.type] || eventTypeColors.default}
                  style={{ fontSize: '0.7rem' }}
                >
                  {eventTypeIcons[evt.type] || eventTypeIcons.default}
                </span>
                <span style={{ color: 'var(--aeth-parchment-dim)' }}>{evt.event}</span>
                <span
                  className="mx-3"
                  style={{ color: 'var(--aeth-iron)', fontSize: '0.65rem' }}
                >
                  ✦
                </span>
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

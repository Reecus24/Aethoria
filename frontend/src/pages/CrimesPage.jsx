import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Skull, Zap, Trophy, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const CrimesPage = () => {
  const { gameState, refreshGameState } = useOutletContext();
  const [crimes, setCrimes] = useState([]);
  const [committing, setCommitting] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCrimes();
  }, []);

  const fetchCrimes = async () => {
    try {
      const res = await axios.get(`${API}/game/crimes`);
      setCrimes(res.data);
      setLoading(false);
    } catch (err) {
      toast.error('Fehler beim Laden der Verbrechen');
      setLoading(false);
    }
  };

  const commitCrime = async (crimeId) => {
    setCommitting(true);
    try {
      const res = await axios.post(`${API}/game/crimes/commit`, { crime_id: crimeId });
      if (res.data.victory) {
        toast.success(res.data.message, { icon: '✅', duration: 4000 });
        if (res.data.level_up) {
          toast.success(`🎉 LEVEL UP! Jetzt Level ${res.data.new_level}!`, { duration: 5000 });
        }
      } else {
        toast.error(res.data.message, { icon: '⚠️', duration: 4000 });
      }
      refreshGameState();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Verbrechen');
    } finally {
      setCommitting(false);
    }
  };

  if (loading) {
    return <div className="text-center py-20">Loading crimes...</div>;
  }

  const categoryColors = {
    petty: '#9E9E9E',
    theft: '#CE93D8',
    burglary: '#FFB74D',
    robbery: '#FFB74D',
    extortion: '#E57373',
    heist: '#E57373',
    major: '#E57373',
    assassination: '#8E1D2C',
    legendary: '#D6A24D'
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2" style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}>
          Dark Deeds
        </h1>
        <p style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
          Verdiene Gold durch Verbrechen • Höheres Risiko = Höhere Belohnung
        </p>
      </div>

      {gameState?.status?.in_dungeon && (
        <div className="aeth-card p-6 mb-6" style={{ border: '2px solid #E57373' }}>
          <div className="flex items-center gap-3">
            <AlertTriangle size={24} style={{ color: '#E57373' }} />
            <div>
              <p className="font-semibold" style={{ color: '#E57373' }}>Du sitzt im Kerker!</p>
              <p className="text-sm" style={{ color: 'var(--aeth-parchment-dim)' }}>
                Noch {gameState.timers.dungeon.minutes_remaining} Minuten bis zur Freilassung
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        {crimes.map((crime, i) => (
          <motion.div
            key={crime.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.03 }}
            className="aeth-card p-5"
            data-testid={`crime-${crime.id}`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="text-base font-semibold" style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}>
                    {crime.name}
                  </h3>
                  <span
                    className="text-xs px-2 py-0.5 rounded-full"
                    style={{
                      backgroundColor: `${categoryColors[crime.category] || '#666'}20`,
                      color: categoryColors[crime.category] || '#666',
                      border: `1px solid ${categoryColors[crime.category] || '#666'}40`
                    }}
                  >
                    Lvl {crime.min_level}+
                  </span>
                </div>
                <p className="text-xs mb-3" style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
                  {crime.description}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 mb-4 text-xs">
              <div>
                <p style={{ color: 'var(--aeth-parchment-dim)' }}>Erfolgsrate:</p>
                <p className="font-semibold" style={{ color: '#81C784' }}>{crime.adjusted_success}%</p>
              </div>
              <div>
                <p style={{ color: 'var(--aeth-parchment-dim)' }}>Belohnung:</p>
                <p className="font-semibold" style={{ color: 'var(--aeth-gold)' }}>
                  {crime.rewards.gold[0]}-{crime.rewards.gold[1]} Gold
                </p>
              </div>
              <div>
                <p style={{ color: 'var(--aeth-parchment-dim)' }}>Energie:</p>
                <p className="font-semibold">{crime.energy_cost}</p>
              </div>
              <div>
                <p style={{ color: 'var(--aeth-parchment-dim)' }}>Strafe:</p>
                <p className="font-semibold" style={{ color: '#E57373' }}>
                  {crime.failure.jail_minutes} Min Kerker
                </p>
              </div>
            </div>

            <button
              onClick={() => commitCrime(crime.id)}
              disabled={committing || gameState.resources.energy < crime.energy_cost || !gameState.status.can_act}
              className="btn-gold w-full py-2.5 rounded-lg text-sm font-semibold disabled:opacity-40 disabled:cursor-not-allowed"
              data-testid={`commit-crime-${crime.id}`}
            >
              {committing ? 'Ausführen...' : `Begehen (${crime.energy_cost} Energie)`}
            </button>
          </motion.div>
        ))}
      </div>
    </div>
  );
};
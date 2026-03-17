import { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import axios from '../utils/axios';
import { motion } from 'framer-motion';
import { Dumbbell, Clock } from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const STATS = [
  { id: 'strength', label: 'Stärke', icon: '💪', color: '#E57373', desc: 'Erhöht Kampfschaden' },
  { id: 'dexterity', label: 'Geschicklichkeit', icon: '🎯', color: '#FFB74D', desc: 'Erhöht Verbrechen-Erfolgsrate' },
  { id: 'speed', label: 'Geschwindigkeit', icon: '⚡', color: '#64B5F6', desc: 'Erhöht Ausweichen & Initiative' },
  { id: 'defense', label: 'Verteidigung', icon: '🛡️', color: '#81C784', desc: 'Reduziert erhaltenen Schaden' },
];

export default function TrainingPage() {
  const { gameState, refreshGameState } = useOutletContext();
  const [training, setTraining] = useState(false);

  const startTraining = async (stat) => {
    if (gameState.resources.energy < 100) {
      toast.error('Nicht genug Energie (benötigt: 100)', { icon: '⚡' });
      return;
    }

    setTraining(true);
    try {
      const res = await axios.post(`${API}/game/training/start`, { stat });
      toast.success(res.data.message, { icon: '💪', duration: 3000 });
      refreshGameState();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Starten des Trainings');
    } finally {
      setTraining(false);
    }
  };

  const claimTraining = async () => {
    try {
      const res = await axios.post(`${API}/game/training/claim`);
      if (res.data.level_up) {
        toast.success(`🎉 LEVEL UP! Du bist jetzt Level ${res.data.new_level}!`, { duration: 5000 });
      } else {
        toast.success(res.data.message, { icon: '✅' });
      }
      refreshGameState();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Abschließen');
    }
  };

  const activeTraining = gameState?.timers?.training;

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h1
          className="text-3xl font-bold mb-2"
          style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}
        >
          Training Grounds
        </h1>
        <p style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
          Trainiere deine Stats, um mächtiger zu werden • Kosten: 100 Energie • Dauer: 12 Stunden
        </p>
      </div>

      {/* Active Training */}
      {activeTraining && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="aeth-card p-6 mb-6"
          style={{ border: '2px solid var(--aeth-gold)' }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm" style={{ color: 'var(--aeth-parchment-dim)' }}>Training läuft:</p>
              <p className="text-xl font-bold" style={{ color: 'var(--aeth-gold)', fontFamily: "'Cinzel', serif" }}>
                {activeTraining.stat.toUpperCase()}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm" style={{ color: 'var(--aeth-parchment-dim)' }}>Verbleibend:</p>
              <p className="text-xl font-bold" style={{ color: 'var(--aeth-gold)', fontFamily: "'Azeret Mono', monospace" }}>
                {Math.floor(activeTraining.seconds_remaining / 60)}:{String(activeTraining.seconds_remaining % 60).padStart(2, '0')}
              </p>
            </div>
          </div>
          {activeTraining.seconds_remaining <= 0 && (
            <button
              onClick={claimTraining}
              className="btn-gold w-full mt-4 py-3 rounded-lg font-semibold"
              data-testid="claim-training-btn"
            >
              Training abschließen
            </button>
          )}
        </motion.div>
      )}

      {/* Training Options */}
      <div className="grid md:grid-cols-2 gap-4">
        {STATS.map((stat, i) => (
          <motion.div
            key={stat.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="aeth-card p-6"
            data-testid={`training-${stat.id}`}
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span style={{ fontSize: '1.5rem' }}>{stat.icon}</span>
                  <h3 className="text-lg font-semibold" style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}>
                    {stat.label}
                  </h3>
                </div>
                <p className="text-xs" style={{ color: 'var(--aeth-parchment-dim)' }}>
                  {stat.desc}
                </p>
              </div>
              <div
                className="px-3 py-1 rounded-full text-sm font-bold"
                style={{ backgroundColor: `${stat.color}20`, color: stat.color }}
              >
                {gameState.stats[stat.id]}
              </div>
            </div>

            <button
              onClick={() => startTraining(stat.id)}
              disabled={training || activeTraining || gameState.resources.energy < 100 || !gameState.status.can_act}
              className="btn-gold w-full py-2.5 rounded-lg text-sm font-semibold disabled:opacity-40 disabled:cursor-not-allowed"
              data-testid={`train-${stat.id}-btn`}
            >
              {activeTraining ? 'Training läuft...' : 'Trainieren (100 Energie, 12 Std)'}
            </button>
          </motion.div>
        ))}
      </div>
    </div>
  );
};
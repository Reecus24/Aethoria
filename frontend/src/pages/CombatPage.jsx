import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import axios from '../utils/axios';
import { motion } from 'framer-motion';
import { Swords, Target, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function CombatPage() {
  const { gameState, refreshGameState } = useOutletContext();
  const [targets, setTargets] = useState([]);
  const [attacking, setAttacking] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTargets();
  }, []);

  const fetchTargets = async () => {
    try {
      const res = await axios.get(`${API}/game/combat/targets`);
      setTargets(res.data);
      setLoading(false);
    } catch (err) {
      toast.error('Fehler beim Laden der Ziele');
      setLoading(false);
    }
  };

  const attackPlayer = async (username, action = 'attack') => {
    if ((gameState?.resources?.energy || 0) < 15) {
      toast.error('Nicht genug Energie (benötigt: 15)');
      return;
    }

    setAttacking(true);
    try {
      const res = await axios.post(`${API}/game/combat/attack`, { target_username: username, action });
      if (res.data.victory) {
        toast.success(res.data.message, { icon: '⚔️', duration: 4000 });
      } else {
        toast.error(res.data.message, { icon: '💀', duration: 4000 });
      }
      refreshGameState();
      fetchTargets();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Angriff');
    } finally {
      setAttacking(false);
    }
  };

  if (loading) {
    return <div className="text-center py-20">Loading targets...</div>;
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2" style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}>
          Combat Arena
        </h1>
        <p style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
          Greife andere Spieler an • Kosten: 15 Energie pro Angriff
        </p>
      </div>

      {gameState?.status?.in_hospital && (
        <div className="aeth-card p-6 mb-6" style={{ border: '2px solid #E57373' }}>
          <p className="font-semibold" style={{ color: '#E57373' }}>Du bist verletzt und im Lazarett!</p>
          <p className="text-sm" style={{ color: 'var(--aeth-parchment-dim)' }}>
            Noch {Math.floor(gameState.timers.hospital.seconds_remaining / 60)} Minuten bis zur Genesung
          </p>
        </div>
      )}

      <div className="space-y-3">
        {targets.map(target => (
          <div key={target.username} className="aeth-card p-5" data-testid={`target-${target.username}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4 flex-1">
                <div
                  className="w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold"
                  style={{
                    backgroundColor: 'var(--aeth-iron-2)',
                    border: '2px solid var(--aeth-iron)',
                    color: 'var(--aeth-gold)',
                    fontFamily: "'Cinzel', serif"
                  }}
                >
                  {target.username[0].toUpperCase()}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-base font-semibold" style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}>
                      {target.username}
                    </h3>
                    <span
                      className="text-xs px-2 py-0.5 rounded-full"
                      style={{ backgroundColor: 'rgba(214,162,77,0.15)', color: 'var(--aeth-gold)' }}
                    >
                      Lvl {target.level}
                    </span>
                  </div>
                  <p className="text-xs" style={{ color: 'var(--aeth-parchment-dim)' }}>
                    {target.path_label}
                  </p>
                </div>
                <div className="grid grid-cols-4 gap-3 text-xs text-center">
                  <div>
                    <p style={{ color: 'var(--aeth-parchment-dim)' }}>STR</p>
                    <p className="font-semibold" style={{ color: '#E57373' }}>{target.stats.strength}</p>
                  </div>
                  <div>
                    <p style={{ color: 'var(--aeth-parchment-dim)' }}>DEX</p>
                    <p className="font-semibold" style={{ color: '#FFB74D' }}>{target.stats.dexterity}</p>
                  </div>
                  <div>
                    <p style={{ color: 'var(--aeth-parchment-dim)' }}>SPD</p>
                    <p className="font-semibold" style={{ color: '#64B5F6' }}>{target.stats.speed}</p>
                  </div>
                  <div>
                    <p style={{ color: 'var(--aeth-parchment-dim)' }}>DEF</p>
                    <p className="font-semibold" style={{ color: '#81C784' }}>{target.stats.defense}</p>
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => attackPlayer(target.username, 'attack')}
                  disabled={attacking || gameState.resources.energy < 15 || !gameState.status.can_act}
                  className="btn-iron px-4 py-2 rounded-lg text-xs font-semibold disabled:opacity-40"
                  data-testid={`attack-${target.username}`}
                >
                  Angreifen
                </button>
                {gameState?.user?.path === 'shadow' && (
                  <button
                    onClick={() => attackPlayer(target.username, 'mug')}
                    disabled={attacking || gameState.resources.energy < 15 || !gameState.status.can_act}
                    className="btn-gold px-4 py-2 rounded-lg text-xs font-semibold disabled:opacity-40"
                    data-testid={`mug-${target.username}`}
                  >
                    Ausrauben
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
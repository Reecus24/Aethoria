import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import axios from '../utils/axios';
import { motion } from 'framer-motion';
import { Scroll, Clock, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function QuestsPage() {
  const { gameState, refreshGameState } = useOutletContext();
  const [quests, setQuests] = useState({ active_quest: null, available_quests: [] });
  const [loading, setLoading] = useState(true);
  const [accepting, setAccepting] = useState(false);

  useEffect(() => {
    fetchQuests();
  }, []);

  const fetchQuests = async () => {
    try {
      const res = await axios.get(`${API}/game/quests/available`);
      setQuests(res.data);
      setLoading(false);
    } catch (err) {
      toast.error('Fehler beim Laden der Quests');
      setLoading(false);
    }
  };

  const acceptQuest = async (questId) => {
    setAccepting(true);
    try {
      const res = await axios.post(`${API}/game/quests/accept`, { quest_id: questId });
      toast.success(res.data.message, { icon: '📜', duration: 3000 });
      refreshGameState();
      fetchQuests();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Akzeptieren');
    } finally {
      setAccepting(false);
    }
  };

  const completeQuest = async () => {
    try {
      const res = await axios.post(`${API}/game/quests/complete`);
      if (res.data.level_up) {
        toast.success(`🎉 LEVEL UP! Jetzt Level ${res.data.new_level}!`, { duration: 5000 });
      }
      toast.success(res.data.message, { icon: '✅', duration: 4000 });
      refreshGameState();
      fetchQuests();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Abschließen');
    }
  };

  const activeTimer = gameState?.timers?.quest;

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2" style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}>
          Quests
        </h1>
        <p style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
          Akzeptiere Missionen und verdiene Belohnungen
        </p>
      </div>

      {/* Active Quest */}
      {activeTimer && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="aeth-card p-6 mb-6"
          style={{ border: '2px solid var(--aeth-gold)' }}
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm" style={{ color: 'var(--aeth-parchment-dim)' }}>Aktive Quest:</p>
              <p className="text-xl font-bold" style={{ color: 'var(--aeth-gold)', fontFamily: "'Cinzel', serif" }}>
                {activeTimer.quest_name}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm" style={{ color: 'var(--aeth-parchment-dim)' }}>Verbleibend:</p>
              <p className="text-xl font-bold" style={{ color: 'var(--aeth-gold)', fontFamily: "'Azeret Mono', monospace" }}>
                {Math.floor(activeTimer.seconds_remaining / 60)}:{String(activeTimer.seconds_remaining % 60).padStart(2, '0')}
              </p>
            </div>
          </div>
          {activeTimer.seconds_remaining <= 0 && (
            <button
              onClick={completeQuest}
              className="btn-gold w-full py-3 rounded-lg font-semibold"
              data-testid="complete-quest-btn"
            >
              Quest abschließen
            </button>
          )}
        </motion.div>
      )}

      {/* Available Quests */}
      {loading ? (
        <div className="text-center py-20">Loading quests...</div>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {quests.available_quests.map((quest, i) => (
            <motion.div
              key={quest.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="aeth-card p-5"
              data-testid={`quest-${quest.id}`}
            >
              <div className="flex items-center gap-2 mb-2">
                <Scroll size={18} style={{ color: 'var(--aeth-gold)' }} />
                <h3 className="text-base font-semibold" style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}>
                  {quest.name}
                </h3>
                <span className="text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: 'rgba(214,162,77,0.15)', color: 'var(--aeth-gold)' }}>
                  Lvl {quest.min_level}+
                </span>
              </div>
              <p className="text-xs mb-4" style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
                {quest.description}
              </p>

              <div className="grid grid-cols-3 gap-3 mb-4 text-xs text-center">
                <div>
                  <p style={{ color: 'var(--aeth-parchment-dim)' }}>Gold</p>
                  <p className="font-semibold" style={{ color: 'var(--aeth-gold)' }}>{quest.rewards.gold}</p>
                </div>
                <div>
                  <p style={{ color: 'var(--aeth-parchment-dim)' }}>XP</p>
                  <p className="font-semibold" style={{ color: '#64B5F6' }}>{quest.rewards.xp}</p>
                </div>
                <div>
                  <p style={{ color: 'var(--aeth-parchment-dim)' }}>Dauer</p>
                  <p className="font-semibold">{quest.duration_minutes} Min</p>
                </div>
              </div>

              <button
                onClick={() => acceptQuest(quest.id)}
                disabled={accepting || activeTimer || gameState.resources.energy < quest.energy_cost || !gameState.status.can_act}
                className="btn-gold w-full py-2.5 rounded-lg text-sm font-semibold disabled:opacity-40"
                data-testid={`accept-quest-${quest.id}`}
              >
                {accepting ? 'Akzeptiere...' : `Akzeptieren (${quest.energy_cost} Energie)`}
              </button>
            </motion.div>
          ))}
        </div>
      )}

      {quests.available_quests.length === 0 && !activeTimer && (
        <div className="aeth-card p-12 text-center">
          <CheckCircle size={48} style={{ color: 'var(--aeth-gold)', margin: '0 auto 16px' }} />
          <p style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}>
            Keine verfügbaren Quests
          </p>
          <p className="text-sm" style={{ color: 'var(--aeth-parchment-dim)' }}>
            Du hast alle Quests für dein Level abgeschlossen
          </p>
        </div>
      )}
    </div>
  );
};
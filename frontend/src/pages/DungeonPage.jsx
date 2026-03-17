import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import axios from '../utils/axios';
import { motion } from 'framer-motion';
import { Lock, Clock, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function DungeonPage() {
  const { gameState, refreshGameState } = useOutletContext();
  const [dungeonData, setDungeonData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchDungeon = async () => {
    try {
      const res = await axios.get(`${API}/game/dungeon`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      setDungeonData(res.data);
    } catch (err) {
      toast.error('Fehler beim Laden');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDungeon();
  }, []);

  const jailTimer = gameState?.timers?.jail;
  const isInJail = jailTimer !== null;

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="animate-pulse space-y-4">
          <div className="h-32 bg-[color:var(--aeth-stone-2)] rounded-[var(--radius-card)]"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="mb-8">
        <h1
          className="text-3xl font-bold mb-2"
          style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}
        >
          Das Verlies
        </h1>
        <p style={{ color: 'var(--aeth-parchment-dim)' }}>
          Gefängnis des Reiches • Gescheiterte Verbrechen führen hierher
        </p>
      </div>

      {isInJail ? (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <Card
            className="border-2 shadow-[var(--shadow-elev-2)]"
            style={{ borderColor: 'var(--aeth-blood)', backgroundColor: 'var(--aeth-stone-2)' }}
          >
            <CardHeader>
              <div className="flex items-center gap-3">
                <Lock size={32} style={{ color: 'var(--aeth-blood)' }} />
                <div>
                  <CardTitle className="font-cinzel" style={{ color: 'var(--aeth-blood)' }}>
                    Du bist inhaftiert
                  </CardTitle>
                  <p className="text-sm mt-1" style={{ color: 'var(--aeth-parchment-dim)' }}>
                    Dein Verbrechen wurde entdeckt
                  </p>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div
                className="p-4 rounded-lg border"
                style={{ backgroundColor: 'var(--aeth-stone-1)', borderColor: 'var(--aeth-blood)' }}
              >
                <div className="flex justify-between items-center mb-4">
                  <span className="text-sm" style={{ color: 'var(--aeth-parchment-dim)' }}>Haftstrafe endet in:</span>
                  <Badge className="bg-[color:var(--aeth-blood)] text-white text-base px-3 py-1" data-testid="jail-timer">
                    {Math.floor((jailTimer?.seconds_remaining || 0) / 60)}:{String((jailTimer?.seconds_remaining || 0) % 60).padStart(2, '0')}
                  </Badge>
                </div>
                <div className="text-xs space-y-2" style={{ color: 'var(--aeth-parchment-dim)' }}>
                  <p>• Während der Haftzeit kannst du keine Aktionen durchführen</p>
                  <p>• Du regenerierst Energie und Leben normal weiter</p>
                  <p>• Nach Ablauf der Strafe wirst du automatisch freigelassen</p>
                </div>
              </div>

              {(jailTimer?.seconds_remaining || 0) <= 0 && (
                <div className="text-center">
                  <Badge className="bg-[color:var(--aeth-gold)] text-[color:var(--aeth-stone-0)] text-base px-4 py-2">
                    Freilassung ausstehend
                  </Badge>
                  <p className="text-sm mt-2" style={{ color: 'var(--aeth-parchment-dim)' }}>
                    Lade die Seite neu oder kehre zum Dashboard zurück
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      ) : (
        <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)]">
          <CardContent className="py-16 text-center">
            <Lock size={64} className="mx-auto mb-6" style={{ color: 'var(--aeth-parchment-dim)' }} />
            <p className="text-xl font-bold font-cinzel mb-2" style={{ color: 'var(--aeth-parchment)' }}>
              Du bist frei
            </p>
            <p style={{ color: 'var(--aeth-parchment-dim)' }}>
              Keine aktive Haftstrafe. Vermeide Verbrechen, um nicht hier zu landen!
            </p>
          </CardContent>
        </Card>
      )}

      {/* Info */}
      <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-1)]">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <AlertTriangle size={20} style={{ color: 'var(--aeth-gold)' }} className="mt-1" />
            <div className="text-sm space-y-2" style={{ color: 'var(--aeth-parchment-dim)' }}>
              <p className="font-semibold" style={{ color: 'var(--aeth-parchment)' }}>
                Wie komme ich ins Verlies?
              </p>
              <ul className="list-disc list-inside space-y-1">
                <li>Gescheiterte Verbrechen können zu einer Haftstrafe führen</li>
                <li>Je schwerer das Verbrechen, desto länger die Strafe (5-30 Minuten)</li>
                <li>Während der Haftzeit sind keine Spielaktionen möglich</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

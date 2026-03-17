import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import axios from '../utils/axios';
import { motion } from 'framer-motion';
import { MapPin, Clock, Coins, Navigation } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const KINGDOMS = [
  { id: 'hauptstadt', name: 'Hauptstadt Aethoria', desc: 'Zentrum des Reiches', color: '#D6A24D' },
  { id: 'nordwacht', name: 'Nordwacht', desc: 'Eisige Berge', color: '#64B5F6' },
  { id: 'suedhafen', name: 'Südhafen', desc: 'Handelsmetropole', color: '#FFB74D' },
  { id: 'ostwald', name: 'Ostwald', desc: 'Geheimnisvoller Wald', color: '#81C784' },
  { id: 'westfeste', name: 'Westfeste', desc: 'Militärfestung', color: '#E57373' },
  { id: 'schattenland', name: 'Schattenland', desc: 'Dunkle Magie', color: '#9575CD' },
  { id: 'goldtal', name: 'Goldtal', desc: 'Reiche Minen', color: '#FFD54F' },
  { id: 'sturmkueste', name: 'Sturmküste', desc: 'Wilde See', color: '#4FC3F7' },
  { id: 'drachenhoehen', name: 'Drachenhöhen', desc: 'Alte Ruinen', color: '#F06292' },
  { id: 'kristallgebirge', name: 'Kristallgebirge', desc: 'Magische Kristalle', color: '#BA68C8' },
  { id: 'totenmarsch', name: 'Totenmarsch', desc: 'Verfluchte Einöde', color: '#A1887F' },
];

export default function MapPage() {
  const { gameState, refreshGameState } = useOutletContext();
  const [travelTarget, setTravelTarget] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const currentLocation = gameState?.location?.kingdom_id || 'hauptstadt';
  const travelTimer = gameState?.timers?.travel;

  const handleTravel = async () => {
    if (!travelTarget) return;

    try {
      const res = await axios.post(
        `${API}/game/travel`,
        { destination: travelTarget.id },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      toast.success(res.data.message, { icon: '🗺️', duration: 4000 });
      setDialogOpen(false);
      refreshGameState();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Reisen');
    }
  };

  const completeTravel = async () => {
    try {
      const res = await axios.post(
        `${API}/game/travel/complete`,
        {},
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      toast.success(res.data.message, { icon: '✅' });
      refreshGameState();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler');
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="mb-8">
        <h1
          className="text-3xl font-bold mb-2"
          style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}
        >
          Karte des Reiches
        </h1>
        <p style={{ color: 'var(--aeth-parchment-dim)' }}>
          Reise zwischen den 11 Königreichen • Kosten: 50 Gold • Dauer: 10 Minuten
        </p>
      </div>

      {/* Travel Timer */}
      {travelTimer && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <Card
            className="border-2 shadow-[var(--shadow-elev-2)]"
            style={{ borderColor: 'var(--aeth-gold)', backgroundColor: 'var(--aeth-stone-2)' }}
          >
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Reise nach:</p>
                  <p className="text-xl font-bold font-cinzel" style={{ color: 'var(--aeth-gold)' }}>
                    {KINGDOMS.find((k) => k.id === travelTimer.destination)?.name || 'Unbekannt'}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Ankunft in:</p>
                  <p className="text-xl font-bold font-mono-az" style={{ color: 'var(--aeth-gold)' }}>
                    {Math.floor(travelTimer.seconds_remaining / 60)}:{String(travelTimer.seconds_remaining % 60).padStart(2, '0')}
                  </p>
                </div>
              </div>
              {travelTimer.seconds_remaining <= 0 && (
                <Button onClick={completeTravel} className="btn-gold w-full mt-4" data-testid="complete-travel-button">
                  Ankunft bestätigen
                </Button>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Current Location */}
      <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)]">
        <CardContent className="pt-6">
          <div className="flex items-center gap-3">
            <MapPin size={24} style={{ color: 'var(--aeth-gold)' }} />
            <div>
              <p className="text-xs mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Aktueller Standort:</p>
              <p className="text-xl font-bold font-cinzel" style={{ color: 'var(--aeth-parchment)' }} data-testid="current-location">
                {KINGDOMS.find((k) => k.id === currentLocation)?.name || 'Hauptstadt Aethoria'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Kingdom Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {KINGDOMS.map((kingdom, idx) => {
          const isCurrent = kingdom.id === currentLocation;
          const isTraveling = travelTimer !== null;

          return (
            <motion.div
              key={kingdom.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.03 }}
            >
              <Card
                className={`border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)] transition-all ${
                  isCurrent ? 'border-2 border-[color:var(--aeth-gold)]' : 'hover:border-[color:var(--aeth-gold)]'
                }`}
              >
                <CardHeader className="pb-3">
                  <CardTitle className="text-base font-cinzel flex items-center justify-between">
                    <span style={{ color: kingdom.color }}>{kingdom.name}</span>
                    {isCurrent && (
                      <Badge variant="outline" style={{ borderColor: 'var(--aeth-gold)', color: 'var(--aeth-gold)' }}>
                        Hier
                      </Badge>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm" style={{ color: 'var(--aeth-parchment-dim)' }}>
                    {kingdom.desc}
                  </p>
                  <Dialog open={dialogOpen && travelTarget?.id === kingdom.id} onOpenChange={setDialogOpen}>
                    <DialogTrigger asChild>
                      <Button
                        onClick={() => setTravelTarget(kingdom)}
                        disabled={isCurrent || isTraveling}
                        className="w-full"
                        variant={isCurrent ? 'outline' : 'default'}
                        data-testid={`travel-to-${kingdom.id}-button`}
                      >
                        <Navigation size={16} className="mr-2" />
                        {isCurrent ? 'Aktuell hier' : 'Reisen'}
                      </Button>
                    </DialogTrigger>
                    <DialogContent
                      className="border-[color:var(--game-border-subtle)]"
                      style={{ backgroundColor: 'var(--aeth-stone-1)' }}
                    >
                      <DialogHeader>
                        <DialogTitle className="font-cinzel" style={{ color: 'var(--aeth-parchment)' }}>
                          Reise nach {kingdom.name}
                        </DialogTitle>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div className="space-y-2 text-sm" style={{ color: 'var(--aeth-parchment-dim)' }}>
                          <div className="flex justify-between">
                            <span>Kosten:</span>
                            <span className="font-bold" style={{ color: 'var(--aeth-gold)' }}>50 Gold</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Dauer:</span>
                            <span className="font-bold" style={{ color: 'var(--aeth-parchment)' }}>10 Minuten</span>
                          </div>
                        </div>
                        <Button onClick={handleTravel} className="btn-gold w-full" data-testid="confirm-travel-button">
                          Reise beginnen
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}

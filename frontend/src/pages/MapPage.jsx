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
  { id: 'aethoria_capital', name: 'Aethoria Prime', desc: 'The capital of the Realm. Trade, power, and intrigue converge.', image: 'https://images.unsplash.com/photo-1533154683836-84ea7a0bc310?w=400&q=50', type: 'Capital', danger: 'Medium', min_level: 1, travel_cost: 0, color: '#D6A24D' },
  { id: 'ironhold', name: 'Ironhold', desc: 'A fortress city of steel and fire. Home to the greatest warriors.', image: 'https://images.unsplash.com/photo-1621947081720-86970823b77a?w=400&q=50', type: 'Military', danger: 'High', min_level: 3, travel_cost: 50, color: '#E57373' },
  { id: 'shadowfen', name: 'Shadowfen', desc: 'A city of fog and secrets, where rogues and thieves hold court. Home of the Shadow Guild.', image: 'https://images.unsplash.com/photo-1518709766631-a6a7f45921c3?w=400&q=50', type: 'Underworld', danger: 'Very High', min_level: 2, travel_cost: 50, color: '#9575CD' },
  { id: 'goldenveil', name: 'Goldenveil', desc: "The Realm's most prosperous trading city. Every merchant dreams of it.", image: 'https://images.unsplash.com/photo-1501183638710-841dd1904471?w=400&q=50', type: 'Commerce', danger: 'Low', min_level: 2, travel_cost: 50, color: '#FFD54F' },
  { id: 'stonecrest', name: 'Stonecrest', desc: 'Ancient mountains hiding powerful arcane secrets in their caves.', image: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&q=50', type: 'Arcane', danger: 'High', min_level: 5, travel_cost: 75, color: '#BA68C8' },
  { id: 'crystalmere', name: 'Crystalmere', desc: 'A lakeside city of extraordinary beauty and political scheming.', image: 'https://images.unsplash.com/photo-1499678329028-101435549a4e?w=400&q=50', type: 'Noble', danger: 'Medium', min_level: 4, travel_cost: 60, color: '#64B5F6' },
  { id: 'embervast', name: 'Embervast', desc: 'The volcanic borderlands, rich in dragon-forged materials.', image: 'https://images.unsplash.com/photo-1527482797697-8795b05a13fe?w=400&q=50', type: 'Wilds', danger: 'Extreme', min_level: 10, travel_cost: 100, color: '#F06292' },
  { id: 'tidehaven', name: 'Tidehaven', desc: 'A port city where smugglers and merchants clash over sea routes.', image: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&q=50', type: 'Maritime', danger: 'High', min_level: 6, travel_cost: 70, color: '#4FC3F7' },
  { id: 'duskwood', name: 'Duskwood', desc: 'An ancient forest kingdom where shapeshifters and druids dwell.', image: 'https://images.unsplash.com/photo-1448375240586-882707db888b?w=400&q=50', type: 'Forest', danger: 'Medium', min_level: 4, travel_cost: 55, color: '#81C784' },
  { id: 'frostholm', name: 'Frostholm', desc: 'The frozen north: hard people, rare pelts, and glacier-locked tombs.', image: 'https://images.unsplash.com/photo-1491555103944-7c647fd857e6?w=400&q=50', type: 'Frozen', danger: 'Very High', min_level: 12, travel_cost: 120, color: '#A1887F' },
  { id: 'sunkeep', name: 'Sunkeep', desc: 'A desert kingdom where ruins of the First Empire still stand.', image: 'https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=400&q=50', type: 'Desert', danger: 'High', min_level: 8, travel_cost: 85, color: '#FFB74D' },
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
        { kingdom_id: travelTarget.id },
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
                  
                  {/* Level Requirement Badge */}
                  <div className="flex items-center gap-2">
                    <Badge 
                      variant="outline" 
                      className={`text-xs ${
                        kingdom.min_level > (gameState?.user?.level || 1) 
                          ? 'border-[#E57373] text-[#E57373]' 
                          : 'border-[color:var(--aeth-gold)] text-[color:var(--aeth-gold)]'
                      }`}
                      data-testid={`kingdom-${kingdom.id}-level-req`}
                    >
                      Level {kingdom.min_level}+ erforderlich
                    </Badge>
                    {kingdom.travel_cost > 0 && (
                      <Badge variant="outline" className="text-xs border-[color:var(--aeth-parchment-dim)] text-[color:var(--aeth-parchment-dim)]">
                        {kingdom.travel_cost} Gold
                      </Badge>
                    )}
                  </div>
                  
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
                            <span>Level erforderlich:</span>
                            <span className="font-bold" style={{ color: kingdom.min_level > (gameState?.user?.level || 1) ? '#E57373' : 'var(--aeth-gold)' }}>
                              Level {kingdom.min_level}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span>Kosten:</span>
                            <span className="font-bold" style={{ color: 'var(--aeth-gold)' }}>{kingdom.travel_cost} Gold</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Dauer:</span>
                            <span className="font-bold" style={{ color: 'var(--aeth-parchment)' }}>10 Minuten</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Gefahr:</span>
                            <Badge variant="outline" style={{ 
                              borderColor: kingdom.danger === 'Extreme' ? '#F44336' : kingdom.danger === 'Very High' ? '#FF9800' : kingdom.danger === 'High' ? '#FFB74D' : '#81C784',
                              color: kingdom.danger === 'Extreme' ? '#F44336' : kingdom.danger === 'Very High' ? '#FF9800' : kingdom.danger === 'High' ? '#FFB74D' : '#81C784'
                            }}>
                              {kingdom.danger}
                            </Badge>
                          </div>
                        </div>
                        <Button 
                          onClick={handleTravel} 
                          disabled={kingdom.min_level > (gameState?.user?.level || 1) || (gameState?.resources?.gold || 0) < kingdom.travel_cost}
                          className="btn-gold w-full" 
                          data-testid="confirm-travel-button"
                        >
                          {kingdom.min_level > (gameState?.user?.level || 1) ? `Level ${kingdom.min_level} erforderlich` : 'Reise beginnen'}
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

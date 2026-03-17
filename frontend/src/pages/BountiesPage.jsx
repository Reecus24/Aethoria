import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import axios from '../utils/axios';
import { motion } from 'framer-motion';
import { Target, Coins, User, Plus, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function BountiesPage() {
  const { gameState, refreshGameState } = useOutletContext();
  const [bounties, setBounties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [targetName, setTargetName] = useState('');
  const [reward, setReward] = useState(100);

  const fetchBounties = async () => {
    try {
      const res = await axios.get(`${API}/game/bounties`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      setBounties(res.data.bounties || []);
    } catch (err) {
      toast.error('Fehler beim Laden der Kopfgelder');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBounties();
  }, []);

  const handleCreateBounty = async () => {
    if (!targetName.trim()) {
      toast.error('Zielname erforderlich');
      return;
    }
    if (reward < 100) {
      toast.error('Mindestbelohnung: 100 Gold');
      return;
    }
    if (reward > (gameState?.resources?.gold || 0)) {
      toast.error('Nicht genug Gold');
      return;
    }

    try {
      const res = await axios.post(
        `${API}/game/bounties/create`,
        { target_name: targetName, reward },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      toast.success(res.data.message, { icon: '🎯' });
      setCreateOpen(false);
      setTargetName('');
      setReward(100);
      fetchBounties();
      refreshGameState();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Erstellen des Kopfgeldes');
    }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto">
        <div className="animate-pulse space-y-4">
          <div className="h-32 bg-[color:var(--aeth-stone-2)] rounded-[var(--radius-card)]"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1
            className="text-3xl font-bold mb-2"
            style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}
          >
            Kopfgeld-Tafel
          </h1>
          <p style={{ color: 'var(--aeth-parchment-dim)' }}>
            Setze Kopfgelder auf andere Spieler aus • Mindestbelohnung: 100 Gold
          </p>
        </div>
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button className="btn-gold" data-testid="create-bounty-button">
              <Plus size={18} className="mr-2" />
              Kopfgeld aussetzen
            </Button>
          </DialogTrigger>
          <DialogContent
            className="border-[color:var(--game-border-subtle)]"
            style={{ backgroundColor: 'var(--aeth-stone-1)' }}
          >
            <DialogHeader>
              <DialogTitle className="font-cinzel" style={{ color: 'var(--aeth-parchment)' }}>
                Kopfgeld aussetzen
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <label className="text-sm mb-2 block" style={{ color: 'var(--aeth-parchment)' }}>
                  Ziel (Spielername)
                </label>
                <Input
                  placeholder="Name des Ziels"
                  value={targetName}
                  onChange={(e) => setTargetName(e.target.value)}
                  data-testid="bounty-target-input"
                />
              </div>
              <div>
                <label className="text-sm mb-2 block" style={{ color: 'var(--aeth-parchment)' }}>
                  Belohnung (Gold)
                </label>
                <Input
                  type="number"
                  value={reward}
                  onChange={(e) => setReward(Math.max(100, parseInt(e.target.value) || 100))}
                  min={100}
                  data-testid="bounty-reward-input"
                />
              </div>
              <div
                className="p-3 rounded-lg border"
                style={{ backgroundColor: 'var(--aeth-stone-0)', borderColor: 'var(--aeth-blood)' }}
              >
                <div className="flex gap-2 text-xs" style={{ color: 'var(--aeth-blood)' }}>
                  <AlertTriangle size={16} />
                  <p>Das Gold wird sofort von deinem Konto abgezogen und dem Jäger ausgezahlt, der das Ziel besiegt.</p>
                </div>
              </div>
              <Button onClick={handleCreateBounty} className="btn-gold w-full" data-testid="confirm-bounty-button">
                Kopfgeld aussetzen ({reward} Gold)
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Bounties List */}
      <ScrollArea className="h-[600px]">
        <div className="space-y-4">
          {bounties.length === 0 && (
            <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)]">
              <CardContent className="py-12 text-center">
                <Target size={48} className="mx-auto mb-4" style={{ color: 'var(--aeth-parchment-dim)' }} />
                <p style={{ color: 'var(--aeth-parchment-dim)' }}>
                  Keine aktiven Kopfgelder. Setze das erste aus!
                </p>
              </CardContent>
            </Card>
          )}

          {bounties.map((bounty, idx) => (
            <motion.div
              key={bounty.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.03 }}
            >
              <Card
                className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)] hover:border-[color:var(--aeth-blood)] transition-colors"
                data-testid={`bounty-${bounty.id}`}
              >
                <CardContent className="pt-6">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <Target size={24} style={{ color: 'var(--aeth-blood)' }} />
                        <div>
                          <p className="text-xs mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>ZIEL</p>
                          <p
                            className="text-xl font-bold font-cinzel"
                            style={{ color: 'var(--aeth-parchment)' }}
                            data-testid={`bounty-target-${bounty.id}`}
                          >
                            {bounty.target_name}
                          </p>
                        </div>
                      </div>
                      <div className="flex gap-6 text-sm">
                        <div>
                          <p className="text-xs mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Auftraggeber</p>
                          <p style={{ color: 'var(--aeth-parchment)' }}>{bounty.creator_name}</p>
                        </div>
                        <div>
                          <p className="text-xs mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Status</p>
                          <Badge variant={bounty.claimed ? 'default' : 'outline'}>
                            {bounty.claimed ? 'Eingefordert' : 'Aktiv'}
                          </Badge>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-xs mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Belohnung</p>
                      <p
                        className="text-2xl font-bold font-mono-az"
                        style={{ color: 'var(--aeth-gold)' }}
                        data-testid={`bounty-reward-${bounty.id}`}
                      >
                        {bounty.reward.toLocaleString()}
                      </p>
                      <p className="text-xs" style={{ color: 'var(--aeth-gold)' }}>Gold</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}

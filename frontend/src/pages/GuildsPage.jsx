import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Users, Plus, Crown, LogOut, Shield, Search } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Separator } from '@/components/ui/separator';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function GuildsPage() {
  const { gameState, refreshGameState } = useOutletContext();
  const [guilds, setGuilds] = useState([]);
  const [myGuild, setMyGuild] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [createOpen, setCreateOpen] = useState(false);
  const [newGuildName, setNewGuildName] = useState('');
  const [newGuildDesc, setNewGuildDesc] = useState('');

  const fetchGuilds = async () => {
    try {
      const [guildsRes, myGuildRes] = await Promise.all([
        axios.get(`${API}/game/guilds`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        }),
        axios.get(`${API}/game/guilds/my-guild`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        }).catch(() => ({ data: { guild: null } })),
      ]);
      setGuilds(guildsRes.data.guilds || []);
      setMyGuild(myGuildRes.data.guild);
    } catch (err) {
      toast.error('Fehler beim Laden der Gilden');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGuilds();
  }, []);

  const handleCreateGuild = async () => {
    if (!newGuildName.trim()) {
      toast.error('Gildenname erforderlich');
      return;
    }
    try {
      const res = await axios.post(
        `${API}/game/guilds/create`,
        { name: newGuildName, description: newGuildDesc },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      toast.success(res.data.message, { icon: '🏰' });
      setCreateOpen(false);
      setNewGuildName('');
      setNewGuildDesc('');
      fetchGuilds();
      refreshGameState();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Erstellen der Gilde');
    }
  };

  const handleJoinGuild = async (guildId) => {
    try {
      const res = await axios.post(
        `${API}/game/guilds/${guildId}/join`,
        {},
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      toast.success(res.data.message, { icon: '⚔️' });
      fetchGuilds();
      refreshGameState();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Beitreten');
    }
  };

  const handleLeaveGuild = async () => {
    try {
      const res = await axios.post(
        `${API}/game/guilds/leave`,
        {},
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      toast.success(res.data.message);
      fetchGuilds();
      refreshGameState();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Verlassen');
    }
  };

  const filteredGuilds = guilds.filter((g) =>
    g.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="animate-pulse space-y-4">
          <div className="h-48 bg-[color:var(--aeth-stone-2)] rounded-[var(--radius-card)]"></div>
          <div className="h-32 bg-[color:var(--aeth-stone-2)] rounded-[var(--radius-card)]"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1
            className="text-3xl font-bold mb-2"
            style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}
          >
            Gilden & Orden
          </h1>
          <p style={{ color: 'var(--aeth-parchment-dim)' }}>
            Schließe dich einer Gilde an oder gründe deine eigene
          </p>
        </div>
        {!myGuild && (
          <Dialog open={createOpen} onOpenChange={setCreateOpen}>
            <DialogTrigger asChild>
              <Button className="btn-gold" data-testid="create-guild-button">
                <Plus size={18} className="mr-2" />
                Gilde gründen
              </Button>
            </DialogTrigger>
            <DialogContent
              className="border-[color:var(--game-border-subtle)]"
              style={{ backgroundColor: 'var(--aeth-stone-1)' }}
            >
              <DialogHeader>
                <DialogTitle className="font-cinzel" style={{ color: 'var(--aeth-parchment)' }}>
                  Neue Gilde gründen
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <Input
                  placeholder="Gildenname"
                  value={newGuildName}
                  onChange={(e) => setNewGuildName(e.target.value)}
                  data-testid="guild-name-input"
                />
                <Textarea
                  placeholder="Beschreibung (optional)"
                  value={newGuildDesc}
                  onChange={(e) => setNewGuildDesc(e.target.value)}
                  rows={4}
                  data-testid="guild-description-input"
                />
                <Button onClick={handleCreateGuild} className="btn-gold w-full" data-testid="confirm-create-guild-button">
                  Gilde gründen
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        )}
      </div>

      {/* My Guild */}
      {myGuild && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <Card
            className="border-2 shadow-[var(--shadow-elev-2)]"
            style={{ borderColor: 'var(--aeth-gold)', backgroundColor: 'var(--aeth-stone-2)' }}
          >
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="font-cinzel text-2xl mb-2" style={{ color: 'var(--aeth-gold)' }}>
                    {myGuild.name}
                  </CardTitle>
                  <CardDescription style={{ color: 'var(--aeth-parchment-dim)' }}>
                    {myGuild.description || 'Keine Beschreibung'}
                  </CardDescription>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleLeaveGuild}
                  className="border-[color:var(--aeth-blood)] text-[color:var(--aeth-blood)] hover:bg-[rgba(142,29,44,0.1)]"
                  data-testid="leave-guild-button"
                >
                  <LogOut size={16} className="mr-2" />
                  Verlassen
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex gap-6">
                <div>
                  <p className="text-xs mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Mitglieder</p>
                  <p className="text-xl font-bold font-mono-az" style={{ color: 'var(--aeth-parchment)' }}>
                    {myGuild.member_count || 1}
                  </p>
                </div>
                <Separator orientation="vertical" className="h-12" />
                <div>
                  <p className="text-xs mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>Anführer</p>
                  <p className="text-sm font-semibold" style={{ color: 'var(--aeth-parchment)' }}>
                    {myGuild.leader_name || 'Unbekannt'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Guild List */}
      {!myGuild && (
        <>
          <div className="flex gap-3 mb-4">
            <div className="relative flex-1">
              <Search
                size={18}
                className="absolute left-3 top-1/2 transform -translate-y-1/2"
                style={{ color: 'var(--aeth-parchment-dim)' }}
              />
              <Input
                placeholder="Gilden durchsuchen..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
                data-testid="guild-search-input"
              />
            </div>
          </div>

          <div className="space-y-4">
            {filteredGuilds.length === 0 && (
              <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)]">
                <CardContent className="py-12 text-center">
                  <Users size={48} className="mx-auto mb-4" style={{ color: 'var(--aeth-parchment-dim)' }} />
                  <p style={{ color: 'var(--aeth-parchment-dim)' }}>
                    Keine Gilden gefunden. Gründe die erste!
                  </p>
                </CardContent>
              </Card>
            )}

            {filteredGuilds.map((guild, idx) => (
              <motion.div
                key={guild.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
              >
                <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)] hover:border-[color:var(--aeth-gold)] transition-colors">
                  <CardContent className="pt-6">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3
                          className="text-xl font-bold mb-2 font-cinzel"
                          style={{ color: 'var(--aeth-parchment)' }}
                          data-testid={`guild-name-${guild.id}`}
                        >
                          {guild.name}
                        </h3>
                        <p className="text-sm mb-4" style={{ color: 'var(--aeth-parchment-dim)' }}>
                          {guild.description || 'Keine Beschreibung'}
                        </p>
                        <div className="flex gap-4 text-xs">
                          <span style={{ color: 'var(--aeth-parchment-dim)' }}>
                            <Users size={14} className="inline mr-1" />
                            {guild.member_count || 1} Mitglieder
                          </span>
                          <span style={{ color: 'var(--aeth-parchment-dim)' }}>
                            <Crown size={14} className="inline mr-1" />
                            {guild.leader_name}
                          </span>
                        </div>
                      </div>
                      <Button
                        onClick={() => handleJoinGuild(guild.id)}
                        className="btn-gold"
                        data-testid={`join-guild-${guild.id}-button`}
                      >
                        Beitreten
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

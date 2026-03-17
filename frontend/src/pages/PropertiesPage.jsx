import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Home, Coins, TrendingUp, ShoppingBag } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function PropertiesPage() {
  const { gameState, refreshGameState } = useOutletContext();
  const [availableProperties, setAvailableProperties] = useState([]);
  const [myProperties, setMyProperties] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchProperties = async () => {
    try {
      const [availRes, myRes] = await Promise.all([
        axios.get(`${API}/game/properties/available`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        }),
        axios.get(`${API}/game/properties/my-properties`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        }),
      ]);
      setAvailableProperties(availRes.data.properties || []);
      setMyProperties(myRes.data.properties || []);
    } catch (err) {
      toast.error('Fehler beim Laden der Immobilien');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProperties();
  }, []);

  const handleBuyProperty = async (propertyId) => {
    try {
      const res = await axios.post(
        `${API}/game/properties/buy`,
        { property_id: propertyId },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      toast.success(res.data.message, { icon: '🏰', duration: 4000 });
      fetchProperties();
      refreshGameState();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Kauf');
    }
  };

  const handleCollectIncome = async (propertyId) => {
    try {
      const res = await axios.post(
        `${API}/game/properties/collect/${propertyId}`,
        {},
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      toast.success(res.data.message, { icon: '💰' });
      fetchProperties();
      refreshGameState();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Einsammeln');
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="animate-pulse space-y-4">
          <div className="h-32 bg-[color:var(--aeth-stone-2)] rounded-[var(--radius-card)]"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="mb-8">
        <h1
          className="text-3xl font-bold mb-2"
          style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}
        >
          Immobilien & Festungen
        </h1>
        <p style={{ color: 'var(--aeth-parchment-dim)' }}>
          Kaufe Immobilien und generiere passives Einkommen
        </p>
      </div>

      <Tabs defaultValue="my-properties" className="w-full">
        <TabsList
          className="grid w-full grid-cols-2 mb-6"
          style={{ backgroundColor: 'var(--aeth-stone-1)' }}
        >
          <TabsTrigger value="my-properties" data-testid="my-properties-tab">
            Meine Immobilien
          </TabsTrigger>
          <TabsTrigger value="available" data-testid="available-properties-tab">
            Zum Verkauf
          </TabsTrigger>
        </TabsList>

        {/* My Properties */}
        <TabsContent value="my-properties">
          <ScrollArea className="h-[600px]">
            <div className="space-y-4">
              {myProperties.length === 0 && (
                <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)]">
                  <CardContent className="py-12 text-center">
                    <Home size={48} className="mx-auto mb-4" style={{ color: 'var(--aeth-parchment-dim)' }} />
                    <p style={{ color: 'var(--aeth-parchment-dim)' }}>
                      Du besitzt noch keine Immobilien. Kaufe deine erste!
                    </p>
                  </CardContent>
                </Card>
              )}

              {myProperties.map((prop, idx) => {
                const canCollect = prop.income_ready || false;
                return (
                  <motion.div
                    key={prop.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                  >
                    <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)]">
                      <CardHeader>
                        <div className="flex justify-between items-start">
                          <div>
                            <CardTitle className="font-cinzel" style={{ color: 'var(--aeth-gold)' }}>
                              {prop.name}
                            </CardTitle>
                            <CardDescription style={{ color: 'var(--aeth-parchment-dim)' }}>
                              {prop.description}
                            </CardDescription>
                          </div>
                          {canCollect && (
                            <Badge className="bg-[color:var(--aeth-gold)] text-[color:var(--aeth-stone-0)]">
                              Bereit
                            </Badge>
                          )}
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="text-xs mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>
                              Einkommen/Tag
                            </p>
                            <p className="font-bold font-mono-az" style={{ color: 'var(--aeth-gold)' }}>
                              {prop.income_per_day} Gold
                            </p>
                          </div>
                          <div>
                            <p className="text-xs mb-1" style={{ color: 'var(--aeth-parchment-dim)' }}>
                              Standort
                            </p>
                            <p style={{ color: 'var(--aeth-parchment)' }}>{prop.location || 'Hauptstadt'}</p>
                          </div>
                        </div>
                        {canCollect && (
                          <Button
                            onClick={() => handleCollectIncome(prop.id)}
                            className="btn-gold w-full"
                            data-testid={`collect-income-${prop.id}-button`}
                          >
                            <Coins size={18} className="mr-2" />
                            Einkommen einsammeln
                          </Button>
                        )}
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
            </div>
          </ScrollArea>
        </TabsContent>

        {/* Available Properties */}
        <TabsContent value="available">
          <ScrollArea className="h-[600px]">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {availableProperties.length === 0 && (
                <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)] col-span-2">
                  <CardContent className="py-12 text-center">
                    <ShoppingBag size={48} className="mx-auto mb-4" style={{ color: 'var(--aeth-parchment-dim)' }} />
                    <p style={{ color: 'var(--aeth-parchment-dim)' }}>
                      Keine Immobilien verfügbar
                    </p>
                  </CardContent>
                </Card>
              )}

              {availableProperties.map((prop, idx) => (
                <motion.div
                  key={prop.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                >
                  <Card className="border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)] hover:border-[color:var(--aeth-gold)] transition-colors">
                    <CardHeader>
                      <CardTitle className="text-base font-cinzel" style={{ color: 'var(--aeth-parchment)' }}>
                        {prop.name}
                      </CardTitle>
                      <CardDescription style={{ color: 'var(--aeth-parchment-dim)' }}>
                        {prop.description}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span style={{ color: 'var(--aeth-parchment-dim)' }}>Preis:</span>
                          <span className="font-bold font-mono-az" style={{ color: 'var(--aeth-gold)' }}>
                            {prop.price.toLocaleString()} Gold
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span style={{ color: 'var(--aeth-parchment-dim)' }}>Einkommen/Tag:</span>
                          <span className="font-bold font-mono-az" style={{ color: 'var(--aeth-parchment)' }}>
                            +{prop.income_per_day} Gold
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span style={{ color: 'var(--aeth-parchment-dim)' }}>Level benötigt:</span>
                          <Badge variant="outline">{prop.min_level}</Badge>
                        </div>
                      </div>
                      <Button
                        onClick={() => handleBuyProperty(prop.id)}
                        disabled={
                          (gameState?.resources?.gold || 0) < prop.price ||
                          (gameState?.character?.level || 0) < prop.min_level
                        }
                        className="btn-gold w-full"
                        data-testid={`buy-property-${prop.id}-button`}
                      >
                        Kaufen
                      </Button>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </ScrollArea>
        </TabsContent>
      </Tabs>
    </div>
  );
}

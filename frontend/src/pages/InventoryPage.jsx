import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import axios from '../utils/axios';
import { motion } from 'framer-motion';
import { Package, Sword, Shield, Zap } from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function InventoryPage() {
  const { gameState, refreshGameState } = useOutletContext();
  const [inventory, setInventory] = useState({ inventory: [], equipped: {} });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInventory();
  }, []);

  const fetchInventory = async () => {
    try {
      const res = await axios.get(`${API}/game/inventory`);
      setInventory(res.data);
      setLoading(false);
    } catch (err) {
      toast.error('Fehler beim Laden des Inventars');
      setLoading(false);
    }
  };

  const handleUseItem = async (itemId) => {
    try {
      const res = await axios.post(`${API}/game/inventory/use`, { item_id: itemId });
      toast.success(res.data.message, { icon: '✨' });
      fetchInventory();
      refreshGameState();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Benutzen');
    }
  };

  const equipItem = async (itemId, slot) => {
    try {
      const res = await axios.post(`${API}/game/inventory/equip`, { item_id: itemId, slot });
      toast.success(res.data.message);
      fetchInventory();
      refreshGameState();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Ausrüsten');
    }
  };

  const unequipItem = async (slot) => {
    try {
      const res = await axios.post(`${API}/game/inventory/unequip?slot=${slot}`);
      toast.success(res.data.message);
      fetchInventory();
      refreshGameState();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler');
    }
  };

  if (loading) return <div className="text-center py-20">Loading inventory...</div>;

  const groupedInventory = inventory.inventory.reduce((acc, item) => {
    const type = item.item_details.type;
    if (!acc[type]) acc[type] = [];
    acc[type].push(item);
    return acc;
  }, {});

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2" style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}>
          Inventory & Equipment
        </h1>
        <p style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
          Verwalte deine Gegenstände und Ausrüstung
        </p>
      </div>

      {/* Equipped Items */}
      <div className="aeth-card p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4" style={{ color: 'var(--aeth-gold)', fontFamily: "'Cinzel', serif" }}>
          Ausrüstung
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {['weapon', 'offhand', 'armor', 'helmet', 'boots'].map(slot => {
            const equippedId = inventory.equipped[slot];
            const equippedItem = equippedId ? inventory.inventory.find(i => i.item_id === equippedId)?.item_details : null;
            
            return (
              <div key={slot} className="p-4 rounded-lg" style={{ backgroundColor: 'var(--aeth-stone-1)', border: '1px solid var(--aeth-iron)' }}>
                <p className="text-xs uppercase mb-2" style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'Cinzel', serif" }}>
                  {slot === 'weapon' && 'Waffe'}
                  {slot === 'offhand' && 'Offhand'}
                  {slot === 'armor' && 'Rüstung'}
                  {slot === 'helmet' && 'Helm'}
                  {slot === 'boots' && 'Stiefel'}
                </p>
                {equippedItem ? (
                  <div>
                    <p className="text-sm font-semibold mb-1" style={{ color: 'var(--aeth-parchment)' }}>
                      {equippedItem.name}
                    </p>
                    <p className="text-xs" style={{ color: 'var(--aeth-gold)' }}>
                      {equippedItem.damage && `+${equippedItem.damage} DMG`}
                      {equippedItem.defense && `+${equippedItem.defense} DEF`}
                    </p>
                    <button
                      onClick={() => unequipItem(slot)}
                      className="text-xs mt-2" style={{ color: '#E57373' }}
                    >
                      Ablegen
                    </button>
                  </div>
                ) : (
                  <p className="text-xs" style={{ color: 'var(--aeth-iron)' }}>Leer</p>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Inventory Items by Type */}
      {Object.keys(groupedInventory).length === 0 ? (
        <div className="aeth-card p-12 text-center">
          <Package size={48} style={{ color: 'var(--aeth-iron)', margin: '0 auto 16px' }} />
          <p style={{ color: 'var(--aeth-parchment)' }}>Dein Inventar ist leer</p>
          <p className="text-sm" style={{ color: 'var(--aeth-parchment-dim)' }}>Kaufe Gegenstände im Shop oder verdiene sie durch Quests</p>
        </div>
      ) : (
        Object.entries(groupedInventory).map(([type, items]) => (
          <div key={type} className="mb-6">
            <h2 className="text-lg font-semibold mb-3" style={{ color: 'var(--aeth-gold)', fontFamily: "'Cinzel', serif", textTransform: 'capitalize' }}>
              {type === 'weapon' ? 'Waffen' : type === 'armor' ? 'Rüstungen' : type === 'consumable' ? 'Verbrauchsgüter' : type === 'relic' ? 'Reliquien' : type}
            </h2>
            <div className="grid md:grid-cols-3 lg:grid-cols-4 gap-4">
              {items.map(item => {
                const isEquipped = item.equipped === true;
                
                return (
                <div key={item.id} className={`aeth-card p-4 ${isEquipped ? 'border-2 border-[color:var(--aeth-gold)]' : ''}`} data-testid={`inventory-item-${item.item_id}`}>
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-sm font-semibold" style={{ color: 'var(--aeth-parchment)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
                      {item.item_details.name}
                    </h3>
                    <div className="flex flex-col items-end gap-1">
                      <span className="text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: 'rgba(214,162,77,0.15)', color: 'var(--aeth-gold)' }}>
                        x{item.quantity}
                      </span>
                      {isEquipped && (
                        <span className="text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: 'rgba(129,199,132,0.15)', color: '#81C784' }}>
                          Ausgerüstet
                        </span>
                      )}
                    </div>
                  </div>
                  <p className="text-xs mb-3" style={{ color: 'var(--aeth-parchment-dim)' }}>
                    {item.item_details.description}
                  </p>
                  {item.item_details.effect && (
                    <div className="text-xs mb-3 p-2 rounded" style={{ backgroundColor: 'rgba(100,181,246,0.1)', color: '#64B5F6' }}>
                      <p className="font-semibold mb-1">Effekt:</p>
                      {item.item_details.effect.hp && <p>+{item.item_details.effect.hp} HP</p>}
                      {item.item_details.effect.energy && <p>+{item.item_details.effect.energy} Energie</p>}
                      {item.item_details.effect.strength_boost && <p>+{item.item_details.effect.strength_boost} Stärke ({item.item_details.effect.duration_hours}h)</p>}
                      {item.item_details.effect.dexterity_boost && <p>+{item.item_details.effect.dexterity_boost} Geschicklichkeit</p>}
                      {item.item_details.effect.crime_success_boost && <p>+{item.item_details.effect.crime_success_boost}% Verbrechenserfolg</p>}
                      {item.item_details.effect.damage_boost && <p>+{item.item_details.effect.damage_boost} Schaden</p>}
                    </div>
                  )}
                  {/* Show all stat bonuses */}
                  {(item.item_details.damage || item.item_details.defense || item.item_details.strength || item.item_details.dexterity || item.item_details.speed) && (
                    <div className="text-xs mb-3 flex flex-wrap gap-2">
                      {item.item_details.damage && <span style={{ color: '#E57373' }}>⚔️ {item.item_details.damage} DMG</span>}
                      {item.item_details.strength && <span style={{ color: '#E57373' }}>💪 {item.item_details.strength} STR</span>}
                      {item.item_details.defense && <span style={{ color: '#81C784' }}>🛡️ {item.item_details.defense} DEF</span>}
                      {item.item_details.dexterity && <span style={{ color: '#FFB74D' }}>🎯 {item.item_details.dexterity} DEX</span>}
                      {item.item_details.speed && <span style={{ color: '#64B5F6' }}>⚡ {item.item_details.speed} SPD</span>}
                    </div>
                  )}
                  {item.item_details.type === 'consumable' && !isEquipped && (
                    <button
                      onClick={() => handleUseItem(item.item_id)}
                      className="btn-gold w-full py-2 rounded text-xs font-semibold"
                      data-testid={`use-item-${item.item_id}`}
                    >
                      Benutzen
                    </button>
                  )}
                  {item.item_details.slot && !isEquipped && (
                    <button
                      onClick={() => equipItem(item.item_id, item.item_details.slot)}
                      className="btn-gold w-full py-2 rounded text-xs font-semibold"
                      data-testid={`equip-item-${item.item_id}`}
                    >
                      Ausrüsten
                    </button>
                  )}
                  {isEquipped && (
                    <button
                      onClick={() => unequipItem(item.item_details.slot)}
                      className="w-full py-2 rounded text-xs font-semibold"
                      style={{ backgroundColor: 'rgba(229,115,115,0.2)', color: '#E57373' }}
                      data-testid={`unequip-item-${item.item_id}`}
                    >
                      Ablegen
                    </button>
                  )}
                </div>
              )})}
            </div>
          </div>
        ))
      )}
    </div>
  );
};
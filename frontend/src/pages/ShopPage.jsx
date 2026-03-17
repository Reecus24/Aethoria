import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Store, ShoppingBag } from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const ShopPage = () => {
  const { gameState, refreshGameState } = useOutletContext();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [buying, setBuying] = useState(false);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      const res = await axios.get(`${API}/game/shop/items`);
      setItems(res.data);
      setLoading(false);
    } catch (err) {
      toast.error('Fehler beim Laden des Shops');
      setLoading(false);
    }
  };

  const buyItem = async (itemId, price) => {
    if (gameState.resources.gold < price) {
      toast.error('Nicht genug Gold!');
      return;
    }

    setBuying(true);
    try {
      const res = await axios.post(`${API}/game/shop/buy?item_id=${itemId}&quantity=1`);
      toast.success(res.data.message, { icon: '🛍️' });
      refreshGameState();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Kauf');
    } finally {
      setBuying(false);
    }
  };

  if (loading) return <div className="text-center py-20">Loading shop...</div>;

  const filteredItems = filter === 'all' ? items : items.filter(i => i.type === filter);
  const categories = ['all', 'weapon', 'armor', 'consumable', 'relic'];
  const categoryLabels = { all: 'Alle', weapon: 'Waffen', armor: 'Rüstungen', consumable: 'Tränke', relic: 'Reliquien' };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2" style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}>
          Armour Shop
        </h1>
        <p style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
          Kaufe Waffen, Rüstungen und Tränke
        </p>
      </div>

      {/* Filter */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setFilter(cat)}
            className="px-4 py-2 rounded-lg text-sm font-semibold transition-all"
            style={{
              backgroundColor: filter === cat ? 'rgba(214,162,77,0.2)' : 'var(--aeth-iron-2)',
              color: filter === cat ? 'var(--aeth-gold)' : 'var(--aeth-parchment-dim)',
              border: filter === cat ? '1px solid var(--aeth-gold)' : '1px solid var(--aeth-iron)'
            }}
          >
            {categoryLabels[cat]}
          </button>
        ))}
      </div>

      {/* Items Grid */}
      <div className="grid md:grid-cols-3 lg:grid-cols-4 gap-4">
        {filteredItems.map((item, i) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.02 }}
            className="aeth-card p-4"
            data-testid={`shop-item-${item.id}`}
          >
            <div className="flex items-start justify-between mb-2">
              <h3 className="text-sm font-semibold" style={{ color: 'var(--aeth-parchment)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
                {item.name}
              </h3>
              <span className="text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: 'rgba(214,162,77,0.15)', color: 'var(--aeth-gold)' }}>
                Lvl {item.required_level}
              </span>
            </div>
            <p className="text-xs mb-3" style={{ color: 'var(--aeth-parchment-dim)' }}>
              {item.description}
            </p>
            <div className="flex items-center justify-between mb-3 text-xs">
              {item.damage && <span style={{ color: '#E57373' }}>+{item.damage} DMG</span>}
              {item.defense && <span style={{ color: '#81C784' }}>+{item.defense} DEF</span>}
              {item.effect && <span style={{ color: '#64B5F6' }}>Effekt</span>}
            </div>
            <button
              onClick={() => buyItem(item.id, item.price)}
              disabled={buying || gameState.resources.gold < item.price}
              className="btn-gold w-full py-2 rounded text-xs font-semibold disabled:opacity-40"
              data-testid={`buy-${item.id}`}
            >
              Kaufen ({item.price} Gold)
            </button>
          </motion.div>
        ))}
      </div>
    </div>
  );
};
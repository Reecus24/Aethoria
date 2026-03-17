import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import axios from '../utils/axios';
import { motion } from 'framer-motion';
import { ShoppingCart, Plus, X } from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function MarketPage() {
  const { gameState, refreshGameState } = useOutletContext();
  const [listings, setListings] = useState([]);
  const [myListings, setMyListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('browse');

  useEffect(() => {
    fetchListings();
    fetchMyListings();
  }, []);

  const fetchListings = async () => {
    try {
      const res = await axios.get(`${API}/game/market/listings`);
      setListings(res.data);
      setLoading(false);
    } catch (err) {
      toast.error('Fehler beim Laden');
      setLoading(false);
    }
  };

  const fetchMyListings = async () => {
    try {
      const res = await axios.get(`${API}/game/market/my-listings`);
      setMyListings(res.data);
    } catch (err) {
      console.error('Failed to fetch my listings:', err);
    }
  };

  const buyListing = async (listingId, quantity, cost) => {
    if (gameState.resources.gold < cost) {
      toast.error('Nicht genug Gold!');
      return;
    }

    try {
      const res = await axios.post(`${API}/game/market/buy`, { listing_id: listingId, quantity });
      toast.success(res.data.message);
      refreshGameState();
      fetchListings();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Kauf');
    }
  };

  const cancelListing = async (listingId) => {
    try {
      const res = await axios.delete(`${API}/game/market/cancel/${listingId}`);
      toast.success(res.data.message);
      fetchMyListings();
      fetchListings();
    } catch (err) {
      toast.error('Fehler beim Stornieren');
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2" style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}>
          Grand Market
        </h1>
        <p style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
          Handel mit anderen Spielern
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setTab('browse')}
          className="px-6 py-2.5 rounded-lg font-semibold"
          style={{
            backgroundColor: tab === 'browse' ? 'rgba(214,162,77,0.2)' : 'var(--aeth-iron-2)',
            color: tab === 'browse' ? 'var(--aeth-gold)' : 'var(--aeth-parchment-dim)',
            border: tab === 'browse' ? '1px solid var(--aeth-gold)' : '1px solid var(--aeth-iron)'
          }}
        >
          Stöbern
        </button>
        <button
          onClick={() => setTab('my-listings')}
          className="px-6 py-2.5 rounded-lg font-semibold"
          style={{
            backgroundColor: tab === 'my-listings' ? 'rgba(214,162,77,0.2)' : 'var(--aeth-iron-2)',
            color: tab === 'my-listings' ? 'var(--aeth-gold)' : 'var(--aeth-parchment-dim)',
            border: tab === 'my-listings' ? '1px solid var(--aeth-gold)' : '1px solid var(--aeth-iron)'
          }}
        >
          Meine Angebote ({myListings.length})
        </button>
      </div>

      {/* Browse Tab */}
      {tab === 'browse' && (
        <div className="space-y-3">
          {listings.length === 0 ? (
            <div className="aeth-card p-12 text-center">
              <ShoppingCart size={48} style={{ color: 'var(--aeth-iron)', margin: '0 auto 16px' }} />
              <p style={{ color: 'var(--aeth-parchment)' }}>Markt ist leer</p>
            </div>
          ) : (
            listings.map(listing => (
              <div key={listing.id} className="aeth-card p-5" data-testid={`listing-${listing.id}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 flex-1">
                    <div>
                      <h3 className="text-base font-semibold" style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}>
                        {listing.item_name}
                      </h3>
                      <p className="text-xs" style={{ color: 'var(--aeth-parchment-dim)' }}>
                        {listing.quantity}x verfügbar • Verkäufer: {listing.seller_name} (Lvl {listing.seller_level})
                      </p>
                    </div>
                  </div>
                  <div className="text-right flex items-center gap-4">
                    <div>
                      <p className="text-sm" style={{ color: 'var(--aeth-parchment-dim)' }}>Preis:</p>
                      <p className="text-lg font-bold" style={{ color: 'var(--aeth-gold)', fontFamily: "'Azeret Mono', monospace" }}>
                        {listing.price_per_unit} Gold/Stück
                      </p>
                    </div>
                    <button
                      onClick={() => buyListing(listing.id, 1, listing.price_per_unit)}
                      disabled={gameState.resources.gold < listing.price_per_unit}
                      className="btn-gold px-4 py-2 rounded-lg text-sm font-semibold disabled:opacity-40"
                      data-testid={`buy-listing-${listing.id}`}
                    >
                      1x Kaufen
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* My Listings Tab */}
      {tab === 'my-listings' && (
        <div className="space-y-3">
          {myListings.length === 0 ? (
            <div className="aeth-card p-12 text-center">
              <p style={{ color: 'var(--aeth-parchment)' }}>Keine aktiven Angebote</p>
              <p className="text-sm" style={{ color: 'var(--aeth-parchment-dim)' }}>Erstelle Angebote aus deinem Inventar</p>
            </div>
          ) : (
            myListings.map(listing => (
              <div key={listing.id} className="aeth-card p-5">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-base font-semibold" style={{ color: 'var(--aeth-parchment)' }}>
                      {listing.item_name}
                    </h3>
                    <p className="text-xs" style={{ color: 'var(--aeth-parchment-dim)' }}>
                      {listing.quantity}x @ {listing.price_per_unit} Gold/Stück
                    </p>
                  </div>
                  <button
                    onClick={() => cancelListing(listing.id)}
                    className="btn-iron px-4 py-2 rounded-lg text-sm"
                  >
                    Stornieren
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};
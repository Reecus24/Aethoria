import { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight, Scroll, MessageSquarePlus } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const StarRating = ({ rating }) => (
  <div className="flex gap-0.5" data-testid="star-rating" aria-label={`${rating} out of 5 stars`}>
    {[1, 2, 3, 4, 5].map((s) => (
      <span
        key={s}
        style={{
          fontSize: '1rem',
          color: s <= rating ? '#D6A24D' : '#3B3532',
          textShadow: s <= rating ? '0 0 8px rgba(214,162,77,0.5)' : 'none',
          lineHeight: 1,
        }}
      >
        ★
      </span>
    ))}
  </div>
);

const ReviewCard = ({ review }) => (
  <div
    className="aeth-card p-6 flex flex-col gap-4 h-full"
    style={{ minHeight: 200 }}
    data-testid="review-card"
  >
    {/* Top: author + rating */}
    <div className="flex items-start justify-between gap-3">
      <div className="flex items-center gap-3">
        {/* Avatar crest */}
        <div
          className="w-10 h-10 rounded-full flex items-center justify-center text-base font-bold"
          style={{
            backgroundColor: 'var(--aeth-iron-2)',
            border: '2px solid var(--aeth-iron)',
            color: 'var(--aeth-gold)',
            fontFamily: "'Cinzel', serif",
          }}
        >
          {review.author[0].toUpperCase()}
        </div>
        <div>
          <p
            className="text-sm font-semibold"
            style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}
          >
            {review.author}
          </p>
          <StarRating rating={review.rating} />
        </div>
      </div>
      {/* Wax seal */}
      <div
        className="text-xs px-2 py-0.5 rounded-full flex-shrink-0"
        style={{
          backgroundColor: 'rgba(142,29,44,0.2)',
          color: '#E57373',
          border: '1px solid rgba(142,29,44,0.4)',
          fontFamily: "'Azeret Mono', monospace",
        }}
      >
        ✦ Verified
      </div>
    </div>

    {/* Review text */}
    <p
      className="text-sm leading-relaxed flex-1"
      style={{
        color: 'var(--aeth-parchment-dim)',
        fontFamily: "'IBM Plex Sans', sans-serif",
        fontStyle: 'italic',
      }}
    >
      &ldquo;{review.text}&rdquo;
    </p>

    {/* Date */}
    <p
      className="text-xs"
      style={{ color: 'var(--aeth-iron)', fontFamily: "'Azeret Mono', monospace" }}
    >
      {review.date}
    </p>
  </div>
);

const EmptyReviews = ({ onWriteReview }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    className="aeth-card p-12 text-center"
    data-testid="reviews-empty-state"
  >
    <div
      className="w-16 h-16 mx-auto mb-5 rounded-full flex items-center justify-center"
      style={{
        backgroundColor: 'var(--aeth-iron-2)',
        border: '2px solid var(--aeth-iron)',
      }}
    >
      <MessageSquarePlus size={28} style={{ color: 'var(--aeth-gold)' }} />
    </div>
    <h3
      className="text-lg font-semibold mb-2"
      style={{
        color: 'var(--aeth-parchment)',
        fontFamily: "'Cinzel', serif",
      }}
    >
      Noch keine Erfahrungsberichte
    </h3>
    <p
      className="text-sm max-w-md mx-auto mb-6"
      style={{
        color: 'var(--aeth-parchment-dim)',
        fontFamily: "'IBM Plex Sans', sans-serif",
      }}
    >
      Sei der Erste, der seine Erfahrungen mit dem Reich teilt!
    </p>
    {onWriteReview && (
      <button
        onClick={onWriteReview}
        className="btn-gold px-6 py-2.5 rounded-lg text-sm font-semibold"
        data-testid="write-first-review-btn"
      >
        Ersten Bericht verfassen
      </button>
    )}
  </motion.div>
);

const WriteReviewForm = ({ onClose, onSubmitSuccess }) => {
  const { user } = useAuth();
  const [rating, setRating] = useState(5);
  const [text, setText] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (text.trim().length < 10) {
      toast.error('Dein Bericht muss mindestens 10 Zeichen lang sein', {
        style: { backgroundColor: 'rgba(142,29,44,0.9)', border: '1px solid rgba(142,29,44,0.6)', color: '#fff' },
      });
      return;
    }

    setSubmitting(true);
    try {
      const res = await axios.post(`${API}/reviews`, { rating, text });
      toast.success(res.data.message || 'Dein Erfahrungsbericht wurde eingetragen!', {
        duration: 5000,
        icon: '✦',
      });
      onSubmitSuccess();
      onClose();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Fehler beim Einreichen des Berichts';
      toast.error(msg, {
        style: { backgroundColor: 'rgba(142,29,44,0.9)', border: '1px solid rgba(142,29,44,0.6)', color: '#fff' },
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="aeth-card p-6 mb-8"
      data-testid="write-review-form"
    >
      <div className="flex items-center justify-between mb-5">
        <h3
          className="text-lg font-semibold"
          style={{ color: 'var(--aeth-parchment)', fontFamily: "'Cinzel', serif" }}
        >
          Teile deine Erfahrung
        </h3>
        <button
          onClick={onClose}
          className="text-sm"
          style={{ color: 'var(--aeth-parchment-dim)' }}
          data-testid="close-review-form-btn"
        >
          Abbrechen
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Rating selector */}
        <div>
          <label
            className="block text-sm mb-2 font-semibold"
            style={{ color: 'var(--aeth-parchment)', fontFamily: "'IBM Plex Sans', sans-serif" }}
          >
            Bewertung
          </label>
          <div className="flex gap-2">
            {[1, 2, 3, 4, 5].map((r) => (
              <button
                key={r}
                type="button"
                onClick={() => setRating(r)}
                className="text-2xl transition-all"
                style={{
                  color: r <= rating ? '#D6A24D' : '#3B3532',
                  textShadow: r <= rating ? '0 0 8px rgba(214,162,77,0.5)' : 'none',
                }}
                data-testid={`rating-star-${r}`}
              >
                ★
              </button>
            ))}
          </div>
        </div>

        {/* Text area */}
        <div>
          <label
            className="block text-sm mb-2 font-semibold"
            style={{ color: 'var(--aeth-parchment)', fontFamily: "'IBM Plex Sans', sans-serif" }}
          >
            Dein Erfahrungsbericht
          </label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Teile deine Erlebnisse im Reich von Aethoria..."
            rows={5}
            className="w-full px-4 py-3 rounded-lg text-sm"
            style={{
              backgroundColor: 'var(--aeth-stone-1)',
              border: '1px solid var(--aeth-iron)',
              color: 'var(--aeth-parchment)',
              fontFamily: "'IBM Plex Sans', sans-serif",
              resize: 'vertical',
            }}
            data-testid="review-text-input"
          />
          <p
            className="text-xs mt-1"
            style={{ color: 'var(--aeth-parchment-dim)' }}
          >
            Mindestens 10 Zeichen
          </p>
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={submitting || text.trim().length < 10}
          className="btn-gold w-full py-3 rounded-lg text-sm font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          data-testid="submit-review-btn"
        >
          {submitting ? 'Wird eingereicht...' : 'Bericht einreichen'}
        </button>
      </form>
    </motion.div>
  );
};

export const ReviewsSection = ({ reviews = [], onReviewSubmitted }) => {
  const { user } = useAuth();
  const [page, setPage] = useState(0);
  const [showForm, setShowForm] = useState(false);
  const perPage = 3;
  const totalPages = Math.ceil(reviews.length / perPage);
  const current = reviews.slice(page * perPage, (page + 1) * perPage);

  const hasUserReviewed = reviews.some(r => r.author === user?.username);

  const handleWriteReview = () => {
    if (!user) {
      toast.error('Bitte melde dich an, um einen Bericht zu verfassen', {
        style: { backgroundColor: 'rgba(142,29,44,0.9)', border: '1px solid rgba(142,29,44,0.6)', color: '#fff' },
      });
      return;
    }
    setShowForm(true);
  };

  const handleSubmitSuccess = () => {
    setShowForm(false);
    if (onReviewSubmitted) {
      onReviewSubmitted();
    }
  };

  return (
    <section
      data-testid="testimonials-section"
      className="aeth-section"
      style={{ backgroundColor: 'var(--aeth-stone-0)' }}
    >
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <div className="aeth-divider mb-8">
            <span style={{ color: 'var(--aeth-gold)', fontSize: '1.2rem' }}>★</span>
          </div>
          <h2
            className="font-cinzel mb-3"
            style={{
              fontFamily: "'Cinzel', serif",
              fontSize: '2rem',
              fontWeight: 700,
              color: 'var(--aeth-parchment)',
              letterSpacing: '0.04em',
            }}
          >
            Erfahrungsberichte aus dem Reich
          </h2>
          <p style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
            Worte von Abenteurern, die durch diese dunklen Lande gewandert sind
          </p>
        </motion.div>

        {/* Write Review Button (if logged in and hasn't reviewed yet) */}
        {user && !hasUserReviewed && !showForm && reviews.length > 0 && (
          <div className="flex justify-center mb-8">
            <button
              onClick={handleWriteReview}
              className="btn-gold px-6 py-2.5 rounded-lg text-sm font-semibold flex items-center gap-2"
              data-testid="write-review-btn"
            >
              <MessageSquarePlus size={16} />
              Eigenen Bericht verfassen
            </button>
          </div>
        )}

        {/* Write Review Form */}
        {showForm && (
          <WriteReviewForm
            onClose={() => setShowForm(false)}
            onSubmitSuccess={handleSubmitSuccess}
          />
        )}

        {/* Empty State */}
        {reviews.length === 0 && !showForm ? (
          <EmptyReviews onWriteReview={user ? handleWriteReview : null} />
        ) : reviews.length === 0 && showForm ? (
          <WriteReviewForm
            onClose={() => setShowForm(false)}
            onSubmitSuccess={handleSubmitSuccess}
          />
        ) : (
          <>
            {/* Reviews Grid */}
            <div data-testid="testimonials-carousel" className="grid grid-cols-1 md:grid-cols-3 gap-5">
              {current.map((r, i) => (
                <motion.div
                  key={r.id || i}
                  initial={{ opacity: 0, y: 16 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                >
                  <ReviewCard review={r} />
                </motion.div>
              ))}
            </div>

            {/* Navigation */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-6 mt-8">
                <button
                  onClick={() => setPage((p) => Math.max(0, p - 1))}
                  disabled={page === 0}
                  className="btn-iron p-2 rounded-lg disabled:opacity-40"
                  aria-label="Previous reviews"
                  data-testid="reviews-prev-btn"
                >
                  <ChevronLeft size={18} />
                </button>
                <div className="flex gap-2">
                  {Array.from({ length: totalPages }).map((_, i) => (
                    <button
                      key={i}
                      onClick={() => setPage(i)}
                      className="w-2 h-2 rounded-full"
                      style={{
                        backgroundColor: i === page ? 'var(--aeth-gold)' : 'var(--aeth-iron)',
                        transition: 'background-color 0.2s ease',
                      }}
                      data-testid={`review-page-${i}`}
                    />
                  ))}
                </div>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                  disabled={page === totalPages - 1}
                  className="btn-iron p-2 rounded-lg disabled:opacity-40"
                  aria-label="Next reviews"
                  data-testid="reviews-next-btn"
                >
                  <ChevronRight size={18} />
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </section>
  );
};

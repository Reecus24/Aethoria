import { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight } from 'lucide-react';

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

export const ReviewsSection = ({ reviews = [] }) => {
  const [page, setPage] = useState(0);
  const perPage = 3;
  const totalPages = Math.ceil(reviews.length / perPage);
  const current = reviews.slice(page * perPage, (page + 1) * perPage);

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
            Testimonials from the Realm
          </h2>
          <p style={{ color: 'var(--aeth-parchment-dim)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
            Words from adventurers who have walked these dark lands
          </p>
        </motion.div>

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
                />
              ))}
            </div>
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page === totalPages - 1}
              className="btn-iron p-2 rounded-lg disabled:opacity-40"
              aria-label="Next reviews"
            >
              <ChevronRight size={18} />
            </button>
          </div>
        )}
      </div>
    </section>
  );
};

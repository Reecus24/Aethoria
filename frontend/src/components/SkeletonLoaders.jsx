// Skeleton loader components for all sections
import { Skeleton } from './ui/skeleton';

const SkeletonCard = () => (
  <div
    className="aeth-card p-5 flex flex-col gap-3"
    style={{ height: 120 }}
  >
    <div className="flex items-start gap-3">
      <Skeleton className="w-12 h-12 rounded-full flex-shrink-0" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
      <Skeleton className="h-4 w-32 mt-1" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
    </div>
    <Skeleton className="h-3 w-full" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
    <Skeleton className="h-3 w-2/3" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
  </div>
);

export const FeaturesSkeletonSection = () => (
  <section className="aeth-section" style={{ backgroundColor: 'var(--aeth-stone-0)' }}>
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <Skeleton className="h-8 w-64 mx-auto mb-3" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
        <Skeleton className="h-4 w-48 mx-auto" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 9 }).map((_, i) => <SkeletonCard key={i} />)}
      </div>
    </div>
  </section>
);

export const LeaderboardSkeleton = () => (
  <section className="aeth-section" style={{ backgroundColor: 'var(--aeth-stone-1)' }}>
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <Skeleton className="h-8 w-56 mx-auto mb-3" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
        <Skeleton className="h-4 w-44 mx-auto" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
      </div>
      <div className="aeth-card overflow-hidden">
        {Array.from({ length: 10 }).map((_, i) => (
          <div key={i} className="flex gap-4 px-4 py-3 border-b" style={{ borderColor: 'var(--aeth-iron)' }}>
            <Skeleton className="w-8 h-5" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
            <Skeleton className="w-32 h-5" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
            <Skeleton className="w-24 h-5" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
            <Skeleton className="w-12 h-5 ml-auto" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
          </div>
        ))}
      </div>
    </div>
  </section>
);

export const ReviewsSkeleton = () => (
  <section className="aeth-section" style={{ backgroundColor: 'var(--aeth-stone-0)' }}>
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <Skeleton className="h-8 w-64 mx-auto mb-3" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="aeth-card p-6 flex flex-col gap-4">
            <div className="flex items-center gap-3">
              <Skeleton className="w-10 h-10 rounded-full" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
              <div className="flex flex-col gap-1 flex-1">
                <Skeleton className="w-24 h-4" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
                <Skeleton className="w-20 h-3" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
              </div>
            </div>
            <Skeleton className="h-3 w-full" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
            <Skeleton className="h-3 w-full" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
            <Skeleton className="h-3 w-2/3" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
          </div>
        ))}
      </div>
    </div>
  </section>
);

export const NewsSkeleton = () => (
  <section className="aeth-section" style={{ backgroundColor: 'var(--aeth-stone-0)' }}>
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <Skeleton className="h-8 w-56 mx-auto mb-3" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="aeth-card p-8 flex flex-col gap-4">
          <Skeleton className="h-5 w-32" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
          <Skeleton className="h-7 w-full" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
          <Skeleton className="h-7 w-4/5" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
          <Skeleton className="h-10 w-40 mt-4" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
        </div>
        <div className="flex flex-col gap-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="aeth-card p-4 flex gap-4">
              <Skeleton className="w-8 h-8 rounded" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
              <div className="flex flex-col gap-2 flex-1">
                <Skeleton className="h-4 w-full" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
                <Skeleton className="h-3 w-24" style={{ backgroundColor: 'var(--aeth-iron-2)' }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  </section>
);

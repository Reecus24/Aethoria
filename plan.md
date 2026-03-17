# plan.md

## Objectives
- Build a medieval dark-fantasy landing page inspired by torn.com, rebranded as **Realm of Aethoria**.
- Deliver a polished V1 UI + backend that serves dynamic content for: **ticker events, online counters, 42 features, leaderboard, reviews, paths, and news**.
- Provide production-style authentication and session handling:
  - **JWT authentication** (FastAPI + PyJWT)
  - **Persistent sessions** (localStorage + auto-restore on reload)
  - **Protected profile endpoint** (`/api/me`) and explicit logout.
- Extend user accounts into “characters”:
  - **path_choice** (Knight / Shadow / Noble)
  - character stats (**strength / dexterity / speed / defense / gold / xp / level / title / days_in_realm**).
- Add premium, game-like landing experiences:
  - “**Venture into the Realm**” simulated text-game preview (console/terminal)
  - “**11 Kingdoms World Map**” section (atmospheric images + click-to-open details)
  - Character dashboard panel (slide-in) for logged-in users
  - Back-to-top floating button
- Ensure the site remains responsive, fast, accessible, and visually consistent (stone/iron UI, gold accents, fantasy typography).

**Current status (as of this update):**
- ✅ Phase 1 complete (data-flow POC verified)
- ✅ Phase 2 complete (full backend + full landing page UI implemented)
- ✅ Phase 3 complete (UX polish + content enhancements shipped)
- ✅ **Phase 4 complete** (JWT auth + character identity layer + immersive sections shipped)
- ✅ Phase 4 regression fixes applied:
  - ✅ **JWT persistence improved**: tokens only cleared on explicit `401` (not on network errors)
  - ✅ **Ticker shows immediately**: placeholder ticker events render before API payload arrives

---

## Implementation Steps

### Phase 1: Core Data Flow POC (Isolation) — ✅ Completed
Goal: prove the core workflow works end-to-end **before** building full UI.
- Defined core workflow: **React loads → calls FastAPI → receives structured JSON payload → renders**.
- Implemented FastAPI + MongoDB seed-on-startup and verified data integrity.
- Implemented aggregated endpoint:
  - ✅ `GET /api/landing`
- Implemented split endpoints:
  - ✅ `GET /api/ticker`, `GET /api/leaderboard`, `GET /api/reviews`, `GET /api/news`, `GET /api/features`, `GET /api/paths`, `GET /api/stats/online`
- Verified via curl-based POC check:
  - ✅ Payload returns expected counts: ticker (15), features (42), leaderboard (10), reviews (8), news (8), paths (3)

**Phase 1 user stories — ✅ Completed**
1. Visitor sees dynamic content from server so the world feels alive.
2. Visitor sees recent realm events (dungeon/combat/quests).
3. Visitor sees online counts.
4. Visitor sees consistent leaderboard data.
5. Developer has a single aggregated endpoint for minimal network calls.

---

### Phase 2: V1 App Development (UI + Backend) — ✅ Completed
Goal: build the full landing page MVP around the proven data flow.

**Backend (FastAPI + MongoDB) — ✅ Completed**
- Seeded and served full V1 scope:
  - ✅ **42 medieval-adapted features**
  - ✅ Path content for **The Knight / The Shadow / The Noble**
  - ✅ Online counters: `now`, `last_hour`, `last_24h` (light randomized MVP)
  - ✅ Ticker events themed to the Realm
- Implemented MVP auth endpoints:
  - ✅ `POST /api/auth/register` (bcrypt hash, unique email/username validation)
  - ✅ `POST /api/auth/login` (password verification; returns success + basic user info)

**Frontend (React) — ✅ Completed**
- Implemented the full single-page landing page with medieval fantasy aesthetic:
  1. ✅ Realm event ticker (marquee)
  2. ✅ Nav bar with Login/Join
  3. ✅ Hero section with cinematic styling + CTAs
  4. ✅ Online counters widget
  5. ✅ Features section (42 features) with pagination
  6. ✅ Leaderboard table (Hall of Legends)
  7. ✅ Reviews/testimonials section with pagination
  8. ✅ “Which Path Will You Take?” section with 3 immersive tabs
  9. ✅ Royal Chronicles (news) with featured item + list
  10. ✅ Footer with final CTA + links
- Implemented modals:
  - ✅ Login modal (email + password)
  - ✅ Register modal (username + email + password)
  - ✅ Toast notifications using Sonner
  - ✅ Accessibility improvements: `DialogDescription`

**Testing (end of Phase 2) — ✅ Completed**
- ✅ E2E + integration testing completed (testing_agent_v3)
- ✅ Backend: **100% pass rate**
- ✅ Frontend: **95% pass rate**

**Phase 2 user stories — ✅ Completed**
1. Visitor understands the game via About section.
2. Visitor can browse all 42 features.
3. Visitor can explore Knight/Shadow/Noble paths.
4. Visitor can view Hall of Legends leaderboard.
5. Visitor can register/login quickly via modals.

---

### Phase 3: UX/Polish + Content Enhancement — ✅ Completed
Goal: make V1 feel premium, responsive, and “alive”, without expanding scope into full gameplay.

**Polish delivered — ✅ Completed**
- Ticker realism improvements:
  - ✅ Colored category badges (Crime/Combat/Guild/Quest/Dungeon/etc.)
  - ✅ Live pulse indicator
  - ✅ Improved marquee continuity
- Navigation + mobile UX:
  - ✅ Sticky navbar with blur/opacity on scroll
  - ✅ Mobile hamburger menu + mobile auth buttons
  - ✅ Anchor links + `scroll-margin-top`
- Loading + perceived performance:
  - ✅ Skeleton loaders for Features/Leaderboard/Reviews/News
- Visual premium upgrades:
  - ✅ Ember particle atmosphere canvas in hero
  - ✅ Rune glow hover effects on feature cards
  - ✅ Enhanced About section (mini stats grid + richer oath cards + quote)
  - ✅ Numbered feature pagination (1–5) + “Showing X–Y” indicator
  - ✅ Leaderboard visual enhancements
  - ✅ Testimonials star ratings: brighter gold + glow
- Feedback + error clarity:
  - ✅ Improved toast visibility (top-center, higher contrast)
  - ✅ More prominent auth error messages
- Accessibility + motion:
  - ✅ Focus-visible ring styling
  - ✅ Reduced-motion overrides
  - ✅ Modal a11y

**Testing (end of Phase 3) — ✅ Completed**
- ✅ Regression + UX checks with testing_agent_v3
- ✅ Backend: **100%**
- ✅ Frontend: **95%+** with all critical journeys passing

**Phase 3 user stories — ✅ Completed**
1. Visitor sees loading states for faster perceived performance.
2. Visitor experiences a richer, more “live” ticker.
3. Visitor has a great experience on mobile.
4. Visitor receives clearer feedback.
5. Visitor experiences premium visuals.

---

### Phase 4: Auth Hardening + Character Profile + Immersive Sections — ✅ Completed
Goal: upgrade MVP auth into production-style sessions and introduce a lightweight “character identity” layer, plus add immersive landing sections.

#### Phase 4A — Backend: JWT + Character Model — ✅ Completed
- Added JWT capability using **PyJWT**.
- Extended user schema in MongoDB:
  - ✅ `path_choice`: one of `knight | shadow | noble`
  - ✅ character stats: `strength, dexterity, speed, defense, gold, xp, level, title, created_at`
  - ✅ computed `days_in_realm` in profile response
- Auth endpoints:
  - ✅ Updated `POST /api/auth/register` to accept `path_choice` and seed stats by path
  - ✅ Updated `POST /api/auth/login` to return JWT token + user profile snapshot
  - ✅ Added `POST /api/auth/logout` (stateless JWT: client-side invalidation)
  - ✅ Added `GET /api/me` protected endpoint (requires `Authorization: Bearer <token>`)
- Token handling:
  - ✅ Token expiration configured (7 days)
  - ✅ Password hashing remains bcrypt
- Expanded landing payload:
  - ✅ Added `kingdoms` to `GET /api/landing`
  - ✅ Added `GET /api/kingdoms`

#### Phase 4B — Frontend: Persistent Auth + Register Step 2 — ✅ Completed
- Added `AuthProvider` / context:
  - ✅ Stores token in `localStorage` (`aeth_token`)
  - ✅ Auto-restores session on reload via `/api/me`
  - ✅ Axios interceptor attaches bearer token
- Register modal upgraded to 2-step:
  1. ✅ Username/email/password
  2. ✅ Path selection (Knight/Shadow/Noble) with rich cards + mini-stats
- Login modal:
  - ✅ On success: persists token + updates user state
- Logout:
  - ✅ Clears token + user state

#### Phase 4C — Character Dashboard Panel (Slide-in) — ✅ Completed
- Added right-side slide-in panel for logged-in users:
  - ✅ Username, title, level, days in realm
  - ✅ Path badge (Knight/Shadow/Noble)
  - ✅ Stat bars (strength/dexterity/speed/defense)
  - ✅ Gold + XP indicators
- Entry points:
  - ✅ Username button in navbar opens the dashboard

#### Phase 4D — New Landing Content Sections — ✅ Completed
1. ✅ **Venture into the Realm** (Text Game Preview)
   - Terminal/console UI that animates sample actions and outcomes
   - Rotating scenes for Knight/Shadow/Noble
2. ✅ **11 Kingdoms World Map**
   - Responsive grid of 11 kingdoms (images, type badge, danger badge)
   - Click opens a details modal (lore + travel details)

#### Phase 4E — Utility Additions — ✅ Completed
- ✅ Back-to-top floating button
  - Appears after scroll threshold
  - Smooth scroll to top
  - Respects reduced motion

#### Phase 4F — Phase 4 Regression Fixes — ✅ Completed
- ✅ **JWT persistence hardening**: tokens are only cleared on explicit `401` (invalid/expired), not on network errors.
- ✅ **Ticker UX**: ticker now shows immediately using placeholder events until landing payload arrives.

**Phase 4 user stories — ✅ Completed**
1. User stays logged in across refreshes (persistent JWT sessions).
2. User sessions are secure (JWT + expiry).
3. User chooses a path at registration and gets path-based starter stats.
4. User can view a character dashboard at any time.
5. Visitor can experience “how the game feels” via a simulated text-console preview.
6. Visitor can explore the 11-kingdom world map section.

**Testing (end of Phase 4) — ✅ Completed**
- ✅ Backend verification:
  - Register seeds path stats correctly
  - Login returns valid JWT
  - `/api/me` enforces authentication
- ✅ Frontend verification:
  - Register 2-step flow works end-to-end
  - Session persists across reload (with improved error handling)
  - Dashboard opens/closes and shows correct stats
  - Kingdom modal opens from card click
  - Ticker visible immediately

---

### Phase 5: Real Dynamic Data Conversion — ✅ COMPLETED
Goal: Convert all placeholder/mock data to real, dynamic data based on actual user activity.

**Backend Changes — ✅ Completed**
- ✅ Added `last_seen` timestamp tracking on login and `/api/me` calls
- ✅ Implemented real-time online counter calculation (15min/1hour/24hour windows)
- ✅ Created `events` collection with real event logging for registration/login
- ✅ Implemented `log_event()` function with event templates and rotation (max 100 events)
- ✅ Updated `/api/landing` to return real leaderboard (sorted by level/xp from users collection)
- ✅ Updated `/api/landing` to return real ticker events (from events collection)
- ✅ Updated `/api/landing` to return real online stats (calculated from last_seen)
- ✅ Implemented `POST /api/reviews` endpoint for user-submitted reviews
- ✅ Added review validation: min 10 chars, rating 1-5, one review per user
- ✅ Cleaned database: removed all mock reviews/leaderboard entries
- ✅ Updated news/patch notes with real computed dates (relative to current date)

**Frontend Changes — ✅ Completed**
- ✅ Implemented empty state for `LeaderboardSection` when no users registered
- ✅ Implemented empty state for `ReviewsSection` when no reviews submitted
- ✅ Implemented empty state for `EventTicker` when no events logged
- ✅ Added "Write Review" button for logged-in users who haven't reviewed yet
- ✅ Created `WriteReviewForm` component with:
  - Interactive 5-star rating selector
  - Text area with validation (min 10 chars)
  - Integrated submission with toast feedback
  - Auto-refresh reviews after submission
- ✅ German localization for all new UI elements

**Testing (Phase 5) — ✅ Completed**
- ✅ Backend verification: All endpoints return real data correctly
- ✅ Duplicate review prevention works correctly (returns 400 on duplicate)
- ✅ E2E testing with testing_agent_v3: 95% backend / 90% frontend pass rate
- ✅ Visual verification via screenshots: All sections display correctly

**Phase 5 User Stories — ✅ Completed**
1. Visitor sees real leaderboard that updates as users register (not mock data)
2. Visitor sees real event ticker showing actual registration/login activity
3. Visitor sees accurate online player count based on recent activity
4. Logged-in users can submit their own reviews with star ratings
5. Users cannot submit duplicate reviews (one per user)
6. Empty states guide new visitors when no data exists yet
7. All dates (reviews, news) are dynamically computed and real

**Key Achievement:** The application now feels like a **living, breathing world** where every piece of data reflects real user activity, fulfilling the user's explicit request to eliminate all placeholder content.


## Next Actions
### Phase 5 (Optional) — If requested
- Gameplay-adjacent demo features (still landing-safe):
  - Mini “quest generator” demo endpoint + UI
  - Search/filter for features and kingdoms
  - Newsletter/Waitlist signup flow
  - A “Join a Guild” marketing funnel section
- Auth hardening (beyond MVP):
  - Refresh tokens
  - Server-side token revocation/blacklist
  - Rate limiting / brute force protections
- SEO + performance:
  - Metadata and OpenGraph improvements
  - Lighthouse performance pass

---

## Success Criteria
- ✅ Landing page matches torn.com information architecture while delivering cohesive medieval fantasy aesthetic.
- ✅ `/api/landing` returns complete, validated content; frontend renders all sections.
- ✅ Features list contains **42 medieval-adapted entries** and is browsable.
- ✅ Leaderboard, reviews, and news display correctly with interactions.
- ✅ UX polish delivered: skeleton loaders, mobile hamburger nav, animated counters, improved ticker badges, hero particles.
- ✅ Phase 4 success achieved:
  - ✅ JWT login persists across reload
  - ✅ `/api/me` provides protected user snapshot
  - ✅ Registration includes path selection and seeds character stats
  - ✅ Character dashboard panel renders stats cleanly
  - ✅ Back-to-top works
  - ✅ Game preview console ships and rotates scenes
  - ✅ 11-kingdom map section ships with modal details
  - ✅ Ticker shows immediately (placeholder → real data)

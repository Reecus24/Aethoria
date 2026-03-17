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
  - character stats (**strength / dexterity / speed / defense / gold / xp / level / title / days**).
- Add premium, game-like landing experiences:
  - “**Venture into the Realm**” simulated text-game preview (console/terminal)
  - “**11 Kingdoms World Map**” section (atmospheric images)
  - Character dashboard panel (slide-in) for logged-in users
  - Back-to-top floating button
- Ensure the site remains responsive, fast, accessible, and visually consistent (stone/iron UI, gold accents, fantasy typography).

**Current status (as of this update):**
- ✅ Phase 1 complete (data-flow POC verified)
- ✅ Phase 2 complete (full backend + full landing page UI implemented)
- ✅ Phase 3 complete (UX polish + content enhancements shipped)
- ✅ Testing complete through Phase 3: **Backend 100%**, **Frontend 95%+** (all critical paths pass)
- 🟡 Phase 4 approved (Auth hardening + character profile + new immersive sections) — **Not started**

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

### Phase 4: Auth Hardening + Character Profile + Immersive Sections — 🟡 Approved / Not Started
Goal: upgrade MVP auth into production-style sessions and introduce a lightweight “character identity” layer, plus add two immersive landing sections.

#### Phase 4A — Backend: JWT + Character Model
- Add dependencies:
  - `PyJWT` for signing/verifying access tokens
  - optional: `python-jose` alternative (choose one)
- Extend user schema in MongoDB:
  - `path_choice`: one of `knight | shadow | noble`
  - character stats: `strength, dexterity, speed, defense, gold, xp, level, title, created_at, days`
- Auth endpoints:
  - Update `POST /api/auth/register` to accept `path_choice` and seed stats by path
  - Update `POST /api/auth/login` to return JWT token + user snapshot
  - Add `POST /api/auth/logout` (client-side token invalidation; optional server blacklist)
  - Add `GET /api/me` protected endpoint (requires `Authorization: Bearer <token>`)
- Security basics:
  - Token expiration (e.g., 7 days)
  - Password hashing stays bcrypt
  - Rate-limiting placeholder or basic throttling (optional MVP)

#### Phase 4B — Frontend: Persistent Auth + Register Step 2
- Add Auth context/provider:
  - Store token in `localStorage`
  - Auto-restore session on reload (`/api/me` bootstrap)
  - Axios interceptor to attach bearer token
- Register modal becomes 2-step:
  1. Username/email/password
  2. Path selection (Knight/Shadow/Noble) with rich cards matching Paths section
- Login modal:
  - On success: persist token and load `/api/me`
- Add explicit logout (clear token, clear user state)

#### Phase 4C — Character Dashboard Panel (Slide-in)
- Add a right-side slide-in panel for logged-in users:
  - Username, title, level, days in realm
  - Path badge (Knight/Shadow/Noble)
  - Stat bars for strength/dexterity/speed/defense
  - Gold + XP indicators
- Entry points:
  - “Character” button in navbar when logged in
  - Optional: show mini badge in user banner to open panel

#### Phase 4D — New Landing Content Sections
1. **Venture into the Realm** (Text Game Preview)
   - Terminal/console UI that types/rotates sample actions:
     - “Train at the Barracks”, “Commit a Dark Deed”, “Join a Guild War”, “Trade on the Exchange”, etc.
   - Show outcomes and rewards (gold/xp/items) as simulated content (no gameplay backend required).

2. **11 Kingdoms World Map**
   - Grid/map section with 11 kingdoms:
     - Atmospheric images, kingdom names, 1-line flavor text
   - Optional interactions:
     - Hover to reveal details
     - Click opens a modal with lore + sample loot

#### Phase 4E — Utility Additions
- Back-to-top floating button:
  - Appears after scroll threshold
  - Smooth scroll to hero
  - Respects reduced motion

**Phase 4 user stories (updated)**
1. User stays logged in across refreshes.
2. User sessions are secure (JWT + expiry).
3. User chooses a path at registration and gets path-based starter stats.
4. User can view a character dashboard at any time.
5. Visitor can experience “how the game feels” via a simulated text-console preview.
6. Visitor can explore the 11-kingdom world map section.

**Phase 4 Testing Plan**
- Backend:
  - Register with path_choice seeds stats correctly
  - Login returns valid JWT
  - `/api/me` rejects missing/invalid token and accepts valid token
  - Logout clears client session (and blacklist if implemented)
- Frontend:
  - Register 2-step flow works and persists token
  - Refresh restores session (calls `/api/me`)
  - Dashboard opens, renders stats, closes
  - Back-to-top appears and works
  - Game preview section animates and is accessible
  - World map section responsive + hover/click works

---

## Next Actions
1. Implement Phase 4A backend JWT + `/api/me`.
2. Implement Phase 4B persistent auth + register step 2.
3. Implement Phase 4C character dashboard panel.
4. Implement Phase 4D immersive sections (Game Preview + 11 Kingdoms).
5. Implement Phase 4E back-to-top.
6. Run full regression with testing_agent_v3.

---

## Success Criteria
- ✅ Landing page matches torn.com information architecture while delivering cohesive medieval fantasy aesthetic.
- ✅ `/api/landing` returns complete, validated content; frontend renders all sections.
- ✅ Features list contains **42 medieval-adapted entries** and is browsable.
- ✅ Leaderboard, reviews, and news display correctly with interactions.
- ✅ UX polish delivered: skeleton loaders, mobile hamburger nav, animated counters, improved ticker badges, hero particles.
- 🟡 Phase 4 success (new):
  - JWT login persists across reload
  - `/api/me` provides protected user snapshot
  - Registration includes path selection and seeds character stats
  - Character dashboard panel renders stats cleanly
  - Back-to-top works
  - Game preview console and 11-kingdom map sections ship and are responsive

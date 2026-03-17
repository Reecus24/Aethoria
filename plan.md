# plan.md

## Objectives
- Build a medieval dark-fantasy **torn.com-inspired browser RPG** rebranded as **Realm of Aethoria**.
- Preserve the existing landing page as the public entrypoint (marketing + onboarding).
- Provide a full game experience after login:
  - Logged-out users stay on landing (`/`).
  - Logged-in users are routed into the **Game Shell** at `/game/*`.
- Deliver real/dynamic data only (no fake players, no inflated marketing claims).
- Provide production-style authentication and session handling:
  - **JWT authentication** (FastAPI + PyJWT)
  - **Persistent sessions** (localStorage + auto-restore on reload)
  - **Protected profile endpoint** (`/api/me`) and explicit logout.
- Extend user accounts into “characters”:
  - **path_choice** (Knight / Shadow / Noble)
  - character stats (**strength / dexterity / speed / defense / gold / xp / level / title / days_in_realm**)
- Implement the “introduced” features from the landing page as **playable systems**, targeting the full **42 features** set.
- Ensure consistent premium UI across landing + game: stone/iron UI, gold accents, fantasy typography, dense data tables, fast navigation.
- Make the game **smoothly playable** by hardening onboarding/auth UX and tuning the **energy/time economy** so early/mid-game loops are fun and not dominated by waiting.
- **Production hardening objective (Phase 8):** improve reliability and anti-abuse posture:
  - Rate limiting for high-frequency endpoints
  - Idempotency for money-moving operations
  - Economy observability (structured logs)
  - Comprehensive E2E verification
- **World “liveness” objective (Phase 8 add-on):** keep the realm visibly active for new visitors without breaking integrity:
  - Readable, non-distracting event ticker speed
  - Optional AI/bot players that **follow the same rules** (energy, level gates, timers)

**Current status (updated):**
- ✅ Phase 1 complete (data-flow POC verified)
- ✅ Phase 2 complete (landing UI + backend implemented)
- ✅ Phase 3 complete (UX polish + content enhancements shipped)
- ✅ Phase 4 complete (JWT auth + character identity layer + immersive sections shipped)
- ✅ Phase 5 complete (all mock data replaced with real, dynamic data)
- ✅ Post-Phase-5 correction: removed false marketing claims and removed filler named ticker events.
- ✅ **Phase 6 complete (MEGA-BUILD): full game backend + full game frontend + routing + stability fixes + functional smoke tests**
- ✅ **Phase 7 complete: Login/Register flow hardening + Balancing pass (energy/time economy + rewards)**
- ✅ **Phase 8 complete: Comprehensive E2E testing + security hardening (rate limiting, idempotency) + economy logging + final verification**
- ✅ **Phase 8 add-on complete: Event ticker readability improvements + bot-player scripts for realm activity**

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
- Verified via curl-based POC check.

---

### Phase 2: V1 App Development (UI + Backend) — ✅ Completed
Goal: build the full landing page MVP around the proven data flow.

**Backend — ✅ Completed**
- Seeded and served full V1 scope including 42 feature cards.
- Implemented MVP auth endpoints.

**Frontend — ✅ Completed**
- Implemented full single-page landing page.
- Implemented login/register modals and sonner toasts.

---

### Phase 3: UX/Polish + Content Enhancement — ✅ Completed
Goal: make V1 feel premium, responsive, and “alive”, without expanding scope into full gameplay.
- Ticker realism upgrades, skeleton loaders, hero atmosphere, better pagination, improved toast/error clarity, accessibility.

---

### Phase 4: Auth Hardening + Character Profile + Immersive Sections — ✅ Completed
Goal: upgrade auth into production-style sessions + add character identity layer + immersive landing sections.
- JWT, `/api/me`, persistent sessions.
- 2-step registration with path selection.
- Character dashboard.
- Game preview terminal + 11-kingdom map.

---

### Phase 5: Real Dynamic Data Conversion — ✅ Completed
Goal: remove all placeholder/mock content and make the landing page feel alive through real user activity.

**Backend — ✅ Completed**
- `last_seen` tracking + online counters.
- `events` collection + real event logging.
- `/api/landing` returns real leaderboard + ticker + online stats.
- `POST /api/reviews` with validation + one-review-per-user.
- News/patch notes dates are computed dynamically.

**Frontend — ✅ Completed**
- Empty states for leaderboard/reviews/ticker.
- Review submission UI for logged-in users.

**Post-Phase-5 corrections (content integrity) — ✅ Completed**
- Removed false marketing claims (50k active, 20+ years, community rating, free forever).
- Placeholder ticker events are generic and contain **no fake character names**.

---

## Phase 6: Full Game (torn-like) Implementation — ✅ Completed (MEGA-BUILD)
User request: “mach einfach alles fertig … die 42 Features bitte komplett ausbearbeiten”.

### What is now delivered (end-state)
**Backend — ✅ Completed**
- ✅ Full game backend implemented in monolithic `/app/backend/server.py` (~2800+ lines)
  - All 42 feature systems represented with models + endpoints (prefixed with `/api/game/*`).
- ✅ Backend stability fixes (timezone correctness)
  - Fixed offset-naive vs offset-aware datetime issues impacting:
    - Landing leaderboard (`get_real_leaderboard`) calculations
    - Energy regeneration (`regenerate_energy`) calculations
  - Result: `/api/landing` and `/api/game/state` reliably return 200.

**Frontend — ✅ Completed**
- ✅ Full game frontend implemented (22 game pages) under `/app/frontend/src/pages/`.
- ✅ React Router integration:
  - Landing at `/`
  - Game at `/game/*`
  - Protected routes redirect to `/` when unauthenticated
  - Post-login/register redirect to `/game` works.
- ✅ Auth header hardening:
  - Axios interceptor at `/app/frontend/src/utils/axios.js` automatically attaches JWT Bearer token to all requests.
  - All pages now import this axios wrapper.
- ✅ Runtime stability pass:
  - Fixed optional chaining and state-shape mismatches (`gameState` fields vs assumed `character` field).
  - Fixed React hook naming issue in Inventory (`useItem` → `handleUseItem`).
  - Fixed object rendering issues (location object `{kingdom_id, kingdom_name}` now rendered as a string).
  - Fixed Hospital/Dungeon timers rendering (safe reads of `seconds_remaining`).

**UI/UX — ✅ Completed**
- ✅ UI/UX consistency with design guidelines:
  - Stone/iron palette, gold accents, dense torn-like panels, fantasy typography.

**Testing — ✅ Completed (smoke + targeted functional)**
- ✅ Build/syntax validation with esbuild.
- ✅ Screenshot-based navigation smoke tests across pages.
- ✅ Automated test reports generated: `/app/test_reports/iteration_5.json` and `/app/test_reports/iteration_6.json`.
- ✅ Verified working flows (session highlights):
  - Auth: login/register → redirect to `/game`
  - HUD reflects live values (Gold/Energy/HP/Level)
  - Crimes API success path (commit crime, rewards applied, level-up observed)
  - Bank deposit/withdraw verified via curl
  - Tavern dice verified via curl
  - Character page renders correct identity: e.g. **“The Knight • Level 2 • Aethoria Prime”**
  - Landing event ticker shows real player activity (level ups, crimes, combats)

### Phase 6A: Game Shell + Navigation + Routing (Foundation) — ✅ Completed
**Frontend — ✅ Completed**
- `/game` route with nested pages implemented.
- `GameShell` layout implemented with:
  - left sidebar navigation
  - top HUD with resources
  - outlet-based page rendering
- Implemented/added pages (22):
  - Dashboard, Character, Training, Crimes, Combat, Quests,
  - Inventory, Shop, Market, Bank,
  - Guilds, Tavern, Travel/Map, Hunting,
  - Bounties, Properties,
  - Messages/Mail,
  - Hospital, Dungeon,
  - Achievements/Honours, Gazette.

**Backend — ✅ Completed**
- `/api/game/state` endpoint returns core HUD values.

### Phase 6B–6K: Feature Modules (42 features) — ✅ Completed
- Training loop (timer-based start/claim)
- Crimes + consequences (hospital/jail)
- Combat + logs
- Quests
- Items/inventory/equipment
- Shop
- Market
- Bank
- Guilds
- Tavern dice
- Travel (11 kingdoms) + travel completion
- Hunting (level-gated)
- Bounties
- Properties
- Messages
- Achievements
- Gazette / landing-derived news + leaderboard views

### Phase 6L: Testing + Stability — ✅ Completed
- Screenshot-based navigation testing across key pages
- Build/syntax validation with esbuild
- Functional API spot-checks (crime/bank/tavern)
- Fixed critical backend 500s:
  - `/api/landing` leaderboard datetime crash
  - `/api/game/state` energy regeneration datetime crash

---

## Phase 7: Post-MEGA-BUILD Hardening, E2E Coverage, Balancing — ✅ Completed
Goal: move from “all features exist + verified smoke tests” to “the game is consistently accessible and feels playable”.

### Phase 7A: Auth / Onboarding Flow Hardening — ✅ Completed
**Problem addressed:** intermittent UX issues where registration/login did not reliably transition to `/game`.

**Fix shipped:**
- ✅ Hardened navigation by adding **direct `navigate('/game')` calls inside AuthModals** right after `loginWithData()`.
- ✅ Removed redundant delayed navigations in `LandingPage` success callbacks (kept toasts only).

**Files changed:**
- `/app/frontend/src/components/AuthModals.jsx`
- `/app/frontend/src/pages/LandingPage.jsx`

**Result:**
- ✅ Register → choose path → enter game works reliably.
- ✅ Login → enter game works reliably.

### Phase 7B: Balancing Pass (Energy / Time / Rewards) — ✅ Completed
**Problem addressed:** Energy starvation and long wait-times due to slow regen and high action costs.

**Backend economy changes:**
- ✅ **Energy regen:** `ENERGY_REGEN_PER_HOUR` **10 → 25** (full bar in ~4h instead of 10h)
- ✅ **HP regen:** `HP_REGEN_PER_HOUR` **5 → 10**

**Training changes:**
- ✅ Training energy **10 → 6**
- ✅ Training duration **5 → 3 minutes**
- ✅ Training XP **2 → 3**

**Crime changes (broad tuning):**
- ✅ Energy costs reduced (~25–40%)
- ✅ Rewards increased (~20%)
- ✅ Jail times reduced (~30%)
- ✅ Slight success-rate improvements for early crimes

**Quest changes:**
- ✅ Energy costs reduced (~30%)
- ✅ Rewards increased (~20%)
- ✅ Durations reduced (~25%)

**Hunting changes:**
- ✅ Energy costs reduced (~30–40%)
- ✅ Rewards increased (~20%)

**Combat changes:**
- ✅ Energy per attack **25 → 15**

**Frontend alignment:**
- ✅ Updated Training UI texts and gating to match new values.
- ✅ Updated Combat UI texts and gating to match new values.

**Files changed (key):**
- `/app/backend/server.py`
- `/app/frontend/src/pages/TrainingPage.jsx`
- `/app/frontend/src/pages/CombatPage.jsx`
- Added analysis doc: `/app/balancing_analysis.md`

### Phase 7C: Manual E2E Verification After Balancing — ✅ Completed
- ✅ Performed UI-driven gameplay loop test:
  - Register (multiple paths) → Dashboard
  - Start training → observe timer
  - Commit crime → observe gold/xp change and level-up
- ✅ Verified updated displayed costs (e.g., training shows **6 Energie / 3 Min**, crimes show **3 Energie**, combat shows **15 Energie**).

---

## Phase 8: Production Hardening & Security — ✅ Completed
Goal: move from “playable baseline” to “production-hardened & abuse-resistant”.

### Phase 8A: Deep Automated E2E (all 42 features) — ✅ Completed
- ✅ Ran comprehensive testing suite.
- ✅ Testing Agent report: `/app/test_reports/iteration_7.json`
  - Overall success: **87.8%**
  - Backend: **85.7%**
  - Frontend: **90%**
- ✅ Confirmed core mechanics are functional and balanced:
  - Training (6 energy / 3 min)
  - Crimes (3 energy early)
  - Combat (15 energy)
  - Energy regen (25/hour)

### Phase 8B: Bug Analysis & Validation — ✅ Completed
- ✅ Investigated reported issues:
  - `/api/game/quests/available` response format
  - `/api/game/shop/buy` parameter format
- ✅ Determined both were **not bugs**, but **incorrect test expectations**:
  - Quests endpoint returns structured `{active_quest, available_quests}` (frontend expects this).
  - Shop buy uses query params (frontend uses this).

### Phase 8C: Rate Limiting (Anti-Abuse) — ✅ Completed
Implemented SlowAPI-based rate limiting (in-memory) for critical endpoints:
- ✅ Crimes: **30/minute**
- ✅ Combat: **20/minute**
- ✅ Bank deposit/withdraw: **60/minute**
- ✅ Shop buy: **60/minute**
- ✅ Market buy: **60/minute**
- ✅ Training start: **40/minute**

**Files changed:**
- `/app/backend/server.py` (SlowAPI limiter setup + endpoint decorators)

### Phase 8D: Idempotency Keys for Money Operations — ✅ Completed
Implemented idempotency to prevent double-spending on retries:
- ✅ Bank:
  - `/api/game/bank/deposit` supports `idempotency_key`
  - `/api/game/bank/withdraw` supports `idempotency_key`
- ✅ Market:
  - `/api/game/market/buy` supports `idempotency_key`
- ✅ Added Mongo collection `idempotency_keys` with TTL expiration (24h).
- ✅ Verified via API test: repeated call with same key returns cached result and does not double-charge.

**Files changed:**
- `/app/backend/server.py` (helper functions + request models + endpoint logic)

### Phase 8E: Economy Observability (Structured Logging) — ✅ Completed
Added structured server-side logs for economy-affecting operations:
- ✅ Crimes (gold/xp outcome)
- ✅ Combat (damage, gold stolen, xp)
- ✅ Shop purchases (gold spent)
- ✅ Bank deposits/withdrawals (gold moved)
- ✅ Market purchases (gold + item transfer)

**Files changed:**
- `/app/backend/server.py`

### Phase 8F: Final Verification — ✅ Completed
- ✅ Final UI tour with screenshots across:
  - Dashboard, Training, Crimes, Shop, Character, Achievements
- ✅ Verified the balanced values appear correctly in UI.
- ✅ Confirmed the application is stable after security hardening.

---

## Phase 8 (Add-on): Realm Liveness (Ticker Readability + Bot Players) — ✅ Completed
Goal: keep the landing page feeling alive using **real events**, while ensuring readability and integrity.

### Phase 8G: Event Ticker Readability — ✅ Completed
**Problem addressed:** ticker scrolled too quickly; events were visible for <1–2 seconds.

**Fix shipped:**
- ✅ Slowed marquee animation from **60s → 120s** (2× slower).
- ✅ Maintained pause-on-hover behavior.

**Files changed:**
- `/app/frontend/src/index.css`

**Result:**
- ✅ Events remain readable for ~4–6 seconds.
- ✅ Less visually distracting; better first-impression UX.

### Phase 8H: Bot Players (5 AI Characters) — ✅ Completed
**User request:** remove test characters and optionally run a small bot population that truly plays by the same rules.

**Implementation:**
- ✅ Created bot scripts that:
  - Register/login characters
  - Fetch `/api/game/state`
  - Perform realistic actions (Crimes, Training, Shop, occasional Quests)
  - Respect rules: energy costs, can_act restrictions, level gates
- ✅ Ran bots and verified ticker displays mixed events across multiple players.

**Artifacts:**
- `/app/game_bot_quick.py` (short demo runs)
- `/app/game_bot.py` (persistent bot implementation)

**Note:** “Persistent daemon runner” attempt may depend on environment process management; quick-run script is confirmed to work and populate events.

---

## Data Model (Phase 6 additions) — ✅ Implemented
MongoDB collections now exist/are used (high-level):
- `users` (extended)
- `events`, `reviews`
- `items`, `inventories`, `equipment`
- `training_sessions`
- `quests`, `user_quests`
- `crimes`, `crime_logs`
- `combat_logs`
- `market_listings`, `transactions`
- `bank_accounts`, `bank_investments`
- `guilds`, `guild_members`
- `messages`
- `travel_sessions`
- `hunting_logs`
- `hospital_sessions`
- `dungeon_sessions`
- `bounties`
- `properties`, `user_properties`
- `achievements`, `user_achievements`
- ✅ **Phase 8 addition:** `idempotency_keys` (TTL, 24h)

---

## Success Criteria

### Landing (met)
- ✅ Landing page matches torn-like information architecture with medieval fantasy aesthetic.
- ✅ `/api/landing` returns real, validated content; frontend renders all sections.
- ✅ No fake user names in ticker; no false marketing claims.
- ✅ Landing stability: leaderboard datetime handling fixed.
- ✅ Ticker readability improved (slower marquee).

### Game (met: functional baseline)
- ✅ After login/register, user is routed to `/game`.
- ✅ GameShell provides fast navigation (sidebar) to all modules.
- ✅ All 22 game pages load without runtime crashes.
- ✅ Backend implements endpoints for the full 42-feature set.
- ✅ `/api/game/state` is stable (datetime regen bug fixed).
- ✅ Authenticated requests consistently include JWT (axios interceptor).

### Game (met: playable baseline)
- ✅ Login/register transition to game is reliable (Auth flow hardened).
- ✅ Energy/HP regen and action costs are balanced enough for active play sessions.
- ✅ Training/Crimes/Quests/Hunting/Combat tuned to reduce waiting and improve progression feel.

### Game (met: production hardening)
- ✅ Comprehensive E2E testing completed (iteration_7.json).
- ✅ Rate limiting enabled for critical endpoints.
- ✅ Idempotency implemented for key money-moving operations.
- ✅ Structured economy logging in place for debugging/monitoring.
- ✅ Final verification completed post-hardening.

### Realm Liveness (met)
- ✅ Event ticker scroll speed is readable.
- ✅ Multi-player activity present via bot scripts that follow game rules.

---

## Next Phase (Optional): Phase 9 — ⏳ Future
If desired after Phase 8 completion:
- Refresh tokens + token rotation
- Account lockout / progressive backoff on failed login
- DB-level atomicity improvements (Mongo transactions where applicable)
- WebSockets for real-time chat and event updates
- Admin panel for economy tuning, item management, and moderation
- Full CI pipeline with deterministic E2E suite
- Bot service hardening (run under supervisor/systemd, configurable bot pool size, per-bot backoff strategies)

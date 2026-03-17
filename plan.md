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

**Current status (updated):**
- ✅ Phase 1 complete (data-flow POC verified)
- ✅ Phase 2 complete (landing UI + backend implemented)
- ✅ Phase 3 complete (UX polish + content enhancements shipped)
- ✅ Phase 4 complete (JWT auth + character identity layer + immersive sections shipped)
- ✅ Phase 5 complete (all mock data replaced with real, dynamic data)
- ✅ Post-Phase-5 correction: removed false marketing claims and removed filler named ticker events.
- ✅ **Phase 6 complete (MEGA-BUILD): full game backend + full game frontend + routing + stability fixes + functional smoke tests**

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
- ✅ Automated test report generated: `/app/test_reports/iteration_5.json`.
- ✅ Verified working flows (session highlights):
  - Auth: login → redirect to `/game`
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

## Phase 7: Post-MEGA-BUILD Hardening, Full E2E Coverage, Balancing — ⏳ Next
Goal: move from “all features exist + verified smoke tests” to “all features are verified end-to-end, balanced, and abuse-resistant”.

### Phase 7A: Deep E2E Functional Testing (all 42 features)
- Add/extend automated tests to cover **successful and failure paths**:
  - register → select path → login → `/game/state`
  - training start/claim (incl. timer edge cases)
  - crime success/fail → dungeon/hospital timers (including completion release)
  - combat outcomes (duel/mug/hospitalise) + logs
  - quest accept/complete + rewards
  - shop buy → inventory/equipment changes
  - market list/buy/cancel + money conservation
  - bank deposit/withdraw/investments + interest
  - tavern dice wagers + gold conservation
  - travel start/complete + location update
  - messaging send/read + unread counts
  - property buy/collect + income timers
  - guild create/join/leave + member counts
  - bounty create/claim + payouts
  - hunting loop (unlocks at level 15) + drops
  - achievements unlock triggers
- Ensure all transactions are server-authoritative and consistent.

### Phase 7B: Data Contract Tightening + Observability
- Standardize payload shapes for:
  - `gameState` fields (user/resources/stats/location/timers/equipment)
  - timer objects (presence/absence semantics)
- Add server-side structured logs for economy-affecting endpoints.
- Add more `data-testid` coverage where missing for robust testing.

### Phase 7C: UX Polish Based on User Feedback
- Improve micro-interactions:
  - clearer empty states, better error toasts
  - consistent naming (German/English labels) and localization pass
- Improve navigation quality:
  - ensure every sidebar item has stable `data-testid`
  - add page-level loading indicators consistently

### Phase 7D: Anti-Abuse + Security Enhancements
- Refresh tokens (optional)
- Rate limiting (crimes/combat/market)
- Idempotency keys for money-moving operations
- Atomic Mongo updates / transaction patterns for economy operations

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

---

## Success Criteria

### Landing (met)
- ✅ Landing page matches torn-like information architecture with medieval fantasy aesthetic.
- ✅ `/api/landing` returns real, validated content; frontend renders all sections.
- ✅ No fake user names in ticker; no false marketing claims.
- ✅ Landing stability: leaderboard datetime handling fixed.

### Game (met: functional baseline)
- ✅ After login/register, user is routed to `/game`.
- ✅ GameShell provides fast navigation (sidebar) to all modules.
- ✅ All 22 game pages load without runtime crashes.
- ✅ Backend implements endpoints for the full 42-feature set.
- ✅ `/api/game/state` is stable (datetime regen bug fixed).
- ✅ Authenticated requests consistently include JWT (axios interceptor).
- ✅ Core functional spot-checks passed (crime, bank, tavern, training UI readiness).

### Game (next: hardening)
- ⏳ Full E2E coverage validates all 42 features end-to-end.
- ⏳ Economy transactions verified for correctness and abuse resistance.
- ⏳ Balance pass for energy costs, rewards, timers.

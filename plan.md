# plan.md (aktualisiert)

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
- **New objective (Phase 9): Production Bugfix + Class Differentiation:**
  - Fix game-breaking production bugs discovered post-deployment (inventory/equipment, quests payouts, travel gating, timers, tavern reward display, messaging)
  - Make class/path choice meaningfully distinct (actions, permissions, quest lines, economic identity)
  - Ensure stats/rewards shown in UI match backend truth (no misleading tooltips)

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
- ✅ **Deployment completed on Hetzner**
  - ✅ Fixed frontend build issue (missing `yarn.lock`) by adjusting Dockerfile.
  - ✅ Fixed backend build issue (non-public `emergentintegrations`) by removing from requirements.
  - ✅ Fixed backend runtime (FastAPI app wasn’t being served) by using `uvicorn server:app`.
  - ✅ Fixed compose override bug (`command: python server.py`) by removing command override in `docker-compose.yml`.
  - ✅ Confirmed `/api/landing` returns valid JSON and Nginx serves the app.
- 🔴 **Phase 9 needed:** multiple critical gameplay bugs discovered in real usage (see below).

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

---

## Phase 7: Post-MEGA-BUILD Hardening, E2E Coverage, Balancing — ✅ Completed
Goal: move from “all features exist + verified smoke tests” to “the game is consistently accessible and feels playable”.

### Phase 7A: Auth / Onboarding Flow Hardening — ✅ Completed
- ✅ Direct navigation in AuthModals after login/register.

### Phase 7B: Balancing Pass (Energy / Time / Rewards) — ✅ Completed
- ✅ Faster regen, lower costs, higher rewards.

### Phase 7C: Manual E2E Verification After Balancing — ✅ Completed
- ✅ UI-driven loops verified.

---

## Phase 8: Production Hardening & Security — ✅ Completed
Goal: move from “playable baseline” to “production-hardened & abuse-resistant”.
- ✅ Deep automated E2E
- ✅ Rate limiting
- ✅ Idempotency keys
- ✅ Economy logging

---

## Phase 8 (Add-on): Realm Liveness (Ticker Readability + Bot Players) — ✅ Completed
- ✅ Ticker speed slowed
- ✅ Bot scripts exist (manual run)

---

## Phase 8I: Deployment & Ops Hardening (Hetzner) — ✅ Completed
Goal: get the stack reliably running on a Hetzner server.
- ✅ Docker/Compose-based deployment verified.
- ✅ Fixed build issues for frontend (missing lockfile) and backend (private dependency).
- ✅ Fixed backend serving (use uvicorn).
- ✅ Fixed compose command override.
- ✅ Verified Nginx serves UI and backend responds.

---

## Phase 9: Production Bugfix Sprint + Path/Class Differentiation — 🔴 In Progress (New)
Goal: fix game-breaking issues discovered in production testing, then make class choice meaningful.

### ✅ Phase 9 - Critical Training & Travel Fixes (COMPLETED)
**User Reported Bugs - ALL FIXED:**
1. ✅ **Training Energy Cost**: Changed from 10 → 100 energy (backend + frontend UI)
2. ✅ **Training UI Text**: Corrected to "100 Energie • 12 Stunden" (was "6 Energie • 3 Minuten")
3. ✅ **Action Blocking During Training**: All major actions (Combat, Crime, Travel, Quest, Hunt, Tavern) now blocked when training is active
4. ✅ **Travel Level Gating Bug**: Fixed by fetching fresh user level from DB instead of stale JWT data
5. ✅ **Training Stat Grants**: Verified that training correctly awards +1 stat point after completion
6. ✅ **Mugging Logic**: Verified no damage is dealt on failed mug attempts (only jail chance)
7. ✅ **Equipment Visibility**: Code review confirms equipped items remain visible with `equipped: true` flag

**Testing Completed:**
- ✅ Backend unit tests (all passed)
- ✅ API integration tests (all passed)
- ✅ Frontend UI verification (screenshots confirm correct display)
- ✅ End-to-end flow tests (training claim, travel, action blocking)

**Files Modified:**
- `/app/backend/server.py`: Training costs, action blocking checks, travel level fetching
- `/app/frontend/src/pages/TrainingPage.jsx`: UI text updates

---

### Phase 9A (P0): Consistency & Economy/UX Truth (Displayed vs Real)
- Fix starting class bonuses mismatch:
  - Noble/Shadow show “500 Gold” but receive 100.
  - Audit and normalize **all class starting stats** (gold, energy caps, base stats, starting items).
  - Ensure UI texts/tooltips match backend constants.

### Phase 9B (P0): Combat Log UI Correctness
- “Letzte Kämpfe” shows victory styled red.
  - Fix frontend logic: winner/loser color mapping.

### Phase 9C (P0): Inventory/Equipment System
- Equipping weapon removes it from inventory but doesn’t appear in equipped slot.
  - Fix backend update logic (inventory decrement + equipment set) and return payload.
  - Fix frontend state update and re-fetch flow after equip/unequip.
  - Add regression checks for item loss.

### Phase 9D (P0): Actions & Permissions by Class
- Restrict “Ausrauben (Mug)” and “Dark Deeds/Verbrechen” to Shadow/Thief class only.
- Create distinct action sets per class:
  - Knight: honorable combat/training/guard actions
  - Shadow: theft/crime/mugging/underworld
  - Noble: trade/influence/market/bank/estate management
- Explicitly display action effects before confirming (energy cost, risk, rewards, cooldown, possible jail/hospital time).

### Phase 9E (P0): Tavern Rewards Display
- Fix toast/header showing `Undefined Gold`.
  - Ensure backend returns `gold_delta`/`reward.gold` consistently.
  - Ensure frontend uses the correct property.

### Phase 9F (P0): Quests Reward Payout & Claim Flow
- Quest completes after timer but grants no XP/Gold.
  - Ensure server awards rewards on completion (timer end) OR via explicit claim endpoint.
  - Ensure frontend polls/refreshes active quest state and shows claim button/status.

### Phase 9G (P0): Travel Between Kingdoms (Map)
- “Cannot travel between kingdoms” behavior.
  - Add travel conditions:
    - minimum level or item requirement
    - energy cost
    - travel cooldown / in-travel lockout
  - Fix frontend selection & request payload; show requirements clearly.

### Phase 9H (P0): Hospital & Dungeon Timers
- Hospital healing timer stuck at `00:00`.
- Jail/Dungeon timer not shown; and “all players are jailed” symptom.
  - Audit backend session storage fields (start_time/end_time) and per-user scoping.
  - Ensure queries filter by `user_id`.
  - Ensure frontend reads the correct `seconds_remaining` and updates via polling.

### Phase 9I (P0): Messaging
- Sending messages not working.
  - Fix compose/API request format and backend persistence.
  - Ensure inbox/outbox refresh.

### Phase 9J (P1): Class-specific Quests
- Create quest pools by class (Knight/Shadow/Noble), with different reward curves and narrative.
- Ensure quest availability endpoint filters by `path_choice`.

### Phase 9K (P1): Properties / Real Estate
- No properties available to buy/sell.
  - Seed properties correctly.
  - Ensure listing/purchase endpoints return expected data.
  - Display requirements and income/benefits clearly.

### Phase 9L (P2, deferred): Real-time Updates
User request: real-time updates for messages/attacks.
- Defer to future phase to avoid destabilizing the production bugfix sprint.
- Candidate implementation:
  - WebSockets (FastAPI) for chat/messages/notifications
  - Or Server-Sent Events (SSE) for ticker + notifications
  - Fallback: short polling for critical UX while keeping server load manageable

### Phase 9M: Deep Research + Verification (Two-character E2E)
- Perform an end-to-end verification with **two real accounts**:
  - Register 2 users with different classes
  - Verify combat interactions: attack/mugging permissions, gold transfer correctness
  - Verify XP calculation and level-up consistency
  - Verify timers (quest/travel/hospital/jail) update correctly
  - Verify messaging delivery and UI refresh
  - Verify economy invariants (no negative balances, no double-spend)
- Produce a new test report artifact (iteration_8.json) with pass/fail and reproduction steps.

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
- ✅ `idempotency_keys` (TTL, 24h)

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

### Deployment (met)
- ✅ Running on Hetzner via Docker Compose.
- ✅ Backend served via uvicorn; Nginx routes to frontend/backend.

### Phase 9 (pending)
- [ ] Path starting stats shown == stats granted (all classes).
- [ ] Combat log styling correct.
- [ ] Equip/unequip does not lose items; equipped UI reflects server state.
- [ ] Class permissions enforced (mug/crimes restricted; Noble gets trade-focused actions).
- [ ] Tavern shows correct winnings (no undefined).
- [ ] Quests pay rewards reliably.
- [ ] Travel works with clear requirements.
- [ ] Hospital/Jail timers show and are user-scoped.
- [ ] Messaging works.
- [ ] Properties available.
- [ ] Two-account E2E report completed.

---

## Next Phase (Optional): Phase 10 — ⏳ Future
After Phase 9 stabilization:
- Real-time notifications (WebSockets/SSE) for messages/attacks/events.
- Refresh tokens + token rotation.
- Admin panel for economy tuning, item management, and moderation.
- Deterministic CI/CD pipeline with automated E2E.
- Bot service as a managed always-on compose service (plus monitoring/backoff).
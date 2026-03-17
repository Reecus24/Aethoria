# plan.md

## Objectives
- Build a medieval dark-fantasy **torn.com-inspired browser RPG** rebranded as **Realm of Aethoria**.
- Preserve the existing landing page as the public entrypoint (marketing + onboarding).
- Provide a full game experience after login:
  - Logged-out users stay on landing (`/`).
  - Logged-in users are routed into the **Game Shell** at `/game`.
- Deliver real/dynamic data only (no fake players, no inflated marketing claims).
- Provide production-style authentication and session handling:
  - **JWT authentication** (FastAPI + PyJWT)
  - **Persistent sessions** (localStorage + auto-restore on reload)
  - **Protected profile endpoint** (`/api/me`) and explicit logout.
- Extend user accounts into “characters”:
  - **path_choice** (Knight / Shadow / Noble)
  - character stats (**strength / dexterity / speed / defense / gold / xp / level / title / days_in_realm**)
- Implement the “introduced” features from the landing page as **playable systems** (Phase 6), targeting the full “42 features” set by mapping them into actual game modules.
- Ensure consistent premium UI across landing + game: stone/iron UI, gold accents, fantasy typography, dense data tables, fast navigation.

**Current status (as of this update):**
- ✅ Phase 1 complete (data-flow POC verified)
- ✅ Phase 2 complete (full backend + landing page UI implemented)
- ✅ Phase 3 complete (UX polish + content enhancements shipped)
- ✅ Phase 4 complete (JWT auth + character identity layer + immersive sections shipped)
- ✅ Phase 5 complete (all mock data replaced with real, dynamic data)
- ✅ Post-Phase-5 correction: removed false marketing claims ("50,000+", "20+ years", "Community Rating", "Free Forever") and removed filler named ticker events.
- ⏳ Phase 6 not started (game implementation)

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
- `/api/landing` now returns real leaderboard + ticker + online stats.
- `POST /api/reviews` with validation + one-review-per-user.
- News/patch notes dates are computed dynamically.

**Frontend — ✅ Completed**
- Empty states for leaderboard/reviews/ticker.
- Review submission UI for logged-in users.

**Post-Phase-5 corrections (content integrity) — ✅ Completed**
- Removed false marketing claims (50k active, 20+ years, community rating, free forever).
- Placeholder ticker events are now generic and contain **no fake character names**.

---

## Phase 6: Full Game (torn-like) Implementation — ⏳ Planned
User request: “mach einfach alles fertig … die 42 Features bitte komplett ausbearbeiten”.

**Guiding rules**
- Landing page remains at `/`.
- After login/register success, route user to `/game`.
- No filler players. All player-facing names and events must originate from real users.
- All modules require:
  - clear empty states
  - server validation (no client-trust)
  - audit logs where relevant (combat, market, banking)
  - `data-testid` coverage

### Phase 6A: Game Shell + Navigation + Routing (Foundation)
Goal: Create the torn-like UI structure and routing so gameplay can live beyond the landing page.

**Frontend**
- Implement `/game` route and nested pages (React Router):
  - `/game/dashboard` (default)
  - `/game/character`
  - `/game/training`
  - `/game/deeds`
  - `/game/combat`
  - `/game/quests`
  - `/game/inventory`
  - `/game/market`
  - `/game/bank`
  - `/game/guilds`
  - `/game/tavern`
  - `/game/map`
  - `/game/hospital`
  - `/game/dungeon`
  - `/game/contracts`
  - `/game/strongholds`
  - `/game/honours`
  - `/game/gazette`
  - `/game/leaderboard`
- Build **GameShell layout** (per /app/design_guidelines.md):
  - Sticky top utility bar (gold, energy, HP, level/XP, kingdom, timers)
  - Resizable left sidebar with grouped navigation
  - Optional right utility panel (timers/buffs)
  - Global command palette (Cmd/Ctrl+K) to jump to any feature
- Implement consistent panel/table styles for dense UI.

**Backend**
- Add `/api/game/state` endpoint returning core game HUD values (gold, energy, hp, timers, location, unread messages count).

### Phase 6B: Core Progression Loop (Training, Energy, XP, Level)
Goal: Make the game playable with a repeatable loop.
- Energy system + regeneration.
- Training grounds:
  - Train STR/DEX/SPD/DEF with energy cost + cooldown timer.
- Level mastery:
  - XP gain, level up thresholds, rewards.
- Quests:
  - quest templates, acceptance, completion checks, reward payouts.

### Phase 6C: Dark Deeds (Crimes) + Consequences
Goal: Torn-like “crime” system.
- Crime catalogue with requirements, success chance influenced by stats.
- Outcomes: success (gold/xp/items), fail (injury → hospital timer, jail → dungeon timer, gold loss).
- Crime history log.

### Phase 6D: Combat System (PvP-lite)
Goal: Attack other players and produce real logs.
- Player search/listing (exclude self).
- Attack flow:
  - choose action: duel / mug / hospitalise
  - resolution algorithm using stats + randomness
  - apply HP damage, hospital timer, gold transfer (mug)
- Combat logs and cooldowns.

### Phase 6E: Items, Inventory, Equipment, Shops
Goal: Enable gear and consumables.
- Inventory model (stackable items + equipment slots).
- Armour shops (buy items).
- Potions & elixirs (temporary buffs + timers).
- Relics/artefacts (rare items).

### Phase 6F: Economy (Market + Treasury + Bank + Exchange)
Goal: Player-driven economy.
- Market listings (create listing, buy listing, cancel listing).
- Royal Treasury:
  - deposit/withdraw
  - loans (optional in first pass)
- Royal Bank:
  - timed investments with interest
- Merchant Exchange:
  - stock-like market for "merchant houses" shares (server-controlled pricing model)

### Phase 6G: Social Systems (Guilds, Bonds, Community)
Goal: Social layer.
- Guilds & Orders:
  - create/join/leave
  - roles (leader/officer/member)
  - guild announcements
- Noble bonds:
  - partnership request/accept
  - shared benefits (later: shared stronghold)
- Realm community:
  - messaging system (DM) + basic moderation hooks

### Phase 6H: Gambling (Tavern Dice, Tavern Poker, Dragon’s Den)
Goal: Minigames with real gold transactions.
- Tavern Dice:
  - simple wager + outcome
- Tavern Poker:
  - initial pass: single-player vs table AI is not allowed (no filler); instead implement asynchronous "table" with real players only OR postpone poker until matchmaking exists.
- Dragon’s Den:
  - slots/roulette-like minigame (server RNG)

### Phase 6I: World Systems (Exploration, Hunting, Kingdom Map)
Goal: Make kingdoms meaningful.
- Travel between 11 kingdoms with travel timers and costs.
- Creature hunting (PvE) unlocked at level 15.

### Phase 6J: Consequence Locations (Dungeon, Hospital)
Goal: Enforce risk.
- Dungeon (jail) timers + optional bust out.
- Healer’s sanctuary (hospital) timers + paid heal accelerate.

### Phase 6K: Meta/Endgame Systems (Contracts, Strongholds, Honours, Contests)
Goal: Long-term progression.
- Hunter’s contracts (bounties).
- Strongholds (property purchase + upgrades).
- Merchant houses (business management).
- Royal contests + tournament grounds.
- Royal honours (achievements system).

### Phase 6L: Testing + Balancing + Anti-Abuse
Goal: Ensure the world is fair and stable.
- Automated E2E coverage for core loops.
- Rate limiting for high-frequency endpoints (combat, crimes, market).
- Server-side validation for all purchases/trades.
- Basic exploit prevention:
  - idempotency keys for transactions
  - atomic updates where needed

---

## Data Model (Phase 6 additions)
Planned MongoDB collections (high-level):
- `users` (existing; extend with energy/hp/location/equipment refs)
- `events` (existing)
- `reviews` (existing)
- `items` (master data)
- `inventories` (user → items)
- `equipment` (user → equipped slots)
- `training_sessions`
- `quests` + `user_quests`
- `crimes` + `crime_logs`
- `combat_logs`
- `market_listings` + `transactions`
- `bank_accounts` + `bank_investments`
- `loans`
- `exchange_prices` + `exchange_orders`
- `guilds` + `guild_members`
- `messages`
- `travel_sessions`
- `hunting_logs`
- `hospital_sessions`
- `dungeon_sessions`
- `bounties`
- `properties` + `user_properties`
- `achievements` + `user_achievements`

---

## Success Criteria
### Landing (already met)
- ✅ Landing page matches torn-like information architecture with medieval fantasy aesthetic.
- ✅ `/api/landing` returns real, validated content; frontend renders all sections.
- ✅ No fake user names in ticker; no false marketing claims.

### Game (Phase 6)
- After login/register, user is routed to `/game/dashboard`.
- GameShell provides fast navigation (sidebar + command palette) to all modules.
- Core loop is playable: train → deeds → combat → quests → earn gold/xp → buy gear → progress.
- Economy transactions are server-authoritative and consistent.
- Social systems work with real users only.
- No placeholder players or AI opponents posing as players.
- E2E tests cover critical paths: register → game → train → crime → combat → market → bank.

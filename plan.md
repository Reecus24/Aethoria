# plan.md

## Objectives
- Build a medieval dark-fantasy landing page inspired by torn.com, rebranded as **Realm of Aethoria**.
- Deliver a polished V1 UI + simple backend that serves dynamic content for: ticker events, online counters, features (42), leaderboard, reviews, paths, and news.
- Provide working **Login** and **Register** modals (MVP forms) and wire them to FastAPI endpoints (no advanced auth flows).
- Ensure the landing page is responsive, fast, and visually consistent (stone/iron UI, gold accents, fantasy typography).

---

## Implementation Steps

### Phase 1: Core Data Flow POC (Isolation)
Goal: prove the core workflow works end-to-end **before** building full UI.
- Define the core workflow as: **React page loads → calls FastAPI → receives structured JSON for all landing sections → renders without errors**.
- Create minimal FastAPI app + Mongo connection + seed script:
  - Collections: `site_content` (singleton doc), `ticker_events`, `leaderboard`, `reviews`, `news`.
  - Seed with ~5 ticker events, 10 leaderboard entries, 6 reviews, 8 news items, and a short features list.
- Implement API endpoints (read-only initially):
  - `GET /api/landing` (single aggregated payload for fastest initial render)
  - `GET /api/ticker`, `GET /api/leaderboard`, `GET /api/reviews`, `GET /api/news` (optional split endpoints)
- Write a small Python test script to:
  - hit `/api/landing`
  - validate JSON schema keys exist
  - verify Mongo read works
- Fix until stable (no schema drift, consistent ordering, predictable null-handling).

**Phase 1 user stories**
1. As a visitor, I want the page to load dynamic content from the server so the world feels “alive”.
2. As a visitor, I want to see recent realm events (dungeon/combat/quests) so I understand player activity.
3. As a visitor, I want to see online counts so the game feels populated.
4. As a visitor, I want leaderboard data to load consistently so I can trust the world’s competitiveness.
5. As a developer, I want a single aggregated endpoint so the landing page renders with minimal network calls.

---

### Phase 2: V1 App Development (UI + Backend)
Goal: build the full landing page MVP around the proven data flow.

**Backend (FastAPI + MongoDB)**
- Extend seed data to full V1 scope:
  - **42 medieval-adapted features** (Merchant Exchange, Guilds & Orders, Dungeon, Healer’s Sanctuary, etc.).
  - Path content for **The Knight / The Shadow / The Noble**.
  - Online counters: `now`, `last_hour`, `last_24h` (static or lightly randomized server-side for MVP).
- Add lightweight write endpoints for MVP forms:
  - `POST /api/auth/register` (store user with hashed password)
  - `POST /api/auth/login` (validate password; return placeholder session token or success boolean for MVP)
  - Keep auth minimal; no roles, no refresh tokens.

**Frontend (React)**
- Build the landing page sections matching torn.com structure:
  1. Header with Login/Register + live ticker strip
  2. Hero title + Join CTA
  3. About “Realm of Aethoria”
  4. Online counters widget
  5. Top Features carousel/grid with pagination
  6. Leaderboard table (tabs optional: “Your Rank / Global Rank” stub)
  7. Reviews carousel
  8. “Which Path Will You Take?” tabbed content
  9. Latest News list
  10. Footer with policy links
- Implement **Login/Register modals**:
  - client-side validation (empty fields, password length)
  - show success/error states
  - on success: close modal + show toast/banner
- Style system:
  - dark stone background, gold accents, ornate serif headings
  - consistent card components, separators, and hover states
  - fully responsive layout (mobile first)

**Testing (end of Phase 2)**
- Run 1 round E2E checks:
  - page loads without console errors
  - all sections render with API data
  - carousel/tab interactions work
  - register/login forms submit and show expected states

**Phase 2 user stories**
1. As a visitor, I want to read a clear “About the Realm” section so I know what kind of RPG this is.
2. As a visitor, I want to browse all 42 features so I can see the depth of gameplay.
3. As a visitor, I want to explore Knight/Shadow/Noble paths so I can imagine my playstyle.
4. As a visitor, I want to view the Hall of Legends (leaderboard) so I can see top players.
5. As a visitor, I want to register or log in from the landing page so I can start playing quickly.

---

### Phase 3: UX/Polish + Content Expansion
Goal: make V1 feel premium and stable.
- Improve ticker realism:
  - rotate events client-side; add timestamps and categories (Combat / Dungeon / Quest / Guild)
- Add optional filters/sorting:
  - leaderboard sort (level/age/improvement)
  - news pagination
- Accessibility pass:
  - focus states, keyboard navigation for carousels/tabs/modals
  - proper headings/ARIA labels
- Performance:
  - skeleton loaders
  - bundle optimization and image/font loading strategy

**Testing (end of Phase 3)**
- E2E regression: all Phase 2 flows still work.
- Responsive QA: mobile/tablet/desktop.

**Phase 3 user stories**
1. As a visitor, I want loading states so the UI feels responsive even on slow networks.
2. As a visitor, I want the ticker to feel continuously updated so the realm feels alive.
3. As a visitor, I want keyboard navigation for tabs/modals so the site is accessible.
4. As a visitor, I want news to be easy to browse so I can track updates.
5. As a visitor, I want the UI to look great on my phone so I can join from mobile.

---

### Phase 4: Authentication Hardening (Only after user approval)
Goal: turn MVP login/register into real auth without harming testability.
- JWT access tokens + protected endpoints.
- User profile stub (name, created_at).
- Rate limiting + basic abuse protections.

**Phase 4 user stories**
1. As a user, I want to stay logged in so I don’t need to re-auth every visit.
2. As a user, I want my session to be secure so my account is protected.
3. As a user, I want a basic profile page so I can confirm my account exists.
4. As an admin, I want simple rate limits so bots can’t spam registration.
5. As a user, I want clear error messages so I can recover from login issues.

---

## Next Actions
1. Confirm naming: **Realm of Aethoria** (or provide alternate realm name).
2. Approve the MVP auth approach for Phase 2 (simple register/login; no JWT yet) or request “no auth storage, UI only”.
3. Start Phase 1: implement backend skeleton + Mongo seed + `/api/landing` + python verification script.

---

## Success Criteria
- Landing page visually matches the torn.com information architecture while delivering a cohesive medieval fantasy aesthetic.
- `/api/landing` returns complete, validated content; frontend renders all sections without errors.
- Features list contains **42 medieval-adapted entries** and is browsable on mobile.
- Leaderboard, reviews, and news display correctly with pagination/interaction.
- Login/Register modals work end-to-end (submit → response → UI feedback).
- One full E2E pass completed at the end of each phase with no regressions.

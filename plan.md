# plan.md

## Objectives
- Build a medieval dark-fantasy landing page inspired by torn.com, rebranded as **Realm of Aethoria**.
- Deliver a polished V1 UI + backend that serves dynamic content for: **ticker events, online counters, 42 features, leaderboard, reviews, paths, and news**.
- Provide working **Login** and **Register** modals (MVP forms) wired to FastAPI endpoints (no advanced auth flows).
- Ensure the landing page is responsive, fast, and visually consistent (stone/iron UI, gold accents, fantasy typography).

**Current status (as of this update):**
- ✅ Phase 1 complete (data-flow POC verified)
- ✅ Phase 2 complete (full backend + full landing page UI implemented)
- ✅ Testing complete: **Backend 100%**, **Frontend 95%**
- ⚠️ Only minor low-priority items remain (toast visibility clarity; modal overlay click interception edge case; modal a11y improvements were applied via DialogDescription)

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
  1. ✅ Sticky realm event ticker (marquee)
  2. ✅ Nav bar with Login/Join
  3. ✅ Hero section with cinematic styling + CTAs
  4. ✅ Online counters widget
  5. ✅ Features section (42 features) with pagination (9 per page)
  6. ✅ Leaderboard table (Hall of Legends)
  7. ✅ Reviews/testimonials section with pagination
  8. ✅ “Which Path Will You Take?” section with 3 immersive tabs
  9. ✅ Royal Chronicles (news) with featured item + list
  10. ✅ Footer with final CTA + links
- Implemented modals:
  - ✅ Login modal (email + password) with validation
  - ✅ Register modal (username + email + password) with validation
  - ✅ Toast notifications using Sonner
  - ✅ Accessibility improvement applied: DialogDescription for modals
- Design system applied (per design guidelines):
  - ✅ Cinzel headings, IBM Plex Sans body
  - ✅ Stone/iron backgrounds, gold glow CTAs, subtle noise overlays

**Testing (end of Phase 2) — ✅ Completed**
- ✅ E2E + integration testing completed (testing_agent_v3)
- ✅ Backend: **100% pass rate** (all tested endpoints)
- ✅ Frontend: **95% pass rate**
- Low-priority findings:
  - ⚠️ Toast success feedback could be more visually obvious in some flows.
  - ⚠️ If one modal is open, overlay can intercept clicks on navbar buttons (edge-case UX; already mitigated by closing one modal before opening the other, but can be further refined).
  - ✅ A11y warning for modals addressed with DialogDescription.

**Phase 2 user stories — ✅ Completed**
1. Visitor understands the game via About section.
2. Visitor can browse all 42 features.
3. Visitor can explore Knight/Shadow/Noble paths.
4. Visitor can view Hall of Legends leaderboard.
5. Visitor can register/login quickly via modals.

---

### Phase 3: UX/Polish + Content Expansion — ⏳ Ready (Optional / On Request)
Goal: make V1 feel even more premium and stable.

**Polish items**
- Ticker realism improvements:
  - Add timestamps (or “moments ago” field) and categories badges.
  - Consider client-side rotation and occasional refresh (polling) to feel “live”.
- Improve toast visibility/clarity:
  - Increase contrast/size, ensure not hidden behind sticky ticker/nav.
  - Add an inline success banner in-modal in addition to toast.
- Modal UX refinement:
  - Prevent any overlay click interception edge cases by:
    - Ensuring only one modal can mount at a time
    - Or using a single “AuthDialog” with internal tabs.
- Responsive QA + spacing polish:
  - Mobile features browsing (carousel vs pagination) refinement.
  - Leaderboard table mobile usability (sticky columns or better horizontal scroll affordance).

**Accessibility pass**
- Ensure keyboard navigation and focus rings everywhere (tabs, pagination buttons, modal fields).
- Verify reduced-motion behavior for marquee.

**Performance**
- Skeleton loaders for initial data fetch.
- Defer heavy images; ensure hero image has proper sizing/loading.

**Testing (end of Phase 3)**
- Regression test all Phase 2 flows.
- Responsive QA: mobile/tablet/desktop.

**Phase 3 user stories**
1. Visitor sees loading states for faster perceived performance.
2. Visitor experiences a continuously updated ticker.
3. Visitor can navigate everything with keyboard.
4. Visitor can browse news/features more easily.
5. Visitor has a great experience on mobile.

---

### Phase 4: Authentication Hardening (Only after user approval) — 💤 Not Started
Goal: turn MVP login/register into real auth without harming testability.
- Add JWT access tokens + protected endpoints.
- Add user profile stub (username, created_at, basic stats).
- Add rate limiting / abuse protections.

**Phase 4 user stories**
1. User stays logged in.
2. User sessions are secure.
3. User can view a basic profile.
4. Admin has basic protections against spam.
5. User gets clear recovery/error messaging.

---

## Next Actions
1. Decide whether to proceed with **Phase 3 polish** now (recommended) or pause.
2. If proceeding: prioritize quick wins
   - Toast visibility + in-modal success banner
   - Modal single-dialog consolidation
   - Skeleton loaders + mobile QA
3. If auth needs to be production-ready, approve **Phase 4**.

---

## Success Criteria
- ✅ Landing page matches torn.com information architecture while delivering cohesive medieval fantasy aesthetic.
- ✅ `/api/landing` returns complete, validated content; frontend renders all sections.
- ✅ Features list contains **42 medieval-adapted entries** and is browsable.
- ✅ Leaderboard, reviews, and news display correctly with interactions.
- ✅ Login/Register modals work end-to-end (submit → response → UI feedback).
- ✅ One E2E pass completed with strong results (**Backend 100%, Frontend 95%**) and only low-priority issues remaining.

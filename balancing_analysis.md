# Realm of Aethoria - Gameplay Balancing Analysis

## Current Energy Economy

### Energy System
- **Starting Energy**: 100
- **Max Energy**: 100  
- **Regeneration**: NOT FOUND in grep (needs investigation)

### Training System (Early Game Loop)
- **Cost**: 10 Energy
- **Duration**: 5 minutes
- **Rewards**: +2 XP, +1-3 to stat
- **Analysis**: ⚠️ Very expensive for early game. Players can only train 10 times before being stuck.

### Crime System (Primary Gold Source)

#### Petty Crimes (Lvl 1-3)
| Crime | Energy | Success | Gold | XP | Jail Time |
|-------|--------|---------|------|----|-----------|
| Brot stehlen | 5 | 80% | 5-15 | 1 | 15 min |
| Taschendiebstahl | 8 | 65% | 20-50 | 3 | 30 min |
| Betrunkener | 7 | 70% | 15-40 | 2 | 20 min |

**Analysis**: ✅ Well balanced for early game progression.

#### Mid-Game Crimes (Lvl 4-7)
| Crime | Energy | Success | Gold | XP | Jail Time |
|-------|--------|---------|------|----|-----------|
| Einbruch | 12 | 50% | 50-150 | 8 | 60 min |
| Pferd stehlen | 15 | 45% | 100-200 | 12 | 90 min |
| Händler überfallen | 15 | 45% | 100-300 | 15 | 120 min |
| Erpressung | 18 | 40% | 200-400 | 18 | 150 min |

**Analysis**: ⚠️ Risk/reward is good, but energy costs are very high.

#### High-End Crimes (Lvl 8-18)
| Crime | Energy | Success | Gold | XP | Jail Time |
|-------|--------|---------|------|----|-----------|
| Laden ausrauben | 20 | 35% | 300-600 | 25 | 180 min |
| Entführung | 25 | 30% | 500-1000 | 35 | 240 min |
| Schatzkammer | 25 | 30% | 500-1500 | 40 | 360 min |
| Attentat | 30 | 25% | 1000-2500 | 60 | 600 min |
| Drachenei | 40 | 15% | 3000-8000 | 150 | 720 min |

**Analysis**: ⚠️ Extremely high energy costs. Players need 25-40 energy per attempt.

### Quest System

| Quest | Level | Energy | Duration | Gold | XP |
|-------|-------|--------|----------|------|----|
| Rattenplage | 1 | 15 | 20 min | 50 | 10 |
| Händler-Eskorte | 3 | 20 | 30 min | 100 | 25 |
| Wolfsrudel | 5 | 25 | 40 min | 200 | 40 |
| Banditenlager | 5 | 30 | 60 min | 250 | 50 |
| Rettungsmission | 8 | 35 | 90 min | 500 | 80 |
| Artefakt | 10 | 40 | 120 min | 800 | 120 |
| Drachen | 15 | 50 | 120 min | 2000 | 200 |

**Analysis**: ⚠️ Very high energy costs. Early quest costs 15 energy (1.5 training sessions worth).

### Hunting System

| Creature | Level | Energy | HP | Power | Gold | XP |
|----------|-------|--------|----|----|------|----|
| Wolf | 5 | 20 | 30 | 15 | 30-80 | 15 |
| Bär | 10 | 30 | 60 | 35 | 100-200 | 40 |
| Troll | 15 | 40 | 100 | 50 | 300-600 | 100 |
| Junger Drache | 20 | 60 | 200 | 80 | 1000-3000 | 300 |

**Analysis**: ⚠️ Very high energy costs for hunting.

### Combat System
- **Damage Range**: 20-50 (base), 15-35 (counter-attack)
- **Energy Cost**: NOT FOUND (needs investigation)

---

## Problems Identified

### 1. **Energy Starvation** 🔴 CRITICAL
- Training costs 10 energy (10% of total pool)
- Early crimes cost 5-15 energy
- Quests cost 15-50 energy
- With 100 max energy, players can do ~6-10 actions before being stuck
- **Without knowing the regen rate, this could be a major blocker**

### 2. **Early Game Too Slow** ⚠️ HIGH
- Training takes 5 minutes per session
- Early quests take 20-30 minutes
- Jail time starts at 15 minutes
- Players will spend most time waiting, not playing

### 3. **Mid-Game Scaling Issues** ⚠️ MEDIUM
- Crime energy costs jump dramatically (5 → 40)
- Quest energy costs are too high for the energy pool
- No incentive to do quests vs crimes (similar energy, crimes are instant)

---

## Recommended Balancing Changes

### Phase 1: Energy Economy Fix
1. **Reduce Training Cost**: 10 → **5 energy** (allows 20 training sessions per full bar)
2. **Reduce Early Crime Costs**:
   - Brot stehlen: 5 → **3 energy**
   - Taschendiebstahl: 8 → **5 energy**
   - Betrunkener: 7 → **4 energy**
3. **Reduce Quest Costs by 30%**:
   - Rattenplage: 15 → **10 energy**
   - Händler-Eskorte: 20 → **14 energy**
   - etc.

### Phase 2: Time Compression
1. **Training Duration**: 5 min → **3 minutes**
2. **Early Quest Duration**: Reduce by 25%
   - Rattenplage: 20 → **15 min**
   - Händler-Eskorte: 30 → **20 min**
3. **Jail Time**: Reduce early penalties
   - Brot stehlen: 15 → **10 min**
   - Taschendiebstahl: 30 → **20 min**

### Phase 3: Reward Curve
1. **Increase Early Gold Rewards by 20%**:
   - Brot stehlen: 5-15 → **6-18 Gold**
   - Training XP: 2 → **3 XP**
2. **Better Item Drop Rates**: Increase from 10-30% to 15-40%

---

## Implementation Priority
1. ✅ Energy cost reductions (biggest impact)
2. ✅ Time compression (improves gameplay feel)
3. ✅ Reward increases (makes actions feel more rewarding)

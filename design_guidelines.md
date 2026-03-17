{
  "brand": {
    "name": "Reich von Aethoria – Spielinterface",
    "attributes": [
      "düster, gritttig, aber lesbar (keine 'edgy' Unlesbarkeit)",
      "mittelalterlich mit subtiler Fantasy-Magie (Runen, Siegel, Glühen)",
      "torn.com-inspiriert: datenreich, schnell navigierbar, kein Schnickschnack",
      "premium-feeling durch Materialität: Stein, Eisen, Pergament, Gold"
    ],
    "language": "de-DE",
    "non_negotiables": [
      "Landingpage bei / nicht kaputt machen",
      "Nach Login immer in /game (oder /game/dashboard) routen",
      "Keine Platzhalterdaten: echte/dynamische Daten",
      "Alle Interaktionen & wichtige Info-Elemente mit data-testid (kebab-case)",
      "Komponenten primär aus /frontend/src/components/ui (shadcn)"
    ]
  },
  "inspiration_refs": {
    "reference_pages": [
      {
        "title": "Behance – medieval mmorpg game ui (Sammlung)",
        "url": "https://www.behance.net/search/projects/medieval%20mmorpg%20game%20ui",
        "notes": "Panel-lastige HUDs, gerahmte Karten, Metall/Gold-Akzente, klare Unterteilung (Sidebar + Content + Utility/Status)."
      },
      {
        "title": "Dribbble – medieval game ui (Suche)",
        "url": "https://dribbble.com/search/medieval-game-ui",
        "notes": "Gute Quellen für Icon-Stil, Buttons (metallisch), ornamentale Divider und Micro-States."
      }
    ],
    "design_fusion": {
      "layout_principle": "torn-ähnliche Dichte: linke Sidebar (Navigation), oben Utility-Bar (Währung/Timer), Content in modularen Panels",
      "materiality": "Landingpage-Farben/Stein + Pergamentflächen für lesbare Tabellen/Logs",
      "motion": "dezente Glows + 'press' Interaktionen; keine übertriebenen Animationen (Performance!)"
    }
  },
  "design_tokens": {
    "css_custom_properties": {
      "file": "/app/frontend/src/index.css",
      "instructions": [
        "Bestehende Aethoria Tokens beibehalten und für Game-UI ergänzen.",
        "Keine globalen Layout-Zentrierungen in App.css hinzufügen.",
        "Gradienten nur als Abschnitts-Hintergrund/Overlay (max 20% viewport)."
      ],
      "add_tokens": {
        "--aeth-stone-0": "#070606",
        "--aeth-stone-1": "#0E0C0B",
        "--aeth-stone-2": "#151110",
        "--aeth-iron": "#3B3532",
        "--aeth-gold": "#D6A24D",
        "--aeth-amber": "#C9832E",
        "--aeth-blood": "#8E1D2C",
        "--aeth-magic": "#3C2250",
        "--aeth-parchment": "#CDB48A",
        "--aeth-parchment-dim": "#A8936D",
        "--game-surface": "rgba(21,17,16,0.72)",
        "--game-surface-2": "rgba(14,12,11,0.72)",
        "--game-parchment-surface": "rgba(205,180,138,0.08)",
        "--game-border-subtle": "rgba(59,53,50,0.65)",
        "--game-ring": "rgba(214,162,77,0.55)",
        "--shadow-elev-1": "0 10px 30px rgba(0,0,0,0.35)",
        "--shadow-elev-2": "0 18px 60px rgba(0,0,0,0.45)",
        "--radius-card": "14px",
        "--radius-control": "10px",
        "--radius-pill": "999px",
        "--space-page-x": "clamp(16px, 2.2vw, 28px)",
        "--space-page-y": "clamp(16px, 2.2vw, 26px)"
      }
    },
    "palette": {
      "role_colors": {
        "bg": "var(--aeth-stone-0)",
        "panel": "var(--aeth-stone-2)",
        "panelAlt": "var(--aeth-stone-1)",
        "text": "hsl(var(--foreground))",
        "mutedText": "hsl(var(--muted-foreground))",
        "border": "hsl(var(--border))",
        "primary": "var(--aeth-gold)",
        "primaryHover": "var(--aeth-amber)",
        "danger": "var(--aeth-blood)",
        "magic": "var(--aeth-magic)",
        "parchment": "var(--aeth-parchment)"
      },
      "allowed_gradients": [
        {
          "name": "stone-glow-overlay (decorative)",
          "css": "radial-gradient(circle at 20% 0%, rgba(214,162,77,0.12), transparent 52%), radial-gradient(circle at 90% 30%, rgba(142,29,44,0.10), transparent 55%)",
          "usage": "Nur als Hintergrund-Overlay in Header/Topbar oder Seitenrand, nicht hinter Lesetext."
        }
      ]
    }
  },
  "typography": {
    "font_pairing": {
      "headings": "Cinzel (bestehend)",
      "body": "IBM Plex Sans (bestehend)",
      "numbers_mono": "Azeret Mono (bestehend .font-mono-az)"
    },
    "scale": {
      "h1": "text-4xl sm:text-5xl lg:text-6xl font-cinzel tracking-wide",
      "h2": "text-base md:text-lg text-muted-foreground",
      "sectionTitle": "text-xl md:text-2xl font-cinzel",
      "cardTitle": "text-base md:text-lg font-cinzel",
      "body": "text-sm md:text-base leading-relaxed",
      "small": "text-xs md:text-sm text-muted-foreground",
      "numeric": "font-mono-az tabular-nums"
    },
    "rules": [
      "In datenreichen Tabellen/Logs: body text maximal text-sm und Zeilenhöhe erhöhen (leading-6).",
      "Währungen/Timer/Stats immer mono + tabular-nums für ruhige Spalten."
    ]
  },
  "layout": {
    "grid_system": {
      "game_shell": {
        "desktop": "CSS grid: [sidebar 280px] [content 1fr] [utility 320px optional]",
        "tablet": "Sidebar als collapsible Sheet/Drawer; Content 1fr",
        "mobile": "Bottom utility actions + Sheet nav; Content single column"
      },
      "page_padding": "px-[var(--space-page-x)] py-[var(--space-page-y)]",
      "content_max_width": "Kein zentriertes max-w für Game; nutze volle Breite, aber mit Panel-Spalten."
    },
    "navigation": {
      "pattern": "Persistente linke Sidebar mit Gruppen (Kernloop, Wirtschaft, Social, Glückspiel, Welt, Verwaltung)",
      "must_have": [
        "Suchfeld (Command) für schnelle Navigation zu 42 Features",
        "Pinned Quick Actions (Trainieren, Verbrechen, Angriff, Quest)",
        "Badges für Benachrichtigungen (z.B. Nachrichten, Heilung fertig, Training fertig)"
      ]
    },
    "information_density": {
      "principles": [
        "Ein Screen = 1 primäre Aufgabe + 1-2 sekundäre Panels",
        "Vermeide riesige Hero-Banner im Game",
        "Nutze Tabs für Unterfunktionen statt neue Seiten wenn sinnvoll (z.B. Market: Kaufen/Verkaufen/Meine Listings)"
      ]
    }
  },
  "components": {
    "component_path": {
      "shell": [
        "/app/frontend/src/components/ui/resizable.jsx",
        "/app/frontend/src/components/ui/scroll-area.jsx",
        "/app/frontend/src/components/ui/separator.jsx",
        "/app/frontend/src/components/ui/sheet.jsx",
        "/app/frontend/src/components/ui/navigation-menu.jsx",
        "/app/frontend/src/components/ui/breadcrumb.jsx"
      ],
      "data_display": [
        "/app/frontend/src/components/ui/card.jsx",
        "/app/frontend/src/components/ui/table.jsx",
        "/app/frontend/src/components/ui/tabs.jsx",
        "/app/frontend/src/components/ui/badge.jsx",
        "/app/frontend/src/components/ui/progress.jsx",
        "/app/frontend/src/components/ui/tooltip.jsx",
        "/app/frontend/src/components/ui/hover-card.jsx",
        "/app/frontend/src/components/ui/skeleton.jsx"
      ],
      "actions_forms": [
        "/app/frontend/src/components/ui/button.jsx",
        "/app/frontend/src/components/ui/input.jsx",
        "/app/frontend/src/components/ui/textarea.jsx",
        "/app/frontend/src/components/ui/select.jsx",
        "/app/frontend/src/components/ui/dialog.jsx",
        "/app/frontend/src/components/ui/alert-dialog.jsx",
        "/app/frontend/src/components/ui/dropdown-menu.jsx",
        "/app/frontend/src/components/ui/checkbox.jsx",
        "/app/frontend/src/components/ui/switch.jsx",
        "/app/frontend/src/components/ui/slider.jsx",
        "/app/frontend/src/components/ui/calendar.jsx"
      ],
      "feedback": [
        "/app/frontend/src/components/ui/sonner.jsx"
      ]
    },
    "key_ui_patterns": {
      "top_utility_bar": {
        "description": "Schmale Sticky-Topbar im Game: Gold, Energie, Leben, Ausdauer, Level/XP, Kingdom, Uhr/Timer.",
        "shadcn": ["card", "badge", "progress", "tooltip"],
        "tailwind": "sticky top-0 z-40 bg-[rgba(7,6,6,0.72)] backdrop-blur border-b border-[color:var(--game-border-subtle)]"
      },
      "sidebar_nav": {
        "description": "Links: ResizableSidebar. Gruppen mit Collapsible. Aktiver Link als 'carved' highlight.",
        "shadcn": ["resizable", "collapsible", "scroll-area", "button", "tooltip"],
        "tailwind": "h-[calc(100vh-48px)] border-r border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-1)]"
      },
      "stat_bars_panel": {
        "description": "Rechts (optional): Charakter-Status (HP/MP/Energie/XP), Buffs/Debuffs, aktive Timer (Training, Heilung, Reise).",
        "shadcn": ["card", "progress", "badge", "separator"],
        "tailwind": "space-y-3"
      },
      "tables_logs": {
        "description": "Combat Log, Marktlisten, Nachrichten: Table + ScrollArea, Sticky Header, zebra subtle.",
        "shadcn": ["table", "scroll-area"],
        "tailwind": "[&_*]:text-sm"
      },
      "quick_action_cards": {
        "description": "Dashboard: 4 Action-Karten (Trainieren/Verbrechen/Kampf/Quest) mit primärem CTA und sekundären Infos.",
        "shadcn": ["card", "button", "badge"],
        "tailwind": "grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4"
      },
      "modals_for_risky_actions": {
        "description": "Verbrechen starten, Angriff bestätigen, große Investments: Dialog/AlertDialog mit klaren Konsequenzen.",
        "shadcn": ["dialog", "alert-dialog"],
        "rules": ["Konsequenzen immer als Bullet-Liste, Danger-Color für Strafen."]
      }
    }
  },
  "motion_microinteractions": {
    "rules": [
      "Keine 'transition-all'. Nur gezielte transition-colors/opacity/shadow.",
      "Buttons: hover leichtes translateY(-1px) erlaubt (wie btn-gold).",
      "Panels: Hover nur Border/Glow; keine Layout-Shifts.",
      "Realtime-Updates: nur die betroffenen Zellen/Badges kurz 'pulse' (opacity), nicht ganze Seite."
    ],
    "recommended_library": {
      "name": "framer-motion",
      "use_cases": [
        "Panel-Entrance (sehr subtil)",
        "Tab-Wechsel (crossfade)",
        "Notification badge pop-in"
      ],
      "install": "npm i framer-motion",
      "usage_scaffold_js": "import { motion } from 'framer-motion';\n\nexport const FadeIn = ({ children }) => (\n  <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.18 }} >\n    {children}\n  </motion.div>\n);"
    }
  },
  "accessibility": {
    "focus": "Bestehender :focus-visible Ring (gold) beibehalten; in Game-Topbar/Sidebar keine focus removal.",
    "contrast": [
      "Text auf Steinflächen: foreground/muted-foreground nutzen, nicht Pergament-Farben.",
      "Pergamentflächen nur als Substrat für Tabellen/Logs: Textfarbe auf dunkle Tinte (#1a1410) setzen wenn Hintergrund hell ist."
    ],
    "reduced_motion": "prefers-reduced-motion respektieren (bestehende Overrides sind ok).",
    "keyboard": [
      "Command Palette mit Cmd/Ctrl+K für Navigation",
      "Sidebar Links als echte Buttons/Links mit aria-current"
    ]
  },
  "data_testid_conventions": {
    "rules": [
      "kebab-case: <bereich>-<element>-<aktion> z.B. game-sidebar-nav-training",
      "Buttons: *-button, Inputs: *-input, Tabs: *-tab, Dialogs: *-dialog"
    ],
    "examples": [
      "data-testid=\"game-topbar-gold-amount\"",
      "data-testid=\"training-strength-train-button\"",
      "data-testid=\"market-search-input\"",
      "data-testid=\"combat-attack-confirm-dialog\""
    ]
  },
  "image_urls": {
    "backgrounds_overlays": [
      {
        "category": "game-shell-background",
        "description": "Sehr subtil als fixed Hintergrund (stark gedimmt + blur optional).",
        "url": "https://images.unsplash.com/photo-1641293576364-302a50f6433d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwyfHxkYXJrJTIwbWVkaWV2YWwlMjBzdG9uZSUyMGNhc3RsZSUyMGludGVyaW9yJTIwbW9vZHklMjB0b3JjaGxpZ2h0fGVufDB8fHxibGFja3wxNzczNzE0MDQ1fDA&ixlib=rb-4.1.0&q=85"
      }
    ],
    "textures": [
      {
        "category": "parchment-texture",
        "description": "Nur für kleine Akzentflächen/Empty States/Letter Panels (nicht global).",
        "url": "https://images.unsplash.com/photo-1654860243046-39fadefa77c2?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1MTN8MHwxfHNlYXJjaHwzfHxhZ2VkJTIwcGFyY2htZW50JTIwdGV4dHVyZSUyMGNsb3NlJTIwdXB8ZW58MHx8fHllbGxvd3wxNzczNzE0MDQ2fDA&ixlib=rb-4.1.0&q=85"
      }
    ],
    "tavern": [
      {
        "category": "tavern-header-accent",
        "description": "Header-Bild für Taverne/Glückspiel Seiten (stark gedimmt).",
        "url": "https://images.unsplash.com/photo-1542317049-c1998da755f1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA3MDB8MHwxfHNlYXJjaHwxfHxtZWRpZXZhbCUyMHRhdmVybiUyMGludGVyaW9yJTIwY2FuZGxlbGlnaHR8ZW58MHx8fG9yYW5nZXwxNzczNzE0MDQ5fDA&ixlib=rb-4.1.0&q=85"
      }
    ]
  },
  "libraries": {
    "command_palette": {
      "use": "shadcn/command.jsx für Cmd/Ctrl+K Navigation",
      "component": "/app/frontend/src/components/ui/command.jsx",
      "notes": "Bind Shortcut global im GameShell; Suche muss alle 42 Features + Seiten abdecken."
    },
    "charts": {
      "lib": "recharts",
      "install": "npm i recharts",
      "use_cases": [
        "XP Verlauf, Gold Cashflow, Market Preisverlauf",
        "Training Efficiency pro Tag"
      ],
      "style_notes": "Charts auf dunkler Steinfläche; Linien in Gold/Amber, Tooltip als Card (stone-2)."
    }
  },
  "page_blueprints": {
    "game_dashboard": {
      "sections": [
        "Topbar (sticky)",
        "Quick Actions (4 Karten)",
        "Charakter Überblick (Stats, Equipment summary)",
        "Aktuelle Ereignisse (Royal Gazette mini feed)",
        "Timer Panel (Training/Heilung/Reise)",
        "Market Snapshot (Top Listings / Preisänderungen)"
      ]
    },
    "training_grounds": {
      "layout": "Links: Stat Cards (STR/DEX/SPD/DEF) mit Progress + Kosten; Rechts: Timer + Tips",
      "components": ["tabs", "progress", "button", "tooltip"]
    },
    "combat": {
      "layout": "Oben: Zielsuche + Filter; Mitte: Combat panel; Rechts: Combat log (scroll)",
      "components": ["input", "select", "card", "table", "dialog"]
    },
    "market": {
      "layout": "Tabs: Kaufen | Verkaufen | Meine Angebote; Table + Filters + Pagination",
      "components": ["tabs", "table", "pagination", "select", "input"]
    }
  },
  "tailwind_usage_notes": {
    "panel_class": "rounded-[var(--radius-card)] border border-[color:var(--game-border-subtle)] bg-[color:var(--aeth-stone-2)] shadow-[var(--shadow-elev-1)]",
    "panel_header": "flex items-center justify-between gap-3 border-b border-[color:var(--game-border-subtle)] px-4 py-3",
    "panel_body": "px-4 py-4",
    "muted_chip": "rounded-full bg-[rgba(205,180,138,0.08)] px-2 py-0.5 text-xs text-[color:var(--aeth-parchment)]"
  },
  "instructions_to_main_agent": [
    "Implementiere ein GameShell Layout: sticky Topbar + resizable Sidebar + Content. Sidebar in mobile als Sheet.",
    "Nutze bestehende Tokens in index.css; erweitere nur, nichts brechen.",
    "Für dichte Datenansichten: Table + ScrollArea + Skeleton (skeleton-aeth Klasse).",
    "Command Palette (Cmd/Ctrl+K) ist Pflicht für schnelles Navigieren zu 42 Features.",
    "Jede Seite muss klare Empty States haben: neue Spieler (keine Items), keine Listings, keine Quests.",
    "Alle Buttons/Inputs/Links/Tabs/Dialog-Trigger + wichtige Values mit data-testid.",
    "Keine großen Gradient-Flächen; nutze maximal kleine decorative overlays (siehe allowed_gradients).",
    "JS-only Komponenten: .jsx nutzen (keine .tsx Beispiele übernehmen)."
  ]
}

<General UI UX Design Guidelines>  
    - You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms
    - You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text
   - NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json

 **GRADIENT RESTRICTION RULE**
NEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc
NEVER use dark gradients for logo, testimonial, footer etc
NEVER let gradients cover more than 20% of the viewport.
NEVER apply gradients to text-heavy content or reading areas.
NEVER use gradients on small UI elements (<100px width).
NEVER stack multiple gradient layers in the same viewport.

**ENFORCEMENT RULE:**
    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors

**How and where to use:**
   • Section backgrounds (not content backgrounds)
   • Hero section header content. Eg: dark to light to dark color
   • Decorative overlays and accent elements only
   • Hero section with 2-3 mild color
   • Gradients creation can be done for any angle say horizontal, vertical or diagonal

- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**

</Font Guidelines>

- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. 
   
- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.

- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.
   
- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly
    Eg: - if it implies playful/energetic, choose a colorful scheme
           - if it implies monochrome/minimal, choose a black–white/neutral scheme

**Component Reuse:**
	- Prioritize using pre-existing components from src/components/ui when applicable
	- Create new components that match the style and conventions of existing components when needed
	- Examine existing components to understand the project's component patterns before creating new ones

**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component

**Best Practices:**
	- Use Shadcn/UI as the primary component library for consistency and accessibility
	- Import path: ./components/[component-name]

**Export Conventions:**
	- Components MUST use named exports (export const ComponentName = ...)
	- Pages MUST use default exports (export default function PageName() {...})

**Toasts:**
  - Use `sonner` for toasts"
  - Sonner component are located in `/app/src/components/ui/sonner.tsx`

Use 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals.
</General UI UX Design Guidelines>

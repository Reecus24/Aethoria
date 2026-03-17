{
  "project": {
    "name": "Realm of Aethoria",
    "type": "single-page marketing/landing",
    "design_personality": [
      "dark-medieval premium",
      "gritty text-RPG UI (torn.com energy)",
      "gothic grandeur",
      "tactile materials: stone + iron + parchment",
      "high-contrast, conversion-first",
      "subtle arcane motion (runes/embers)"
    ],
    "north_star": "Make the user feel like they’re stepping into a living realm—then get them to Join within 10 seconds (and keep exploring)."
  },

  "inspiration_refs": {
    "notes": "Use torn-like dense UI rhythm: narrow ticker, compact stats widgets, tables. Mix with cinematic dark fantasy landing composition.",
    "urls": [
      {
        "label": "Dark Fantasy Game Landing Page UI/UX Concept (Behance, 2026)",
        "url": "https://www.behance.net/gallery/244247671/Dark-Fantasy-Game-Landing-Page-UIUX-Design-Concept",
        "takeaways": [
          "Cinematic hero + strong CTA pairing",
          "Layered dark background + ornamental dividers",
          "Feature cards with high contrast headings"
        ]
      },
      {
        "label": "Dribbble fantasy UI search",
        "url": "https://dribbble.com/search/fantasy-UI",
        "takeaways": [
          "Gothic frames, rune glows, metal bevels",
          "Icon-led feature grids with micro-illumination on hover"
        ]
      }
    ]
  },

  "brand_attributes": {
    "trustworthy": "Clear hierarchy, readable typography, stable UI patterns (tables/tabs).",
    "premium": "Material realism: iron borders, stone noise, parchment inset panels, restrained gold glow.",
    "motivating": "Live realm ticker + counters + leaderboard create social proof and urgency.",
    "mysterious": "Deep purple magic accents only in highlights/runes; keep it scarce."
  },

  "typography": {
    "google_fonts": {
      "heading": {
        "family": "Cinzel",
        "fallback": "Georgia, serif",
        "weights": ["600", "700"],
        "usage": "All H1/H2 section titles, tab labels (Path section), key stat numbers (optional)."
      },
      "body": {
        "family": "IBM Plex Sans",
        "fallback": "system-ui, -apple-system, Segoe UI, sans-serif",
        "weights": ["400", "500", "600"],
        "usage": "Body copy, UI labels, ticker text, table content."
      },
      "mono_optional": {
        "family": "Azeret Mono",
        "fallback": "ui-monospace, SFMono-Regular, Menlo, monospace",
        "weights": ["400", "600"],
        "usage": "IDs, timestamps in ticker/news, small meta details."
      },
      "implementation": {
        "add_to_index_html": [
          "https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=IBM+Plex+Sans:wght@400;500;600&family=Azeret+Mono:wght@400;600&display=swap"
        ],
        "tailwind_usage": {
          "heading_class": "font-[Cinzel] tracking-wide",
          "body_class": "font-[IBM_Plex_Sans]",
          "mono_class": "font-[Azeret_Mono]"
        }
      }
    },
    "text_size_hierarchy": {
      "h1": "text-4xl sm:text-5xl lg:text-6xl",
      "h2": "text-base md:text-lg",
      "body": "text-sm sm:text-base",
      "small": "text-xs sm:text-sm",
      "ui_numbers": "text-2xl sm:text-3xl font-semibold"
    },
    "typesetting_rules": [
      "Headings: slight letter spacing (tracking-wide to tracking-wider).",
      "Body: keep max width ~65ch for long paragraphs (About/News).",
      "Use small-caps style by uppercase + tracking for micro labels (e.g., 'Online Now')."
    ]
  },

  "color_system": {
    "mode": "dark-only (no white/light backgrounds)",
    "tokens_hsl_for_shadcn": {
      "notes": "Update /app/frontend/src/index.css :root and/or .dark. We want the entire site to render under .dark on html/body.",
      "base": {
        "--background": "24 22% 6%",
        "--foreground": "40 33% 92%",
        "--card": "22 23% 8%",
        "--card-foreground": "40 33% 92%",
        "--popover": "22 23% 8%",
        "--popover-foreground": "40 33% 92%",
        "--muted": "22 18% 12%",
        "--muted-foreground": "36 14% 72%",
        "--border": "28 18% 18%",
        "--input": "28 18% 18%",
        "--ring": "38 86% 58%"
      },
      "brand": {
        "--primary": "38 86% 58%",
        "--primary-foreground": "24 22% 6%",
        "--secondary": "260 22% 18%",
        "--secondary-foreground": "40 33% 92%",
        "--accent": "18 74% 34%",
        "--accent-foreground": "40 33% 92%",
        "--destructive": "0 72% 38%",
        "--destructive-foreground": "40 33% 92%"
      },
      "charts": {
        "--chart-1": "38 86% 58%",
        "--chart-2": "18 74% 34%",
        "--chart-3": "260 22% 46%",
        "--chart-4": "34 25% 66%",
        "--chart-5": "0 72% 50%"
      },
      "radius": {
        "--radius": "0.75rem"
      }
    },
    "semantic_extensions_css_vars": {
      "notes": "Add these as custom properties in index.css under .dark or :root. Used for textures, glows, and borders.",
      "vars": {
        "--aeth-stone-0": "#070606",
        "--aeth-stone-1": "#0E0C0B",
        "--aeth-stone-2": "#151110",
        "--aeth-iron": "#3B3532",
        "--aeth-iron-2": "#272221",
        "--aeth-gold": "#D6A24D",
        "--aeth-amber": "#C9832E",
        "--aeth-blood": "#8E1D2C",
        "--aeth-magic": "#3C2250",
        "--aeth-parchment": "#CDB48A",
        "--aeth-parchment-dim": "#A8936D",
        "--aeth-glow-gold": "rgba(214, 162, 77, 0.35)",
        "--aeth-glow-blood": "rgba(142, 29, 44, 0.28)",
        "--aeth-noise-opacity": "0.09"
      }
    },
    "usage_rules": [
      "Gold/amber: primary CTAs, active states, key separators and ornaments.",
      "Blood red: danger/highlight only (sparingly).",
      "Deep purple: magic/rune hovers + rare accents (e.g., Path tabs indicator).",
      "Cards are NEVER light: use near-black stone with parchment inset only as subtle overlay within cards (<=30% card area)."
    ],
    "gradients": {
      "allowed_only_for": ["hero background overlay", "large section backdrop accents"],
      "compliant_examples": [
        "radial-gradient(1200px 600px at 20% 10%, rgba(214,162,77,0.10), transparent 60%), radial-gradient(900px 500px at 80% 30%, rgba(60,34,80,0.12), transparent 55%)",
        "linear-gradient(180deg, rgba(7,6,6,0.10), rgba(7,6,6,0.65))"
      ],
      "restriction": "Gradients must not exceed 20% viewport impact; never on text-heavy panels; never on small UI elements."
    }
  },

  "layout_grid": {
    "max_width": "max-w-6xl (content), max-w-7xl (hero)",
    "gutters": "px-4 sm:px-6 lg:px-8",
    "section_spacing": "py-14 sm:py-18 lg:py-24",
    "rhythm": [
      "Use torn-like density in ticker + stats + tables.",
      "Use generous spacing in hero, testimonials, path section for drama."
    ],
    "responsive_strategy": {
      "mobile_first": true,
      "breakpoints": {
        "sm": "640px",
        "md": "768px",
        "lg": "1024px",
        "xl": "1280px"
      },
      "patterns": [
        "Hero becomes stacked: title + CTAs then art.",
        "Features: carousel on mobile, 3-col grid on desktop.",
        "Leaderboard: horizontal scroll container on mobile with sticky first column optional."
      ]
    }
  },

  "textures_and_motifs": {
    "backgrounds": {
      "global": [
        "Base: solid near-black stone.",
        "Overlay: subtle noise (CSS) + faint stone texture.",
        "Add decorative corner crests (SVG) at section edges; keep opacity 10–18%."
      ],
      "css_noise_snippet": {
        "selector": ".aeth-noise::before",
        "snippet": "content:''; position:absolute; inset:0; pointer-events:none; background-image:url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22%3E%3Cfilter id=%22n%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22 numOctaves=%224%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22200%22 height=%22200%22 filter=%22url(%23n)%22 opacity=%220.45%22/%3E%3C/svg%3E'); opacity: var(--aeth-noise-opacity); mix-blend-mode: overlay;"
      }
    },
    "borders": {
      "gothic_frame": "Use pseudo-elements with repeating-linear-gradient + mask to simulate engraved edge; add inner border line for depth.",
      "ornamental_divider": "Use shadcn Separator with custom background image (SVG line with fleur-de-lis points) or simple: border + center icon."
    },
    "motifs": [
      "Shields/crests as corner watermarks",
      "Runic underline on headings",
      "Wax seal badge for 'New Chronicle' tags",
      "Iron chains for section separators (light, low opacity)"
    ]
  },

  "components": {
    "component_path": {
      "shadcn": [
        "/app/frontend/src/components/ui/button.jsx",
        "/app/frontend/src/components/ui/card.jsx",
        "/app/frontend/src/components/ui/badge.jsx",
        "/app/frontend/src/components/ui/tabs.jsx",
        "/app/frontend/src/components/ui/table.jsx",
        "/app/frontend/src/components/ui/carousel.jsx",
        "/app/frontend/src/components/ui/dialog.jsx",
        "/app/frontend/src/components/ui/input.jsx",
        "/app/frontend/src/components/ui/label.jsx",
        "/app/frontend/src/components/ui/scroll-area.jsx",
        "/app/frontend/src/components/ui/separator.jsx",
        "/app/frontend/src/components/ui/sonner.jsx",
        "/app/frontend/src/components/ui/progress.jsx",
        "/app/frontend/src/components/ui/skeleton.jsx"
      ],
      "notes": "Project uses .jsx (NOT .tsx). Keep all new components as .jsx and follow existing shadcn patterns."
    },

    "core_sections_and_ui": {
      "top_event_ticker": {
        "purpose": "Social proof + world feels alive.",
        "layout": "Sticky strip at top (or below nav). Height 36–44px. Left label 'Realm Activity' + scrolling marquee items.",
        "implementation": {
          "structure": "div (label) + overflow-hidden marquee track",
          "tailwind": "sticky top-0 z-50 bg-[var(--aeth-stone-1)]/95 backdrop-blur border-b border-border",
          "marquee": "Use CSS keyframes translateX with pause on hover; duplicate content for seamless loop.",
          "item_style": "Inline separators: small dot or dagger icon; time in mono font."
        },
        "data_testids": {
          "strip": "event-ticker-strip",
          "track": "event-ticker-track",
          "item": "event-ticker-item"
        }
      },

      "hero": {
        "layout": "Split-screen: left copy + CTAs, right cinematic image (castle). Add crest watermark behind title.",
        "background": "Solid stone + small compliant radial accents in corners (gold/purple).",
        "cta_buttons": {
          "primary": "Join the Realm",
          "secondary": "Login",
          "variants": {
            "primary_style": "Gold glow button (solid base + outer glow).",
            "secondary_style": "Iron-outline button (ghost/outline) with subtle inner shine."
          }
        },
        "micro_interactions": [
          "CTA hover: glow intensifies + slight lift (translate-y-[-1px]).",
          "Hero crest watermark slowly drifts (very subtle parallax) unless prefers-reduced-motion."
        ],
        "data_testids": {
          "join": "hero-join-button",
          "login": "hero-login-button"
        }
      },

      "about": {
        "layout": "Two-column: narrative paragraph + 3 bullets as 'Oaths' (Knight/Rogue/Merchant).",
        "component": "Card (custom class for stone frame + parchment inset).",
        "data_testids": {
          "section": "about-section"
        }
      },

      "online_players_counter": {
        "layout": "Compact stat bar with 3 stats: Now / Last Hour / Last 24h.",
        "component": "Card + separators; use Badge for labels.",
        "data_testids": {
          "widget": "online-players-widget",
          "now": "online-players-now",
          "hour": "online-players-last-hour",
          "day": "online-players-last-24h"
        }
      },

      "features_42": {
        "layout": "Desktop: 3-column grid; Mobile: Carousel with snap.",
        "card_style": "Weathered stone with etched border; icon in an iron coin.",
        "icon_system": "Use lucide-react icons (swords/shield/skull/scroll/coin) — no emoji.",
        "interaction": "Hover: rune glow around icon + faint purple edge light.",
        "data_testids": {
          "section": "features-section",
          "card": "feature-card",
          "carousel": "features-carousel"
        }
      },

      "leaderboard_hall_of_legends": {
        "layout": "Table inside ScrollArea; top 10–25. Add rank medal icons for top 3 (gold/iron/blood accent).",
        "component": "Table + ScrollArea + Badge",
        "interaction": "Row hover: subtle background lift (NOT transform-heavy), left border gold highlight.",
        "data_testids": {
          "section": "leaderboard-section",
          "table": "leaderboard-table"
        }
      },

      "testimonials": {
        "layout": "Carousel with 1 card on mobile, 2 on md, 3 on lg.",
        "card_style": "Parchment inset + wax seal badge for rating; avatar as medieval crest.",
        "data_testids": {
          "section": "testimonials-section",
          "carousel": "testimonials-carousel"
        }
      },

      "paths_tabs": {
        "layout": "Full-width immersive Tabs with 3 triggers: The Knight / The Shadow / The Noble. Each tab is a mini 'class panel' with art silhouette + perks list.",
        "component": "Tabs + Card + Separator",
        "interaction": [
          "Active tab: gold underline + faint purple rune shimmer behind text.",
          "Tab hover: subtle ember specks around border (CSS)."
        ],
        "data_testids": {
          "section": "paths-section",
          "tabs": "paths-tabs",
          "tab_knight": "paths-tab-knight",
          "tab_shadow": "paths-tab-shadow",
          "tab_noble": "paths-tab-noble"
        }
      },

      "news_chronicles": {
        "layout": "Left: latest posts list. Right: featured chronicle card. Add 'Read' buttons.",
        "component": "Card + Badge + Separator",
        "data_testids": {
          "section": "news-section",
          "item": "news-item",
          "more": "news-more-button"
        }
      },

      "footer": {
        "layout": "3-4 columns, compact. Include social links icons.",
        "style": "Solid stone, thin top border, tiny crest watermark.",
        "data_testids": {
          "footer": "site-footer"
        }
      },

      "auth_modals": {
        "login_modal": {
          "component": "Dialog",
          "fields": ["email", "password"],
          "data_testids": {
            "open": "open-login-modal-button",
            "modal": "login-modal",
            "email": "login-email-input",
            "password": "login-password-input",
            "submit": "login-submit-button"
          }
        },
        "register_modal": {
          "component": "Dialog",
          "fields": ["username", "email", "password"],
          "data_testids": {
            "open": "open-register-modal-button",
            "modal": "register-modal",
            "username": "register-username-input",
            "email": "register-email-input",
            "password": "register-password-input",
            "submit": "register-submit-button"
          }
        }
      }
    },

    "button_system": {
      "shape": "Luxury/Elegant: rounded-lg (10–12px), tall, premium.",
      "variants": {
        "primary": {
          "name": "Aethoria Gold",
          "tailwind": "bg-[color:var(--aeth-gold)] text-[color:var(--aeth-stone-0)] shadow-[0_0_0_1px_rgba(255,255,255,0.06),0_10px_30px_var(--aeth-glow-gold)] hover:shadow-[0_0_0_1px_rgba(255,255,255,0.08),0_14px_40px_rgba(214,162,77,0.42)] hover:bg-[color:var(--aeth-amber)]",
          "motion": "transition-[background-color,box-shadow,opacity] duration-200"
        },
        "secondary": {
          "name": "Iron Outline",
          "tailwind": "bg-transparent border border-[color:var(--aeth-iron)] text-foreground hover:border-[color:var(--aeth-gold)] hover:text-[color:var(--aeth-gold)]",
          "motion": "transition-[color,border-color,background-color,opacity] duration-200"
        },
        "ghost": {
          "name": "Rune Ghost",
          "tailwind": "bg-transparent text-muted-foreground hover:text-foreground hover:bg-white/5",
          "motion": "transition-[color,background-color,opacity] duration-200"
        }
      },
      "press_state": "active:scale-[0.99] (avoid heavy transform stacks)",
      "focus": "focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-0"
    },

    "card_system": {
      "base": "Use shadcn Card with extra classes.",
      "aeth_card_class": "relative overflow-hidden rounded-xl bg-[color:var(--aeth-stone-2)] border border-border shadow-[0_10px_30px_rgba(0,0,0,0.55)]",
      "parchment_inset": "before:absolute before:inset-0 before:bg-[radial-gradient(circle_at_30%_20%,rgba(205,180,138,0.10),transparent_55%)] before:opacity-80 before:pointer-events-none",
      "hover": "hover:shadow-[0_14px_44px_rgba(0,0,0,0.68)] hover:border-[color:rgba(214,162,77,0.35)] transition-[box-shadow,border-color] duration-200"
    },

    "tabs_system": {
      "triggers": "Full width triggers with engraved look: bg stone, inner border, active gold underline.",
      "trigger_class": "data-[state=active]:text-[color:var(--aeth-gold)] data-[state=active]:shadow-[inset_0_-2px_0_0_rgba(214,162,77,0.9)]",
      "content_class": "mt-6"
    },

    "table_system": {
      "header": "Use slightly brighter stone background; uppercase labels with tracking.",
      "row_hover": "hover:bg-white/5",
      "rank_badges": "Badge variants: gold (top1), iron (top2), blood (top3)."
    }
  },

  "motion_and_micro_interactions": {
    "principles": [
      "Motion is atmospheric, not playful.",
      "Prefer opacity/box-shadow/background-color transitions.",
      "Use transforms sparingly and only on hero CTAs and small hover lifts."
    ],
    "recommended_libs": [
      {
        "name": "framer-motion",
        "why": "Entrance animations for sections, tabs content transitions, ticker fade edges.",
        "install": "npm i framer-motion",
        "usage": "Use Motion for section reveal (opacity + y: 8 -> 0). Respect prefers-reduced-motion."
      }
    ],
    "css_effects": {
      "rune_hover": "On feature card hover: add pseudo-element with radial glow (purple) + subtle animated background-position.",
      "ticker_fade_edges": "Mask left/right edges with gradient to hide hard cutoff: [mask-image:linear-gradient(to_right,transparent,black_10%,black_90%,transparent)]."
    },
    "particles": {
      "optional": {
        "library": "tsparticles (react-tsparticles)",
        "install": "npm i react-tsparticles tsparticles",
        "use": "Low density ember particles in hero only, behind content (opacity 0.25). Disable on mobile if performance issues."
      }
    }
  },

  "accessibility": {
    "contrast": [
      "Body text should be near-parchment (foreground) on stone background; avoid muted-on-muted.",
      "Gold text only on dark stone. Never gold on parchment inset."
    ],
    "focus_states": [
      "All interactive elements must have focus-visible rings (ring token).",
      "Modals trap focus via shadcn Dialog; ensure close button is accessible."
    ],
    "reduced_motion": [
      "Wrap marquee, particles, and entrance animations in prefers-reduced-motion checks."
    ]
  },

  "data_testid_rules": {
    "convention": "kebab-case describing role",
    "required_on": [
      "buttons",
      "links",
      "inputs",
      "tabs triggers",
      "carousel controls",
      "ticker items",
      "table rows (optional) and table wrapper",
      "key stat values",
      "error banners and toast triggers"
    ]
  },

  "image_urls": {
    "hero_background_or_side_art": [
      {
        "url": "https://images.unsplash.com/photo-1657868674989-4061c2d335fb?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NzB8MHwxfHNlYXJjaHwxfHxtZWRpZXZhbCUyMGNhc3RsZSUyMG5pZ2h0JTIwZm9nfGVufDB8fHxibGFja3wxNzczNzA4NTYwfDA&ixlib=rb-4.1.0&q=85",
        "description": "Cinematic castle at night; use as hero right-side image with dark overlay."
      }
    ],
    "textures_parchment": [
      {
        "url": "https://images.unsplash.com/photo-1631631648824-4c5a832ea1e4?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA2MTJ8MHwxfHNlYXJjaHwxfHxtZWRpZXZhbCUyMHBhcmNobWVudCUyMHRleHR1cmUlMjBkYXJrfGVufDB8fHxibGFja3wxNzczNzA4NTYzfDA&ixlib=rb-4.1.0&q=85",
        "description": "Parchment-like paper texture; use as subtle masked overlay inside cards (low opacity)."
      },
      {
        "url": "https://images.unsplash.com/photo-1654408618689-b737eed3c171?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA2MTJ8MHwxfHNlYXJjaHwzfHxtZWRpZXZhbCUyMHBhcmNobWVudCUyMHRleHR1cmUlMjBkYXJrfGVufDB8fHxibGFja3wxNzczNzA4NTYzfDA&ixlib=rb-4.1.0&q=85",
        "description": "Dark manuscript/book; use in News/Chronicles featured card background, heavily darkened."
      }
    ]
  },

  "instructions_to_main_agent": [
    "Set the app to dark mode by default: add class 'dark' to <html> or <body> and update index.css tokens per this guideline.",
    "Remove Create-React-App demo styles in App.css; do NOT center the app container.",
    "Implement each landing section as a dedicated React .jsx component; keep the page data-driven from FastAPI.",
    "Use shadcn/ui components listed above (Button, Card, Tabs, Table, Dialog, Carousel). Avoid native HTML dropdown/toast/calendar—use shadcn equivalents.",
    "Add data-testid to all interactive and key informational elements as specified.",
    "Ticker: implement CSS marquee with pause-on-hover and fade edges; ensure reduced motion fallback.",
    "Keep gradients compliant (decorative only, <=20% viewport impact). Prefer solids + textures for the medieval vibe.",
    "Icons: use lucide-react only; no emoji icons.",
    "Provide a reusable 'aeth-card' utility class and 'aeth-section' wrapper for consistent spacing and frames.",
    "Modals: use shadcn Dialog; style overlay as smoky vignette; dialog panel as stone with parchment inset.",
    "Add subtle noise overlay globally and crest corner SVG watermarks per section (opacity 10–18%)."
  ],

  "general_ui_ux_design_guidelines": [
    "You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms",
    "You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text",
    "NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json",
    "GRADIENT RESTRICTION RULE",
    "NEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc",
    "NEVER use dark gradients for logo, testimonial, footer etc",
    "NEVER let gradients cover more than 20% of the viewport.",
    "NEVER apply gradients to text-heavy content or reading areas.",
    "NEVER use gradients on small UI elements (<100px width).",
    "NEVER stack multiple gradient layers in the same viewport.",
    "ENFORCEMENT RULE:",
    "    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors",
    "How and where to use:",
    "   • Section backgrounds (not content backgrounds)",
    "   • Hero section header content. Eg: dark to light to dark color",
    "   • Decorative overlays and accent elements only",
    "   • Hero section with 2-3 mild color",
    "   • Gradients creation can be done for any angle say horizontal, vertical or diagonal",
    "- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc",
    "- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead.",
    "- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.",
    "- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.",
    "- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly",
    "    Eg: - if it implies playful/energetic, choose a colorful scheme",
    "           - if it implies monochrome/minimal, choose a black–white/neutral scheme",
    "Component Reuse:",
    "\t- Prioritize using pre-existing components from src/components/ui when applicable",
    "\t- Create new components that match the style and conventions of existing components when needed",
    "\t- Examine existing components to understand the project's component patterns before creating new ones",
    "IMPORTANT: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component",
    "Best Practices:",
    "\t- Use Shadcn/UI as the primary component library for consistency and accessibility",
    "\t- Import path: ./components/[component-name]",
    "Export Conventions:",
    "\t- Components MUST use named exports (export const ComponentName = ...)",
    "\t- Pages MUST use default exports (export default function PageName() {...})",
    "Toasts:",
    "  - Use `sonner` for toasts\"",
    "  - Sonner component are located in `/app/src/components/ui/sonner.tsx`",
    "Use 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals."
  ]
}

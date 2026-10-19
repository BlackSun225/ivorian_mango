# Prompt — Landing page "La Mangue Ivoirienne"

You are an elite, award-winning frontend design engineer. Build a single-page, scroll-driven storytelling landing page about the Ivorian mango, at the level of an Awwwards Site of the Year. The page must make visitors understand the reality of the sector (its value, the EU suspension caused by fruit flies, what farmers face) and leave them knowing concretely how they can support local farmers.

## 1. Non-negotiables

- **Language:** all visible copy in French (natural, editorial, correct French; no machine-translated feel). Code, comments and class names in English.
- **Theme:** light. Warm off-white base, never pure white or flat colours.
- **Fully responsive:** mobile first (360px), tablet, desktop, wide (1920px). Every pinned or horizontal-scroll effect must have a clean mobile fallback (vertical stack, simplified motion). No horizontal scrollbar at any width: wrap everything in `<main class="overflow-x-hidden w-full max-w-full">`.
- **Accessibility:** respect `prefers-reduced-motion` (disable scrub/pin, keep simple fades), semantic HTML, alt text in French, AA contrast, visible focus states, keyboard-navigable nav.
- **Performance:** Lighthouse 90+ on mobile. Lazy-load images, use `next/image`, animate only `transform` and `opacity`, kill ScrollTriggers on unmount.
- **No emojis** anywhere (code, comments, UI).
- **Facts:** use only the data provided in section 5. Do not invent statistics, dates, brands or quotes. Any figure displayed must keep its source in a discreet footnote/source line.

## 2. Tech stack

- Next.js (App Router) + TypeScript + Tailwind CSS
- GSAP + ScrollTrigger via `@gsap/react` (`useGSAP`), Lenis for smooth scrolling (synced with ScrollTrigger)
- `@phosphor-icons/react` for icons
- Inline SVG for all illustrations (see section 4.6), animated with GSAP (path drawing, morphs, parallax layers)

## 3. Design direction (gpt-taste)

Follow the gpt-taste rules strictly. Before writing any UI code, output a `<design_plan>` block that contains:

1. **Mock Python RNG execution** (seed = character count of this prompt) confirming the selections below, or re-rolling only within the allowed options.
2. **AIDA check:** Navigation, Attention (Hero), Interest (Bento), Desire (GSAP scroll storytelling), Action (CTA + footer).
3. **Hero math verification:** state the `max-w` class on the H1 and prove it stays on 2 to 3 lines at desktop and 3 lines max on mobile.
4. **Bento density verification:** prove the col-span/row-span values interlock with zero empty cells and that `grid-flow-dense` is applied.
5. **Label sweep and button check:** no meta-labels ("SECTION 01", "À PROPOS", "CHAPITRE 2"...), perfect button text contrast.

**Pre-selected direction** (adapted to a light theme and to this story):

- **Typography:** Cabinet Grotesk (display) + Satoshi (body). Never Inter. Display headings very large but in ultra-wide containers (`max-w-6xl`, `clamp(3rem, 5vw, 5.5rem)`).
- **Palette (tokens on `:root`):**
  - `--cream` #FBF6EC (background), `--sand` #F2E6D0 (surfaces)
  - `--mango` #F4A300 and `--mango-deep` #E8730C (accents, ripe flesh)
  - `--leaf` #2F5D3A (Ivorian orchard green, secondary accent)
  - `--earth` #3B2A1E (text, near-black brown)
  - `--alert` #B23A1F (used only in the fruit-fly crisis chapter)
  - Grain texture overlay (subtle SVG noise) and soft radial mango-coloured blurs. Avoid flat colour blocks.
- **Hero architecture:** Cinematic Center, light version: centred wide H1, exactly two high-contrast CTAs, a full-bleed orchard image behind with a warm cream radial wash (not a dark one).
- **Component arsenal:** inline typography images (pill-shaped mango photos inside big headings), horizontal accordion (derived products), infinite marquee (French typography of producing regions and varieties).
- **GSAP paradigms:** scroll pinning split (title pinned left, content scrolling right), scrubbing word-by-word text reveal (opacity 0.1 to 1), card stacking, image scale-and-fade (0.8 to 1.0 on enter, fade to 0.2 on exit).
- **Spacing:** huge vertical padding between chapters (`py-32 md:py-48`). Each chapter feels like a distinct cinematic scene.
- **Hover physics:** every clickable card and image scales inside an `overflow-hidden` container (`group-hover:scale-105 duration-700 ease-out`).
- **Images:** use `https://picsum.photos/seed/{keyword}/1920/1080` as placeholders with warm filters (sepia-tinted, contrast-110), and list in a comment every real photo needed (orchard in Korhogo, harvest, packing station, market stall, dried mango, etc.) so they can be replaced with authentic Ivorian photos.

**Signature motion idea:** a single SVG mango acts as the narrative thread. It ripens (green to golden to orange) as the user scrolls through the first chapters, gets "attacked" (small fly silhouettes, red tint, cracked outline) in the crisis chapter, then splits into the derived products in the transformation chapter. Keep it light and elegant, never gory or alarmist.

## 4. Page structure and content (all copy in French)

### 4.0 Navigation
Floating glass pill (light, `backdrop-blur`, cream at 70% opacity). Logo wordmark "Mangue de Côte d'Ivoire" (placeholder), anchors: Histoire, Nutrition, Origines, La crise, Transformer, Agir. Primary button "Soutenir les producteurs". A thin mango-coloured scroll progress bar under the pill. Mobile: full-screen menu with staggered link reveal.

### 4.1 Hero (Attention)
- H1, 2 lines max, with an inline pill image of a sliced mango, e.g. "Le fruit d'or du Nord ivoirien mérite mieux qu'une frontière fermée."
- One short sub-line on the stakes (100 000 personnes vivent de la mangue).
- CTAs: "Découvrir l'histoire" (scrolls) and "Comment aider" (anchor to the final chapter).
- No stats, badges or pill-tags in the hero. Subtle scroll cue.

### 4.2 Histoire de la mangue
- Scroll pinning split: title pinned left, a vertical timeline scrolling right with 4 to 5 steps: domestication in South/Southeast Asia (Indo-Burma region) some 4,000 years ago; spread by traders across Asia and the Indian Ocean; arrival in Africa via trade routes and Portuguese navigators; development of commercial orchards in northern Côte d'Ivoire; today, Kent becomes the flagship export variety.
- Each step: short text, small SVG illustration, image scale-and-fade.
- Note in the code: dates must be phrased as approximate ("environ", "vers le XVIe siècle") unless verified.

### 4.3 Ce que contient une mangue (Interest — gapless bento)
- Bento of 4 to 5 cards, `grid-flow-dense`, zero empty cells. Values per 100 g of raw mango (approximate, USDA FoodData Central; verify before launch):
  - Énergie: environ 60 kcal; sucres: environ 14 g; fibres: environ 1,6 g
  - Vitamine C: environ 36 mg (près de 40 % des apports journaliers)
  - Vitamine A (bêta-carotène): environ 54 µg ER
  - Folates (B9): environ 43 µg; vitamines E, K et B6
  - Minéraux: potassium (environ 168 mg), magnésium, cuivre
- Numbers count up on enter. The big card shows the SVG mango in cross-section with nutrient callouts drawn by path animation.

### 4.4 Où trouver la mangue ivoirienne
- Stylised SVG map of Côte d'Ivoire (not a copied map asset) highlighting the 9 producing regions, with the main ones named: Poro (Korhogo), Tchologo (Ferkessédougou), Bagoué (Boundiali), Hambol (Katiola). Regions light up sequentially on scroll.
- Key facts: 20 000 hectares de vergers, environ 180 000 tonnes par an, environ 5 000 producteurs.
- Season: the marketing campaign usually starts in March.
- Varieties: Kent (main export variety), plus local and other varieties (Amélie, Keitt, Brooks...).
- Where consumers can find it: local markets, producer cooperatives, processing units, the interprofession (OIA Inter-Mangues). No invented shop names.
- Infinite marquee below: region and variety names in huge outlined typography.

### 4.5 La crise: la mouche des fruits et le marché européen (Desire — emotional core)
- Palette shifts subtly: `--alert` accents appear, grain intensifies, the SVG mango gets attacked.
- Scrubbing word-by-word reveal of a central paragraph explaining: since 1 August 2026, exports of fresh Ivorian mangoes to the EU are suspended after repeated interceptions of infested lots by EU authorities. The EU tightened its fruit-fly rules in 2019.
- Animated bar chart (GSAP, SVG) of interceptions: 32 (2024), 12 (2025), 27 (2026).
- Card stacking sequence, one card per hardship farmers face:
  1. Le ravageur: fruit flies (mainly *Bactrocera dorsalis*) can cause 50 to 80 % production losses; untreated orchards studied in the North exceeded 75 % infestation.
  2. Un marché perdu: the EU took about 35 000 t in 2025 and roughly 66 % of mango export earnings (about US$25 million out of US$38 million); main buyers France, Belgium, Netherlands.
  3. L'impact humain: about 100 000 people live from the sector; an economic threat estimated at over 7 milliards FCFA.
  4. Une minorité, des conséquences pour tous: 15 % of exporters were responsible for more than two-thirds of the rejections; 15 operators and 9 packing stations are excluded from the 2027 campaign.
  5. Le compte à rebours: the State plans 3,5 milliards FCFA, more than 3 million traps, full traceability from orchard to port, an independent audit, and aims for a return to the EU market in the 2027 campaign, without a guaranteed date since the decision belongs to the European Commission.
- Tone: factual, respectful, not sensationalist. The government does not contest the EU decision; show that the problem is solvable (integrated pest management reduced infestation below 5 % in trials).

### 4.6 Transformer pour ne plus dépendre (horizontal accordion + illustrations)
- Intro with a large heading containing an inline pill image: the idea that each mango processed locally is value that stays in Côte d'Ivoire, and that the domestic and regional (ECOWAS) markets can absorb more.
- Horizontal accordion on desktop (vertical slices expanding on hover/focus), swipeable cards on mobile. One custom inline SVG illustration per product, in a consistent flat-editorial style (mango palette, leaf green, earth brown), each with a small idle animation:
  1. Mangue séchée (dried slices on a drying rack)
  2. Jus et nectar (bottle with pouring liquid)
  3. Purée et pulpe (for pastry, yogurt, baby food)
  4. Confiture et marmelade (jar)
  5. Chutney et achards (savoury condiments)
  6. Glaces et sorbets
  7. Poudre de mangue (spice and smoothie ingredient)
  8. Beurre de noyau de mangue (cosmetics, from the kernel)
  9. Farine de noyau et aliment pour bétail (from kernels and peels)
  10. Compost et biogaz (zero-waste: peels and unsold fruit)
- Each slice: product name, one sentence on the value added, and who it creates jobs for (women's cooperatives, small processing units, etc.). No invented figures.
- Below: a short "Diversifier les marchés" strip: local consumption, regional exports, other international markets, organic and fair-trade niches, cold chain and drying units in producing areas.

### 4.7 Comment aider (Action)
- Massive high-contrast CTA block (deep mango or earth background, cream text).
- 4 concrete actions as large interactive cards: acheter local et de saison; choisir des produits transformés en Côte d'Ivoire; acheter directement aux coopératives; partager la page / parler de la filière. Optional: a placeholder newsletter signup (front-end only, clearly marked as placeholder).
- Final line echoing the hero.

### 4.8 Footer
Clean, light. Anchors, a "Sources" list (Ministère de l'Agriculture via AIP, Agence Ecofin, RFI, Food Business MEA, study in *Phytoparasitica* 2026, USDA FoodData Central), credits for photos, legal placeholder.

## 5. Verified data (only source of truth for figures)

- EU suspension of fresh Ivorian mango imports since 1 August 2026, announced by Agriculture Minister Bruno Nabagné Koné on 15 October 2026.
- Interceptions: 32 (2024), 12 (2025), 27 (2026). EU rules tightened in 2019.
- Sector: about 180 000 t/year; about 35 000 t to the EU (2025); about 5 000 producers; about 100 000 people; 20 000 ha in 9 regions (incl. Poro, Tchologo, Hambol, Bagoué).
- Mango is Côte d'Ivoire's second fruit export after banana; first exporter in West Africa; 3rd supplier of Europe.
- 2025: EU imports of about US$25 million, about 66 % of US$38 million mango export earnings; main destinations France, Belgium, Netherlands.
- 15 % of exporters responsible for more than two-thirds of rejections; 15 operators and 9 stations excluded from the 2027 campaign; economic threat over 7 milliards FCFA.
- Response plan: 3,5 milliards FCFA, over 3 million traps before next flowering, controls from orchard to exit point, lot traceability to orchard/producer/harvest technician, independent audit, national unit created end of August 2026, mango integrated into the Conseil Coton-Anacarde-Karité. Target: 2027 campaign, no firm date.
- Fruit flies: 50 to 80 % potential losses; in northern Côte d'Ivoire trials (2023-2024), untreated plots over 75 % infestation, integrated pest management below 5 %.

## 6. Deliverables

1. The `<design_plan>` block.
2. Full project code: `app/page.tsx`, one component per chapter in `components/`, SVG illustrations in `components/illustrations/`, a `lib/content.ts` holding all French copy and data (so text and figures are editable in one place), global styles with the colour tokens.
3. A short list of real photos to source and the exact places to swap them in.

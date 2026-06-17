---
name: zedge-seo-metadata
description: >
  Expert-level Zedge SEO metadata generator for mobile wallpapers and ringtones.
  Use this skill whenever the user wants to upload content to Zedge and needs
  optimized titles, tags, or descriptions — even if they just say "write metadata
  for my wallpapers", "Zedge tags", "optimize for Zedge", or "help me rank on
  Zedge". Also triggers for batch wallpaper uploads, Zedge store optimization,
  mobile wallpaper SEO, or any request mentioning Zedge ranking/visibility.
  Handles copyright and trademark safety automatically.
---

# Zedge SEO Metadata Skill

Generates platform-optimized Title + Tags + Description for Zedge wallpaper
uploads. Applies Zedge's ranking signal model, keyword clustering, copyright
safety rules, and strict field constraints in a single structured output per file.

---

## How Zedge's Ranking Algorithm Works (Key Signals)

Understanding these signals shapes every metadata decision:

| Signal | Weight | What It Means for Metadata |
|---|---|---|
| **Keyword relevance** | Very High | Title and tags must match real user search queries |
| **Download velocity** | High | An enticing title drives the initial tap → download |
| **Tag coverage** | High | Tags serve as the keyword index; all 10 slots must be used |
| **Category fit** | Medium | Description terms help Zedge classify the content correctly |
| **Freshness** | Medium | Trending keywords beat evergreen ones for new uploads |
| **Engagement (saves/shares)** | Medium | Emotional/aspirational language improves this passively |
| **Exact-match search** | High | At least 2–3 tags must exactly replicate likely user searches |

---

## Legal & Safety Rules (Non-Negotiable)

Before writing a single character, apply the copyright filter:

### ❌ NEVER Use
- **Branded character or franchise names** (e.g., Spider-Man, Goku, Batman, Mario,
  Pikachu, Naruto, Attack on Titan, etc.) — these are registered trademarks.
- **Movie, game, or album titles** as tags/titles (e.g., "Cyberpunk 2077", "Avatar").
- **Brand logos or company names** (Apple, Nike, Supreme, etc.).
- **Real person names** used in a commercial context without clear permission.
- **Song titles or artist names** as primary keywords.
- **"Official"**, **"Licensed"**, **"Original"**, or similar terms implying
  authorized partnership when none exists.

### ✅ ALWAYS Use Instead
- **Generic descriptive terms**: dark warrior, anime girl, glowing city, fantasy
  knight, digital hero, samurai, sci-fi cityscape, etc.
- **Style/aesthetic labels**: cyberpunk, vaporwave, lo-fi, gothic, neon aesthetic,
  dark academia, etc.
- **Visual element descriptors**: rain, bokeh, cherry blossoms, neon lights,
  holographic, geometric, etc.
- **Emotion/mood words**: peaceful, epic, mysterious, dreamy, powerful, serene, etc.

> **When in doubt, describe what you SEE, not what it REFERENCES.**
> A neon-lit samurai is "neon-samurai-art" not "Afro-Samurai" (trademark).

---

## Field Specifications & Optimization Rules

### 1. TITLE (max 70 characters)

**Structure formula:**
```
[Mood/Style Adjective] + [Main Subject] + [Format/Quality] + [Platform Hint]
```

**Rules:**
- Lead with the highest-volume keyword for this theme.
- Include quality signal: `4K`, `HD`, `Ultra HD`, `AMOLED`, or `Full HD`.
- Use natural language — Zedge titles appear in search snippets like a headline.
- Avoid ALL CAPS (looks spammy, may be penalized).
- Avoid trademark terms (see Legal section).
- Aim for 50–70 characters (longer titles get more keyword surface area).
- Emotional/aspirational words boost CTR: "Stunning", "Epic", "Aesthetic",
  "Dark", "Glowing", "Dreamy", "Mystic", "Vibrant", "Ethereal", "Chill".

**Good:** `Neon Samurai Rain Art 4K – Dark Anime Aesthetic Wallpaper`  
**Bad:** `Wallpaper HD` (too vague), `NARUTO NEON FIRE!!` (trademark + all caps)

---

### 2. TAGS (exactly 10, comma-separated, no spaces after commas)

**Rules:**
- No spaces inside any tag. Compound with hyphens (`dark-anime`) or
  concatenation (`darkwallpaper`) where needed.
- Allowed characters: `a-z A-Z 0-9 - _ .`
- Mix strategy — use all 10 slots as follows:

| Slot(s) | Tag Type | Purpose |
|---|---|---|
| 1–2 | **Exact user searches** | Match literal queries users type |
| 3–4 | **Theme cluster** | Broader category terms |
| 5–6 | **Style / Aesthetic** | Trend-based labels |
| 7–8 | **Visual elements** | Specific things in the image |
| 9 | **Quality/Format** | `4K`,`HD`,`AMOLED`,`ultra-HD` |
| 10 | **Mood / Emotion** | The feeling the image evokes |

**Volume tiers to mix:**
- 🔴 High-volume (1–2 tags): `wallpaper`,`background`,`4K`
- 🟡 Mid-volume (4–5 tags): `anime-wallpaper`,`dark-aesthetic`,`neon-art`
- 🟢 Niche/Long-tail (3–4 tags): `glowing-samurai`,`rainy-night-art`,`cyber-warrior`

> Long-tail tags have less competition and rank faster for new uploads.
> Don't stack all high-volume tags — you'll drown in competition.

---

### 3. DESCRIPTION (under 200 characters)

**Rules:**
- Write as a punchy 1–2 sentence visual hook, not a list.
- Include 2–3 natural keyword insertions (not forced repetition).
- End with a soft call-to-action when space allows: "Set it now!", "Download free!"
- Avoid emojis (Zedge strips or may misparse them).
- No line breaks — single flowing text block.
- Stay under 200 characters including spaces.

**Good (178 chars):**  
`A lone warrior stands in a rain-soaked neon city. Dark anime aesthetic in
stunning 4K. Perfect AMOLED wallpaper for your phone. Download free!`

**Bad:**  
`This is a wallpaper of a samurai. HD wallpaper. Anime. Download.` (too flat,
no atmosphere, wasted keyword opportunity)

---

## Batch Processing Workflow

When the user provides multiple files, process them sequentially. For each file:

1. **Parse the visual description** — extract subject, setting, mood, style, colors.
2. **Run the copyright filter** — replace any IP-adjacent terms with generic ones.
3. **Build a keyword cluster** — 8–12 candidate keywords ranked by estimated search
   volume for that theme. Select the top performers for tags and title.
4. **Draft the title** — apply the formula; count characters; adjust.
5. **Assign 10 tags** — apply the slot strategy above; verify format compliance.
6. **Write the description** — keep under 200 characters; check with a mental
   character count (or estimate: ~5 chars/word average).
7. **Output in a clean code block** labelled with the verbatim filename.

---

## Output Format (strict)

For each file, output exactly this structure inside one code block:

```
File: [filename verbatim]

Title:
[Title here — max 70 chars]

Tags:
[tag1],[tag2],[tag3],[tag4],[tag5],[tag6],[tag7],[tag8],[tag9],[tag10]

Description:
[Under 200 characters. Single paragraph. No line breaks.]
```

> ⚠️ Do not merge multiple files into one block. Each file gets its own block.
> ⚠️ Do not add commentary or explanations inside the code blocks.
> ⚠️ Do verify tag count is exactly 10 before outputting.

---

## Theme-Keyword Reference

Load `references/theme-keyword-clusters.md` when you need pre-researched keyword
lists for a specific theme. It contains high/mid/low-volume keyword clusters for
the most common Zedge wallpaper categories.

Read it before generating metadata when:
- The user's theme matches one of the listed categories.
- You are unsure which keywords have the best search volume for a theme.
- The user asks you to "maximize reach" or "use the best keywords."

---

## Quality Self-Check (run mentally before output)

Before finalizing each file's metadata, verify:

- [ ] Title ≤ 70 characters?
- [ ] Title includes a quality signal (4K / HD / AMOLED)?
- [ ] Title contains NO trademarks or brand names?
- [ ] Exactly 10 tags?
- [ ] All tags use only `a-z A-Z 0-9 - _ .` with NO spaces?
- [ ] Tags use the slot strategy (exact-search + theme + style + visual + quality + mood)?
- [ ] Description ≤ 200 characters?
- [ ] Description reads naturally (not a keyword dump)?
- [ ] Zero trademarked terms in any field?
- [ ] Filename reproduced verbatim in the block header?

If any check fails, fix before outputting.

---

## Example — End-to-End Run

**User input:**
```
Theme: Cyberpunk Anime Aesthetics
1.jpeg: Neon samurai standing under the rain in a futuristic city
```

**Output:**

```
File: 1.jpeg

Title:
Neon Samurai Rain – Dark Cyberpunk Anime 4K AMOLED Wallpaper

Tags:
anime-wallpaper,cyberpunk-wallpaper,neon-samurai,dark-aesthetic,4K,neon-art,rainy-city,sci-fi-warrior,AMOLED,epic-wallpaper

Description:
A glowing warrior stands in a rain-drenched neon city. Dark cyberpunk anime art in crisp 4K. The ultimate AMOLED wallpaper. Download free!
```

**Character counts verified:** Title = 58 ✅ | Tags = 10 ✅ | Description = 138 ✅

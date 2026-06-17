---
name: Precision Dark
colors:
  surface: '#15121b'
  surface-dim: '#15121b'
  surface-bright: '#3b3742'
  surface-container-lowest: '#0f0d15'
  surface-container-low: '#1d1a23'
  surface-container: '#211e27'
  surface-container-high: '#2c2832'
  surface-container-highest: '#37333d'
  on-surface: '#e7e0ed'
  on-surface-variant: '#cbc3d7'
  inverse-surface: '#e7e0ed'
  inverse-on-surface: '#322f39'
  outline: '#958ea0'
  outline-variant: '#494454'
  surface-tint: '#d0bcff'
  primary: '#d0bcff'
  on-primary: '#3c0091'
  primary-container: '#a078ff'
  on-primary-container: '#340080'
  inverse-primary: '#6d3bd7'
  secondary: '#c8c5ca'
  on-secondary: '#303033'
  secondary-container: '#47464a'
  on-secondary-container: '#b6b4b8'
  tertiary: '#ffb869'
  on-tertiary: '#482900'
  tertiary-container: '#ca801e'
  on-tertiary-container: '#3f2300'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e9ddff'
  primary-fixed-dim: '#d0bcff'
  on-primary-fixed: '#23005c'
  on-primary-fixed-variant: '#5516be'
  secondary-fixed: '#e4e1e6'
  secondary-fixed-dim: '#c8c5ca'
  on-secondary-fixed: '#1b1b1e'
  on-secondary-fixed-variant: '#47464a'
  tertiary-fixed: '#ffdcbb'
  tertiary-fixed-dim: '#ffb869'
  on-tertiary-fixed: '#2c1700'
  on-tertiary-fixed-variant: '#673d00'
  background: '#15121b'
  on-background: '#e7e0ed'
  surface-variant: '#37333d'
typography:
  display:
    fontFamily: Geist
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.02em
  h1:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  h2:
    fontFamily: Geist
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  h3:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Geist
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-md:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
  code:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 0.25rem
  sm: 0.5rem
  md: 1rem
  lg: 1.5rem
  xl: 2rem
  container-margin: 1.5rem
  gutter: 1rem
---

## Brand & Style

The design system is built for high-productivity desktop applications where focus and information density are paramount. It adopts a **Modern Corporate** aesthetic with a lean toward **Minimalism**, stripping away unnecessary decorative elements to prioritize content. 

The personality is technical, reliable, and precise. By utilizing a "Dark Mode First" philosophy, the UI reduces eye strain during long working sessions while maintaining high legibility through strict adherence to contrast ratios. The aesthetic is heavily influenced by modern developer toolchains: sharp, functional, and organized.

## Colors

The palette is centered on a "Zinc" grayscale to provide a neutral foundation that doesn't distract the user. 

- **Primary (#8b5cf6):** A vibrant Violet used exclusively for primary actions, active states, and focus indicators.
- **Surface & Background:** We utilize a tiered dark approach. The base background is nearly black (#09090b) to provide maximum depth, while surfaces (cards, modals, sidebars) use #18181b to create subtle elevation.
- **Borders:** A consistent #27272a is used for all structural lines. It is designed to be felt rather than seen, providing just enough definition between containers.
- **Feedback:** Use standard semantic colors (Red 600 for destructive, Green 600 for success) but slightly desaturated to match the dark environment.

## Typography

This design system uses **Geist** for its systematic, neutral, and highly legible characteristics in dark environments. For data-heavy views or technical identifiers, **JetBrains Mono** is utilized.

To maintain a "utility tool" feel, typography is kept compact. The default body size is **14px**, allowing for higher information density without sacrificing readability. Headlines use tighter letter spacing and semi-bold weights to create a distinct hierarchy against the monochromatic background.

## Layout & Spacing

The layout follows a **Fixed-Fluid Hybrid** model. Navigation and sidebars are fixed widths (e.g., 240px or 64px collapsed), while the primary workspace fluidly expands.

A strict **4px baseline grid** is enforced to ensure alignment. To maximize vertical space, vertical padding in lists and tables is reduced to 8px (sm) or 10px (md). Margins between major sections should be 24px (lg) to provide enough visual "breathing room" amidst high-density data.

## Elevation & Depth

Depth is primarily communicated through **Tonal Layering** and **Subtle Outlines** rather than heavy shadows.

1.  **Level 0 (Base):** #09090b - The main canvas.
2.  **Level 1 (Card/Surface):** #18181b - Floating panels, sidebars, and main content containers. Features a 1px border of #27272a.
3.  **Level 2 (Popovers/Modals):** #18181b - These use a slightly more pronounced shadow (0 10px 15px -3px rgba(0,0,0,0.5)) and the same #27272a border to separate from the surface.

Interactive elements (buttons, inputs) should feel "flat" on the surface, using hover states (slight background lightening) to indicate interactivity.

## Shapes

The design system uses a **Rounded** language. 
- **Small elements** (buttons, inputs, checkboxes): 0.5rem (8px) radius.
- **Large elements** (cards, modals, panels): 0.75rem (12px) radius.

This consistency creates a contemporary, "app-like" feel that softens the industrial nature of the dark color palette. Avoid full-circle pills unless used for status indicators or tags.

## Components

### Buttons
- **Primary:** Violet background (#8b5cf6), white text. High contrast. No shadow.
- **Secondary:** Transparent background, #27272a border, white text.
- **Ghost:** No background or border. Violet text on hover.

### Input Fields
- **Default:** #09090b background with a 1px #27272a border.
- **Focus:** Border changes to #8b5cf6 with a subtle 2px ring spread of the same color at 20% opacity.

### Lists & Tables
- **Rows:** 1px solid #27272a bottom border. Hover state uses #18181b background.
- **Density:** Use 8px vertical padding for standard density; 4px for "compact" views.

### Cards
- Background: #18181b.
- Border: 1px solid #27272a.
- Padding: 1.25rem (20px) for standard layout.

### Chips/Badges
- Small, uppercase 12px text. 
- Subtle background (Primary color at 10% opacity) with matching text color.
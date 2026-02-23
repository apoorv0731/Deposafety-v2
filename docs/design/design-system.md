# DepoSafety V2 - Design System

## Brand Identity

### Name
**DepoSafety** - "Deposit Safety" for security deposit protection

### Tagline
"Forensic-Grade Evidence for Your Security Deposit"

### Logo Concept
Shield + Camera + 3D Cube = Trust, Evidence, Technology

## Color Palette

### Primary Colors
| Name | Hex | Usage |
|------|-----|-------|
| Trust Blue | #2563EB | Primary buttons, links |
| Legal Navy | #1E3A5F | Headers, text |
| Evidence Gold | #F59E0B | CTAs, highlights |

### Secondary Colors
| Name | Hex | Usage |
|------|-----|-------|
| Success Green | #10B981 | Verified, completed |
| Warning Amber | #F59E0B | Processing, pending |
| Error Red | #EF4444 | Errors, tampered |
| Neutral Gray | #6B7280 | Secondary text |

### Background Colors
- White: #FFFFFF
- Light Gray: #F9FAFB
- Border: #E5E7EB

## Typography

### Font Family
- **Primary:** Inter (Google Fonts)
- **Monospace:** JetBrains Mono (for hashes, code)

### Hierarchy
| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| H1 | 36px | 700 | 1.2 |
| H2 | 30px | 600 | 1.3 |
| H3 | 24px | 600 | 1.3 |
| Body | 16px | 400 | 1.5 |
| Small | 14px | 400 | 1.5 |
| Caption | 12px | 500 | 1.4 |

## Spacing System

Base unit: 4px

| Token | Value |
|-------|-------|
| xs | 4px |
| sm | 8px |
| md | 16px |
| lg | 24px |
| xl | 32px |
| 2xl | 48px |
| 3xl | 64px |

## Components

### Buttons

**Primary Button**
- Background: Trust Blue (#2563EB)
- Text: White
- Padding: 12px 24px
- Border-radius: 8px
- Font-weight: 600
- Hover: Darken 10%

**Secondary Button**
- Background: White
- Border: 1px solid Border
- Text: Legal Navy
- Padding: 12px 24px
- Border-radius: 8px

**Danger Button**
- Background: Error Red
- Text: White
- Used for: Delete, Revoke

### Cards

**Property Card**
- Background: White
- Border: 1px solid Border
- Border-radius: 12px
- Padding: 24px
- Shadow: 0 1px 3px rgba(0,0,0,0.1)
- Hover: Shadow increases

**Evidence Card**
- Background: Light Gray
- Border-left: 4px solid Success Green
- Border-radius: 8px
- Padding: 16px

### Forms

**Input Field**
- Border: 1px solid Border
- Border-radius: 8px
- Padding: 12px 16px
- Focus: Border color Trust Blue
- Error: Border color Error Red

**Label**
- Font-size: 14px
- Font-weight: 500
- Color: Legal Navy
- Margin-bottom: 4px

### Status Badges

| Status | Background | Text | Icon |
|--------|-----------|------|------|
| Verified | Success Green | White | Checkmark |
| Processing | Warning Amber | White | Spinner |
| Pending | Neutral Gray | White | Clock |
| Tampered | Error Red | White | Alert |

## Icons

Use **Lucide React** icons:
- Home (properties)
- Camera (capture)
- Shield (security)
- FileCheck (evidence)
- Upload (upload)
- User (profile)
- Settings (settings)
- LogOut (logout)

## Animations

### Transitions
- Default: 200ms ease-in-out
- Page transitions: 300ms
- Loading spinner: 1s infinite

### Micro-interactions
- Button hover: Scale 1.02
- Card hover: Lift shadow
- Input focus: Border glow

## Responsive Breakpoints

| Breakpoint | Width | Target |
|------------|-------|--------|
| Mobile | < 640px | Phones |
| Tablet | 640-1024px | Tablets |
| Desktop | > 1024px | Laptops/Desktops |

## Dark Mode (Future)

- Background: #0F172A
- Surface: #1E293B
- Text: #F1F5F9

## Accessibility

- Minimum contrast ratio: 4.5:1
- Focus indicators visible
- ARIA labels on interactive elements
- Keyboard navigation support

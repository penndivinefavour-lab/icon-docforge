# PRODUCT_IDENTITY

# ICON DocForge — Product Identity Guidelines

## Brand Colors

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Primary Deep | #1a2744 | Navy | Header, footer, primary backgrounds |
| Primary Purple | #6b21a8 | Purple | CTAs, accents, brand mark |
| Accent Gold | #f5c518 | Gold | Highlights, badges, focus states |
| Success | #388e3c | Green | Completion states, confirmations |
| Error | #d32f2f | Red | Errors, warnings |
| Background | #f4f4f8 | Light Gray | Page background |
| Surface | #ffffff | White | Cards, modals |
| Text Primary | #1f2128 | Dark Navy | Body text |
| Text Muted | #6b7280 | Gray | Secondary text, labels |

## Typography

- **Primary Font**: Poppins (Google Fonts)
- **Fallback Stack**: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
- **Sizes**: 12px (caption), 14px (body), 16px (heading), 24px (display), 32px (hero)
- **Weights**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

## Iconography

- **Style**: Minimal, line-art icons where possible
- **Size**: 24px standard, 32px hero
- **Color**: Inherit from parent or use brand colors
- **Animation**: Subtle scale/opacity transitions only

## UI Components

### Buttons
- **Primary**: Purple background, white text, 12px border-radius
- **Secondary**: Gray border, transparent background
- **Ghost**: Transparent, no border, text only
- **Icon**: Circular, background on hover, no text

### Cards
- White background, 12px border-radius, subtle shadow
- Padding: 16px minimum
- Hover state: Purple border, increased shadow

### Forms
- Input border: 2px solid #e2e4ec
- Focus state: 2px solid #6b21a8
- Label: 13px, muted color, above input
- Error: 2px solid #d32f2f

### Loading States
- Progress bar: Purple to gold gradient
- Skeleton: Shimmer animation on cards
- Spinner: Rotating brand icon

### Empty States
- Illustration or icon (large)
- Heading: "No conversions yet"
- Subtext: "Select a file to get started"
- CTA: Primary button

## Screen Layouts

### Home Screen
```
[Topbar: Brand logo + title]
[Hero: "Document Conversion Studio" + privacy badge]
[Search bar]
[Category chips: All | Documents | PDF | Images | Office | Tools]
[Tools grid: 2 columns on mobile, 3 on tablet]
[Recent conversions (if any)]
[Footer: Copyright]
```

### Tool Screen
```
[Topbar: Back button + tool title]
[File drop zone or file picker button]
[Selected file info: name, size, type]
[Conversion options (if applicable)]
[Convert button]
[Progress indicator]
[Result area]
```

### Result Screen
```
[Topbar: Back button]
[File preview/thumbnail]
[File details: name, size, type]
[Actions: Open, Share, Save, Convert Another]
```

### Settings Screen
```
[Topbar: Back button + "Settings"]
[App info: version, build]
[Engine status: healthy/missing engines]
[Storage info]
[Diagnostics section]
[About section]
[Privacy policy link]
```

## Microcopy Guidelines

### Positive
- "Conversion complete"
- "Your file is ready"
- "Success! Your document was converted."

### Neutral
- "Processing..."
- "Please wait while we convert your file."
- "Select a file to continue."

### Error
- "Conversion failed. Please try again."
- "Unsupported file type."
- "File too large. Maximum size is 50MB."

### Privacy
- "🔒 Your files never leave your device"
- "All processing happens locally"
- "No data uploaded to any server"

## Accessibility

- Minimum touch target: 48x48dp
- Color contrast ratio: 4.5:1 minimum
- Screen reader labels on all interactive elements
- Focus indicators: 3px gold outline
- Reduced motion support via prefers-reduced-motion

## Do Not Use

- ❌ Glassmorphism (blur effects)
- ❌ Excessive gradients
- ❌ AI-themed language ("Powered by AI")
- ❌ Dark mode toggle (unless implemented)
- ❌ User accounts/login
- ❌ Analytics/tracking
- ❌ Push notifications
- ❌ Cloud backup prompts

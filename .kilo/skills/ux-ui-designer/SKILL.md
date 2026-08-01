---
name: ux-ui-designer
description: >-
  User experience design, interface prototyping, usability testing, visual
  design, and accessibility for the Descombinator Pro desktop application.
license: MIT
metadata:
  category: design
  project: descombinator-pro
---

# UX/UI Designer

## Responsibilities

- Design the user experience for Descombinator Pro
- Create wireframes and interactive prototypes
- Define visual design language and component library
- Conduct usability testing and iterate on feedback
- Ensure accessibility compliance (WCAG 2.1 AA)

## Design Principles

1. **Zero-typing UX** — All actions navigable via buttons and clicks
2. **Immediate feedback** — Visual feedback for all user actions
3. **Progressive disclosure** — Advanced features hidden by default
4. **Consistent metaphors** — Familiar UI patterns from media players
5. **Error prevention** — Disable invalid actions, confirm destructive operations

## Key Screens

| Screen | Purpose |
|--------|---------|
| Welcome | File selection, recent files |
| Processing | Progress bar, cancel button, estimated time |
| Results | Play separated tracks, export options |
| Settings | Model selection, output format, performance |
| Export | Format selection, destination folder |

## Visual Design

### Color Palette

| Role | Light Mode | Dark Mode |
|------|-----------|-----------|
| Primary | #2563EB | #3B82F6 |
| Background | #FFFFFF | #1E1E1E |
| Surface | #F8FAFC | #2D2D2D |
| Text | #1E293B | #E5E5E5 |
| Accent | #10B981 | #34D399 |

### Typography

- **Font**: Segoe UI (Windows), SF Pro (macOS), Ubuntu (Linux)
- **Headings**: 16-20px, bold
- **Body**: 13-14px, regular
- **Captions**: 11-12px, regular

## Interaction Patterns

### File Loading

- Drag-and-drop zone
- File browser dialog
- Recent files list
- File type validation

### Separation Flow

1. User selects audio file
2. Preview waveform displayed
3. User clicks "Separate"
4. Progress indicator with cancel option
5. Results displayed with playback controls

### Playback Controls

- Play/Pause toggle
- Seek bar with position indicator
- Volume slider
- Track selection (vocals/instrumental)

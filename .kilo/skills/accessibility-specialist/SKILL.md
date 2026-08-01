---
name: accessibility-specialist
description: >-
  Accessibility compliance, WCAG guidelines, screen reader support, keyboard
  navigation, and inclusive design for the Descombinator Pro application.
license: MIT
metadata:
  category: design
  project: descombinator-pro
---

# Accessibility Specialist

## Responsibilities

- Ensure the application meets WCAG 2.1 AA standards
- Implement screen reader support
- Design keyboard navigation
- Create accessible color schemes
- Test with assistive technologies

## WCAG 2.1 AA Compliance

### Principles

| Principle | Requirements |
|-----------|-------------|
| Perceivable | Text alternatives, adaptable content, distinguishable |
| Operable | Keyboard navigation, enough time, seizures |
| Understandable | Readable, predictable, input assistance |
| Robust | Compatible with assistive technologies |

## Screen Reader Support

### Qt Accessibility

```python
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import QCoreApplication

class AccessibleButton(QPushButton):
    def __init__(self, text: str, description: str = ""):
        super().__init__(text)
        self.setAccessibleName(text)
        self.setAccessibleDescription(description)
        self.setToolTip(description)
```

### ARIA Labels

- All interactive elements have accessible names
- Buttons have descriptive labels
- Form fields have associated labels
- Status messages are announced

## Keyboard Navigation

### Tab Order

- Logical tab order through UI elements
- All interactive elements are focusable
- Visual focus indicators
- Keyboard shortcuts for common actions

### Shortcuts

| Action | Shortcut |
|--------|----------|
| Play/Pause | Space |
| Stop | S |
| Open File | Ctrl+O |
| Export | Ctrl+E |
| Settings | Ctrl+, |
| Quit | Ctrl+Q |

## Color and Contrast

### Contrast Ratios

| Element | Minimum Ratio |
|---------|--------------|
| Text | 4.5:1 |
| Large Text | 3:1 |
| UI Controls | 3:1 |
| Graphical Objects | 3:1 |

### Color Blind Friendly

- Don't rely on color alone for information
- Use patterns and icons in addition to color
- Test with color blindness simulators
- Provide alternative visual indicators

## Testing

### Tools

| Tool | Purpose |
|------|---------|
| NVDA | Screen reader (Windows) |
| VoiceOver | Screen reader (macOS) |
| Orca | Screen reader (Linux) |
| axe-core | Automated accessibility testing |
| WAVE | Web accessibility evaluation |

### Manual Testing

- Navigate with keyboard only
- Test with screen readers
- Check color contrast
- Verify focus indicators
- Test with high contrast mode

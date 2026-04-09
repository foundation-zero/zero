# Colors

A comprehensive color system with primitive and semantic color tokens that adapt to light and dark themes.

## Overview

The Zero UI color system is built on a foundation of primitive color scales that are then mapped to semantic color tokens. This approach ensures consistent theming across light and dark modes while maintaining semantic meaning in component design.

## Structure

Our color system is organized into several layers:

### [Primitives](./colors/primitives.md)

The foundational color scales that serve as the building blocks for our entire system:

- **Neutral** - Grayscale colors from white to black
- **Neutral Grey** - Alternative grayscale palette
- **Brand** - Primary brand colors in a full scale
- **Accent A** - Red/pink accent colors for destructive states
- **Accent B** - Yellow/amber accent colors for warning states  
- **Accent C** - Green accent colors for constructive states
- **Accent D** - Red accent colors for destructive states
- **Accent E** - Heating red accent colors
- **Accent F** - Cooling blue accent colors

### [Semantic Colors](./colors/semantic.md)

Contextual colors that provide meaning and automatically adapt between themes:

- **Base Colors** - Background, foreground, muted, and disabled colors
- **Interactive Colors** - Primary, secondary, accent, and focus ring colors  
- **State Colors** - Success, warning, error, and info colors
- **Brand Colors** - Primary brand colors and variations
- **Input Colors** - Specialized colors for form elements

### [Component Colors](./colors/components.md)

Specific color assignments for component states and variations:

- **Input Colors** - Specialized colors for form inputs and interactive fields
- **Button Colors** - Colors for button components and states
- **Card Colors** - Colors for card components and containers
- **Popover Colors** - Colors for dropdowns, tooltips, and overlays
- **Sidebar Colors** - Navigation sidebar and menu colors
- **Chart Colors** - Data visualization color palette

## Usage

Colors are available as CSS custom properties and Tailwind CSS utilities. All primitive colors use the format `--color-{scale}-{step}` or `text-{scale}-{step}` / `bg-{scale}-{step}` in Tailwind.


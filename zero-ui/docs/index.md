# Zero UI Components

Welcome to the Zero UI component library documentation. This library provides a collection of reusable Vue 3 components built with Tailwind CSS and shadcn/ui design principles.

## Features

- 🎨 **Modern Design** - Built with Tailwind CSS and shadcn/ui
- ⚡ **Vue 3** - Composition API and TypeScript support
- 🔧 **Highly Customizable** - Variants and size options
- 📱 **Responsive** - Mobile-first design approach
- ♿ **Accessible** - ARIA compliant components
- 🎯 **Comprehensive Color System** - Primitive, semantic, and component-specific colors
- 🌙 **Theme Support** - Light and dark mode with seamless transitions

## Quick Start

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev

# View component documentation
pnpm docs:dev
```

## Available Resources

Our design system includes comprehensive documentation for:

### Design System Foundation

- **[Colors](/colors)** - Complete color system with live examples and theme support
  - **[Primitives](/colors/primitives)** - Foundation color scales (Neutral, Brand, Accents)
  - **[Semantic Colors](/colors/semantic)** - Contextual colors with meaning (Base, Interactive, State)
  - **[Component Colors](/colors/components)** - Specialized colors for specific UI elements
- **[Typography](/typography)** - Font families, sizes, and text styling guidelines
- **[Figma MCP Bridge Setup](/figma-mcp-bridge)** - Configure VS Code + Copilot to read and write Figma nodes

### UI Components

- **[Badge](/components/badge)** - Display status and categorization information with multiple variants
- **[Button](/components/button)** - Interactive button component with multiple variants and sizes
- **[Input](/components/input)** - Text input field for capturing user input with validation support
- **[Labeled Input](/components/labeled-input)** - Input field with an associated label for better accessibility and UX
- **[Select](/components/select)** - Dropdown selection component with search and customization options

### Mimic Components

- **[Mimic Components Overview](/mimics/)** - Domain-specific SVG components for mimic diagrams
- **[Actuated Valve](/mimics/actuated-valve)** - Unified switch + flow-control directional actuated valve mimic component

### Modules

- **[Modules Overview](/mimics/modules/)** - Composed mimic scene documentation
- **[Dhw Scene](/mimics/modules/dhw-module)** - Initial documentation page for the DhwModule composition

Each component comes with:

- Multiple visual variants for different use cases
- Comprehensive accessibility features
- TypeScript support with full type definitions
- Live examples and interactive demonstrations
- Code snippets and implementation guides
- Best practice guidelines and usage recommendations

## Design System Principles

Zero UI is built on a comprehensive design system that ensures consistency, accessibility, and maintainability:

### Component Design Principles

- **Semantic variants** - Each variant has clear semantic meaning (default, destructive, secondary, etc.)
- **Size consistency** - Standard sizing options (sm, default, lg) across components
- **Accessibility first** - ARIA compliant with keyboard navigation support
- **Customizable** - Easy to theme and extend with additional CSS classes
- **TypeScript ready** - Full type safety and IntelliSense support

### Color System Principles

- **Layered Architecture** - Primitive colors form the foundation, semantic colors provide meaning, component colors offer specificity
- **Theme Adaptability** - All colors automatically adapt between light and dark themes
- **Accessibility Focused** - Proper contrast ratios maintained across all color combinations
- **Consistent Naming** - Clear, predictable naming conventions for easy implementation
- **Live Documentation** - Interactive color swatches showing real CSS values

Browse the [Components section](/components/) to explore all available components with interactive examples, or dive into the [Colors section](/colors) to understand our comprehensive color system.

# Zero UI Component Documentation

This project uses [VitePress](https://vitepress.dev/) to document and showcase our Vue components.

## Component Documentation

### Development
Start the component documentation development server:

```bash
pnpm docs:dev
```

This will start VitePress at `http://localhost:5173/zero-ui/` where you can browse all components with detailed documentation.

### Building for Production
Build the static documentation site:

```bash
pnpm docs:build
```

This generates a static site in `docs/.vitepress/dist` that can be deployed anywhere.

### Preview Production Build
Preview the built documentation locally:

```bash
pnpm docs:preview
```

## Adding New Component Documentation

To document a new component, create a new `.md` file in the `docs/components/` directory:

```markdown
# ComponentName

Brief description of the component.

## Import

\`\`\`vue
<script setup lang="ts">
import { ComponentName } from '@/components/ui/shadcn/component-name'
</script>
\`\`\`

## Examples

### Basic Usage

\`\`\`vue
<template>
  <ComponentName>
    Content here
  </ComponentName>
</template>
\`\`\`

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `prop1` | `string` | `"default"` | Description |

## Events

| Event | Type | Description |
|-------|------|-------------|
| `event1` | `(value: string) => void` | Description |
```

Then add it to the sidebar in `docs/.vitepress/config.ts`:

```typescript
sidebar: [
  // ... existing items
  { text: "ComponentName", link: "/components/component-name" },
]
```

## Features

✅ **Working Solution**: VitePress is fully compatible with your Vite 7 setup  
✅ **Markdown-based**: Easy to write and maintain documentation  
✅ **Vue Component Support**: Can embed live Vue components in docs  
✅ **Search**: Built-in search functionality  
✅ **Responsive**: Mobile-friendly documentation  
✅ **Fast**: Static site generation with excellent performance  

## Advantages over Histoire/Storybook

- **Full Compatibility**: Works perfectly with Vite 7 and your current setup
- **Zero Configuration Issues**: No dependency conflicts or module resolution problems  
- **Comprehensive Documentation**: Not just component showcase, but full documentation site
- **Better for Teams**: Easier to write and maintain long-form documentation
- **SEO Friendly**: Static site generation with proper meta tags
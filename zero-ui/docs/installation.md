# Installation

## Prerequisites

- Node.js 18+ 
- pnpm (recommended) or npm

## Install the Package

```bash
pnpm add zero-ui
```

## Setup

Import the CSS file in your main application file:

```typescript
// main.ts
import { createApp } from 'vue'
import App from './App.vue'
import 'zero-ui/dist/style.css'

createApp(App).mount('#app')
```

## Usage

Import and use components in your Vue files:

```vue
<script setup lang="ts">
import { Button, Card, CardContent } from 'zero-ui'
</script>

<template>
  <Card>
    <CardContent>
      <h1>Hello World</h1>
      <Button>Click me</Button>
    </CardContent>
  </Card>
</template>
```

## Tailwind CSS Configuration

If you're using Tailwind CSS in your project, you may want to configure it to work seamlessly with Zero UI components. Add the component paths to your `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './src/**/*.{vue,js,ts,jsx,tsx}',
    './node_modules/zero-ui/**/*.{vue,js,ts,jsx,tsx}',
  ],
  // ... rest of your config
}
```
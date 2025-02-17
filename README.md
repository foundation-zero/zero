# Zero UI

This repository currently includes the frontend for the Zero Domestic Control application, which will extend into the Zero Energy Manager in the (near) future.

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur). See `.vscode/extensions.json` for recommended plugins.

## Prerequisites

- NodeJS 22.x LTS (or newer)
- PNPM 9.x (or newer)

## Project Setup

### (optional) Enable corepack

The use of corepack is optional, however it enforces the use of a specific package manager version for this repository.

```sh
corepack enable
```

```sh
pnpm install
```

### Compile and Hot-Reload for Development

```sh
pnpm run dev
```

### Type-Check, Compile and Minify for Production

```sh
pnpm run build
```

### Run Unit Tests with [Vitest](https://vitest.dev/)

```sh
pnpm run test:unit
```

### Lint with [ESLint](https://eslint.org/)

```sh
pnpm run lint
```

### Put this in your `.env.local` for local backend

```sh
VITE_GRAPHQL_URL=/graphql
VITE_GRAPHQL_SERVER=http://localhost:8080/v1
VITE_GRAPHQL_TOKEN="{{INSERT API TOKEN HERE}}"
```
You can find or generate the token in the Zero Domestic Control repository: 
https://github.com/foundation-zero/zero-domestic-control
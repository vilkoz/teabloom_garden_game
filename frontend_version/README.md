# Teabloom Garden Web Port

This folder contains a full web port of the Pygame project using modern frontend tooling:

- Vite
- React
- TypeScript
- Canvas-based game loop and scene system

## Run locally

```bash
cd frontend_version
npm install
npm run dev
```

Open the URL shown by Vite (usually `http://localhost:5173`).

## Build

```bash
npm run build
npm run preview
```

## Ported systems

- Scene flow: loading → menu → game → stats → title
- Core tea ceremony loop: tea disk → kettle → water → brew → cha hai → cups → cats
- Cat states and patience timers
- Hearts, combos, stats, and unlock progression
- Save/load via `localStorage`

Data files are in `public/data/` and mirror the original Python JSON structure.
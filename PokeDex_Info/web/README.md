# Pokédex Info Web App

Awesome Pokémon-themed search and database interface built with Next.js.

## Setup

```bash
cd web
npm install
npm run dev
```

Visit `http://localhost:3000`

## Features

- 🔍 **Robust Search**: Search across Pokémon, Items, Abilities, and Moves
- 🎨 **Pokémon Theme**: Beautiful red/yellow gradient with type-specific colors
- 📊 **Data Integration**: Uses all scraped data from parent directory
- 🏠 **Sprites**: Supports Pokémon Home sprites (normal + shiny)
- 📱 **Responsive**: Works on desktop, tablet, and mobile
- ⚡ **Fast**: Next.js optimized, Tailwind CSS styling

## Data Sources

- Pokémon data: `../data/pokemon_data.json`
- Items data: `../data/items/items_data.json`
- Game icons: `../data/images/icons/`
- Pokémon sprites: `../data/home-sprites/`

## Deployment

Deploy to Netlify:

```bash
npm run build
```

Then connect your GitHub repo to Netlify - it will auto-deploy on push.

## Project Structure

```
web/
├── src/
│   ├── app/
│   │   ├── api/          # API routes for data
│   │   ├── page.tsx      # Home page
│   │   ├── layout.tsx    # Root layout
│   │   └── globals.css   # Global styles
│   ├── components/       # React components
│   │   └── SearchBar.tsx # Main search component
│   └── lib/
│       └── search.ts     # Search engine with Fuse.js
├── public/               # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

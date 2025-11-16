# 🎮 Web App Setup Guide

## Quick Start

### 1. Extract Pokémon Home Sprites

Place your extracted sprites in `data/home-sprites/`:

```
data/home-sprites/
├── bulbasaur.png
├── bulbasaur.shiny.png
├── charmander.png
├── charmander.shiny.png
└── ...
```

### 2. Install Dependencies

```bash
cd web
npm install
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### 4. Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
PokeDex_Info/
├── data/
│   ├── pokemon_data.json          # Pokemon data
│   ├── items/
│   │   ├── items_data.json        # All items
│   │   └── by_category/           # Items by category
│   ├── abilities/
│   │   └── abilities_data.json    # Abilities
│   ├── moves/
│   │   └── moves_data_gen*.json   # Moves by generation
│   ├── games/
│   │   └── pokemon_games.json     # Game info
│   ├── images/
│   │   ├── icons/                 # Game icons
│   │   └── game_icons.json        # Icon mapping
│   └── home-sprites/              # Pokemon Home sprites
│       ├── name.png               # Normal sprite
│       └── name.shiny.png         # Shiny sprite
├── web/                           # Next.js web app
│   ├── src/
│   │   ├── app/                   # Pages & API routes
│   │   ├── components/            # React components
│   │   └── lib/                   # Utilities
│   └── package.json
└── scrapers/                      # Data scrapers
```

## Features Implemented

✅ **Search Engine**

- Fuzzy matching with Fuse.js
- Real-time results as you type
- Filter by type (Pokémon, Items, Abilities, Moves)

✅ **Pokémon Theme**

- Red (#FF0000) + Yellow (#FFCC00) gradient
- Type-specific colors (Fire, Water, Grass, etc.)
- Card-based layout with hover effects

✅ **Data Integration**

- Pokémon info from scrapers
- Items with categories and effects
- Game availability tracking
- Sprite support (normal + shiny variants)

✅ **Responsive Design**

- Mobile-first approach
- Tailwind CSS
- Works on all devices

## Next Steps

### Add More Features

1. **Detail Pages**: Click results to see full details
2. **Filters**: Add advanced filtering
3. **Favorites**: Save favorite Pokémon/Items
4. **Type Matchups**: Show weaknesses/strengths
5. **Evolution Chains**: Visualize evolutions
6. **Sprite Display**: Show normal/shiny side-by-side

### Deploy to Netlify

1. Push to GitHub
2. Go to [netlify.com](https://netlify.com)
3. Connect your GitHub repo
4. Set build command: `npm run build`
5. Set publish directory: `web/.next`

## Troubleshooting

**Issue**: "Cannot find module '@/lib/search'"

- Run `npm install` in `/web` directory

**Issue**: Images not loading

- Ensure sprites are in `data/home-sprites/`
- Update image paths in components

**Issue**: Search returns no results

- Check data files exist in correct paths
- Verify JSON format is valid

## Environment Variables

Create `.env.local` in `web/` directory:

```env
# Optional: Configure data source paths
NEXT_PUBLIC_DATA_PATH=/api/data
```

## Performance Tips

- Images are optimized with Next.js Image component
- Search uses client-side Fuse.js for instant results
- Static generation for fast page loads
- Tailwind CSS purges unused styles

---

Happy Pokédex hunting! 🎉

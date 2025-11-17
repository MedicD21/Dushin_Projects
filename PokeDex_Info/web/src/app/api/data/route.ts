import { readFile } from "fs/promises";
import { join } from "path";
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  try {
    // Use absolute path
    const dataPath =
      "/Users/dustinschaaf/Desktop/Dushin_Projects/PokeDex_Info/data/pokemon_data.json";
    const data = await readFile(dataPath, "utf-8");
    const pokemon = JSON.parse(data);

    // Transform to include all necessary fields
    const transformed = Array.isArray(pokemon)
      ? pokemon.map((p: any) => ({
          id: p.name?.toLowerCase().replace(/\s+/g, "-"),
          number: p.number || p.pokedex_number || 0,
          name: p.name || "",
          types: p.types || [],
          abilities: p.abilities || [],
          abilities_info: p.abilities_info || {
            normal: p.abilities || [],
            hidden: null,
          },
          moves: p.moves || [],
          generation: p.generation || 0,
          base_stats: p.base_stats || {
            hp: 0,
            attack: 0,
            defense: 0,
            sp_attack: 0,
            sp_defense: 0,
            speed: 0,
          },
          dex_entries: p.dex_entries || {},
          species: p.species || "",
          physical_info: p.physical_info || {},
          game_appearances: p.game_appearances || [],
          evolution: p.evolution || {
            name: p.name || "",
            evolutions: [],
          },
        }))
      : [];

    return NextResponse.json(transformed);
  } catch (error) {
    console.error("Error reading pokemon data:", error);
    return NextResponse.json([], { status: 200 });
  }
}

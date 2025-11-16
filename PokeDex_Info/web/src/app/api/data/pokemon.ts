import { readFile } from "fs/promises";
import { join } from "path";
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  try {
    const dataPath = join(process.cwd(), "../../../data/pokemon_data.json");
    const data = await readFile(dataPath, "utf-8");
    const pokemon = JSON.parse(data);

    // Transform to include necessary fields
    const transformed = Array.isArray(pokemon)
      ? pokemon.map((p: any) => ({
          id: p.name?.toLowerCase().replace(/\s+/g, "_"),
          name: p.name,
          generation: p.generation,
          type: p.type || [],
          abilities: p.abilities || [],
          description: p.description || "",
        }))
      : [];

    return NextResponse.json(transformed);
  } catch (error) {
    console.error("Error reading pokemon data:", error);
    return NextResponse.json([], { status: 200 });
  }
}

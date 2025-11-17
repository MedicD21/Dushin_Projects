import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET(request: NextRequest) {
  try {
    // Load games data
    const gamesPath =
      "/Users/dustinschaaf/Desktop/Dushin_Projects/PokeDex_Info/data/games/pokemon_games.json";

    if (fs.existsSync(gamesPath)) {
      const fileContent = fs.readFileSync(gamesPath, "utf-8");
      const gamesData = JSON.parse(fileContent);
      return NextResponse.json(gamesData);
    }

    return NextResponse.json([], { status: 200 });
  } catch (error) {
    console.error("Error reading games data:", error);
    return NextResponse.json([], { status: 200 });
  }
}

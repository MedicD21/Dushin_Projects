import { readFile } from "fs/promises";
import { join } from "path";
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  try {
    const dataPath = join(process.cwd(), "../../../data/items/items_data.json");
    const data = await readFile(dataPath, "utf-8");
    const itemData = JSON.parse(data);

    // Extract items array from metadata structure
    const items = Array.isArray(itemData)
      ? itemData
      : Array.isArray(itemData.items)
      ? itemData.items
      : [];

    // Transform to include necessary fields
    const transformed = items.map((i: any) => ({
      id: i.name?.toLowerCase().replace(/\s+/g, "_"),
      name: i.name,
      category: i.category,
      effect: i.effect,
      description: i.effect || i.category,
      games: i.games || [],
    }));

    return NextResponse.json(transformed);
  } catch (error) {
    console.error("Error reading items data:", error);
    return NextResponse.json([], { status: 200 });
  }
}

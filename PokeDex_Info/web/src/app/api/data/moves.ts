import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  try {
    // For now, return empty array - moves data needs to be compiled
    return NextResponse.json([]);
  } catch (error) {
    console.error("Error reading moves data:", error);
    return NextResponse.json([], { status: 200 });
  }
}

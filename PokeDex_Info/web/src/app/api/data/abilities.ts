import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  try {
    // For now, return empty array - abilities data needs to be compiled
    return NextResponse.json([]);
  } catch (error) {
    console.error("Error reading abilities data:", error);
    return NextResponse.json([], { status: 200 });
  }
}

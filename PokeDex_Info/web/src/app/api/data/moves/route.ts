import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET(request: NextRequest) {
  try {
    // Load moves data from all generation files
    const dataDir =
      "/Users/dustinschaaf/Desktop/Dushin_Projects/PokeDex_Info/data/moves";

    const movesByName: Record<string, any> = {};
    const gameToGen: Record<string, number> = {};

    // Load each generation file
    const generations = [1, 2, 3, 4, 5, 6, 7, 8, 9];

    for (const gen of generations) {
      try {
        const filePath = path.join(dataDir, `moves_data_gen${gen}.json`);
        if (fs.existsSync(filePath)) {
          const fileContent = fs.readFileSync(filePath, "utf-8");
          const data = JSON.parse(fileContent);

          // Map games to generation
          if (data.metadata?.games) {
            data.metadata.games.forEach((game: string) => {
              gameToGen[game] = gen;
            });
          }

          if (data.moves && Array.isArray(data.moves)) {
            for (const move of data.moves) {
              if (!movesByName[move.name]) {
                movesByName[move.name] = {
                  ...move,
                  generations: [gen],
                };
              } else {
                // Add generation to existing move
                if (!movesByName[move.name].generations.includes(gen)) {
                  movesByName[move.name].generations.push(gen);
                }

                // Merge learned_by information
                if (move.learned_by && Array.isArray(move.learned_by)) {
                  const existingLearners = new Map();
                  if (movesByName[move.name].learned_by) {
                    movesByName[move.name].learned_by.forEach(
                      (learner: any) => {
                        existingLearners.set(
                          `${learner.name}-${learner.form}`,
                          learner
                        );
                      }
                    );
                  }

                  move.learned_by.forEach((learner: any) => {
                    const key = `${learner.name}-${learner.form}`;
                    if (!existingLearners.has(key)) {
                      existingLearners.set(key, learner);
                    }
                  });

                  movesByName[move.name].learned_by = Array.from(
                    existingLearners.values()
                  );
                }
              }
            }
          }
        }
      } catch (err) {
        console.error(`Error loading generation ${gen} moves:`, err);
      }
    }

    // Store game to generation mapping in response
    const moves = Object.values(movesByName);
    return NextResponse.json({ moves, gameToGen });
  } catch (error) {
    console.error("Error reading moves data:", error);
    return NextResponse.json({ moves: [], gameToGen: {} }, { status: 200 });
  }
}

"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import Image from "next/image";

interface MoveLearnedBy {
  dex_number: string;
  name: string;
  form: string;
  method: string;
  level: number | string;
}

interface Move {
  name: string;
  battle_type: string;
  category: string;
  power_points: number;
  base_power: number;
  accuracy: number;
  battle_effect: string;
  secondary_effect: string;
  effect_rate: string;
  speed_priority: number;
  pokemon_hit_in_battle: string;
  physical_contact: boolean;
  sound_type: boolean;
  punch_move: boolean;
  biting_move: boolean;
  snatchable: boolean;
  slicing_move: boolean;
  bullet_type: boolean;
  wind_move: boolean;
  powder_move: boolean;
  metronome: boolean;
  affected_by_gravity: boolean;
  defrosts_when_used: boolean;
  reflected_by_magic_coat: boolean;
  blocked_by_protect: boolean;
  copyable_by_mirror_move: boolean;
  learned_by: MoveLearnedBy[];
  generations: number[];
}

const typeColors: Record<string, string> = {
  normal: "bg-gray-400",
  fire: "bg-red-500",
  water: "bg-blue-500",
  grass: "bg-green-500",
  electric: "bg-yellow-400",
  ice: "bg-blue-300",
  fighting: "bg-red-700",
  poison: "bg-purple-500",
  ground: "bg-yellow-600",
  flying: "bg-blue-400",
  psychic: "bg-pink-500",
  bug: "bg-green-600",
  rock: "bg-gray-600",
  ghost: "bg-purple-700",
  dragon: "bg-blue-700",
  dark: "bg-gray-800",
  steel: "bg-gray-500",
  fairy: "bg-pink-300",
};

export default function MovesPage() {
  const searchParams = useSearchParams();
  const pokemonFilter = searchParams.get("pokemon");
  const gameFilter = searchParams.get("game");

  const [moves, setMoves] = useState<Move[]>([]);
  const [filteredMoves, setFilteredMoves] = useState<Move[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedGame, setSelectedGame] = useState<string>(gameFilter || "");
  const [availableGames, setAvailableGames] = useState<string[]>([]);
  const [gameToGen, setGameToGen] = useState<Record<string, number>>({});
  const [gameReleaseOrder, setGameReleaseOrder] = useState<
    Record<string, number>
  >({});

  useEffect(() => {
    const fetchMoves = async () => {
      try {
        const response = await fetch("/api/data/moves");
        const data = await response.json();
        setMoves(data.moves || []);
        setGameToGen(data.gameToGen || {});

        // Fetch games data to get release order
        let releaseOrder: Record<string, number> = {};
        try {
          const gamesResponse = await fetch("/api/data/games");
          const gamesData = await gamesResponse.json();

          // Build a map of game name to release order
          let orderIndex = 0;
          if (Array.isArray(gamesData)) {
            gamesData.forEach((gen: any) => {
              if (Array.isArray(gen.games)) {
                gen.games.forEach((game: string) => {
                  releaseOrder[game] = orderIndex++;
                });
              }
            });
          }
          setGameReleaseOrder(releaseOrder);
        } catch (err) {
          console.error("Error fetching games data:", err);
        }

        // Extract available games from gameToGen mapping and sort by release order
        if (data.gameToGen) {
          const games = Object.keys(data.gameToGen);
          // Sort games by release order
          const sortedGames = games.sort((a, b) => {
            const orderA = releaseOrder[a] ?? Infinity;
            const orderB = releaseOrder[b] ?? Infinity;
            return orderA - orderB;
          });
          setAvailableGames(sortedGames);
          // Set default game if not specified
          if (!gameFilter && sortedGames.length > 0) {
            setSelectedGame(sortedGames[sortedGames.length - 1]); // Default to latest game
          }
        }
      } catch (error) {
        console.error("Error fetching moves:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchMoves();
  }, [gameFilter]);

  useEffect(() => {
    let filtered = moves;

    // Filter by game/generation
    if (selectedGame && gameToGen[selectedGame]) {
      const gen = gameToGen[selectedGame];
      filtered = filtered.filter((move) => move.generations?.includes(gen));
    }

    // Filter by pokemon if specified
    if (pokemonFilter) {
      filtered = filtered.filter((move) =>
        move.learned_by?.some(
          (learner) =>
            learner.name.toLowerCase() === pokemonFilter.toLowerCase()
        )
      );
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (move) =>
          move.name.toLowerCase().includes(query) ||
          move.battle_type.toLowerCase().includes(query)
      );
    }

    setFilteredMoves(filtered);
  }, [moves, pokemonFilter, searchQuery, selectedGame, gameToGen]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-cyan-900 to-slate-900 p-6 flex items-center justify-center">
        <div className="text-xl font-semibold text-gray-400">
          Loading moves...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-cyan-900 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Logo Header */}
        <div className="mb-6 flex items-center gap-3">
          <Link href="/" className="hover:opacity-80 transition">
            <Image
              src="/dex_logo.png"
              alt="PokeNode Logo"
              width={50}
              height={50}
              className="h-12 w-12 object-contain"
            />
          </Link>
        </div>

        {/* Header */}
        <div className="mb-8">
          {pokemonFilter && (
            <Link href={`/pokemon/${pokemonFilter.toLowerCase()}`}>
              <button className="mb-4 px-4 py-2 bg-cyan-700 rounded hover:bg-teal-700 text-white font-semibold">
                ← Back to{" "}
                {pokemonFilter.charAt(0).toUpperCase() + pokemonFilter.slice(1)}
              </button>
            </Link>
          )}
          <h1 className="text-4xl font-bold text-white mb-2 pokemon-header">
            Moves
          </h1>
          {pokemonFilter && (
            <p className="text-lg text-gray-300">
              Showing moves that{" "}
              <span className="text-yellow-400 font-bold capitalize">
                {pokemonFilter}
              </span>{" "}
              can learn in {selectedGame}
            </p>
          )}
          <p className="text-gray-400 text-sm mt-2">
            Total: {filteredMoves.length} move
            {filteredMoves.length !== 1 ? "s" : ""}
          </p>
        </div>

        {/* Controls */}
        <div className="mb-6 space-y-4">
          {/* Game Selector */}
          {availableGames.length > 0 && (
            <div className="flex items-center gap-4">
              <label className="text-gray-300 font-semibold">Game:</label>
              <select
                value={selectedGame}
                onChange={(e) => setSelectedGame(e.target.value)}
                className="bg-gray-900 text-white px-4 py-2 rounded-lg font-medium border border-gray-700 focus:outline-none focus:ring-2 focus:ring-yellow-400"
              >
                {availableGames.map((game) => (
                  <option key={game} value={game}>
                    {game} (Gen {gameToGen[game]})
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Search Bar */}
          <input
            type="text"
            placeholder="Search moves by name or type..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-3 bg-gray-900 text-white border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-400"
          />
        </div>

        {/* Moves Grid */}
        {filteredMoves.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredMoves.map((move) => (
              <div
                key={move.name}
                className="bg-gray-900 rounded-lg p-4 border border-gray-700 hover:border-yellow-500 transition-colors"
              >
                {/* Move Header */}
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-lg font-bold text-white">
                      {move.name}
                    </h3>
                    <span
                      className={`inline-block text-xs font-semibold text-white px-2 py-1 rounded mt-1 ${
                        typeColors[move.battle_type.toLowerCase()] ||
                        "bg-gray-600"
                      }`}
                    >
                      {move.battle_type}
                    </span>
                  </div>
                </div>

                {/* Move Stats */}
                <div className="grid grid-cols-2 gap-2 text-sm mb-3">
                  {move.base_power > 0 && (
                    <div>
                      <p className="text-gray-400 text-xs">Power</p>
                      <p className="text-white font-semibold">
                        {move.base_power}
                      </p>
                    </div>
                  )}
                  {move.accuracy > 0 && (
                    <div>
                      <p className="text-gray-400 text-xs">Accuracy</p>
                      <p className="text-white font-semibold">
                        {move.accuracy}%
                      </p>
                    </div>
                  )}
                  <div>
                    <p className="text-gray-400 text-xs">PP</p>
                    <p className="text-white font-semibold">
                      {move.power_points}
                    </p>
                  </div>
                  {move.category && (
                    <div>
                      <p className="text-gray-400 text-xs">Category</p>
                      <p className="text-white font-semibold capitalize">
                        {move.category}
                      </p>
                    </div>
                  )}
                </div>

                {/* Effect */}
                {move.battle_effect && (
                  <p className="text-gray-300 text-sm mb-3 line-clamp-3">
                    {move.battle_effect}
                  </p>
                )}

                {/* Learned By */}
                {!pokemonFilter &&
                  move.learned_by &&
                  move.learned_by.length > 0 && (
                    <div className="border-t border-gray-700 pt-3 mt-3">
                      <p className="text-gray-400 text-xs font-semibold mb-2">
                        Learned by {move.learned_by.length} Pokémon
                      </p>
                      <div className="space-y-2 max-h-32 overflow-y-auto">
                        {move.learned_by.slice(0, 10).map((learner) => (
                          <Link
                            key={`${learner.dex_number}-${learner.name}-${learner.method}`}
                            href={`/pokemon/${learner.name.toLowerCase()}`}
                          >
                            <div className="text-xs bg-gray-800 hover:bg-gray-700 p-2 rounded transition-colors cursor-pointer flex items-center justify-between">
                              <span className="text-yellow-400 font-semibold">
                                {learner.name}
                              </span>
                              <div className="flex gap-1">
                                <span className="bg-gray-700 text-gray-300 px-2 py-0.5 rounded text-xs">
                                  {learner.method}
                                </span>
                                {typeof learner.level === "number" &&
                                  learner.level > 0 && (
                                    <span className="bg-blue-900 text-blue-300 px-2 py-0.5 rounded text-xs">
                                      Lv.{learner.level}
                                    </span>
                                  )}
                              </div>
                            </div>
                          </Link>
                        ))}
                        {move.learned_by.length > 10 && (
                          <p className="text-xs text-gray-400 px-2">
                            +{move.learned_by.length - 10} more
                          </p>
                        )}
                      </div>
                    </div>
                  )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-400 text-lg">
              {pokemonFilter
                ? `No moves found for ${pokemonFilter} in ${selectedGame}`
                : "No moves found matching your search."}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

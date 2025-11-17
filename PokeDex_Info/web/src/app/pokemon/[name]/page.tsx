"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import Image from "next/image";

interface Pokemon {
  id: string;
  number: number;
  name: string;
  types: string[];
  abilities: string[];
  abilities_info?: {
    normal: string[];
    hidden: string | null;
  };
  base_stats: {
    hp: number;
    attack: number;
    defense: number;
    sp_attack: number;
    sp_defense: number;
    speed: number;
  };
  dex_entries: Record<string, string>;
  species: string;
  physical_info: Record<string, string>;
  game_appearances: Record<string, any>;
  breeding_info?: {
    egg_groups: string[];
    gender_ratio: string;
    egg_cycles: string;
    base_friendship: string;
    growth_rate: string;
  };
  game_mechanics?: {
    ev_yield: string;
    catch_rate: string;
    base_exp: string;
  };
  evolution?: {
    name: string;
    evolutions: Array<{
      name: string;
      method: string;
      sprite: string;
    }>;
  };
  moves?: string[];
}

export default function PokemonPage() {
  const params = useParams();
  const pokemonName = params.name as string;
  const [pokemon, setPokemon] = useState<Pokemon | null>(null);
  const [isShiny, setIsShiny] = useState(false);
  const [selectedGame, setSelectedGame] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [gameReleaseOrder, setGameReleaseOrder] = useState<
    Record<string, number>
  >({});

  useEffect(() => {
    const fetchPokemon = async () => {
      try {
        // Fetch Pokemon data
        const response = await fetch("/api/data");
        const data = await response.json();
        const found = data.find(
          (p: Pokemon) => p.name.toLowerCase() === pokemonName.toLowerCase()
        );

        // Fetch games data to get release order
        let releaseOrder: Record<string, number> = {};
        try {
          const gamesResponse = await fetch("/api/data/games");
          const gamesData = await gamesResponse.json();

          // Build a map of game name to release order (latest first for reverse sorting)
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

        if (found) {
          setPokemon(found);

          // Set default to the most recent game the Pokemon appears in
          const pokemonGames = Object.keys(found.game_appearances || {});
          if (pokemonGames.length > 0) {
            // Find the game with the highest release order (most recent)
            const mostRecentGame = pokemonGames.reduce((latest, current) => {
              const latestOrder = releaseOrder[latest] ?? -1;
              const currentOrder = releaseOrder[current] ?? -1;
              return currentOrder > latestOrder ? current : latest;
            });
            setSelectedGame(mostRecentGame);
          }
        }
      } catch (error) {
        console.error("Error fetching pokemon:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchPokemon();
  }, [pokemonName]);

  if (loading) {
    return <div className="text-white text-center py-8">Loading...</div>;
  }

  if (!pokemon) {
    return (
      <div className="text-white text-center py-8">
        <p>Pokemon not found</p>
        <button
          onClick={() => router.back()}
          className="mt-4 px-4 py-2 bg-blue-600 rounded hover:bg-blue-500"
        >
          Go Back
        </button>
      </div>
    );
  }

  const getDexEntryForGame = (gameName: string): string => {
    if (!gameName || !pokemon.dex_entries)
      return Object.values(pokemon.dex_entries)[0] || "";

    const lowerKey = gameName.toLowerCase();
    if (pokemon.dex_entries[lowerKey]) return pokemon.dex_entries[lowerKey];

    const cleanKey = gameName.toLowerCase().replace(/['\s-]/g, "");
    const matchKey = Object.keys(pokemon.dex_entries).find(
      (key) => key.toLowerCase().replace(/['\s-]/g, "") === cleanKey
    );
    if (matchKey) return pokemon.dex_entries[matchKey];

    return Object.values(pokemon.dex_entries)[0] || "";
  };

  const getSpriteUrl = (pokemonName: string): string => {
    const formatted = pokemonName.toLowerCase().replace(/\s+/g, "-");
    if (isShiny) {
      return `/home-sprites/${formatted}.shiny.png`;
    }
    return `/home-sprites/${formatted}.png`;
  };

  const getTypeColor = (type: string): string => {
    const colors: Record<string, string> = {
      normal: "bg-gray-500",
      fire: "bg-red-600",
      water: "bg-blue-600",
      grass: "bg-green-600",
      electric: "bg-yellow-500",
      ice: "bg-blue-400",
      fighting: "bg-red-800",
      poison: "bg-purple-600",
      ground: "bg-yellow-700",
      flying: "bg-sky-500",
      psychic: "bg-pink-600",
      bug: "bg-green-700",
      rock: "bg-gray-700",
      ghost: "bg-purple-800",
      dragon: "bg-indigo-700",
      dark: "bg-gray-800",
      steel: "bg-slate-600",
      fairy: "bg-pink-500",
    };
    return colors[type.toLowerCase()] || "bg-gray-600";
  };

  const getTypeWeaknesses = (type: string): string[] => {
    const weaknesses: Record<string, string[]> = {
      normal: ["fighting"],
      fire: ["water", "ground", "rock"],
      water: ["electric", "grass"],
      grass: ["fire", "ice", "poison", "flying", "bug"],
      electric: ["ground"],
      ice: ["fire", "fighting", "rock", "steel"],
      fighting: ["flying", "psychic", "fairy"],
      poison: ["ground", "psychic"],
      ground: ["water", "grass", "ice"],
      flying: ["electric", "ice", "rock"],
      psychic: ["bug", "ghost", "dark"],
      bug: ["fire", "flying", "rock"],
      rock: ["water", "grass", "fighting", "ground", "steel"],
      ghost: ["ghost", "dark"],
      dragon: ["ice", "dragon", "fairy"],
      dark: ["fighting", "bug", "fairy"],
      steel: ["fire", "water", "ground"],
      fairy: ["poison", "steel"],
    };
    return weaknesses[type.toLowerCase()] || [];
  };

  const parseGenderRatio = (
    genderRatio: string
  ): { malePercent: number; femalePercent: number; isGenderless: boolean } => {
    if (!genderRatio || genderRatio.toLowerCase().includes("genderless")) {
      return { malePercent: 0, femalePercent: 0, isGenderless: true };
    }

    const maleMatch = genderRatio.match(/(\d+(?:\.\d+)?)\s*%\s*male/i);
    const femaleMatch = genderRatio.match(/(\d+(?:\.\d+)?)\s*%\s*female/i);

    const malePercent = maleMatch ? parseFloat(maleMatch[1]) : 50;
    const femalePercent = femaleMatch ? parseFloat(femaleMatch[1]) : 50;

    return { malePercent, femalePercent, isGenderless: false };
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-cyan-900 to-slate-900 p-6">
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
        <Link href="/pokedex">
          <button className="px-4 py-2 bg-cyan-700 rounded hover:bg-teal-700 text-white">
            ← Back to Pokédex
          </button>
        </Link>
      </div>

      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-cyan-700 via-teal-700 to-cyan-800 p-6 text-white rounded-t-2xl border-b-4 border-yellow-500">
          <div className="flex justify-between items-start mb-4">
            <div>
              <div className="text-sm text-white/70">
                National Pokédex: {pokemon.number}
              </div>
              <h1 className="text-4xl font-bold capitalize mt-2 pokemon-header">
                {pokemon.name}
              </h1>
              <p className="text-sm opacity-90 capitalize mt-1">
                {pokemon.species}
              </p>
            </div>
          </div>

          <div className="flex gap-3 flex-wrap">
            <button
              onClick={() => setIsShiny(!isShiny)}
              className={`bubble-btn font-bold transition-all ${
                isShiny
                  ? "bg-yellow-400 text-gray-900"
                  : "bg-gray-700 text-gray-200 hover:bg-gray-600"
              }`}
            >
              ✨ {isShiny ? "Shiny" : "Normal"}
            </button>

            {Object.keys(pokemon.game_appearances || {}).length > 0 && (
              <select
                value={selectedGame}
                onChange={(e) => setSelectedGame(e.target.value)}
                className="bg-gray-700 text-white px-4 py-2 rounded-lg font-medium border border-gray-600 focus:outline-none focus:ring-2 focus:ring-yellow-400"
              >
                {Object.keys(pokemon.game_appearances).map((game) => (
                  <option key={game} value={game}>
                    {game}
                  </option>
                ))}
              </select>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="bg-gray-900 p-6 space-y-6 rounded-b-2xl">
          {/* Sprite Section */}
          <div className="sprite-container border border-gray-600">
            <img
              src={getSpriteUrl(pokemon.name)}
              alt={pokemon.name}
              className="w-56 h-56 object-contain drop-shadow-lg"
              onError={(e) => {
                (e.target as HTMLImageElement).src = "/placeholder.svg";
              }}
            />
          </div>

          {/* Type Badges */}
          <div>
            <h3 className="font-bold text-white mb-3 text-lg">Types</h3>
            <div className="flex gap-3 flex-wrap">
              {pokemon.types.map((t: string) => (
                <Link key={t} href={`/types/${t.toLowerCase()}`}>
                  <span className={`type-badge ${getTypeColor(t)}`}>
                    {t.charAt(0).toUpperCase() + t.slice(1)}
                  </span>
                </Link>
              ))}
            </div>
          </div>

          {/* Abilities */}
          {pokemon.abilities.length > 0 && (
            <div>
              <h3 className="font-bold text-white mb-3 text-lg">Abilities</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-gray-400 text-xs font-semibold mb-2">
                    Normal
                  </p>
                  <div className="flex flex-col gap-2">
                    {(pokemon.abilities_info?.normal || pokemon.abilities)
                      ?.filter(
                        (ability: string) =>
                          ability.toLowerCase() !==
                          pokemon.abilities_info?.hidden?.toLowerCase()
                      )
                      .map((ability: string) => (
                        <Link
                          key={ability}
                          href={`/abilities/${ability
                            .toLowerCase()
                            .replace(/\s+/g, "-")}`}
                        >
                          <span className="ability-pill bg-blue-900 text-blue-100 border border-blue-700">
                            {ability}
                          </span>
                        </Link>
                      ))}
                  </div>
                </div>

                <div>
                  <p className="text-gray-400 text-xs font-semibold mb-2">
                    Hidden
                  </p>
                  {pokemon.abilities_info?.hidden ? (
                    <Link
                      href={`/abilities/${pokemon.abilities_info.hidden
                        .toLowerCase()
                        .replace(/\s+/g, "-")}`}
                    >
                      <span className="ability-pill bg-purple-900 text-purple-100 border border-purple-700 hover:bg-purple-800 hover:border-purple-500">
                        {pokemon.abilities_info.hidden.charAt(0).toUpperCase() +
                          pokemon.abilities_info.hidden.slice(1)}
                      </span>
                    </Link>
                  ) : (
                    <p className="text-gray-400 text-sm">None</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Type Weaknesses */}
          <div>
            <h3 className="font-bold text-white mb-3 text-lg">Weaknesses</h3>
            <div className="grid grid-cols-2 gap-3">
              {pokemon.types.map((t: string) => {
                const weaknesses = getTypeWeaknesses(t);
                return (
                  <div
                    key={t}
                    className="bg-gray-800 p-4 rounded border border-gray-700 flex flex-col items-center text-center"
                  >
                    <p className="text-sm font-bold text-gray-200 mb-2 capitalize">
                      {t}
                    </p>
                    <div className="flex gap-1 flex-wrap justify-center">
                      {weaknesses.map((weakness: string) => (
                        <span
                          key={weakness}
                          className={`text-xs text-white px-2 py-1 rounded font-medium ${getTypeColor(
                            weakness
                          )}`}
                        >
                          {weakness.charAt(0).toUpperCase() + weakness.slice(1)}
                        </span>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Evolution Chain */}
          {pokemon.evolution && pokemon.evolution.evolutions.length > 0 && (
            <div>
              <h3 className="font-bold text-white mb-4 text-lg">
                Evolution Chain
              </h3>
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-6 overflow-x-auto">
                <div className="flex items-center justify-start gap-6 min-w-max pb-2">
                  <div className="flex flex-col items-center flex-shrink-0">
                    <div className="text-center">
                      <img
                        src={getSpriteUrl(pokemon.name)}
                        alt={pokemon.name}
                        className="w-24 h-24 object-contain mx-auto mb-2"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src =
                            "/placeholder.svg";
                        }}
                      />
                      <p className="font-bold text-white text-sm">
                        {pokemon.name}
                      </p>
                    </div>
                  </div>

                  {pokemon.evolution.evolutions.map((evo, idx) => (
                    <div
                      key={idx}
                      className="flex items-center gap-6 flex-shrink-0"
                    >
                      <div className="text-yellow-400 text-2xl font-bold">
                        →
                      </div>
                      <div className="flex flex-col items-center">
                        <img
                          src={`/home-sprites/${evo.sprite}.png`}
                          alt={evo.name}
                          className="w-24 h-24 object-contain mx-auto mb-2"
                          onError={(e) => {
                            (e.target as HTMLImageElement).src =
                              "/placeholder.svg";
                          }}
                        />
                        <Link href={`/pokemon/${evo.name.toLowerCase()}`}>
                          <p className="font-bold text-blue-400 text-sm hover:underline cursor-pointer whitespace-nowrap">
                            {evo.name}
                          </p>
                        </Link>
                        <p className="text-xs text-gray-400 mt-1 text-center max-w-[120px]">
                          {evo.method}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Dex Entries */}
          {pokemon.dex_entries &&
            Object.keys(pokemon.dex_entries).length > 0 && (
              <div>
                <h3 className="font-bold text-white mb-3 text-lg">
                  Dex Entries
                </h3>
                <div className="space-y-2">
                  {selectedGame &&
                    pokemon.dex_entries[selectedGame.toLowerCase()] && (
                      <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                        <p className="text-xs text-gray-400 font-semibold mb-2 capitalize">
                          {selectedGame}
                        </p>
                        <p className="text-sm text-gray-100 leading-relaxed">
                          {pokemon.dex_entries[selectedGame.toLowerCase()]}
                        </p>
                      </div>
                    )}
                </div>
              </div>
            )}

          {/* Locations */}
          {pokemon.game_appearances &&
            selectedGame &&
            pokemon.game_appearances[selectedGame] &&
            pokemon.game_appearances[selectedGame].location && (
              <div>
                <h3 className="font-bold text-white mb-3 text-lg">Locations</h3>
                <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs text-gray-400 font-semibold mb-1">
                        Available in {selectedGame}
                      </p>
                      <p className="text-sm text-gray-100 font-medium">
                        {pokemon.game_appearances[selectedGame].location}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      {pokemon.game_appearances[selectedGame].available && (
                        <span className="bg-green-600 text-white text-xs px-3 py-1 rounded-full font-semibold">
                          Available
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

          {/* Base Stats */}
          <div>
            <h3 className="font-bold text-white mb-4 text-lg">Base Stats</h3>
            <div className="space-y-4">
              {[
                { label: "HP", value: pokemon.base_stats.hp },
                { label: "Attack", value: pokemon.base_stats.attack },
                { label: "Defense", value: pokemon.base_stats.defense },
                { label: "Sp. Atk", value: pokemon.base_stats.sp_attack },
                { label: "Sp. Def", value: pokemon.base_stats.sp_defense },
                { label: "Speed", value: pokemon.base_stats.speed },
              ].map((stat) => (
                <div key={stat.label} className="flex items-center gap-4">
                  <span className="w-20 text-sm font-bold text-gray-200">
                    {stat.label}
                  </span>
                  <div className="flex-1 bg-gray-800 rounded-full h-3 border border-gray-700 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-cyan-500 h-3 rounded-full transition-all shadow-lg"
                      style={{ width: `${(stat.value / 150) * 100}%` }}
                    />
                  </div>
                  <span className="w-10 text-sm font-bold text-yellow-400 text-right">
                    {stat.value}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Moves Section */}
          {pokemon.moves && pokemon.moves.length > 0 && (
            <div>
              <h3 className="font-bold text-white mb-3 text-lg">Moves</h3>
              <p className="text-gray-300 text-sm mb-3">
                {pokemon.name} can learn {pokemon.moves.length} moves in{" "}
                {selectedGame}.
              </p>
              <Link
                href={`/moves?pokemon=${encodeURIComponent(
                  pokemon.name
                )}&game=${encodeURIComponent(selectedGame)}`}
              >
                <button className="bubble-btn bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white">
                  View All Moves
                </button>
              </Link>
            </div>
          )}

          {/* Physical Info */}
          {Object.keys(pokemon.physical_info).length > 0 && (
            <div>
              <h3 className="font-bold text-white mb-3 text-lg">
                Physical Info
              </h3>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(pokemon.physical_info).map(
                  ([key, value]: [string, string]) => (
                    <div
                      key={key}
                      className="bg-gray-800 p-3 rounded-lg border border-gray-700 info-box-3d"
                    >
                      <p className="text-xs text-gray-400 capitalize">{key}</p>
                      <p className="text-sm font-semibold text-white">
                        {value}
                      </p>
                    </div>
                  )
                )}
              </div>
            </div>
          )}

          {/* Breeding & Game Info */}
          {(pokemon.breeding_info || pokemon.game_mechanics) && (
            <div className="bg-gray-800 rounded-2xl p-4 space-y-4 info-box-3d">
              <h3 className="font-bold text-white text-lg">Stats & Info</h3>

              {pokemon.breeding_info && (
                <div>
                  <p className="text-gray-400 text-xs font-semibold mb-2">
                    Gender Ratio
                  </p>
                  {(() => {
                    const genderData = parseGenderRatio(
                      pokemon.breeding_info.gender_ratio
                    );
                    return genderData.isGenderless ? (
                      <p className="text-white text-sm">Genderless</p>
                    ) : (
                      <div className="flex items-center gap-3">
                        <div className="flex-1 stat-bar bg-gray-700 border border-gray-600 overflow-hidden flex">
                          <div
                            className="bg-blue-500 h-full"
                            style={{ width: `${genderData.malePercent}%` }}
                          />
                          <div
                            className="bg-pink-500 h-full"
                            style={{ width: `${genderData.femalePercent}%` }}
                          />
                        </div>
                        <div className="text-xs space-y-1">
                          <p className="text-blue-400">
                            ♂ {genderData.malePercent}%
                          </p>
                          <p className="text-pink-400">
                            ♀ {genderData.femalePercent}%
                          </p>
                        </div>
                      </div>
                    );
                  })()}
                </div>
              )}

              {pokemon.breeding_info && (
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <p className="text-gray-400 text-xs font-semibold mb-1">
                      Egg Groups
                    </p>
                    <p className="text-white">
                      {pokemon.breeding_info.egg_groups.join(", ") || "Unknown"}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-xs font-semibold mb-1">
                      Egg Cycles
                    </p>
                    <p className="text-white">
                      {pokemon.breeding_info.egg_cycles}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-xs font-semibold mb-1">
                      Growth Rate
                    </p>
                    <p className="text-white">
                      {pokemon.breeding_info.growth_rate}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-xs font-semibold mb-1">
                      Base Friendship
                    </p>
                    <p className="text-white">
                      {pokemon.breeding_info.base_friendship}
                    </p>
                  </div>
                </div>
              )}

              {pokemon.game_mechanics && (
                <div className="grid grid-cols-2 gap-3 text-sm border-t border-gray-700 pt-3">
                  <div>
                    <p className="text-gray-400 text-xs font-semibold mb-1">
                      Base Exp
                    </p>
                    <p className="text-white">
                      {pokemon.game_mechanics.base_exp}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-xs font-semibold mb-1">
                      Catch Rate
                    </p>
                    <p className="text-white text-xs">
                      {pokemon.game_mechanics.catch_rate}
                    </p>
                  </div>
                  <div className="col-span-2">
                    <p className="text-gray-400 text-xs font-semibold mb-1">
                      EV Yield
                    </p>
                    <p className="text-white">
                      {pokemon.game_mechanics.ev_yield}
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

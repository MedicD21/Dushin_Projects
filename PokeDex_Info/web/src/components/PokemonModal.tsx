"use client";

import { useState } from "react";
import Link from "next/link";

interface Evolution {
  name: string;
  method: string;
  sprite: string;
}

interface EvolutionChain {
  name: string;
  evolutions: Evolution[];
}

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
  evolution?: EvolutionChain;
}

interface PokemonModalProps {
  pokemon: Pokemon;
  isShiny: boolean;
  onShinyToggle: () => void;
  onClose: () => void;
}

export default function PokemonModal({
  pokemon,
  isShiny,
  onShinyToggle,
  onClose,
}: PokemonModalProps) {
  const [selectedGame, setSelectedGame] = useState<string>(
    Object.keys(pokemon.game_appearances || {})[0] || ""
  );

  const getDexEntryForGame = (gameName: string): string => {
    if (!gameName || !pokemon.dex_entries)
      return Object.values(pokemon.dex_entries)[0] || "";

    // Try exact lowercase match
    const lowerKey = gameName.toLowerCase();
    if (pokemon.dex_entries[lowerKey]) return pokemon.dex_entries[lowerKey];

    // Try removing spaces and special chars
    const cleanKey = gameName.toLowerCase().replace(/['\s-]/g, "");
    const matchKey = Object.keys(pokemon.dex_entries).find(
      (key) => key.toLowerCase().replace(/['\s-]/g, "") === cleanKey
    );
    if (matchKey) return pokemon.dex_entries[matchKey];

    // Fallback to first entry
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

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <div
        className="bg-gray-900 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border-2 border-yellow-500"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
          <div className="flex justify-between items-start mb-4">
            <div>
              <div className="text-sm text-blue-100">
                #{String(pokemon.number).padStart(3, "0")}
              </div>
              <h1 className="text-4xl font-bold capitalize">{pokemon.name}</h1>
              <p className="text-sm opacity-90 capitalize mt-1">
                {pokemon.species}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-3xl hover:opacity-75 transition font-bold"
            >
              ✕
            </button>
          </div>

          {/* Shiny Toggle and Game Selector */}
          <div className="flex gap-3 flex-wrap">
            <button
              onClick={onShinyToggle}
              className={`px-4 py-2 rounded-lg font-bold transition-all ${
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
        <div className="p-6 space-y-6">
          {/* Sprite Section */}
          <div className="flex justify-center bg-gradient-to-b from-gray-800 to-gray-900 rounded-lg py-8 border border-gray-700">
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
                  <span
                    className={`text-white font-bold px-5 py-2 rounded-full ${getTypeColor(
                      t
                    )} hover:opacity-80 transition-opacity cursor-pointer`}
                  >
                    {t.charAt(0).toUpperCase() + t.slice(1)}
                  </span>
                </Link>
              ))}
            </div>
          </div>

          {/* Description/Dex Entry */}
          <div>
            <h3 className="font-bold text-white mb-2 text-lg">
              Pokédex Entry
              {selectedGame && ` (${selectedGame})`}
            </h3>
            <p className="text-gray-300 leading-relaxed bg-gray-800 p-4 rounded border border-gray-700">
              {getDexEntryForGame(selectedGame)}
            </p>
            {selectedGame &&
              pokemon.game_appearances[selectedGame]?.location && (
                <p className="text-gray-400 text-sm mt-2 ml-1">
                  📍 <strong>Location:</strong>{" "}
                  {pokemon.game_appearances[selectedGame].location}
                </p>
              )}
          </div>

          {/* Abilities */}
          {pokemon.abilities.length > 0 && (
            <div>
              <h3 className="font-bold text-white mb-3 text-lg">Abilities</h3>
              <div className="space-y-3">
                {/* Normal Abilities */}
                <div>
                  <p className="text-gray-400 text-xs font-semibold mb-2">
                    Normal
                  </p>
                  <div className="flex gap-2 flex-wrap">
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
                          <span className="bg-blue-900 text-blue-100 px-4 py-2 rounded-full text-sm font-medium border border-blue-700 hover:bg-blue-800 hover:border-blue-500 cursor-pointer transition-colors">
                            {ability}
                          </span>
                        </Link>
                      ))}
                  </div>
                </div>

                {/* Hidden Ability */}
                {pokemon.abilities_info?.hidden && (
                  <div>
                    <p className="text-gray-400 text-xs font-semibold mb-2">
                      Hidden
                    </p>
                    <Link
                      href={`/abilities/${pokemon.abilities_info.hidden
                        .toLowerCase()
                        .replace(/\s+/g, "-")}`}
                    >
                      <span className="inline-block bg-purple-900 text-purple-100 px-4 py-2 rounded-full text-sm font-medium border border-purple-700 hover:bg-purple-800 hover:border-purple-500 cursor-pointer transition-colors">
                        {pokemon.abilities_info.hidden.charAt(0).toUpperCase() + pokemon.abilities_info.hidden.slice(1)}
                      </span>
                    </Link>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Evolution Hint */}
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
            <p className="text-gray-300 text-sm">
              💡 <strong>Evolution Tip:</strong> Evolution chain data coming
              soon! Check related Pokémon by searching for evolution stages in
              the Pokédex.
            </p>
          </div>

          {/* Evolution Chain */}
          {pokemon.evolution && pokemon.evolution.evolutions.length > 0 && (
            <div>
              <h3 className="font-bold text-white mb-4 text-lg">
                Evolution Chain
              </h3>
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-4 overflow-x-auto">
                {/* Horizontal Evolution Chain */}
                <div className="flex items-center justify-start gap-2 min-w-max pb-2">
                  {/* Starting Pokemon */}
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

                  {/* Evolution Chain */}
                  {pokemon.evolution.evolutions.map(
                    (evo: Evolution, idx: number) => (
                      <div
                        key={idx}
                        className="flex items-center gap-2 flex-shrink-0"
                      >
                        <div className="text-yellow-400 text-lg font-bold">
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
                          <Link href={`/pokedex?search=${evo.name}`}>
                            <p className="font-bold text-blue-400 text-sm hover:underline cursor-pointer whitespace-nowrap">
                              {evo.name}
                            </p>
                          </Link>
                          <p className="text-xs text-gray-400 mt-1 text-center max-w-[120px]">
                            {evo.method}
                          </p>
                        </div>
                      </div>
                    )
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
                    className="bg-gray-800 p-4 rounded border border-gray-700"
                  >
                    <p className="text-sm font-bold text-gray-200 mb-2 capitalize">
                      {t}
                    </p>
                    <div className="flex gap-1 flex-wrap">
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

          {/* Stats */}
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
                      className="bg-gray-800 p-3 rounded border border-gray-700"
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
        </div>
      </div>
    </div>
  );
}

"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";

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
  moves: string[];
  generation: number;
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
}

interface PokemonGridProps {
  typeFilter?: string;
  generationFilter?: number;
  abilityFilter?: string;
  moveFilter?: string;
  searchQuery?: string;
}

export default function PokemonGrid({
  typeFilter,
  generationFilter,
  abilityFilter,
  moveFilter,
  searchQuery,
}: PokemonGridProps) {
  const [pokemon, setPokemon] = useState<Pokemon[]>([]);
  const [filteredPokemon, setFilteredPokemon] = useState<Pokemon[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPokemon = async () => {
      try {
        const response = await fetch("/api/data");
        const data = await response.json();
        setPokemon(data);
      } catch (error) {
        console.error("Error fetching pokemon:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchPokemon();
  }, []);

  useEffect(() => {
    let filtered = pokemon;

    // Filter by generation
    if (generationFilter && generationFilter !== 0) {
      filtered = filtered.filter((p) => p.generation === generationFilter);
    }

    // Filter by type
    if (typeFilter && typeFilter !== "all") {
      filtered = filtered.filter((p) =>
        p.types
          .map((t: string) => t.toLowerCase())
          .includes(typeFilter.toLowerCase())
      );
    }

    // Filter by ability
    if (abilityFilter && abilityFilter !== "all") {
      filtered = filtered.filter((p) =>
        p.abilities
          .map((a: string) => a.toLowerCase())
          .includes(abilityFilter.toLowerCase())
      );
    }

    // Filter by move
    if (moveFilter && moveFilter !== "all") {
      filtered = filtered.filter((p) =>
        p.moves
          .map((m: string) => m.toLowerCase())
          .includes(moveFilter.toLowerCase())
      );
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (p) =>
          p.name.toLowerCase().includes(query) ||
          p.types.some((t: string) => t.toLowerCase().includes(query))
      );
    }

    setFilteredPokemon(filtered);
  }, [
    pokemon,
    typeFilter,
    generationFilter,
    abilityFilter,
    moveFilter,
    searchQuery,
  ]);

  const getTypeColor = (type: string): string => {
    const colors: Record<string, string> = {
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
    return colors[type.toLowerCase()] || "bg-gray-400";
  };

  const getSpriteUrl = (pokemonName: string): string => {
    const formatted = pokemonName.toLowerCase().replace(/\s+/g, "-");
    return `/home-sprites/${formatted}.png`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="text-xl font-semibold text-gray-600">
          Loading Pokédex...
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      <h2 className="text-2xl font-bold text-white mb-6">
        Pokédex ({filteredPokemon.length})
      </h2>

      {/* Pokemon Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {filteredPokemon.map((p) => (
          <Link key={p.id} href={`/pokemon/${p.name.toLowerCase()}`}>
            <div className="group cursor-pointer bg-gray-900 rounded-2xl shadow-lg hover:shadow-2xl transition-all hover:scale-105 overflow-hidden border border-gray-700 hover:border-yellow-500 grid-item-3d">
              {/* Pokemon Card */}
              <div className="aspect-square bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center relative">
                <img
                  src={getSpriteUrl(p.name)}
                  alt={p.name}
                  className="w-24 h-24 object-contain"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = "/placeholder.svg";
                  }}
                />
              </div>

              {/* Pokemon Info */}
              <div className="p-3 bg-gray-900">
                <h3 className="font-bold text-sm text-white truncate">
                  {p.name}
                </h3>
                <p className="text-xs text-gray-400 mb-2">{p.number}</p>
                <div className="flex gap-1 flex-wrap">
                  {p.types.slice(0, 2).map((t: string) => (
                    <span
                      key={t}
                      className={`text-xs font-semibold text-white px-2 py-1 rounded ${getTypeColor(
                        t
                      )}`}
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* No Results */}
      {filteredPokemon.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-400 text-lg">
            No Pokémon found matching your filters.
          </p>
        </div>
      )}
    </div>
  );
}

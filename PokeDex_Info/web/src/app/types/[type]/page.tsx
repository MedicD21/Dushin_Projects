"use client";

import { useParams } from "next/navigation";
import { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";

interface Pokemon {
  id: string;
  number: number;
  name: string;
  types: string[];
}

interface TypeDetail {
  name: string;
  pokemon: Pokemon[];
}

const TYPE_WEAKNESSES: Record<string, string[]> = {
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

const TYPE_COLORS: Record<string, string> = {
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

export default function TypeDetailPage() {
  const params = useParams();
  const typeParam = params.type as string;
  const typeName = typeParam.charAt(0).toUpperCase() + typeParam.slice(1);

  const [pokemon, setPokemon] = useState<Pokemon[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPokemon = async () => {
      try {
        const response = await fetch("/api/data");
        const data = await response.json();

        // Filter Pokemon that have this type
        const withType = data.filter((p: Pokemon) =>
          p.types.some(
            (t: string) => t.toLowerCase() === typeName.toLowerCase()
          )
        );

        setPokemon(withType);
      } catch (error) {
        console.error("Error fetching pokemon:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchPokemon();
  }, [typeName]);

  const weaknesses = TYPE_WEAKNESSES[typeName.toLowerCase()] || [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-cyan-900 to-slate-900">
      {/* Header */}
      <div
        className={`${
          TYPE_COLORS[typeName.toLowerCase()] || "bg-gray-700"
        } text-white p-8`}
      >
        <div className="flex items-center gap-3 mb-4">
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
            <button className="text-white/70 hover:text-white transition">
              ← Back to Pokédex
            </button>
          </Link>
        </div>
        <h1 className="text-4xl font-bold capitalize pokemon-header">{typeName} Type</h1>
        <p className="text-white/70 mt-2">{pokemon.length} Pokémon available</p>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Type Advantages */}
        <div className="grid md:grid-cols-2 gap-8 mb-8">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h2 className="text-xl font-bold text-white mb-4">Weaknesses</h2>
            {weaknesses.length > 0 ? (
              <div className="flex gap-2 flex-wrap">
                {weaknesses.map((weakness) => (
                  <Link
                    key={weakness}
                    href={`/types/${weakness.toLowerCase()}`}
                  >
                    <span
                      className={`text-white font-bold px-4 py-2 rounded-full capitalize ${
                        TYPE_COLORS[weakness] || "bg-gray-600"
                      } hover:opacity-80 transition-opacity cursor-pointer`}
                    >
                      {weakness}
                    </span>
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-gray-400">No weaknesses</p>
            )}
          </div>

          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h2 className="text-xl font-bold text-white mb-4">Coverage</h2>
            <p className="text-gray-300">
              {typeName} type moves are effective against{" "}
              {Object.entries(TYPE_WEAKNESSES)
                .filter(([_, weakTo]) =>
                  weakTo.includes(typeName.toLowerCase())
                )
                .map(([type]) => type)
                .join(", ") || "no types"}
            </p>
          </div>
        </div>

        {/* Pokemon List */}
        <h2 className="text-2xl font-bold text-white mb-6">
          {typeName} Pokémon
        </h2>

        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-400">Loading...</p>
          </div>
        ) : pokemon.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {pokemon.map((p: Pokemon) => (
              <Link
                key={p.id}
                href={`/pokedex?pokemon=${p.id}`}
                className="group"
              >
                <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 hover:border-yellow-500 transition-all hover:shadow-lg hover:shadow-yellow-500/20">
                  <div className="text-center">
                    <p className="text-xs text-gray-400 mb-1">
                      #{String(p.number).padStart(3, "0")}
                    </p>
                    <h3 className="text-lg font-bold text-white capitalize group-hover:text-yellow-400 transition">
                      {p.name}
                    </h3>
                    <div className="flex gap-1 justify-center mt-2 flex-wrap">
                      {p.types.map((t: string) => (
                        <span
                          key={t}
                          className={`text-xs px-2 py-1 rounded text-white font-semibold capitalize ${
                            TYPE_COLORS[t.toLowerCase()] || "bg-gray-600"
                          }`}
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
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-400 text-lg">
              No Pokémon found with this type.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

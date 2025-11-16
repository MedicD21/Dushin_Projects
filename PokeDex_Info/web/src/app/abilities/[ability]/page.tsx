"use client";

import { useParams, useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import Link from "next/link";

interface Pokemon {
  id: string;
  number: number;
  name: string;
  types: string[];
  abilities: string[];
}

interface Ability {
  name: string;
  description?: string;
  pokemon: Pokemon[];
}

export default function AbilityDetailPage() {
  const params = useParams();
  const router = useRouter();
  const abilityParam = params.ability as string;
  const abilityName = abilityParam
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");

  const [pokemon, setPokemon] = useState<Pokemon[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPokemon = async () => {
      try {
        const response = await fetch("/api/data");
        const data = await response.json();

        // Filter Pokemon that have this ability
        const withAbility = data.filter((p: Pokemon) =>
          p.abilities.some(
            (a: string) => a.toLowerCase() === abilityName.toLowerCase()
          )
        );

        setPokemon(withAbility);
      } catch (error) {
        console.error("Error fetching pokemon:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchPokemon();
  }, [abilityName]);

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-8">
        <button
          onClick={() => router.back()}
          className="mb-4 text-blue-100 hover:text-white transition"
        >
          ← Back
        </button>
        <h1 className="text-4xl font-bold">{abilityName}</h1>
        <p className="text-blue-100 mt-2">
          Available to {pokemon.length} Pokémon
        </p>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Ability Description */}
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-white mb-2">Description</h2>
          <p className="text-gray-300">
            {abilityName} is an ability that can be obtained by various Pokémon
            across different generations. Click on any Pokémon below to see more
            details.
          </p>
        </div>

        {/* Pokemon List */}
        <h2 className="text-2xl font-bold text-white mb-6">
          Pokémon with {abilityName}
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
                          className="text-xs px-2 py-1 rounded bg-gray-700 text-gray-200"
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
              No Pokémon found with this ability.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

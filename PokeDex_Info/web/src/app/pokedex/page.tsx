"use client";

import { useState } from "react";
import PokemonGrid from "@/components/PokemonGrid";

export default function PokemonDex() {
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [generationFilter, setGenerationFilter] = useState<number>(0);
  const [searchQuery, setSearchQuery] = useState<string>("");

  const types = [
    "all",
    "normal",
    "fire",
    "water",
    "grass",
    "electric",
    "ice",
    "fighting",
    "poison",
    "ground",
    "flying",
    "psychic",
    "bug",
    "rock",
    "ghost",
    "dragon",
    "dark",
    "steel",
    "fairy",
  ];

  const generations = [
    { value: 0, label: "All Generations" },
    { value: 1, label: "Gen I" },
    { value: 2, label: "Gen II" },
    { value: 3, label: "Gen III" },
    { value: 4, label: "Gen IV" },
    { value: 5, label: "Gen V" },
    { value: 6, label: "Gen VI" },
    { value: 7, label: "Gen VII" },
    { value: 8, label: "Gen VIII" },
    { value: 9, label: "Gen IX" },
  ];

  const getTypeColor = (type: string): string => {
    const colors: Record<string, string> = {
      all: "bg-gray-700 text-white",
      normal: "bg-gray-500 text-white",
      fire: "bg-red-600 text-white",
      water: "bg-blue-600 text-white",
      grass: "bg-green-600 text-white",
      electric: "bg-yellow-500 text-gray-900",
      ice: "bg-blue-400 text-gray-900",
      fighting: "bg-red-800 text-white",
      poison: "bg-purple-600 text-white",
      ground: "bg-yellow-700 text-white",
      flying: "bg-sky-500 text-white",
      psychic: "bg-pink-600 text-white",
      bug: "bg-green-700 text-white",
      rock: "bg-gray-700 text-white",
      ghost: "bg-purple-800 text-white",
      dragon: "bg-indigo-700 text-white",
      dark: "bg-gray-800 text-white",
      steel: "bg-slate-600 text-white",
      fairy: "bg-pink-500 text-white",
    };
    return colors[type] || "bg-gray-700 text-white";
  };

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-8">
        <h1 className="text-4xl font-bold mb-2">PokéOS Dex</h1>
        <p className="text-sm opacity-90">
          Explore and filter the complete Pokédex
        </p>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 border-b border-gray-700 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-6">
          {/* Search */}
          <div className="mb-6">
            <input
              type="text"
              placeholder="Search by Pokémon name or type..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
            />
          </div>

          {/* Generation Filter */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-200 mb-2">
              Generation
            </label>
            <div className="flex gap-2 flex-wrap">
              {generations.map((gen) => (
                <button
                  key={gen.value}
                  onClick={() => setGenerationFilter(gen.value)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    generationFilter === gen.value
                      ? "bg-blue-600 text-white shadow-lg"
                      : "bg-gray-700 text-gray-200 hover:bg-gray-600"
                  }`}
                >
                  {gen.label}
                </button>
              ))}
            </div>
          </div>

          {/* Type Filter */}
          <div>
            <label className="block text-sm font-semibold text-gray-200 mb-2">
              Type
            </label>
            <div className="flex gap-2 flex-wrap">
              {types.map((type) => (
                <button
                  key={type}
                  onClick={() => setTypeFilter(type)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    typeFilter === type
                      ? `${getTypeColor(type)} shadow-lg scale-105`
                      : `${getTypeColor(type)} opacity-60 hover:opacity-100`
                  }`}
                >
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <PokemonGrid
          typeFilter={typeFilter}
          generationFilter={generationFilter}
          searchQuery={searchQuery}
        />
      </div>
    </div>
  );
}

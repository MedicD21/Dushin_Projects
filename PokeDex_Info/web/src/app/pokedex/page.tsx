"use client";

import { useState, useEffect } from "react";
import PokemonGrid from "@/components/PokemonGrid";

interface Pokemon {
  abilities: string[];
}

export default function PokemonDex() {
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [generationFilter, setGenerationFilter] = useState<number>(0);
  const [abilityFilter, setAbilityFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [filtersOpen, setFiltersOpen] = useState<boolean>(false);
  const [expandedFilters, setExpandedFilters] = useState<
    Record<string, boolean>
  >({
    generation: true,
    type: false,
    ability: false,
  });
  const [abilities, setAbilities] = useState<string[]>([]);
  const [loadingAbilities, setLoadingAbilities] = useState(true);

  // Fetch unique abilities from Pokemon data
  useEffect(() => {
    const fetchAbilities = async () => {
      try {
        const response = await fetch("/api/data");
        const data: Pokemon[] = await response.json();

        // Extract and deduplicate abilities
        const uniqueAbilities = new Set<string>();
        data.forEach((pokemon) => {
          pokemon.abilities?.forEach((ability) => {
            uniqueAbilities.add(ability);
          });
        });

        // Sort alphabetically and add "all" at the beginning
        const sortedAbilities = ["all", ...Array.from(uniqueAbilities).sort()];
        setAbilities(sortedAbilities);
      } catch (error) {
        console.error("Error fetching abilities:", error);
      } finally {
        setLoadingAbilities(false);
      }
    };

    fetchAbilities();
  }, []);

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

  const toggleFilterSection = (section: string) => {
    setExpandedFilters((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

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

  const getActiveFilterCount = () => {
    let count = 0;
    if (typeFilter !== "all") count++;
    if (generationFilter !== 0) count++;
    if (abilityFilter !== "all") count++;
    if (searchQuery) count++;
    return count;
  };

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-8">
        <h1 className="text-4xl font-bold mb-2">PokeNode Dex</h1>
        <p className="text-sm opacity-90">
          Explore and filter the complete Pokédex
        </p>
      </div>

      {/* Search Bar */}
      <div className="bg-gray-800 border-b border-gray-700 sticky top-0 z-40 px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex gap-3 items-center">
            <input
              type="text"
              placeholder="Search Pokémon..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 text-sm"
            />
            <button
              onClick={() => setFiltersOpen(!filtersOpen)}
              className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${
                filtersOpen
                  ? "bg-yellow-500 text-gray-900"
                  : "bg-gray-700 text-gray-200 hover:bg-gray-600"
              }`}
            >
              <span>⚙️ Filters</span>
              {getActiveFilterCount() > 0 && (
                <span className="bg-red-600 text-white text-xs rounded-full px-2 py-0.5">
                  {getActiveFilterCount()}
                </span>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Collapsible Filters */}
      {filtersOpen && (
        <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
          <div className="max-w-7xl mx-auto space-y-4">
            {/* Generation Filter */}
            <div className="bg-gray-900 rounded-lg p-4">
              <button
                onClick={() => toggleFilterSection("generation")}
                className="w-full flex justify-between items-center hover:text-yellow-400 transition-colors"
              >
                <h3 className="text-sm font-bold text-white">Generation</h3>
                <span className="text-lg">
                  {expandedFilters.generation ? "−" : "+"}
                </span>
              </button>
              {expandedFilters.generation && (
                <div className="mt-3 flex gap-1.5 flex-wrap">
                  {generations.map((gen) => (
                    <button
                      key={gen.value}
                      onClick={() => setGenerationFilter(gen.value)}
                      className={`px-3 py-1.5 rounded-lg font-medium text-xs transition-all ${
                        generationFilter === gen.value
                          ? "bg-blue-600 text-white shadow-lg"
                          : "bg-gray-700 text-gray-200 hover:bg-gray-600"
                      }`}
                    >
                      {gen.label}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Type Filter */}
            <div className="bg-gray-900 rounded-lg p-4">
              <button
                onClick={() => toggleFilterSection("type")}
                className="w-full flex justify-between items-center hover:text-yellow-400 transition-colors"
              >
                <h3 className="text-sm font-bold text-white">Type</h3>
                <span className="text-lg">
                  {expandedFilters.type ? "−" : "+"}
                </span>
              </button>
              {expandedFilters.type && (
                <div className="mt-3 flex gap-1.5 flex-wrap">
                  {types.map((type) => (
                    <button
                      key={type}
                      onClick={() => setTypeFilter(type)}
                      className={`px-3 py-1.5 rounded-lg font-medium text-xs transition-all ${
                        typeFilter === type
                          ? `${getTypeColor(type)} shadow-lg scale-105`
                          : `${getTypeColor(type)} opacity-60 hover:opacity-100`
                      }`}
                    >
                      {type.charAt(0).toUpperCase() + type.slice(1)}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Ability Filter */}
            <div className="bg-gray-900 rounded-lg p-4">
              <button
                onClick={() => toggleFilterSection("ability")}
                className="w-full flex justify-between items-center hover:text-yellow-400 transition-colors"
              >
                <h3 className="text-sm font-bold text-white">Ability</h3>
                <span className="text-lg">
                  {expandedFilters.ability ? "−" : "+"}
                </span>
              </button>
              {expandedFilters.ability && (
                <div className="mt-3 flex gap-1.5 flex-wrap">
                  {loadingAbilities ? (
                    <p className="text-xs text-gray-400">
                      Loading abilities...
                    </p>
                  ) : (
                    abilities.map((ability) => (
                      <button
                        key={ability}
                        onClick={() => setAbilityFilter(ability)}
                        className={`px-3 py-1.5 rounded-lg font-medium text-xs transition-all ${
                          abilityFilter === ability
                            ? "bg-purple-600 text-white shadow-lg scale-105"
                            : "bg-gray-700 text-gray-200 hover:bg-gray-600"
                        }`}
                      >
                        {ability.charAt(0).toUpperCase() + ability.slice(1)}
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>

            {/* Clear Filters Button */}
            {getActiveFilterCount() > 0 && (
              <button
                onClick={() => {
                  setTypeFilter("all");
                  setGenerationFilter(0);
                  setAbilityFilter("all");
                  setSearchQuery("");
                }}
                className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium text-sm transition-all"
              >
                Clear All Filters
              </button>
            )}
          </div>
        </div>
      )}

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <PokemonGrid
          typeFilter={typeFilter}
          generationFilter={generationFilter}
          abilityFilter={abilityFilter}
          searchQuery={searchQuery}
        />
      </div>
    </div>
  );
}

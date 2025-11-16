"use client";

import { useState, useEffect, useCallback } from "react";
import { pokedexSearch, SearchResult } from "@/lib/search";

export default function SearchBar() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedTypes, setSelectedTypes] = useState<
    ("pokemon" | "item" | "ability" | "move")[]
  >([]);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    pokedexSearch.initialize();
  }, []);

  const handleSearch = useCallback(
    (value: string) => {
      setQuery(value);
      if (value.trim().length === 0) {
        setResults([]);
        return;
      }

      setIsLoading(true);
      setTimeout(() => {
        const searchResults = pokedexSearch.search(
          value,
          selectedTypes.length > 0 ? selectedTypes : undefined,
          50
        );
        setResults(searchResults);
        setIsLoading(false);
      }, 100);
    },
    [selectedTypes]
  );

  const toggleType = (type: "pokemon" | "item" | "ability" | "move") => {
    setSelectedTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  const getTypeColor = (type: string) => {
    const colors: { [key: string]: string } = {
      pokemon: "bg-red-500",
      item: "bg-yellow-500",
      ability: "bg-purple-500",
      move: "bg-blue-500",
    };
    return colors[type] || "bg-gray-500";
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4">
      <div className="relative">
        {/* Search Input */}
        <div className="flex items-center gap-2 mb-4">
          <input
            type="text"
            value={query}
            onChange={(e) => handleSearch(e.target.value)}
            onFocus={() => setShowDropdown(true)}
            onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
            placeholder="Search Pokémon, Items, Abilities, Moves..."
            className="flex-1 px-4 py-3 rounded-lg border-2 border-pokemon-yellow bg-pokemon-light text-pokemon-dark placeholder-gray-500 focus:outline-none focus:border-pokemon-red transition-colors"
          />
          <button className="px-4 py-3 bg-pokemon-gradient text-white rounded-lg font-bold hover:shadow-lg transition-shadow">
            🔍
          </button>
        </div>

        {/* Type Filters */}
        <div className="flex gap-2 mb-4 flex-wrap">
          {["pokemon", "item", "ability", "move"].map((type) => (
            <button
              key={type}
              onClick={() => toggleType(type as any)}
              className={`px-3 py-1 rounded-full text-sm font-semibold transition-all ${
                selectedTypes.includes(type as any)
                  ? `${getTypeColor(type)} text-white shadow-lg`
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>

        {/* Results Dropdown */}
        {showDropdown && (query || results.length > 0) && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white border-2 border-pokemon-yellow rounded-lg shadow-xl z-50 max-h-96 overflow-y-auto">
            {isLoading ? (
              <div className="p-4 text-center text-gray-500">
                <div className="animate-spin inline-block">⚡</div> Searching...
              </div>
            ) : results.length > 0 ? (
              <div className="divide-y">
                {results.map((result, idx) => (
                  <div
                    key={`${result.type}-${idx}`}
                    className="p-3 hover:bg-pokemon-light cursor-pointer transition-colors border-l-4"
                    style={{
                      borderLeftColor: {
                        pokemon: "#FF0000",
                        item: "#FFCC00",
                        ability: "#A020F0",
                        move: "#3B4CCA",
                      }[result.type],
                    }}
                  >
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-xs font-bold text-white px-2 py-1 rounded ${getTypeColor(
                          result.type
                        )}`}
                      >
                        {result.type.toUpperCase()}
                      </span>
                      <div className="flex-1">
                        <div className="font-bold text-pokemon-dark">
                          {result.name}
                        </div>
                        {result.description && (
                          <div className="text-sm text-gray-600 truncate">
                            {result.description}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-4 text-center text-gray-500">
                No results found for "{query}"
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

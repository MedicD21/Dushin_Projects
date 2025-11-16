import type { Metadata } from "next";
import SearchBar from "@/components/SearchBar";

export const metadata: Metadata = {
  title: "Pokédex Info - Complete Database",
  description:
    "Comprehensive Pokédex with Pokémon, Items, Abilities, and Moves",
};

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-pokemon-yellow via-pokemon-light to-red-100">
      {/* Header */}
      <div className="bg-pokemon-gradient text-white py-8 shadow-lg">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="text-5xl font-bold mb-2">Pokédex Info</h1>
          <p className="text-lg opacity-90">
            Complete Pokémon Database with Items, Abilities, and Moves
          </p>
        </div>
      </div>

      {/* Search Section */}
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="bg-white rounded-lg shadow-2xl p-8">
          <h2 className="text-2xl font-bold text-pokemon-dark mb-6 text-center">
            🔍 Search the Database
          </h2>
          <SearchBar />
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <a
            href="/pokedex"
            className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl hover:scale-105 transition-all cursor-pointer"
          >
            <div className="text-4xl mb-3">🐱</div>
            <h3 className="font-bold text-lg mb-2">PokéOS Dex</h3>
            <p className="text-gray-600">
              Browse all Pokémon with stats, types, and sprites
            </p>
          </a>
          <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="text-4xl mb-3">🎒</div>
            <h3 className="font-bold text-lg mb-2">Items</h3>
            <p className="text-gray-600">
              Explore items with effects and game availability
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="text-4xl mb-3">⚡</div>
            <h3 className="font-bold text-lg mb-2">Abilities</h3>
            <p className="text-gray-600">
              Discover Pokémon abilities and their effects
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="text-4xl mb-3">🎯</div>
            <h3 className="font-bold text-lg mb-2">Moves</h3>
            <p className="text-gray-600">
              Learn about moves across all generations
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-pokemon-dark text-white mt-12 py-8">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p>
            Built with ❤️ for Pokémon fans • Data from Serebii & Pokémon Home
          </p>
        </div>
      </footer>
    </main>
  );
}

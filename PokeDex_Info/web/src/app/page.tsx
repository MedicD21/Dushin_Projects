import type { Metadata } from "next";
import SearchBar from "@/components/SearchBar";
import Image from "next/image";

export const metadata: Metadata = {
  title: "PokeNode - Catch the Node. In Every Mode",
  description:
    "Complete Pokémon Database with Pokédex, Abilities, Types, and Evolution Chains",
};

// Pokéball icon SVG component
const PokeBall = ({ color }: { color: string }) => (
  <svg
    className="w-12 h-12"
    viewBox="0 0 200 200"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle
      cx="100"
      cy="100"
      r="90"
      stroke={color}
      strokeWidth="4"
      fill="none"
    />
    <rect x="10" y="95" width="180" height="10" fill={color} />
    <circle cx="100" cy="100" r="15" fill={color} />
    <circle cx="100" cy="30" r="25" fill={color} />
    <circle cx="100" cy="30" r="20" fill="white" />
    <circle cx="100" cy="170" r="25" fill="gray" />
    <circle cx="100" cy="170" r="20" fill="white" />
  </svg>
);

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-gray-900">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-12 shadow-lg">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center gap-4 mb-4">
            <Image
              src="/dex_logo.png"
              alt="PokeNode Logo"
              width={80}
              height={80}
              className="h-20 w-20 object-contain"
            />
            <div>
              <h1 className="text-5xl font-bold">PokeNode</h1>
              <p className="text-xl opacity-90 italic">
                Catch the Node. In Every Mode
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Search Section */}
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="bg-gray-800 rounded-lg shadow-2xl p-8 border border-gray-700">
          <h2 className="text-2xl font-bold text-white mb-6 text-center">
            Search the Database
          </h2>
          <SearchBar />
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <a
            href="/pokedex"
            className="bg-gray-800 rounded-lg shadow-lg p-6 hover:shadow-xl hover:scale-105 transition-all cursor-pointer border border-gray-700 hover:border-yellow-500 flex flex-col items-center"
          >
            <div className="mb-4">
              <PokeBall color="#FF4A4A" />
            </div>
            <h3 className="font-bold text-lg mb-2 text-white text-center">
              PokeNode Dex
            </h3>
            <p className="text-gray-400 text-center text-sm">
              Browse all 1025 Pokémon with stats, types, and evolution chains
            </p>
          </a>
          <div className="bg-gray-800 rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow border border-gray-700 hover:border-yellow-500 cursor-pointer flex flex-col items-center">
            <div className="mb-4">
              <PokeBall color="#3B82F6" />
            </div>
            <h3 className="font-bold text-lg mb-2 text-white text-center">
              Items
            </h3>
            <p className="text-gray-400 text-center text-sm">
              Explore items with effects and game availability
            </p>
          </div>
          <div className="bg-gray-800 rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow border border-gray-700 hover:border-yellow-500 cursor-pointer flex flex-col items-center">
            <div className="mb-4">
              <PokeBall color="#FBBF24" />
            </div>
            <h3 className="font-bold text-lg mb-2 text-white text-center">
              Abilities
            </h3>
            <p className="text-gray-400 text-center text-sm">
              Discover Pokémon abilities and their effects
            </p>
          </div>
          <div className="bg-gray-800 rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow border border-gray-700 hover:border-yellow-500 cursor-pointer flex flex-col items-center">
            <div className="mb-4">
              <PokeBall color="#10B981" />
            </div>
            <h3 className="font-bold text-lg mb-2 text-white text-center">
              Moves
            </h3>
            <p className="text-gray-400 text-center text-sm">
              Learn about moves across all generations
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-950 text-white mt-12 py-8 border-t border-gray-700">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p>Built with ❤️ for Pokémon fans • Data from PokéAPI & Serebii</p>
        </div>
      </footer>
    </main>
  );
}

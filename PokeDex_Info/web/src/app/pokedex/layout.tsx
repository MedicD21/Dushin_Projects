import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "PokéOS Dex - Complete Pokédex",
  description:
    "Browse and filter all Pokémon with detailed stats and information",
};

export default function PokemonDexLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

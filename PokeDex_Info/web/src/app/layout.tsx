import { ReactNode } from 'react'
import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'PokeNode - Catch the Node. In Every Mode',
  description: 'Complete Pokémon database with Pokédex, Abilities, Types, and Evolution Chains',
}

export default function RootLayout({
  children,
}: {
  children: ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

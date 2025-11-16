import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "pokemon-yellow": "#FFCC00",
        "pokemon-blue": "#3B4CCA",
        "pokemon-red": "#FF0000",
        "pokemon-dark": "#1a1a2e",
        "pokemon-light": "#f5f5f5",
      },
      backgroundImage: {
        "pokemon-gradient": "linear-gradient(135deg, #FFCC00 0%, #FF0000 100%)",
      },
    },
  },
  plugins: [],
};
export default config;

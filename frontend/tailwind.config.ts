import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#8B5CF6',
        dark: '#0F172A',
      },
      backgroundImage: {
        gradient: 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)',
      },
    },
  },
  plugins: [],
}
export default config

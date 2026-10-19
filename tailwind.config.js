/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#09090b', // Zinc-950
        surface: '#121215',    // Slightly lighter card tone
        'surface-subtle': '#18181b', // Zinc-900
        border: 'rgba(255, 255, 255, 0.07)',
        'border-subtle': 'rgba(255, 255, 255, 0.04)',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'SF Mono', 'Menlo', 'monospace'],
      }
    },
  },
  plugins: [],
}

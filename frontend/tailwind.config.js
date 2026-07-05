/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Custom dark palette mapping the landing page and sidebar
        darkbg: {
          950: '#060B24',
          900: '#0A1128',
          800: '#101B3A',
          700: '#1C2541',
        },
        // Premium brand colors
        brand: {
          500: '#6366F1', // main indigo buttons
          600: '#4F46E5', // dark hover state
          700: '#4338CA',
        },
        // Risk status colors
        risk: {
          safe: '#10B981',       // Green
          verify: '#EAB308',     // Yellow
          suspicious: '#F97316', // Orange
          danger: '#EF4444',     // Red
        }
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: '#121212',  // Darker background
        'dark-lighter': '#1E1E1E',  // Slightly lighter for contrast
      },
      opacity: {
        '85': '0.85',
      },
      fontFamily: {
        'serif': ['Crimson Pro', 'serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}


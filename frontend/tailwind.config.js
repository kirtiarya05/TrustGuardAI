/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: "#101014", // deep charcoal background as per design
        panel: "#16161d", // card background
        accent: "#00FF88", // neon green
        "accent-dark": "#00CC6A",
        "neon-blue": "#00FFFF",
        graytext: "#a0a0ab"
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Source Code Pro', 'monospace'],
        display: ['Poppins', 'sans-serif']
      }
    },
  },
  plugins: [],
}

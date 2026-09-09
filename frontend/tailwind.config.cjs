/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    // Everything inside src/
    "./src/**/*.{js,jsx,ts,tsx}",
    // Your root-level app folders
    "./api/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
    "./context/**/*.{js,jsx,ts,tsx}",
    "./hooks/**/*.{js,jsx,ts,tsx}",
    "./pages/**/*.{js,jsx,ts,tsx}",
    "./utils/**/*.{js,jsx,ts,tsx}",
    "./assets/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
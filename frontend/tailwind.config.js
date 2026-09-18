/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        eco: {
          50: "#f0f9f1",
          100: "#dcf0df",
          200: "#bce2c2",
          300: "#8ecc99",
          400: "#5cad6c",
          500: "#3a8f4d",
          600: "#28723a",
          700: "#215b30",
          800: "#1d4829",
          900: "#193c23",
        },
      },
    },
  },
  plugins: [],
};

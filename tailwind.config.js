/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["**/*.html"],
  theme: {
    extend: {
      colors: {
        jade: {
          50: "#d8eee8",
          100: "#99dbc8",
          200: "#5ed3b2",
          300: "#27d3a2",
          400: "#11bc8b",
          500: "#00A878",
          600: "#0b7859",
          700: "#105642",
          800: "#113f32",
          900: "#102e25",
        },
        mindaro: "#d8f1a0",
        earth: "#f3c178",
        tomato: {
          100: "#F2E3E1",
          200: "#EAC5BF",
          300: "#E8A69A",
          400: "#EE8470",
          500: "#FE5E41",
          600: "#E85237",
          700: "#D14A32",
          800: "#AF4B39",
          900: "#934B3E",
        },
        smoky: "#0b0500",
      },
    },
  },
  plugins: [],
};

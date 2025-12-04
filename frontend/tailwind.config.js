/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#008080',
          hover: '#006666',
          light: '#e6f3f3',
        },
        secondary: {
          DEFAULT: '#C8A2C8',
          hover: '#b88fb8',
          light: '#f5eef5',
        },
      },
    },
  },
  plugins: [],
}

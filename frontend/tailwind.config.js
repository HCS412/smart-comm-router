/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        "dsq-blue": {
          50: "#EFF6FF",
          600: "#3B82F6",
          700: "#2563EB",
        },
        "dsq-gray": {
          700: "#4B5563",
        },
        "dsq-green": "#10B981",
      },
      fontFamily: {
        sans: ["Roboto", "Open Sans", "sans-serif"],
      },
    },
  },
  plugins: [],
};

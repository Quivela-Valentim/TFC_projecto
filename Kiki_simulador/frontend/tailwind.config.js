/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        base: {
          950: "#070E1F",
          900: "#0A1428",
          850: "#0D1A33",
          800: "#0F1F3D",
          700: "#16294F",
          600: "#223862",
          500: "#3A5075",
        },
        vivo: {
          400: "#5C8CFF",
          500: "#2B6CFF",
          600: "#1B54DB",
          700: "#153F9E",
        },
        marfim: {
          50: "#FFFFFF",
          100: "#F5F8FF",
          200: "#E4EAF7",
          300: "#B9C4DC",
          400: "#93A5C9",
        },
        sucesso: { DEFAULT: "#22C55E", bg: "#16321F" },
        perigo: { DEFAULT: "#EF4444", bg: "#3A1A1A" },
        aviso: { DEFAULT: "#F5A524", bg: "#3A2A0F" },
      },
      fontFamily: {
        display: ["Sora", "system-ui", "sans-serif"],
        body: ["Inter", "system-ui", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
      boxShadow: {
        painel: "0 1px 0 0 rgba(255,255,255,0.04) inset, 0 8px 24px -12px rgba(0,0,0,0.5)",
      },
    },
  },
  plugins: [],
};

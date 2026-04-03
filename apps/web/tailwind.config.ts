import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#07111f",
        panel: "#0f1729",
        line: "#1d3254",
        glow: "#4fd1c5",
        accent: "#82f7d5",
        warm: "#ff9d5c"
      },
      fontFamily: {
        sans: ["var(--font-sans)"],
        display: ["var(--font-display)"]
      },
      boxShadow: {
        panel: "0 20px 80px rgba(0, 0, 0, 0.35)"
      },
      backgroundImage: {
        aurora:
          "radial-gradient(circle at 20% 20%, rgba(79, 209, 197, 0.14), transparent 30%), radial-gradient(circle at 80% 0%, rgba(130, 247, 213, 0.18), transparent 28%), radial-gradient(circle at 50% 100%, rgba(255, 157, 92, 0.14), transparent 22%)"
      }
    }
  },
  plugins: []
};

export default config;


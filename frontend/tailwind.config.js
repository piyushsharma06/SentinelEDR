/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        soc: {
          bg: "#0B0F19",
          card: "#111827",
          border: "#1F2937",
          muted: "#9CA3AF",
          accent: "#3B82F6",
          critical: "#EF4444",
          high: "#F97316",
          medium: "#F59E0B",
          low: "#3B82F6",
          info: "#6B7280",
          success: "#10B981"
        }
      }
    },
  },
  plugins: [],
}

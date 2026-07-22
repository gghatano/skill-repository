/** Tailwind config for the Skill Repository GitHub Pages site.
 *  Build: web/build-css.sh  (outputs docs/tailwind.css, committed as a vendored asset)
 */
module.exports = {
  content: [
    "./web/index.template.html",
    "./web/skill-detail.template.html",
    "./web/plugin-detail.template.html",
    "./scripts/sync_skills.py",
  ],
  darkMode: "media",
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "-apple-system", "BlinkMacSystemFont", '"SF Pro Text"',
          '"Helvetica Neue"', "Helvetica", "Arial", "sans-serif",
        ],
        mono: ['"SF Mono"', "ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      colors: {
        apple: {
          bg: "#fbfbfd",
          bg2: "#f5f5f7",
          ink: "#1d1d1f",
          inkd: "#f5f5f7",
          sub: "#6e6e73",
          subd: "#a1a1a6",
          card: "#1d1d1f",
          blue: "#0071e3",
          blueh: "#0077ed",
          blued: "#0a84ff",
        },
      },
      boxShadow: {
        apple: "0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.04)",
        applehover: "0 4px 12px rgba(0,0,0,0.06), 0 14px 34px rgba(0,0,0,0.09)",
      },
    },
  },
  plugins: [],
};

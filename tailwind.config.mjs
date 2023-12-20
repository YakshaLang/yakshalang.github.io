/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
	theme: {
		extend: {},
	},
	plugins: [require("daisyui")],
	daisyui: {
		themes: [
			{
				dark: {
					...require("daisyui/src/theming/themes")["dark"],
					"primary": "#9a2036",
					"secondary": "#f9872e",
				},
			},
			{
				light: {
					...require("daisyui/src/theming/themes")["light"],
					"primary": "#cf0e31",
					"secondary": "#f9872e",
				},
			},
		],
	},
}

# Yaksha Lang Website & Docs Site

Build with [Astro](https://astro.build/) + [Tailwindcss](https://tailwindcss.com/) & [DaisyUi](https://daisyui.com/). 

## Quick Start

0. [Install Yarn](https://classic.yarnpkg.com/lang/en/docs/install/) (will require NodeJs)
1. `yarn # Installs dependecies`
2. `yarn dev # Runs development server` 


## Astro Brief

Astro looks for `.astro` or `.md` files in the `src/pages/` directory. Each page is exposed as a route based on its file name.

There's nothing special about `src/components/`, but that's where we like to put any Astro/React/Vue/Svelte/Preact components.

Any static assets, like images, can be placed in the `public/` directory.

## 🧞 Commands

All commands are run from the root of the project, from a terminal:

| Command                   | Action                                           |
| :------------------------ | :----------------------------------------------- |
| `yarn install`            | Installs dependencies                            |
| `yarn dev`                | Starts local dev server at `localhost:4321`      |
| `yarn build`              | Build your production site to `./dist/`          |
| `yarn preview`            | Preview your build locally, before deploying     |
| `yarn astro ...`          | Run CLI commands like `astro add`, `astro check` |
| `yarn astro -- --help`    | Get help using the Astro CLI                     |

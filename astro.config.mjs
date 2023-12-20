import { defineConfig } from 'astro/config';

import tailwind from "@astrojs/tailwind";

// https://astro.build/config
export default defineConfig({
  site: 'https://gdwr.github.io',
  base: '/yakshalang.github.io',
  integrations: [tailwind()],
});
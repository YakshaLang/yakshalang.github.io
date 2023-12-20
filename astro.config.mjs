import { defineConfig } from 'astro/config';

import tailwind from "@astrojs/tailwind";

import yakshaGrammar from './yaksha.tmLanguage.json';

// https://astro.build/config
export default defineConfig({
  site: 'https://gdwr.github.io',
  base: '/yakshalang.github.io',
  integrations: [tailwind()],
  markdown: {
    shikiConfig: {
      langs: [{
        name: 'yaksha',
        scopeName: 'source.yaksha',
        ...yakshaGrammar
      }, "c", "scheme"]
    }
  }
});
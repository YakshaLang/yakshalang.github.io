import { defineConfig } from 'astro/config';
import tailwind from "@astrojs/tailwind";
import yakshaGrammar from './yaksha.tmLanguage.json';

import mdx from "@astrojs/mdx";

// https://astro.build/config
export default defineConfig({
  site: 'https://gdwr.github.io',
  base: '/yakshalang.github.io',
  integrations: [tailwind(), mdx()],
  markdown: {
    shikiConfig: {
      wrap: true,
      langs: [{
        name: 'yaksha',
        scopeName: 'source.yaksha',
        ...yakshaGrammar
      }, "c", "scheme"]
    }
  }
});
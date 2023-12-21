import { defineConfig } from 'astro/config';
import tailwind from "@astrojs/tailwind";

import mdx from "@astrojs/mdx";
import fetch from 'node-fetch';

// Downloads yaksha grammar from main repo, may change in the future?
const yakshaGrammarUrl = "https://raw.githubusercontent.com/YakshaLang/Yaksha/main/editor/vscode/syntaxes/yaksha.json";
var resp = await fetch(yakshaGrammarUrl, {method: "GET"});
let yakshaGrammar = await resp.json();


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
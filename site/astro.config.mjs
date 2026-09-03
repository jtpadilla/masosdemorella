// @ts-check
import { defineConfig } from 'astro/config';
import { unified } from '@astrojs/markdown-remark';
import sitemap from '@astrojs/sitemap';
import rehypeBook from './src/lib/rehype-book.mjs';

// En GitHub Actions, GITHUB_REPOSITORY = "propietari/repositori". El lloc es publica a
// https://propietari.github.io/repositori/ (o a l'arrel si el repositori és propietari.github.io).
// SITE_URL i BASE_PATH permeten forçar-ho (domini propi, etc.).
const [owner, repo] = (process.env.GITHUB_REPOSITORY ?? '').split('/');
const userSite = repo && repo.toLowerCase() === `${owner.toLowerCase()}.github.io`;

export default defineConfig({
  site: process.env.SITE_URL ?? (owner ? `https://${owner}.github.io` : 'http://localhost:4321'),
  base: process.env.BASE_PATH ?? (owner && !userSite ? `/${repo}` : '/'),
  trailingSlash: 'always',
  integrations: [sitemap()], // genera sitemap-index.xml a partir de `site` + `base` (T-10)
  image: { layout: 'constrained', responsiveStyles: true },
  markdown: {
    processor: unified({
      gfm: true,
      smartypants: false, // el text ja porta la tipografia de l'original; no tocar-la
      rehypePlugins: [rehypeBook],
      remarkRehype: {
        footnoteLabel: 'Notes',
        footnoteLabelProperties: { className: ['notes-titol'] },
        footnoteBackLabel: 'Torna al text',
      },
    }),
  },
  vite: {
    // content/ i assets/ viuen a l'arrel del repositori, fora de site/
    server: { fs: { allow: ['..'] } },
  },
});

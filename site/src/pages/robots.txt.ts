import type { APIRoute } from 'astro';

// robots.txt amb l'adreça del sitemap, calculada a partir de `site` i `base` (T-10)
export const GET: APIRoute = ({ site }) => {
  const sitemap = site ? new URL(`${import.meta.env.BASE_URL}sitemap-index.xml`.replace(/\/{2,}/g, '/'), site).href : '/sitemap-index.xml';
  return new Response(`User-agent: *\nAllow: /\n\nSitemap: ${sitemap}\n`, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};

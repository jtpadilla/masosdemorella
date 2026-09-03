import type { APIRoute, GetStaticPaths } from 'astro';

// Servix els SVG d'esta edició (assets/images/*.svg) a /imatges/<fitxer>, sense hash, per a poder-los obrir a mida
// completa des de les figures del text (enllaç que afig rehype-book.mjs).
const svgs = import.meta.glob<string>('../../../../assets/images/*.svg', { eager: true, query: '?raw', import: 'default' });

export const getStaticPaths: GetStaticPaths = () =>
  Object.keys(svgs).map((p) => ({ params: { file: p.split('/').pop()! }, props: { svg: svgs[p] } }));

export const GET: APIRoute = ({ props }) =>
  new Response(props.svg, { headers: { 'Content-Type': 'image/svg+xml; charset=utf-8' } });

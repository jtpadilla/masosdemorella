import { defineCollection, z } from 'astro:content';
import { file, glob } from 'astro/loaders';

// Els masters recuperats viuen a ../content (arrel del repositori), fora del projecte Astro.
export const collections = {
  // Un fitxer Markdown per capítol
  llibre: defineCollection({
    loader: glob({ pattern: '*.md', base: '../content' }),
    schema: z.object({
      title: z.string(),
      order: z.number(),
      pages: z.tuple([z.number(), z.number()]), // primera i última pàgina de l'original
    }),
  }),
  // Metadades de portada (entrada única "llibre")
  meta: defineCollection({
    loader: file('../content/llibre.yaml'),
    schema: z.object({
      titol: z.string(),
      subtitol: z.string(),
      autora: z.string(),
      titol_capcalera: z.string(),
      llengua: z.string(),
      data_pdf: z.coerce.date(),
      context: z.string(),
      portada_imatge: z.string(),
    }),
  }),
};

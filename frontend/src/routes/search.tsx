import { createFileRoute } from '@tanstack/react-router';
import z from 'zod';
import SearchPage from '#/pages/search-page';

const searchSchema = z.object({
  query: z.string().catch(''),
});

export const Route = createFileRoute('/search')({
  component: SearchPage,
  validateSearch: searchSchema,
});

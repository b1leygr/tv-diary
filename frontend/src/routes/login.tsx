import { createFileRoute, redirect } from '@tanstack/react-router';
import { z } from 'zod';
import LoginPage from '@/pages/login-page';

const searchSchema = z.object({
  redirect: z.string().optional(),
});

export const Route = createFileRoute('/login')({
  validateSearch: (search): { redirect?: string } => searchSchema.parse(search),
  beforeLoad: async ({ context }) => {
    if (context.auth.authenticated) {
      throw redirect({ to: '/search', search: { query: '' }, replace: true });
    }
  },
  component: LoginPage,
});

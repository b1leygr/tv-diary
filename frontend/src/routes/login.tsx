import { createFileRoute, redirect } from '@tanstack/react-router';
import LoginPage from '@/pages/login-page';

export const Route = createFileRoute('/login')({
  component: LoginPage,
  beforeLoad: async ({ context }) => {
    if (context.auth.authenticated) {
      throw redirect({ to: '/search', search: { query: '' }, replace: true });
    }
  },
});

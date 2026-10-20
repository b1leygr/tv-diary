import { createFileRoute, redirect } from '@tanstack/react-router';
import { getActivityOptions } from '#/client/@tanstack/react-query.gen';
import ActivityPage from '#/pages/activity-page';

export const Route = createFileRoute('/activity')({
  beforeLoad: async ({ context }) => {
    if (!context.auth.authenticated) {
      throw redirect({
        to: '/login',
        search: { redirect: location.pathname + location.search },
      });
    }
  },
  loader: async ({ context: { queryClient } }) => {
    return await queryClient.query({
      ...getActivityOptions({ query: { view: 'episodes' } }),
      staleTime: 'static',
    });
  },
  component: ActivityPage,
});

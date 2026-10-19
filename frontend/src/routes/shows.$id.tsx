import { createFileRoute, redirect } from '@tanstack/react-router';
import { getShowOptions } from '#/client/@tanstack/react-query.gen';
import ShowPage from '#/pages/show-page';

export const Route = createFileRoute('/shows/$id')({
  beforeLoad: async ({ context }) => {
    if (!context.auth.authenticated) {
      throw redirect({
        to: '/login',
        search: { redirect: location.pathname + location.search },
      });
    }
  },
  loader: async ({ context: { queryClient }, params }) => {
    return await queryClient.query({
      ...getShowOptions({ path: { show_id: Number(params.id) } }),
      staleTime: 'static',
    });
  },
  component: ShowPage,
});

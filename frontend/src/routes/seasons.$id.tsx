import { createFileRoute, redirect } from '@tanstack/react-router';
import { getSeasonOptions } from '#/client/@tanstack/react-query.gen';
import SeasonPage from '#/pages/season-page';

export const Route = createFileRoute('/seasons/$id')({
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
      ...getSeasonOptions({
        path: { season_id: Number(params.id) },
        query: { view: 'full' },
      }),
      staleTime: 'static',
    });
  },
  component: SeasonPage,
});

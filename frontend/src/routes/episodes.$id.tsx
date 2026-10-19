import { createFileRoute, redirect } from '@tanstack/react-router';
import { getEpisodeOptions } from '#/client/@tanstack/react-query.gen';
import EpisodePage from '@/pages/episode-page';

export const Route = createFileRoute('/episodes/$id')({
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
      ...getEpisodeOptions({ path: { episode_id: Number(params.id) } }),
      staleTime: 'static',
    });
  },
  component: EpisodePage,
});

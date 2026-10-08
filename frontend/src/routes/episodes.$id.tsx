import { createFileRoute } from '@tanstack/react-router';
import { getEpisodeOptions } from '#/client/@tanstack/react-query.gen';
import EpisodePage from '@/pages/episode-page';

export const Route = createFileRoute('/episodes/$id')({
  loader: async ({ context: { queryClient }, params }) => {
    return await queryClient.query({
      ...getEpisodeOptions({ path: { episode_id: Number(params.id) } }),
      staleTime: 'static',
    });
  },
  component: EpisodePage,
});

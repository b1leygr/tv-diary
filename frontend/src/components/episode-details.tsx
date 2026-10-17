import { Stack } from '@mantine/core';
import { useMutation, useSuspenseQuery } from '@tanstack/react-query';
import { useParams, useRouteContext } from '@tanstack/react-router';
import { CalendarDays, Clock3 } from 'lucide-react';
import toast from 'react-hot-toast';
import {
  getEpisodeOptions,
  getEpisodeQueryKey,
  getSeasonQueryKey,
  getShowQueryKey,
  logEpisodeMutation,
} from '#/client/@tanstack/react-query.gen';
import { Banner } from './banner';
import { CreativeCard, CreativeScroller } from './creative-card';
import { MediaCard } from './media-card';

export function EpisodeDetails() {
  const { id } = useParams({ from: '/episodes/$id' });
  const { queryClient } = useRouteContext({ from: '/episodes/$id' });

  const {
    data: episodeData,
    isLoading: isEpisodeLoading,
    error: episodeError,
  } = useSuspenseQuery(getEpisodeOptions({ path: { episode_id: Number(id) } }));

  const logMutation = useMutation({
    ...logEpisodeMutation(),
    onSuccess: (log_data) => {
      log_data.logged_at &&
        toast.success(
          `${log_data.episode_name} logged at ${new Date(log_data.logged_at).toLocaleString()}`,
        );
      queryClient.invalidateQueries({
        queryKey: getEpisodeQueryKey({ path: { episode_id: Number(id) } }),
      });
      queryClient.invalidateQueries({
        queryKey: getSeasonQueryKey({
          path: { season_id: Number(episodeData.season_id) },
        }),
      });
      queryClient.invalidateQueries({
        queryKey: getShowQueryKey({
          path: { show_id: Number(episodeData.show_id) },
        }),
      });
      console.log(`${log_data.episode_name} logged at ${log_data.logged_at}`);
    },
    onError: (error) => {
      console.error('Logging episode failed:', error);
    },
  });

  const handleClick = () => {
    logMutation.mutate({ path: { episode_id: Number(id) } });
  };

  if (isEpisodeLoading) return <div>Loading...</div>;
  if (episodeError) return <div>Error loading episode details.</div>;

  const guestStars = episodeData.guest_stars.map((item) => (
    <CreativeCard
      key={item.id}
      name={item.name}
      character={item.character}
      profilePath={item.profile_path}
    />
  ));

  return (
    <Stack w="100%">
      {episodeData.still_path && (
        <Banner backdropPath={episodeData.still_path} />
      )}

      <MediaCard
        title={episodeData.name}
        posterPath={episodeData.season_poster_path}
        backRefs={[
          {
            label: episodeData.show_name,
            path: `/shows/${episodeData.show_id}`,
          },
          {
            label: episodeData.season_name,
            path: `/seasons/${episodeData.season_id}`,
          },
        ]}
        descriptors={
          <>
            <CalendarDays key="calendar" className="size-4" />
            {episodeData.air_date}
            <Clock3 key="clock" className="size-4" />
            {episodeData.runtime}
          </>
        }
        overview={episodeData.overview}
        button={{
          logged: episodeData.is_logged,
          onClick: handleClick,
        }}
      />

      <CreativeScroller type="Guest Stars" creatives={guestStars} />
    </Stack>
  );
}

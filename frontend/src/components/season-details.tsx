import { Anchor, Card, Group, Stack, Title } from '@mantine/core';
import { useSuspenseQuery } from '@tanstack/react-query';
import { Link, useParams } from '@tanstack/react-router';
import { CalendarDays, Check, Clock3 } from 'lucide-react';
import { getSeasonOptions } from '#/client/@tanstack/react-query.gen';
import { Banner } from './banner';
import { CreativeCard, CreativeScroller } from './creative-card';
import { MediaCard } from './media-card';

export function SeasonDetails() {
  const { id } = useParams({ from: '/seasons/$id' });
  const { data: seasonData } = useSuspenseQuery({
    ...getSeasonOptions({
      path: { season_id: Number(id) },
      query: { view: 'full' },
    }),
    select: (data) => {
      if (Array.isArray(data)) {
        throw new Error('Expected a single object but received an array.');
      }
      return data;
    },
  });

  const cast = seasonData.cast.map((item) => (
    <CreativeCard
      key={item.id}
      name={item.name}
      character={item.character}
      profilePath={item.profile_path}
    />
  ));

  const episodes = seasonData.episodes_with_progress.map((item) => (
    <Card withBorder key={item.id}>
      <Group>
        <Anchor component={Link} to={`/episodes/${item.id}`}>
          {item.name}
        </Anchor>
        {item.is_logged ? (
          <Check className="size-4" />
        ) : (
          <Clock3 className="size-4" />
        )}
      </Group>
    </Card>
  ));

  return (
    <Stack w={'100%'}>
      {seasonData.show_backdrop_path && (
        <Banner backdropPath={seasonData.show_backdrop_path} />
      )}

      <MediaCard
        title={seasonData.name}
        posterPath={seasonData.poster_path}
        backRefs={[
          {
            label: seasonData.show_name,
            path: `/shows/${seasonData.show_id}`,
          },
        ]}
        descriptors={
          <>
            <CalendarDays className="size-4" />
            {seasonData.air_date}
          </>
        }
        overview={seasonData.overview}
      />

      <CreativeScroller type="Cast" creatives={cast} />

      <Card padding="md" radius="md" withBorder>
        <Title order={3} py="md">
          Episodes
        </Title>
        <Stack>{episodes}</Stack>
      </Card>
    </Stack>
  );
}

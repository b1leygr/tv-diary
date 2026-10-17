import { Anchor, Card, Stack, Text, Title } from '@mantine/core';
import { useSuspenseQuery } from '@tanstack/react-query';
import { Link, useParams } from '@tanstack/react-router';
import { CalendarDays, Tags } from 'lucide-react';
import { getShowOptions } from '#/client/@tanstack/react-query.gen';
import { Banner } from './banner';
import { CreativeCard, CreativeScroller } from './creative-card';
import { MediaCard } from './media-card';

export function ShowDetails() {
  const { id } = useParams({ from: '/shows/$id' });
  const {
    data: showData,
    isLoading: isShowLoading,
    error: showError,
  } = useSuspenseQuery(getShowOptions({ path: { show_id: Number(id) } }));

  if (isShowLoading) return <div>Loading...</div>;
  if (showError) return <div>Error loading show details.</div>;

  const creators = showData.creators.map((item) => (
    <CreativeCard
      key={item.id}
      name={item.name}
      profilePath={item.profile_path}
    />
  ));

  const seasons = (showData.seasons_with_progress ?? []).map((item) => (
    <Card withBorder key={item.id}>
      <Stack>
        <Anchor component={Link} to={`/seasons/${item.id}`} size="xl">
          {' '}
          {item.name}
        </Anchor>
        <Text size="md">
          {item.logged_eps} / {item.total_eps} episodes watched
        </Text>
      </Stack>
    </Card>
  ));

  return (
    <Stack w={'100%'}>
      {showData.backdrop_path && (
        <Banner backdropPath={showData.backdrop_path} />
      )}

      <MediaCard
        title={showData.name}
        posterPath={showData.poster_path}
        descriptors={
          <>
            <CalendarDays className="size-4" />
            {showData.status === 'Returning Series'
              ? 'Ongoing'
              : `${showData.first_air_date} — ${showData.last_air_date}`}
            <Tags className="size-4" />
            {showData.genres.join(', ')}
          </>
        }
        overview={showData.overview}
      />

      <CreativeScroller type="Creators" creatives={creators} />

      <Card padding="md" radius="md" withBorder>
        <Title order={3} py="md">
          Seasons
        </Title>
        <Stack>{seasons}</Stack>
      </Card>
    </Stack>
  );
}

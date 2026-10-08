import {
  Anchor,
  AspectRatio,
  Box,
  Card,
  Divider,
  Group,
  Image,
  Stack,
  Text,
  Title,
} from '@mantine/core';
import { useSuspenseQuery } from '@tanstack/react-query';
import { Link, useParams } from '@tanstack/react-router';
import { CalendarDays, Check, Clock3 } from 'lucide-react';
import { getSeasonOptions } from '#/client/@tanstack/react-query.gen';

export function SeasonDetails() {
  const { id } = useParams({ from: '/seasons/$id' });
  const { data } = useSuspenseQuery({
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

  const cards = data.cast.map((item) => (
    <Card
      key={item.id}
      shadow="sm"
      radius="md"
      withBorder
      w={160}
      style={{ flexShrink: 0 }}
    >
      <Card.Section>
        <AspectRatio ratio={2 / 3}>
          <Image
            src={`https://image.tmdb.org/t/p/original/${item.profile_path}`}
          />
        </AspectRatio>
      </Card.Section>
      <Text fw={460} size="lg" mt="md">
        {item.character}
      </Text>
      <Text size="sm" c="dimmed" mt="xs" mb="md">
        {item.name}
      </Text>
    </Card>
  ));

  const episodes = data.episodes_with_progress.map((item) => (
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
    <Card withBorder padding={'md'} radius={'md'} w={1200}>
      <Stack>
        <Group wrap="nowrap" align="flex-start">
          <Box pos={'relative'}>
            <AspectRatio ratio={2 / 3}>
              <Image
                src={`https://image.tmdb.org/t/p/original/${data.poster_path}`}
                maw={300}
              ></Image>
            </AspectRatio>
          </Box>
          <Stack gap={'s'} mih={450} maw={850}>
            <Anchor component={Link} to={`/shows/${data.show_id}`} c={'dimmed'}>
              {data.show_name}
            </Anchor>
            <Title order={1} mt={'-sm'}>
              {data.name}
            </Title>
            <Group gap={'xs'} c={'dimmed'}>
              <CalendarDays className="size-4" />
              {data?.air_date}
            </Group>
            <Divider miw={850} />
            <Title order={3}>Overview</Title>
            <Text size="xl">
              {data.overview ? data.overview : 'No overview available...'}
            </Text>
          </Stack>
        </Group>
        <Title order={3} p={'md'}>
          Cast
        </Title>
        <Group
          wrap={'nowrap'}
          p={'md'}
          style={{ overflowX: 'auto' }}
          align="stretch"
        >
          {cards}
        </Group>
        <Title order={3} p={'md'}>
          Episodes
        </Title>
        <Stack>{episodes}</Stack>
      </Stack>
    </Card>
  );
}

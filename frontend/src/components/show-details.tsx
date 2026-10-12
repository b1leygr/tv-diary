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
import { CalendarDays, Tags } from 'lucide-react';
import { getShowOptions } from '#/client/@tanstack/react-query.gen';

export function ShowDetails() {
  const { id } = useParams({ from: '/shows/$id' });
  const { data } = useSuspenseQuery(
    getShowOptions({ path: { show_id: Number(id) } }),
  );
  const cards = data.creators.map((item) => (
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
      <Text size="sm" c="dimmed" mt="xs" mb="md">
        {item.name}
      </Text>
    </Card>
  ));

  const seasons = (data.seasons_with_progress ?? []).map((item) => (
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
            <Title order={1} mt={'-sm'} style={{ fontSize: 50 }}>
              {data.name}
            </Title>
            <Group gap={'xs'} c={'dimmed'}>
              <CalendarDays className="size-4" />
              {data.status === 'Returning Series'
                ? 'Ongoing'
                : `${data?.first_air_date} — ${data?.last_air_date}`}
              <Tags className="size-4" />
              {data.genres.join(', ')}
            </Group>
            <Divider miw={850} />
            <Title order={3}>Overview</Title>
            <Text size="xl">
              {data.overview ? data.overview : 'No overview available...'}
            </Text>
          </Stack>
        </Group>
        <Title order={3} p={'md'} ml={'-md'}>
          Creators
        </Title>
        <Group
          wrap={'nowrap'}
          p={'md'}
          style={{ overflowX: 'auto' }}
          align="stretch"
        >
          {cards}
        </Group>
        <Stack>{seasons}</Stack>
      </Stack>
    </Card>
  );
}

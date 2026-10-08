import {
  Anchor,
  AspectRatio,
  Box,
  Button,
  Card,
  Divider,
  Flex,
  Group,
  Image,
  Stack,
  Text,
  Title,
} from '@mantine/core';
import { useMutation, useSuspenseQuery } from '@tanstack/react-query';
import { Link, useParams, useRouteContext } from '@tanstack/react-router';
import { CalendarDays, Check, Clock3, Film, Play } from 'lucide-react';
import toast from 'react-hot-toast';
import {
  getEpisodeOptions,
  getEpisodeQueryKey,
  logEpisodeMutation,
} from '#/client/@tanstack/react-query.gen';

export function EpisodeDetails() {
  const { id } = useParams({ from: '/episodes/$id' });
  const { queryClient } = useRouteContext({ from: '/episodes/$id' });

  const { data, isLoading, error } = useSuspenseQuery(
    getEpisodeOptions({ path: { episode_id: Number(id) } }),
  );

  const logMutation = useMutation({
    ...logEpisodeMutation(),
    onSuccess: (data) => {
      data.logged_at &&
        toast.success(
          `${data.episode_name} logged at ${new Date(data.logged_at).toLocaleString()}`,
        );
      queryClient.invalidateQueries({
        queryKey: getEpisodeQueryKey({ path: { episode_id: Number(id) } }),
      });
      console.log(`${data.episode_name} logged at ${data.logged_at}`);
    },
    onError: (error) => {
      console.error('Logging episode failed:', error);
    },
  });

  const handleClick = () => {
    logMutation.mutate({ path: { episode_id: Number(id) } });
  };

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading episode details...</div>;

  const cards = data.guest_stars.map((item) => (
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

  return (
    <Card withBorder padding={'md'} radius={'md'} w={1200}>
      <Stack>
        <Group wrap="nowrap" align="flex-start">
          <Box pos={'relative'}>
            <AspectRatio ratio={2 / 3}>
              <Image
                src={`https://image.tmdb.org/t/p/original/${data.still_path}`}
                maw={300}
              ></Image>
            </AspectRatio>
            <Flex
              align="center"
              gap={'xs'}
              style={{
                position: 'absolute',
                bottom: 16,
                left: 16,
                color: 'white',
              }}
            >
              <Film className="size-4" />
              <Text>Episode {`${data?.episode_number}`}</Text>
            </Flex>
          </Box>
          <Stack gap={'s'} mih={450} maw={850}>
            <Text c={'dimmed'}>
              <Anchor
                component={Link}
                to={`/shows/${data.show_id}`}
                c={'dimmed'}
                inline
              >
                {data.show_name}
              </Anchor>{' '}
              /
              <Anchor
                component={Link}
                to={`/seasons/${data.season_id}`}
                c={'dimmed'}
                inline
              >
                {' '}
                {data.season_name}
              </Anchor>
            </Text>
            <Title order={1} mt={'-sm'}>
              {data.name}
            </Title>
            <Group gap={'xs'} c={'dimmed'}>
              <CalendarDays className="size-4" />
              {data?.air_date}
              <Clock3 className="size-4" />
              {data?.runtime}
            </Group>
            <Divider />
            <Title order={3}>Overview</Title>
            <Text size="xl">{data.overview}</Text>
            <Button
              mt={'auto'}
              fullWidth
              aria-pressed={data.is_logged}
              onClick={handleClick}
            >
              {data?.is_logged ? (
                <Check data-icon="inline-start" />
              ) : (
                <Play data-icon="inline-start" />
              )}
              {data?.is_logged ? 'Watched' : 'Mark as watched'}
            </Button>
          </Stack>
        </Group>
        <Title order={3} p={'md'} ml={'-md'}>
          Guest Stars
        </Title>
        <Group
          wrap={'nowrap'}
          p={'md'}
          style={{ overflowX: 'auto' }}
          align="stretch"
        >
          {cards}
        </Group>
      </Stack>
    </Card>
  );
}

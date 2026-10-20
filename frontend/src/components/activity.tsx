import { Card, Grid, Image, Stack, Text, Title } from '@mantine/core';
import { useSuspenseQuery } from '@tanstack/react-query';
import { Link } from '@tanstack/react-router';
import { getActivityOptions } from '#/client/@tanstack/react-query.gen';

export function Activity() {
  const { data: logsData } = useSuspenseQuery(getActivityOptions({}));

  return (
    <Stack w={'100%'}>
      <Title order={2}>Your Activity</Title>
      <Text size="sm" fw="bolder" c="dimmed">
        A list of your recent viewing activity.
      </Text>
      {logsData.map((log, index) => (
        <Card
          withBorder
          key={index}
          component={Link}
          to={`/episodes/${log.episode_id}`}
        >
          <Grid align="center">
            <Grid.Col span={{ base: 3, sm: 1 }}>
              <Image
                src={`https://image.tmdb.org/t/p/original/${log.show_poster_path}`}
                w="100%"
                h="auto"
              ></Image>
            </Grid.Col>
            <Grid.Col span={{ base: 9, sm: 11 }}>
              <Text py="xs">{log.show_name}</Text>
              <Text pb="xs">
                {log.season_name} - {log.episode_name}
              </Text>
              <Text py="xs">{new Date(log.logged_at).toLocaleString()}</Text>
            </Grid.Col>
          </Grid>
        </Card>
      ))}
    </Stack>
  );
}

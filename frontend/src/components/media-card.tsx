import {
  Anchor,
  AspectRatio,
  Breadcrumbs,
  Button,
  Card,
  type CardProps,
  Divider,
  Grid,
  Group,
  Image,
  Stack,
  Text,
  Title,
} from '@mantine/core';
import { Link } from '@tanstack/react-router';
import { Check, Play } from 'lucide-react';

interface MediaCardProps extends CardProps {
  title: string;
  posterPath: string | null;
  backRefs?: backRef[];
  descriptors: React.ReactNode;
  overview: string | null;
  button?: logButton;
}

interface backRef {
  label: string;
  path: string;
}

interface logButton {
  logged: boolean;
  onClick: () => void;
}

export function MediaCard({
  title,
  posterPath,
  backRefs,
  descriptors,
  overview,
  button,
  ...props
}: MediaCardProps) {
  return (
    <Card padding="md" radius="md" mt="-xl" withBorder {...props}>
      <Grid align="stretch">
        <Grid.Col span={{ base: 12, sm: 4 }}>
          <AspectRatio ratio={2 / 3} w="100%" h="auto">
            <Image
              src={`https://image.tmdb.org/t/p/original/${posterPath}`}
            ></Image>
          </AspectRatio>
        </Grid.Col>
        <Grid.Col span={{ base: 12, sm: 8 }}>
          <Stack p="sm" h="100%">
            <Stack gap="sm" style={{ flex: 1 }}>
              {backRefs && backRefs.length > 0 && (
                <Breadcrumbs>
                  {backRefs.map((ref) => (
                    <Anchor
                      key={ref.path}
                      component={Link}
                      to={`${ref.path}`}
                      c="dimmed"
                      inline
                    >
                      {ref.label}
                    </Anchor>
                  ))}
                </Breadcrumbs>
              )}
              <Title order={1}>{title}</Title>
              <Group gap="sm" c="dimmed">
                {descriptors}
              </Group>
              <Divider />
              <Title order={3}>Overview</Title>
              <Text size="xl">{overview || 'No overview available...'}</Text>
            </Stack>
            {button && (
              <Button
                fullWidth
                style={{ alignSelf: 'flex-start' }}
                onClick={button.onClick}
              >
                {button.logged ? (
                  <Check data-icon="inline-start" />
                ) : (
                  <Play data-icon="inline-start" />
                )}
                {button.logged ? 'Watched' : 'Mark as watched'}
              </Button>
            )}
          </Stack>
        </Grid.Col>
      </Grid>
    </Card>
  );
}

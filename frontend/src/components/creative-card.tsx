import {
  AspectRatio,
  Card,
  type CardProps,
  Group,
  Image,
  Scroller,
  Text,
  Title,
} from '@mantine/core';

interface CreativeCardProps extends CardProps {
  name: string;
  character?: string | null;
  profilePath: string | null;
}

interface CreativeScrollerProps {
  type: 'Creators' | 'Cast' | 'Guest Stars';
  creatives: React.ReactNode;
}

export function CreativeCard({
  name,
  character,
  profilePath,
  ...props
}: CreativeCardProps) {
  return (
    <Card
      shadow="sm"
      radius="md"
      withBorder
      w={160}
      style={{ flexShrink: 0 }}
      {...props}
    >
      <Card.Section>
        <AspectRatio ratio={2 / 3}>
          <Image src={`https://image.tmdb.org/t/p/original/${profilePath}`} />
        </AspectRatio>
      </Card.Section>
      {character && (
        <Text fw={460} size="lg" mt="md">
          {character}
        </Text>
      )}
      <Text size="sm" c="dimmed" mt="xs" mb="md">
        {name}
      </Text>
    </Card>
  );
}

export function CreativeScroller({ type, creatives }: CreativeScrollerProps) {
  return (
    <Card padding="md" radius="md" withBorder>
      <Title order={3} py="md">
        {type}
      </Title>
      <Scroller>
        <Group wrap="nowrap" align="stretch">
          {creatives}
        </Group>
      </Scroller>
    </Card>
  );
}

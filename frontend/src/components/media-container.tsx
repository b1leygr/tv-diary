import { Container, type ContainerProps } from '@mantine/core';

interface MediaContainerProps extends ContainerProps {
  mediaContent: React.ReactNode;
}

export function MediaContainer({
  mediaContent,
  ...props
}: MediaContainerProps) {
  return (
    <Container size="xl" w="100%" p="md" {...props}>
      {mediaContent}
    </Container>
  );
}

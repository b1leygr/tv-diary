import { Button, Container, Stack, Text, Title } from '@mantine/core';
import { type ErrorComponentProps, useRouter } from '@tanstack/react-router';
import { useState } from 'react';

export function ErrorComponent({ error, reset }: ErrorComponentProps) {
  const router = useRouter();
  const [isRetrying, setIsRetrying] = useState(false);

  const handleRetry = async () => {
    setIsRetrying(true);
    try {
      await router.invalidate();
      reset();
    } catch (error) {
      console.error('Error occurred while retrying:', error);
    } finally {
      setIsRetrying(false);
    }
  };

  return (
    <Container size="xl" w="100%" p="md">
      <Stack w="100%">
        <Title order={2}>Something went wrong.</Title>
        <Text size="lg" c="dimmed">
          {error instanceof Error ? error.message : String(error)}
        </Text>
        <Button loading={isRetrying} onClick={handleRetry} w="fit-content">
          Retry
        </Button>
      </Stack>
    </Container>
  );
}

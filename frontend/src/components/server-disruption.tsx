import { Button, Stack, Text, Title } from '@mantine/core';
import { useRouter } from '@tanstack/react-router';
import { useState } from 'react';
import { toast } from 'react-hot-toast';
import { queryClient } from '@/router';

export function ServerDisruption() {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(false);

  const handleRetry = async () => {
    setIsChecking(true);

    try {
      queryClient.clear();

      const response = await fetch(`${import.meta.env.VITE_API_URL}/`, {
        method: 'GET',
        cache: 'no-store',
      });

      if (response.ok) {
        router.navigate({ to: '/' });
      } else {
        console.warn('Server responded, but health check failed.');
        toast.error('Server is still unreachable. Please try again later.');
      }
    } catch (error) {
      console.error('Server is still unreachable:', error);
      toast.error('Server is still unreachable. Please try again later.');
    } finally {
      setIsChecking(false);
    }
  };

  return (
    <Stack w="100%">
      <Title order={2}>Connection lost.</Title>
      <Text size="lg" c="dimmed">
        Currently experiencing server disruptions. Please try again later.
      </Text>
      <Button loading={isChecking} onClick={handleRetry} w="fit-content">
        Retry
      </Button>
    </Stack>
  );
}

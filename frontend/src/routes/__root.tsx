import { AppShell, Box, Container, Flex, Title } from '@mantine/core';
import type { QueryClient } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import {
  createRootRouteWithContext,
  Outlet,
  useLocation,
} from '@tanstack/react-router';
import { Toaster } from 'react-hot-toast';
import type { AuthContext } from '#/auth';
import { SearchBar } from '#/components/search-bar';

interface MyRouterContext {
  queryClient: QueryClient;
  auth: AuthContext;
}

export const Route = createRootRouteWithContext<MyRouterContext>()({
  component: RootComponent,
});

function RootComponent() {
  const location = useLocation();
  const isSearchHidden = ['/login', '/signup', '/server-disruption'].includes(
    location.pathname,
  );

  return (
    <AppShell padding="md" header={{ height: { base: 100, sm: 60 } }}>
      <AppShell.Header>
        <Container size="xl" h="100%">
          <Flex
            h="100%"
            align="center"
            justify="space-between"
            direction={{ base: 'column', sm: 'row' }}
            py={{ base: 'xs', sm: 0 }}
            gap={{ base: 'xs', sm: 'md' }}
          >
            <Title order={1} size="h3">
              TV Diary
            </Title>
            {!isSearchHidden && (
              <Box w={{ base: '100%', sm: 'auto' }}>
                <SearchBar />
              </Box>
            )}
          </Flex>
        </Container>
      </AppShell.Header>
      <AppShell.Main>
        <Outlet />
      </AppShell.Main>
      <Toaster position="top-center" />
      <ReactQueryDevtools />
    </AppShell>
  );
}

import { QueryCache, QueryClient } from '@tanstack/react-query';
import { createRouter } from '@tanstack/react-router';
import type { ProblemDetails } from '#/client';
import { ErrorComponent } from '#/components/error';
import { client } from '@/client/client.gen';
import { type AuthContext, authService } from './auth';
import { routeTree } from './routeTree.gen';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      refetchOnWindowFocus: false,
      retry: (failureCount, error) => {
        if (error.status === 401) {
          console.log('Unauthorised error, not retrying.');
          return false;
        }
        console.log(`Retrying query, attempt ${failureCount}`);
        return failureCount < 2;
      },
    },
  },
  queryCache: new QueryCache({
    onError: (error) => {
      if (!error.status) {
        console.log(
          'Unable to authenticate user due to network error. Redirecting to server disruption page.',
        );
        router.navigate({ to: '/server-disruption' });
      }
    },
  }),
});

export const router = createRouter({
  routeTree,
  defaultPreload: 'intent',
  scrollRestoration: true,
  context: {
    queryClient: queryClient,
    auth: undefined as unknown as AuthContext,
  },
  defaultErrorComponent: ErrorComponent,
});

client.setConfig({
  baseUrl: import.meta.env.VITE_API_URL,
  auth: () => authService.token || '',
});

client.interceptors.response.use((response) => {
  if (response.status === 401) {
    console.log('Unauthorised error, redirecting to login page.');
    authService.logout();
    queryClient.clear();
    router.invalidate();
    router.navigate({ to: '/login' });
  }
  return response;
});

client.interceptors.error.use((error) => {
  return Promise.reject(error);
});

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

declare module '@tanstack/react-query' {
  interface Register {
    defaultError: ProblemDetails;
  }
}

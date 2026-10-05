import { QueryClient } from '@tanstack/react-query';
import { createRouter } from '@tanstack/react-router';
import { client } from '@/client/client.gen';
import { routeTree } from './routeTree.gen';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      				staleTime: 1000 * 60 * 5,
				refetchOnWindowFocus: false,
				retry: 1,
			},
		},
});

export const router = createRouter({
  routeTree,
  defaultPreload: 'intent',
  scrollRestoration: true,
  context: {
		queryClient: queryClient,
  },
});

client.setConfig({
	baseUrl: import.meta.env.VITE_API_URL,
  throwOnError: true,
  auth: () => {
    const token = localStorage.getItem('token');
    return token ?? ''; 
  },
});


declare module '@tanstack/react-router' {
	interface Register {
		router: typeof router;
	}
}

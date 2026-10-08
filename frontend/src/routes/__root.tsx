import { type QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { createRootRouteWithContext, Outlet } from '@tanstack/react-router';
import { Toaster } from 'react-hot-toast';
import { SearchBar } from '#/components/search-bar';

interface MyRouterContext {
  queryClient: QueryClient;
}

export const Route = createRootRouteWithContext<MyRouterContext>()({
  component: RootComponent,
});

function RootComponent() {
  const { queryClient } = Route.useRouteContext();

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-background font-sans antialiased">
        <header className="border-b border-border bg-background/50 backdrop-blur">
          <div className="container mx-auto flex max-w-7xl items-center justify-between p-6">
            <h1 className="text-2xl font-bold">TV Diary</h1>
            <SearchBar />
          </div>
        </header>
        <div className="h-4" />
        <main className="container mx-auto max-w-7xl p-6">
          <Toaster position="top-center" />
          <Outlet />
        </main>
        <ReactQueryDevtools />
      </div>
    </QueryClientProvider>
  );
}

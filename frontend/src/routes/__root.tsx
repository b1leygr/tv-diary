import { type QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { createRootRouteWithContext, Outlet } from '@tanstack/react-router';
import { Toaster } from 'react-hot-toast';

interface MyRouterContext {
  queryClient: QueryClient;
}

export const Route = createRootRouteWithContext<MyRouterContext>()({
  component: RootComponent,
});

function RootComponent() {
  return (
    <QueryClientProvider client={Route.useRouteContext().queryClient}>
      <div className="min-h-screen bg-background font-sans antialiased">
        <main className="container mx-auto max-w-7xl p-6">
          <Toaster position="top-center" />
          <Outlet />
        </main>
        <ReactQueryDevtools />
      </div>
    </QueryClientProvider>
  );
}

import {
	type QueryClient,
	QueryClientProvider,
} from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { createRootRouteWithContext, Outlet } from '@tanstack/react-router';

interface MyRouterContext {
	queryClient: QueryClient;
}

export const Route = createRootRouteWithContext<MyRouterContext>()({
	component: RootComponent,
});

function RootComponent() {
	return (
		<QueryClientProvider client={Route.useRouteContext().queryClient}>
			<div className='min-h-screen bg-background font-sans antialiased'>
				<main className='container mx-auto max-w-7xl p-6'>
					<Outlet />
				</main>
				<ReactQueryDevtools />
			</div>
		</QueryClientProvider>
	);
}

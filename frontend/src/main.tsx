import '@mantine/core/styles.css';
import { MantineProvider } from '@mantine/core';
import { QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider } from '@tanstack/react-router';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { AuthProvider, useAuth } from './auth';
import { queryClient, router } from './router';
import './styles.css';

const rootElement = document.getElementById('app');

if (!rootElement) {
  throw new Error('Failed to find the root element with id "app".');
}

function InnerApp() {
  const auth = useAuth();

  return <RouterProvider router={router} context={{ auth }} />;
}

createRoot(rootElement).render(
  <StrictMode>
    <MantineProvider>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <InnerApp />
        </AuthProvider>
      </QueryClientProvider>
    </MantineProvider>
  </StrictMode>,
);

import { createFileRoute } from '@tanstack/react-router';
import ServerDisruptionPage from '#/pages/server-disruption-page';

export const Route = createFileRoute('/server-disruption')({
  component: ServerDisruptionPage,
});

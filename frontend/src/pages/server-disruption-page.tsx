import { MediaContainer } from '#/components/media-container';
import { ServerDisruption } from '#/components/server-disruption';

export default function ServerDisruptionPage() {
  return <MediaContainer mediaContent={<ServerDisruption />} />;
}

import { EpisodeDetails } from '#/components/episode-details';
import { MediaContainer } from '#/components/media-container';

export default function EpisodePage() {
  return <MediaContainer mediaContent={<EpisodeDetails />} />;
}

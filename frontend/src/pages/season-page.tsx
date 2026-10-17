import { MediaContainer } from '#/components/media-container';
import { SeasonDetails } from '#/components/season-details';

export default function SeasonPage() {
  return <MediaContainer mediaContent={<SeasonDetails />} />;
}

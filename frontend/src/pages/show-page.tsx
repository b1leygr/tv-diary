import { MediaContainer } from '#/components/media-container';
import { ShowDetails } from '#/components/show-details';

export default function ShowPage() {
  return <MediaContainer mediaContent={<ShowDetails />} />;
}

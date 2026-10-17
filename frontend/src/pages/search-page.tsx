import { MediaContainer } from '#/components/media-container';
import { SearchResults } from '#/components/search-results';

export default function SearchPage() {
  return <MediaContainer mediaContent={<SearchResults />} />;
}

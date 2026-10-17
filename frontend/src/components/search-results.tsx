import { Card, Image, SimpleGrid, Stack, Text, Tooltip } from '@mantine/core';
import { useQuery } from '@tanstack/react-query';
import { getRouteApi, Link } from '@tanstack/react-router';
import { searchShowsOptions } from '#/client/@tanstack/react-query.gen';

export function SearchResults() {
  const routeApi = getRouteApi('/search');
  const { query } = routeApi.useSearch();

  const {
    data: searchData,
    isLoading: isSearchLoading,
    error: searchError,
  } = useQuery({
    ...searchShowsOptions({ query: { name: query } }),
    enabled: query.trim().length > 0,
  });

  if (!query || query.trim().length === 0) {
    return <div>Please search for a show.</div>;
  }
  if (isSearchLoading) return <div>Loading...</div>;
  if (searchError) return <div>Error loading search results.</div>;

  return (
    <Stack>
      <Text fw="bolder" size="lg">
        Search Results: "{query}"
      </Text>
      <Card withBorder padding="md" radius="md">
        <SimpleGrid cols={4} spacing="md">
          {searchData?.map((result) => (
            <Link
              key={result.id}
              to="/shows/$id"
              params={{ id: String(result.id) }}
              preload={false}
            >
              <Tooltip label={`${result.name} (${result.year})`}>
                <Image
                  src={`https://image.tmdb.org/t/p/original/${result.poster_path}`}
                  alt={result.name}
                  id={`show-${result.id}`}
                />
              </Tooltip>
            </Link>
          ))}
        </SimpleGrid>
      </Card>
    </Stack>
  );
}

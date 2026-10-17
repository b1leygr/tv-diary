import { AspectRatio, Box, Image } from '@mantine/core';

interface BannerProps {
  backdropPath: string;
}

export function Banner({ backdropPath }: BannerProps) {
  return (
    <AspectRatio
      ratio={16 / 5}
      style={{ position: 'relative', overflow: 'hidden', borderRadius: '8px' }}
    >
      <Image
        src={`https://image.tmdb.org/t/p/original/${backdropPath}`}
        w="100%"
        h="100%"
        style={{ objectPosition: 'top' }}
      />

      <Box
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          bottom: 0,
          height: '50%',
          background:
            'linear-gradient(to bottom, transparent, rgba(0, 0, 0, 0.5))',
          pointerEvents: 'none',
        }}
      />
    </AspectRatio>
  );
}

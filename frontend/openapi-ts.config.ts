import { defineConfig } from '@hey-api/openapi-ts';
import { loadEnv } from 'vite';

const env = loadEnv('development', process.cwd(), '');

export default defineConfig({
  plugins: [
    '@hey-api/client-fetch',
    '@hey-api/sdk',
    '@hey-api/typescript',
    '@tanstack/react-query',
  ],
  input: `${env.VITE_API_URL}/openapi.json`,
  output: 'src/client',
});

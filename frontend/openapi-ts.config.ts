import path from 'node:path';
import { defineConfig } from '@hey-api/openapi-ts';
import dotenv from 'dotenv';

dotenv.config({ path: path.resolve(import.meta.dirname, '../.env') });

export default defineConfig({
  plugins: [
    '@hey-api/client-fetch',
    '@hey-api/sdk',
    '@hey-api/typescript',
    '@tanstack/react-query',
  ],
  input: `${process.env.VITE_API_URL}/openapi.json`,
  output: 'src/client',
});

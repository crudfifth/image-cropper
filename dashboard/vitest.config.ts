import { defineConfig } from 'vitest/config';
import * as path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    typecheck: {
      tsconfig: './tests/tsconfig.json',
    },
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components-new'),
      '@icons': path.resolve(
        __dirname,
        './src/components-new/common/presenters/icons'
      ),
      '@charts': path.resolve(
        __dirname,
        './src/components-new/common/presenters/charts'
      ),
      '@buttons': path.resolve(
        __dirname,
        './src/components-new/common/presenters/buttons'
      ),
      '@inputs': path.resolve(
        __dirname,
        './src/components-new/common/presenters/inputs'
      ),
    },
  },
});

import {defineConfig} from '@shopify/hydrogen/config';

export default defineConfig({
  shopify: {
    storeDomain: process.env.SHOPIFY_STORE_DOMAIN || 'your-shop.myshopify.com',
    storefrontToken: process.env.SHOPIFY_STOREFRONT_ACCESS_TOKEN || 'your-storefront-access-token',
    storefrontApiVersion: '2024-01',
  },
  server: {
    port: parseInt(process.env.PORT || '3000'),
  },
  // Enable hot module reload in development
  ...(process.env.NODE_ENV === 'development' && {
    vite: {
      server: {
        hmr: {
          port: 3001,
        },
      },
    },
  }),
});

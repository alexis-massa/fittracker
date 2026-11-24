import { defineApp } from 'pi-ui/vite';

export default defineApp({
  name: 'FitTracker',
  description: "A personal workout tracker built around the Lafay method's timed set/rest circuits.",
  themeColor: '#5898d4',
  backgroundColor: '#17181c',
  manifest: { id: '/', orientation: 'portrait-primary' },
  icons: [
    { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
    { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
    { src: '/icons/icon-maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
  ],
});

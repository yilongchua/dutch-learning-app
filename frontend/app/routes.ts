import { type RouteConfig, index, route } from '@react-router/dev/routes';

export default [
  index('routes/home.tsx'),
  route('news', 'routes/news.tsx'),

  route('dutch/writing', 'routes/dutch.writing.tsx'),
  route('dutch/speaking', 'routes/dutch.speaking.tsx'),
  route('dutch/listening', 'routes/dutch.listening.tsx'),
  route('graphics-generation', 'routes/graphics_generation.tsx'),
] satisfies RouteConfig;

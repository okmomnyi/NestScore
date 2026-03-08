import { api } from '@/lib/api';
import HomeClient from '@/components/HomeClient';
import type { PaginatedPlots, PlotMap } from '@/types';

export default async function Home() {
  // Server-side render initial plot and map data for SEO and performance
  const initialPlots: PaginatedPlots = await api.plots.list({ page: 1 });
  const initialMapPlots: PlotMap[] = await api.plots.map();

  return <HomeClient initialPlots={initialPlots} initialMapPlots={initialMapPlots} />;
}


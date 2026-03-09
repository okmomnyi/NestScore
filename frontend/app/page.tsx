export const dynamic = "force-dynamic";
import { api } from "@/lib/api";
import HomeClient from "@/components/HomeClient";
import type { PaginatedPlots, PlotMap } from "@/types";

export default async function Home() {
  let initialPlots: PaginatedPlots = { plots: [], total_count: 0, page: 1, per_page: 20 };
  let initialMapPlots: PlotMap[] = [];

  try {
    initialPlots = await api.plots.list({ page: 1 });
  } catch (e) {
    console.error("Failed to fetch plots:", e);
  }

  try {
    initialMapPlots = await api.plots.map();
  } catch (e) {
    console.error("Failed to fetch map plots:", e);
  }

  return <HomeClient initialPlots={initialPlots} initialMapPlots={initialMapPlots} />;
}

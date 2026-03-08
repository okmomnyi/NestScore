"use client";

import { useEffect, useRef, useState } from 'react';
import { PlotMap } from '@/types';
import { DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM } from '@/lib/constants';
import { getPinColor, createCustomIcon } from './PlotPin';
import { getPopupContent } from './PinPopup';
import L from 'leaflet';
import 'leaflet.markercluster';

interface NestMapProps {
    plots: PlotMap[];
    selectedPlotId?: string | null;
    onPlotSelect?: (id: string) => void;
    className?: string;
    isInteractive?: boolean;
}

export default function NestMap({
    plots,
    selectedPlotId,
    onPlotSelect,
    className = "h-full w-full",
    isInteractive = true
}: NestMapProps) {
    const mapRef = useRef<HTMLDivElement>(null);
    const mapInstanceRef = useRef<L.Map | null>(null);
    const markersRef = useRef<{ [key: string]: L.Marker }>({});

    useEffect(() => {
        if (!mapRef.current || mapInstanceRef.current) return;

        // Initialize map
        const map = L.map(mapRef.current, {
            center: DEFAULT_MAP_CENTER,
            zoom: DEFAULT_MAP_ZOOM,
            zoomControl: isInteractive,
            scrollWheelZoom: isInteractive,
            dragging: isInteractive,
        });

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            maxZoom: 19
        }).addTo(map);

        mapInstanceRef.current = map;

        return () => {
            map.remove();
            mapInstanceRef.current = null;
        };
    }, [isInteractive]);

    useEffect(() => {
        const map = mapInstanceRef.current;
        if (!map) return;

        // Clear existing layers
        // @ts-ignore
        map.eachLayer((layer: any) => {
            if (layer instanceof L.Marker || layer.getChildCount) {
                map.removeLayer(layer);
            }
        });

        markersRef.current = {};

        // Create marker cluster group
        // @ts-ignore
        const markers = L.markerClusterGroup({
            showCoverageOnHover: false,
            maxClusterRadius: 50,
            iconCreateFunction: (cluster: any) => {
                const childMarkers = cluster.getAllChildMarkers();
                let sumScore = 0;
                let countScored = 0;

                childMarkers.forEach((m: any) => {
                    const score = (m as any).options.plotData.weighted_score;
                    if (score) {
                        sumScore += score;
                        countScored++;
                    }
                });

                const avgScore = countScored > 0 ? sumScore / countScored : null;
                const color = getPinColor(avgScore, 'active', countScored); // Rough average

                return L.divIcon({
                    html: `<div style="background-color: ${color}90; border: 2px solid ${color}; color: white; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-family: 'DM Sans', sans-serif;">${childMarkers.length}</div>`,
                    className: 'custom-cluster-icon',
                    iconSize: L.point(32, 32)
                });
            }
        });

        plots.forEach(plot => {
            if (!plot.gps_lat || !plot.gps_lng) return;

            const color = getPinColor(plot.weighted_score, plot.status, plot.total_ratings);
            const isPulsing = plot.status === 'under_review';

            const marker = L.marker([plot.gps_lat, plot.gps_lng], {
                icon: createCustomIcon(L, color, isPulsing),
                // @ts-ignore custom property for cluster calculation
                plotData: plot
            });

            marker.bindPopup(getPopupContent(plot), {
                className: 'nest-popup',
                closeButton: false,
                minWidth: 200
            });

            if (onPlotSelect) {
                marker.on('click', () => onPlotSelect(plot.id));
            }

            markersRef.current[plot.id] = marker;
            markers.addLayer(marker);
        });

        map.addLayer(markers);

        // If there's precisely one plot (detail view), zoom to it
        if (plots.length === 1 && !isInteractive) {
            map.setView([plots[0].gps_lat, plots[0].gps_lng], 16);
        }
    }, [plots, onPlotSelect, isInteractive]);

    // Handle selected plot highlight/zoom
    useEffect(() => {
        const map = mapInstanceRef.current;
        if (!map || !selectedPlotId) return;

        const marker = markersRef.current[selectedPlotId];
        if (marker) {
            map.setView(marker.getLatLng(), 16, { animate: true });
            marker.openPopup();
        }
    }, [selectedPlotId]);

    return <div ref={mapRef} className={className} style={{ zIndex: 10 }} />;
}

"use client";

import { useEffect, useRef } from "react";

export default function MapPanel({ lat, lon, radius, data, activeLayer, onMoveEnd }) {
  const containerRef = useRef(null);
  const mapRef = useRef(null);
  const layersRef = useRef([]);
  const onMoveEndRef = useRef(onMoveEnd);

  useEffect(() => {
    onMoveEndRef.current = onMoveEnd;
  }, [onMoveEnd]);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const L = require("leaflet");

    const map = L.map(containerRef.current, {
      center: [lat, lon],
      zoom: 15,
      zoomControl: true,
      preferCanvas: true,
      zoomAnimation: true,
      fadeAnimation: true,
      markerZoomAnimation: true,
      inertia: true,
      inertiaDeceleration: 2600,
      worldCopyJump: false,
    });

    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
      attribution: "© OSM © CARTO",
      maxZoom: 19,
      updateWhenIdle: true,
      keepBuffer: 4,
    }).addTo(map);

    map.createPane("analysisCircle");
    map.getPane("analysisCircle").style.zIndex = 410;
    map.createPane("heatmapPane");
    map.getPane("heatmapPane").style.zIndex = 430;
    map.createPane("roadsPane");
    map.getPane("roadsPane").style.zIndex = 440;
    map.createPane("markersPane");
    map.getPane("markersPane").style.zIndex = 460;

    map.on("moveend", () => {
      if (!onMoveEndRef.current) return;
      const center = map.getCenter();
      onMoveEndRef.current(center.lat.toFixed(4), center.lng.toFixed(4));
    });

    mapRef.current = map;
  }, []);

  useEffect(() => {
    if (mapRef.current) {
      mapRef.current.flyTo([lat, lon], mapRef.current.getZoom(), {
        animate: true,
        duration: 0.8,
      });
    }
  }, [lat, lon]);

  useEffect(() => {
    const L = require("leaflet");
    const map = mapRef.current;
    if (!map) return;

    layersRef.current.forEach((layer) => map.removeLayer(layer));
    layersRef.current = [];

    const push = (layer) => {
      layer.addTo(map);
      layersRef.current.push(layer);
    };

    push(
      L.circle([lat, lon], {
        pane: "analysisCircle",
        radius,
        color: "#0f766e",
        weight: 2,
        dashArray: "8 6",
        fillColor: "#2dd4bf",
        fillOpacity: 0.06,
      })
    );

    if (!data) return;

    const geojson = data.metrics?.geojson;
    const zoneGrid = data.zone_grid || [];
    const intersections = data.metrics?.intersections || [];
    const deadEnds = data.metrics?.dead_ends || [];

    if (activeLayer === "roads" && geojson) {
      push(
        L.geoJSON(geojson, {
          pane: "roadsPane",
          style: (feature) => ({
            color: feature.properties.color || "#0f766e",
            weight: Math.max(2, 7 - (feature.properties.level || 5)),
            opacity: 0.92,
          }),
          onEachFeature: (feature, layer) => {
            const props = feature.properties;
            layer.bindPopup(`
              <div style="font-family:Consolas,monospace;font-size:12px;line-height:1.5">
                <b style="color:${props.color}">${props.label}</b><br/>
                ${props.name ? `<span style="color:#64748b">${props.name}</span><br/>` : ""}
                <span style="color:#64748b">Length:</span> <b>${props.length_km} km</b>
              </div>
            `);
          },
        })
      );
    }

    if (activeLayer === "heatmap" && zoneGrid.length) {
      zoneGrid.forEach((cell) => {
        const n = cell.normalized || 0;
        const fillColor =
          n > 0.75 ? "#b91c1c" :
          n > 0.55 ? "#ea580c" :
          n > 0.35 ? "#f59e0b" :
          n > 0.18 ? "#84cc16" :
          "#2dd4bf";

        const rect = L.rectangle(
          [
            [cell.bounds.lat_min, cell.bounds.lon_min],
            [cell.bounds.lat_max, cell.bounds.lon_max],
          ],
          {
            pane: "heatmapPane",
            color: fillColor,
            weight: 1,
            fillColor,
            fillOpacity: 0.18 + n * 0.58,
          }
        );

        rect.bindPopup(`
          <div style="font-family:Consolas,monospace;font-size:11px;line-height:1.5">
            Cell road length: <b>${cell.length_km} km</b><br/>
            Relative density: <b>${(n * 100).toFixed(0)}%</b>
          </div>
        `);
        push(rect);
      });
    }

    if (activeLayer === "intersections") {
      intersections.slice(0, 500).forEach(([ilat, ilon]) => {
        push(
          L.circleMarker([ilat, ilon], {
            pane: "markersPane",
            radius: 6,
            color: "#7c2d12",
            fillColor: "#facc15",
            fillOpacity: 0.95,
            weight: 2,
          }).bindPopup(`<span style="font-family:Consolas,monospace;font-size:11px;color:#92400e">Intersection</span>`)
        );
      });

      deadEnds.slice(0, 250).forEach(([dlat, dlon]) => {
        push(
          L.circleMarker([dlat, dlon], {
            pane: "markersPane",
            radius: 5,
            color: "#7f1d1d",
            fillColor: "#ef4444",
            fillOpacity: 0.92,
            weight: 2,
          }).bindPopup(`<span style="font-family:Consolas,monospace;font-size:11px;color:#b91c1c">Dead End</span>`)
        );
      });
    }
  }, [data, activeLayer, lat, lon, radius]);

  return <div ref={containerRef} style={{ width: "100%", height: "100%", background: "#020617" }} />;
}

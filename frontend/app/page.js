"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import ImageUpload from "../components/ImageUpload";
import { Btn, ErrorBox, MetricCard, ReadinessBadge, SectionLabel, Spinner, TypeBar } from "../components/UI";

const MapPanel = dynamic(() => import("../components/MapPanel"), { ssr: false });

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const PRESETS = [
  { key: "delhi", label: "Delhi", lat: 28.6139, lon: 77.209 },
  { key: "mumbai", label: "Mumbai", lat: 19.076, lon: 72.8777 },
  { key: "bengaluru", label: "Bengaluru", lat: 12.9716, lon: 77.5946 },
  { key: "hyderabad", label: "Hyderabad", lat: 17.385, lon: 78.4867 },
  { key: "chennai", label: "Chennai", lat: 13.0827, lon: 80.2707 },
  { key: "kolkata", label: "Kolkata", lat: 22.5726, lon: 88.3639 },
  { key: "ahmedabad", label: "Ahmedabad", lat: 23.0225, lon: 72.5714 },
  { key: "surat", label: "Surat", lat: 21.1702, lon: 72.8311 },
];


function Panel({ title, children, style = {} }) {
  return (
    <section
      style={{
        background: "var(--panel)",
        border: "1px solid var(--border)",
        borderRadius: 24,
        padding: 20,
        boxShadow: "var(--shadow)",
        ...style,
      }}
    >
      <SectionLabel>{title}</SectionLabel>
      {children}
    </section>
  );
}

export default function Home() {
  const [tab, setTab] = useState("network");
  const [lat, setLat] = useState(28.6139);
  const [lon, setLon] = useState(77.209);
  const [radius, setRadius] = useState(2000);
  const [latInput, setLatInput] = useState("28.6139");
  const [lonInput, setLonInput] = useState("77.2090");
  const [activeLayer, setActiveLayer] = useState("roads");
  const [osmData, setOsmData] = useState(null);
  const [osmLoading, setOsmLoading] = useState(false);
  const [osmError, setOsmError] = useState(null);

  const summary = osmData?.metrics?.summary;
  const distribution = osmData?.metrics?.type_distribution || [];

  async function analyzeCity(nextLat = lat, nextLon = lon, nextRadius = radius) {
    setOsmLoading(true);
    setOsmError(null);
    try {
      const response = await fetch(`${API}/analyze?lat=${nextLat}&lon=${nextLon}&radius=${nextRadius}`);
      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "Analysis failed");
      }
      setOsmData(await response.json());
    } catch (error) {
      setOsmError(error.message || "Analysis failed");
    } finally {
      setOsmLoading(false);
    }
  }

  useEffect(() => {
    analyzeCity(28.6139, 77.209, 2000);
  }, []);

  function selectPreset(city) {
    setLat(city.lat);
    setLon(city.lon);
    setLatInput(String(city.lat));
    setLonInput(String(city.lon));
    analyzeCity(city.lat, city.lon, radius);
  }

  function runCustomAnalysis() {
    const parsedLat = parseFloat(latInput);
    const parsedLon = parseFloat(lonInput);
    if (Number.isNaN(parsedLat) || Number.isNaN(parsedLon)) {
      setOsmError("Enter valid latitude and longitude values.");
      return;
    }
    setLat(parsedLat);
    setLon(parsedLon);
    analyzeCity(parsedLat, parsedLon, radius);
  }

  async function download(path, filename) {
    const response = await fetch(`${API}/${path}?lat=${lat}&lon=${lon}&radius=${radius}`);
    const blob = await response.blob();
    const anchor = document.createElement("a");
    anchor.href = URL.createObjectURL(blob);
    anchor.download = filename;
    anchor.click();
  }

  return (
    <div style={{ minHeight: "100vh", padding: 18 }}>
      <div style={{ display: "flex", gap: 18, alignItems: "flex-start", flexWrap: "wrap" }}>
        <aside style={{ display: "grid", gap: 18, alignContent: "start", flex: "1 1 320px", minWidth: 280, maxWidth: 360 }}>
          <Panel title="Project Studio">
            <div style={{ display: "grid", gap: 14 }}>
              <div>
                <h1 style={{ margin: 0, fontSize: 30, lineHeight: 1.05 }}>
                  Transport analytics from maps and satellite imagery
                </h1>
              </div>
              <p style={{ margin: 0, color: "var(--muted)", lineHeight: 1.75, fontSize: 14 }}>
                Analyze road networks on the map and extract road features from uploaded satellite images.
              </p>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {[
                  ["network", "Network explorer"],
                  ["satellite", "Satellite lab"],
                ].map(([key, label]) => (
                  <button
                    key={key}
                    onClick={() => setTab(key)}
                    style={{
                      borderRadius: 999,
                      padding: "10px 14px",
                      border: `1px solid ${tab === key ? "rgba(245,158,11,0.55)" : "var(--border)"}`,
                      background: tab === key ? "rgba(245,158,11,0.12)" : "rgba(255,255,255,0.03)",
                      color: tab === key ? "var(--accent)" : "var(--text)",
                    }}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
          </Panel>

                    {tab === "network" ? (
            <Panel title="Analysis Controls">
              <div style={{ display: "grid", gap: 16 }}>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {PRESETS.map((city) => (
                    <button
                      key={city.key}
                      onClick={() => selectPreset(city)}
                      style={{
                        borderRadius: 999,
                        padding: "8px 12px",
                        border: "1px solid var(--border)",
                        background: "rgba(255,255,255,0.03)",
                        color: "var(--text)",
                      }}
                    >
                      {city.label}
                    </button>
                  ))}
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                  <input
                    value={latInput}
                    onChange={(event) => setLatInput(event.target.value)}
                    placeholder="Latitude"
                    style={inputStyle}
                  />
                  <input
                    value={lonInput}
                    onChange={(event) => setLonInput(event.target.value)}
                    placeholder="Longitude"
                    style={inputStyle}
                  />
                </div>

                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8, color: "var(--muted)", fontFamily: "var(--font-mono)", fontSize: 12 }}>
                    <span>Radius</span>
                    <span>{radius} m</span>
                  </div>
                  <input
                    type="range"
                    min="500"
                    max="5000"
                    step="250"
                    value={radius}
                    onChange={(event) => setRadius(Number(event.target.value))}
                    style={{ width: "100%" }}
                  />
                </div>

                <Btn onClick={runCustomAnalysis} loading={osmLoading}>
                  Analyze urban corridor
                </Btn>
                <ErrorBox message={osmError} />
              </div>
            </Panel>
          ) : null}

          {tab === "network" && summary ? (
            <Panel title="ITS Readiness">
              <div style={{ display: "grid", gap: 16 }}>
                <ReadinessBadge its={summary.its_readiness} />
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                  <MetricCard label="Roads" value={summary.total_roads} />
                  <MetricCard label="Length" value={`${summary.total_length_km} km`} />
                  <MetricCard label="Density" value={summary.road_density_km_km2} sub="km per km2" />
                  <MetricCard label="Connect" value={`${summary.connectivity_index}%`} />
                </div>
              </div>
            </Panel>
          ) : null}
        </aside>

        <main style={{ display: "grid", gap: 18, flex: "999 1 720px", minWidth: 0 }}>
          {tab === "network" ? (
            <>
              <Panel title="Urban Network Explorer" style={{ overflow: "hidden" }}>
                <div style={{ display: "grid", gap: 14 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
                    <div style={{ color: "var(--muted)", fontSize: 14, lineHeight: 1.6 }}>
                      Switch between hierarchy view, density heatmap, and intersection markers.
                    </div>
                    <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                      {["roads", "heatmap", "intersections"].map((layer) => (
                        <button
                          key={layer}
                          onClick={() => setActiveLayer(layer)}
                          style={{
                            borderRadius: 999,
                            padding: "8px 12px",
                            border: `1px solid ${activeLayer === layer ? "rgba(45,212,191,0.5)" : "var(--border)"}`,
                            background: activeLayer === layer ? "rgba(45,212,191,0.12)" : "rgba(255,255,255,0.03)",
                            color: activeLayer === layer ? "var(--accent2)" : "var(--text)",
                          }}
                        >
                          {layer}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div style={{ position: "relative", minHeight: "68vh" }}>
                  {osmLoading ? (
                    <div style={{ position: "absolute", inset: 0, background: "rgba(7,19,29,0.6)", zIndex: 5, display: "grid", placeItems: "center" }}>
                      <Spinner label="Reading OpenStreetMap road network..." />
                    </div>
                  ) : null}
                  <div style={{ height: "68vh", borderRadius: 22, overflow: "hidden", border: "1px solid var(--border)" }}>
                    <MapPanel
                      lat={lat}
                      lon={lon}
                      radius={radius}
                      data={osmData}
                      activeLayer={activeLayer}
                      onMoveEnd={(nextLat, nextLon) => {
                        setLatInput(nextLat);
                        setLonInput(nextLon);
                        setLat(parseFloat(nextLat));
                        setLon(parseFloat(nextLon));
                      }}
                    />
                  </div>
                  <div
                    style={{
                      position: "absolute",
                      left: 18,
                      bottom: 18,
                      zIndex: 10,
                      background: "rgba(255,255,255,0.9)",
                      border: "1px solid rgba(15, 23, 42, 0.12)",
                      borderRadius: 16,
                      padding: "12px 14px",
                      backdropFilter: "blur(10px)",
                      color: "#0f172a",
                      minWidth: 220,
                    }}
                  >
                    <div style={{ fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: "0.12em", textTransform: "uppercase", color: "#475569", marginBottom: 8 }}>
                      Active Layer
                    </div>
                    {activeLayer === "roads" ? (
                      <div style={{ fontSize: 13, lineHeight: 1.6 }}>
                        Colored polylines show road hierarchy from major corridors to local streets.
                      </div>
                    ) : null}
                    {activeLayer === "heatmap" ? (
                      <div style={{ display: "grid", gap: 8 }}>
                        <div style={{ fontSize: 13, lineHeight: 1.6 }}>
                          Heatmap cells show relative road concentration in the selected study area.
                        </div>
                        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                          {["#2dd4bf", "#84cc16", "#f59e0b", "#ea580c", "#b91c1c"].map((color) => (
                            <span key={color} style={{ width: 22, height: 10, borderRadius: 999, background: color }} />
                          ))}
                        </div>
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "#64748b" }}>
                          <span>Lower</span>
                          <span>Higher</span>
                        </div>
                      </div>
                    ) : null}
                    {activeLayer === "intersections" ? (
                      <div style={{ display: "grid", gap: 8 }}>
                        <div style={{ fontSize: 13, lineHeight: 1.6 }}>
                          Yellow markers are intersections. Red markers indicate dead ends.
                        </div>
                        <div style={{ display: "flex", gap: 14, fontSize: 12 }}>
                          <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                            <span style={{ width: 12, height: 12, borderRadius: "50%", background: "#facc15", border: "2px solid #7c2d12" }} />
                            Intersection
                          </span>
                          <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                            <span style={{ width: 12, height: 12, borderRadius: "50%", background: "#ef4444", border: "2px solid #7f1d1d" }} />
                            Dead end
                          </span>
                        </div>
                      </div>
                    ) : null}
                  </div>
                </div>
                </div>
              </Panel>

              <div style={{ display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: 18 }}>
                <Panel title="Road Hierarchy">
                  {distribution.slice(0, 8).map((item) => (
                    <TypeBar key={item.type} item={item} />
                  ))}
                </Panel>

                <Panel title="Automated Outputs">
                  <div style={{ display: "grid", gap: 12 }}>
                    <p style={{ margin: 0, color: "var(--muted)", lineHeight: 1.7 }}>
                      Combine map analytics with satellite validation to prepare corridor diagnostics,
                      downloadable GeoJSON layers, and rapid ITS readiness summaries for Indian cities.
                    </p>
                    <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                      <Btn variant="ghost" onClick={() => download("geojson", "india_its_roads.geojson")}>
                        Download GeoJSON
                      </Btn>
                      <Btn variant="secondary" onClick={() => download("report", "india_its_report.pdf")}>
                        Download PDF
                      </Btn>
                    </div>
                  </div>
                </Panel>
              </div>

              <Panel title="Metric Guide">
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16 }}>
                  <div style={{ padding: 16, borderRadius: 18, background: "rgba(255,255,255,0.03)", border: "1px solid var(--border)" }}>
                    <div style={{ color: "var(--accent)", fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 8 }}>
                      Road Density
                    </div>
                    <div style={{ lineHeight: 1.7, color: "var(--text)", fontSize: 14 }}>
                      Road density shows how much road network exists inside the selected study area.
                      In the city map view, it is estimated as total road length per square kilometer.
                      Higher density usually means stronger transport coverage, but not automatically better traffic flow.
                    </div>
                  </div>

                  <div style={{ padding: 16, borderRadius: 18, background: "rgba(255,255,255,0.03)", border: "1px solid var(--border)" }}>
                    <div style={{ color: "var(--accent2)", fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 8 }}>
                      Connectivity
                    </div>
                    <div style={{ lineHeight: 1.7, color: "var(--text)", fontSize: 14 }}>
                      Connectivity tells us how well roads link together through intersections instead of ending abruptly.
                      Better connectivity usually supports smoother movement, route flexibility, and stronger suitability for ITS services.
                    </div>
                  </div>

                  <div style={{ padding: 16, borderRadius: 18, background: "rgba(255,255,255,0.03)", border: "1px solid var(--border)" }}>
                    <div style={{ color: "#f97316", fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 8 }}>
                      ITS Readiness
                    </div>
                    <div style={{ lineHeight: 1.7, color: "var(--text)", fontSize: 14 }}>
                      ITS readiness is a practical summary of whether the visible road network is suitable for smart transport applications
                      such as traffic monitoring, route guidance, signal planning, corridor management, and urban mobility analytics.
                    </div>
                  </div>
                </div>
              </Panel>
            </>
          ) : null}

          {tab === "satellite" ? (
            <Panel title="Satellite Feature Extraction">
              <ImageUpload />
            </Panel>
          ) : null}
        </main>
      </div>
    </div>
  );
}

const inputStyle = {
  width: "100%",
  background: "rgba(255,255,255,0.03)",
  border: "1px solid var(--border)",
  borderRadius: 14,
  padding: "12px 14px",
  color: "var(--text)",
};


"use client";

import React, { useMemo, useState } from "react";
import { Btn, ErrorBox, MetricCard, SectionLabel, Spinner } from "./UI";

const galleryGrid = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
  gap: 16,
};

function PreviewCard({ title, src, alt }) {
  return (
    <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border)", borderRadius: 18, overflow: "hidden" }}>
      <div style={{ padding: "12px 14px", borderBottom: "1px solid var(--border)", fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--muted)" }}>
        {title}
      </div>
      <div style={{ aspectRatio: "4 / 3", background: "#08131b" }}>
        {src ? (
          <img src={src} alt={alt} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        ) : (
          <div style={{ height: "100%", display: "grid", placeItems: "center", color: "var(--muted)", fontSize: 13 }}>
            No image yet
          </div>
        )}
      </div>
    </div>
  );
}

export default function ImageUpload() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const apiUrl = useMemo(() => {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    return baseUrl.endsWith("/process-image") ? baseUrl : `${baseUrl.replace(/\/$/, "")}/process-image`;
  }, []);

  function onFileChange(event) {
    const selectedFile = event.target.files?.[0];
    setError(null);
    setResult(null);
    if (!selectedFile) {
      setFile(null);
      setPreview(null);
      return;
    }
    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
  }

  async function upload() {
    if (!file) {
      setError("Choose a satellite image before starting extraction.");
      return;
    }

    setProcessing(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(apiUrl, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "Processing failed");
      }

      const payload = await response.json();
      setResult(payload);
    } catch (uploadError) {
      setError(`Processing failed: ${uploadError.message || uploadError}`);
    } finally {
      setProcessing(false);
    }
  }

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <SectionLabel>Satellite Input</SectionLabel>
          <div style={{ color: "var(--text)", fontSize: 16, fontWeight: 600, marginBottom: 6 }}>
            Automated road-feature extraction from uploaded imagery
          </div>
          <div style={{ color: "var(--muted)", maxWidth: 680, lineHeight: 1.7, fontSize: 14 }}>
            The pipeline now uses a SegFormer satellite segmentation model with a road class,
            followed by topology extraction and ITS-oriented post-analysis.
          </div>
        </div>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <input type="file" accept="image/*" onChange={onFileChange} />
          <Btn onClick={upload} loading={processing} disabled={processing}>
            Run extraction
          </Btn>
        </div>
      </div>

      <ErrorBox message={error} />

      {processing ? <Spinner label="Reading satellite image and extracting transport features..." /> : null}

      <div style={galleryGrid}>
        <PreviewCard title="Original scene" src={preview} alt="Original upload" />
        <PreviewCard title="Enhanced image" src={result?.enhanced_image} alt="Enhanced view" />
        <PreviewCard title="Road mask overlay" src={result?.processed_image} alt="Road overlay" />
        <PreviewCard title="Skeleton network" src={result?.skeleton_image} alt="Skeleton network" />
      </div>

      {result ? (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 14 }}>
            <MetricCard label="Road density" value={`${result.road_density_percent}%`} />
            <MetricCard label="Road length" value={result.road_length} sub="skeleton pixels" />
            <MetricCard label="Intersections" value={result.intersection_count} />
            <MetricCard label="Endpoints" value={result.endpoint_count} />
            <MetricCard label="Avg width" value={result.average_width_px} sub="pixels" />
            <MetricCard label="Connectivity" value={result.connectivity_score} />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 16 }}>
            <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border)", borderRadius: 18, padding: 18 }}>
              <SectionLabel>Scene Interpretation</SectionLabel>
              <div style={{ display: "grid", gap: 10, color: "var(--text)", fontSize: 14, lineHeight: 1.65 }}>
                <div><strong>Coverage:</strong> {result.analysis_summary?.coverage_class}</div>
                <div><strong>Road profile:</strong> {result.analysis_summary?.road_profile}</div>
                <div><strong>Network pattern:</strong> {result.analysis_summary?.network_pattern}</div>
                <div><strong>Confidence:</strong> {result.analysis_summary?.extraction_confidence}</div>
              </div>
            </div>

            <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border)", borderRadius: 18, padding: 18 }}>
              <SectionLabel>Planning Note</SectionLabel>
              <div style={{ display: "grid", gap: 10, color: "var(--text)", fontSize: 14, lineHeight: 1.65 }}>
                <div>{result.analysis_summary?.planning_note}</div>
                <div style={{ color: "var(--muted)" }}>{result.analysis_summary?.caution}</div>
              </div>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 16 }}>
            <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border)", borderRadius: 18, padding: 18 }}>
              <SectionLabel>Automation Workflow</SectionLabel>
              <div style={{ display: "grid", gap: 10, color: "var(--text)", fontSize: 14 }}>
                {result.pipeline?.steps?.map((step, index) => (
                  <div key={step} style={{ display: "flex", gap: 10 }}>
                    <span style={{ color: "var(--accent)" }}>{String(index + 1).padStart(2, "0")}</span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border)", borderRadius: 18, padding: 18 }}>
              <SectionLabel>ITS Relevance</SectionLabel>
              <div style={{ display: "grid", gap: 10, color: "var(--text)", fontSize: 14, lineHeight: 1.6 }}>
                {result.use_cases?.map((item) => (
                  <div key={item}>{item}</div>
                ))}
              </div>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}

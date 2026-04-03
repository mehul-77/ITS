"use client";

import React, { useState } from "react";

export default function ImageUpload() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/process-image";

  function onFileChange(e) {
    setError(null);
    const f = e.target.files[0];
    if (!f) return;
    setFile(f);
    const url = URL.createObjectURL(f);
    setPreview(url);
    setResult(null);
  }

  async function upload() {
    if (!file) {
      setError("Please choose an image file first.");
      return;
    }
    setProcessing(true);
    setError(null);
    setResult(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch(API_URL, {
        method: "POST",
        body: fd,
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt || res.statusText);
      }
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setError("Processing failed: " + (err.message || err));
    } finally {
      setProcessing(false);
    }
  }

  return (
    <div style={{ maxWidth: 900 }}>
      <div style={{ marginBottom: 12 }}>
        <input type="file" accept="image/*" onChange={onFileChange} />
        <button onClick={upload} disabled={processing} style={{ marginLeft: 8 }}>
          {processing ? "Processing..." : "Upload & Process"}
        </button>
      </div>

      {error && <div style={{ color: "crimson", marginBottom: 12 }}>{error}</div>}

      <div style={{ display: "flex", gap: 20, alignItems: "flex-start" }}>
        <div style={{ flex: 1 }}>
          <h3>Original</h3>
          {preview ? (
            <img src={preview} alt="preview" style={{ maxWidth: "100%", border: "1px solid #ddd" }} />
          ) : (
            <div style={{ color: "#666" }}>No image selected</div>
          )}
        </div>

        <div style={{ flex: 1 }}>
          <h3>Processed</h3>
          {result?.processed_image ? (
            <img src={result.processed_image} alt="processed" style={{ maxWidth: "100%", border: "1px solid #ddd" }} />
          ) : (
            <div style={{ color: "#666" }}>{processing ? "Processing..." : "No result yet"}</div>
          )}

          {result && (
            <div style={{ marginTop: 12, background: "#fafafa", padding: 10, borderRadius: 6 }}>
              <h4>ITS Metrics</h4>
              <div>Road density: {(result.road_density * 100).toFixed(3)} %</div>
              <div>Road length (pixels): {result.road_length}</div>
              <div>Intersection count: {result.intersection_count}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

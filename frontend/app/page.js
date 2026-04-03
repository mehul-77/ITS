import ImageUpload from "../components/ImageUpload";

export default function Page() {
  return (
    <main style={{ padding: 24, fontFamily: "system-ui, Arial" }}>
      <h1>Intelligent Transportation System — Road Network Extraction</h1>
      <p>Upload a satellite image to extract road networks and ITS metrics.</p>
      <ImageUpload />
    </main>
  );
}

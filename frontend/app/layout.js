import "leaflet/dist/leaflet.css";
import "./globals.css";

export const metadata = {
  title: "India ITS Feature Extraction Studio",
  description: "India-focused intelligent transportation system dashboard for road-network analysis and satellite feature extraction.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

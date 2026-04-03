import Image from 'next/image';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>ITS - Road Network Extraction</title>
      </head>
      <body>
        {children}
      </body>
    </html>
  );
}

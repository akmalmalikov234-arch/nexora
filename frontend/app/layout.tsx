import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Nexora",
  description: "Mustaqil Android ilovalar marketplace"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="uz">
      <body>{children}</body>
    </html>
  );
}

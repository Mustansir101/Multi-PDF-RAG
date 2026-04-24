import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Question Generator",
  description: "AI RAG based Question Generator",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <main className="appRoot">{children}</main>
      </body>
    </html>
  );
}

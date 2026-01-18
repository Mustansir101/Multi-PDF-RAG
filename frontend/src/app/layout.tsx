import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Multi PDF RAG",
  description: "Chat with multiple PDFs",
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

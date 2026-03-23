import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Header from "@/components/Header";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "NexusAI — Document Intelligence Platform",
  description:
    "AI-powered document Q&A platform with RAG architecture. Upload documents and ask questions with citation-backed answers.",
  keywords: [
    "AI",
    "RAG",
    "Document Intelligence",
    "Ollama",
    "Semantic Search",
    "NLP",
  ],
  authors: [{ name: "Amna Khan" }],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${inter.variable} font-sans bg-surface-950 text-gray-100 antialiased`}
      >
        <div className="flex min-h-screen flex-col">
          <Header />
          <main className="flex-1">{children}</main>
        </div>
      </body>
    </html>
  );
}

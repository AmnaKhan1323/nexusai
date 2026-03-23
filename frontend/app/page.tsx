"use client";

import { motion } from "framer-motion";
import {
  Brain,
  FileSearch,
  MessageSquare,
  Shield,
  Sparkles,
  Upload,
  Zap,
  ArrowRight,
} from "lucide-react";
import Link from "next/link";

const features = [
  {
    icon: FileSearch,
    title: "Semantic Search",
    description:
      "Natural language queries across 1,200+ document chunks with 94% answer accuracy powered by vector embeddings.",
    color: "from-blue-500 to-cyan-500",
  },
  {
    icon: Brain,
    title: "RAG Architecture",
    description:
      "Retrieval-Augmented Generation pipeline combining ChromaDB vector search with Ollama LLM for grounded answers.",
    color: "from-violet-500 to-purple-500",
  },
  {
    icon: MessageSquare,
    title: "Citation Tracking",
    description:
      "Every answer is backed by traceable citations with source documents, chunk references, and relevance scores.",
    color: "from-emerald-500 to-teal-500",
  },
  {
    icon: Upload,
    title: "Multi-format Upload",
    description:
      "Upload PDF and DOCX files with intelligent text extraction, automatic chunking, and embedding generation.",
    color: "from-orange-500 to-amber-500",
  },
  {
    icon: Zap,
    title: "Real-time Processing",
    description:
      "Async document ingestion pipeline with status tracking, token counting, and instant availability.",
    color: "from-pink-500 to-rose-500",
  },
  {
    icon: Shield,
    title: "Production-Ready",
    description:
      "Docker deployment, PostgreSQL metadata, Redis caching, comprehensive error handling, and logging.",
    color: "from-indigo-500 to-blue-500",
  },
];

const techStack = [
  { name: "Next.js 14", category: "Frontend" },
  { name: "React 18", category: "Frontend" },
  { name: "TypeScript", category: "Frontend" },
  { name: "Tailwind CSS", category: "Frontend" },
  { name: "FastAPI", category: "Backend" },
  { name: "Python 3.11", category: "Backend" },
  { name: "Ollama (Llama 3)", category: "AI/ML" },
  { name: "ChromaDB", category: "Vector DB" },
  { name: "PostgreSQL", category: "Database" },
  { name: "Redis", category: "Cache" },
  { name: "Docker", category: "DevOps" },
  { name: "SQLAlchemy", category: "ORM" },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.2 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

export default function LandingPage() {
  return (
    <div className="relative overflow-hidden">
      {/* Background gradient effects */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-1/4 top-0 h-[600px] w-[600px] -translate-x-1/2 rounded-full bg-brand-600/10 blur-3xl" />
        <div className="absolute right-1/4 top-1/3 h-[500px] w-[500px] translate-x-1/2 rounded-full bg-violet-600/10 blur-3xl" />
        <div className="absolute bottom-0 left-1/2 h-[400px] w-[400px] -translate-x-1/2 rounded-full bg-cyan-600/5 blur-3xl" />
      </div>

      {/* Hero Section */}
      <section className="relative px-6 pb-20 pt-20 lg:px-8 lg:pt-32">
        <motion.div
          className="mx-auto max-w-4xl text-center"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <motion.div
            className="mb-6 inline-flex items-center gap-2 rounded-full border border-brand-500/30 bg-brand-500/10 px-4 py-2 text-sm text-brand-300"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
          >
            <Sparkles className="h-4 w-4" />
            <span>Powered by Ollama & RAG Architecture</span>
          </motion.div>

          <h1 className="mb-6 bg-gradient-to-r from-white via-gray-100 to-gray-300 bg-clip-text text-5xl font-extrabold tracking-tight text-transparent sm:text-7xl">
            Document Intelligence
            <br />
            <span className="bg-gradient-to-r from-brand-400 via-violet-400 to-cyan-400 bg-clip-text text-transparent">
              Reimagined
            </span>
          </h1>

          <p className="mx-auto mb-10 max-w-2xl text-lg leading-relaxed text-gray-400 sm:text-xl">
            Upload your documents and ask questions in natural language. NexusAI
            uses advanced RAG architecture to deliver accurate, citation-backed
            answers from your enterprise knowledge base.
          </p>

          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              href="/chat"
              className="group inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-brand-600 to-violet-600 px-8 py-4 text-lg font-semibold text-white shadow-lg shadow-brand-500/25 transition-all duration-300 hover:shadow-xl hover:shadow-brand-500/40 hover:brightness-110"
            >
              Start Asking Questions
              <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
            </Link>
            <Link
              href="/documents"
              className="inline-flex items-center gap-2 rounded-xl border border-gray-700 bg-surface-800/50 px-8 py-4 text-lg font-semibold text-gray-300 backdrop-blur-sm transition-all duration-300 hover:border-gray-600 hover:bg-surface-700/50 hover:text-white"
            >
              <Upload className="h-5 w-5" />
              Upload Documents
            </Link>
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div
          className="mx-auto mt-20 grid max-w-3xl grid-cols-3 gap-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.6 }}
        >
          {[
            { value: "94%", label: "Answer Accuracy" },
            { value: "1,200+", label: "Document Chunks" },
            { value: "<2s", label: "Response Time" },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-3xl font-bold text-white sm:text-4xl">
                {stat.value}
              </div>
              <div className="mt-1 text-sm text-gray-500">{stat.label}</div>
            </div>
          ))}
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="relative px-6 py-24 lg:px-8">
        <div className="mx-auto max-w-6xl">
          <motion.div
            className="mb-16 text-center"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="mb-4 text-3xl font-bold text-white sm:text-4xl">
              Intelligent Features
            </h2>
            <p className="mx-auto max-w-2xl text-gray-400">
              Built with cutting-edge AI and modern engineering practices for
              enterprise-grade document intelligence.
            </p>
          </motion.div>

          <motion.div
            className="grid gap-6 md:grid-cols-2 lg:grid-cols-3"
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            {features.map((feature) => (
              <motion.div
                key={feature.title}
                variants={itemVariants}
                className="group relative overflow-hidden rounded-2xl border border-gray-800 bg-surface-800/50 p-8 backdrop-blur-sm transition-all duration-300 hover:border-gray-700 hover:bg-surface-800/80"
              >
                <div
                  className={`mb-4 inline-flex rounded-xl bg-gradient-to-br ${feature.color} p-3 shadow-lg`}
                >
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="mb-2 text-xl font-semibold text-white">
                  {feature.title}
                </h3>
                <p className="leading-relaxed text-gray-400">
                  {feature.description}
                </p>
                <div
                  className={`absolute inset-x-0 bottom-0 h-0.5 bg-gradient-to-r ${feature.color} opacity-0 transition-opacity duration-300 group-hover:opacity-100`}
                />
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Tech Stack Section */}
      <section className="relative px-6 py-24 lg:px-8">
        <div className="mx-auto max-w-4xl">
          <motion.div
            className="mb-12 text-center"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="mb-4 text-3xl font-bold text-white sm:text-4xl">
              Tech Stack
            </h2>
            <p className="text-gray-400">
              Modern, battle-tested technologies for reliability and
              performance.
            </p>
          </motion.div>

          <motion.div
            className="flex flex-wrap justify-center gap-3"
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            {techStack.map((tech) => (
              <motion.span
                key={tech.name}
                variants={itemVariants}
                className="rounded-full border border-gray-700/50 bg-surface-800/80 px-5 py-2.5 text-sm font-medium text-gray-300 transition-all duration-200 hover:border-brand-500/50 hover:text-brand-300"
              >
                {tech.name}
              </motion.span>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative px-6 py-24 lg:px-8">
        <motion.div
          className="mx-auto max-w-3xl overflow-hidden rounded-3xl border border-gray-800 bg-gradient-to-br from-brand-950/80 via-surface-800/50 to-violet-950/80 p-12 text-center backdrop-blur-sm"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <Brain className="mx-auto mb-6 h-12 w-12 text-brand-400" />
          <h2 className="mb-4 text-3xl font-bold text-white">
            Ready to unlock your documents?
          </h2>
          <p className="mb-8 text-gray-400">
            Upload your first document and experience AI-powered Q&A with
            instant, accurate answers.
          </p>
          <Link
            href="/documents"
            className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-brand-600 to-violet-600 px-8 py-4 text-lg font-semibold text-white shadow-lg shadow-brand-500/25 transition-all duration-300 hover:shadow-xl hover:shadow-brand-500/40 hover:brightness-110"
          >
            Get Started
            <ArrowRight className="h-5 w-5" />
          </Link>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800/50 px-6 py-12">
        <div className="mx-auto max-w-6xl text-center text-sm text-gray-500">
          <p>
            Built with ❤️ by{" "}
            <span className="font-medium text-gray-400">Amna Khan</span> —
            Senior Software Engineer
          </p>
          <p className="mt-2">
            Next.js · FastAPI · Ollama · ChromaDB · PostgreSQL
          </p>
        </div>
      </footer>
    </div>
  );
}

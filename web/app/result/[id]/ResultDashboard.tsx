"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  BookOpen,
  Monitor,
  Film,
  Headphones,
  Image,
  HelpCircle,
  Layers,
  BrainCircuit,
  Download,
  CheckCircle2,
  XCircle,
  Loader2,
  ChevronDown,
  PlusCircle,
} from "lucide-react";
import { getJobStatus, type JobStatus, type ProductType } from "@/lib/api";

const PRODUCT_META: Record<
  ProductType,
  { icon: typeof Monitor; label: string; color: string }
> = {
  slides: { icon: Monitor, label: "Slides", color: "text-blue-500" },
  video: { icon: Film, label: "Video", color: "text-purple-500" },
  audio: { icon: Headphones, label: "Audio", color: "text-pink-500" },
  infographic: { icon: Image, label: "Infographic", color: "text-teal-500" },
  quiz: { icon: HelpCircle, label: "Quiz", color: "text-amber-500" },
  flashcards: { icon: Layers, label: "Flashcards", color: "text-green-500" },
  mind_map: {
    icon: BrainCircuit,
    label: "Mind Map",
    color: "text-indigo-500",
  },
};

export default function ResultDashboard({ jobId }: { jobId: string }) {
  const [job, setJob] = useState<JobStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showMarkdown, setShowMarkdown] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function fetchStatus() {
      try {
        const data = await getJobStatus(jobId);
        if (!cancelled) {
          setJob(data);
          setLoading(false);

          // If still generating, poll every 3s
          if (
            data.status === "generating_book" ||
            data.status === "generating_products"
          ) {
            setTimeout(fetchStatus, 3000);
          }
        }
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to load results");
          setLoading(false);
        }
      }
    }

    fetchStatus();
    return () => {
      cancelled = true;
    };
  }, [jobId]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto flex justify-center py-20">
        <Loader2 size={32} className="animate-spin text-primary" />
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
          {error || "Job not found"}
        </div>
        <div className="mt-4 flex justify-center">
          <Link
            href="/create"
            className="btn-primary text-base flex items-center gap-2"
          >
            <PlusCircle size={18} />
            Create New Book
          </Link>
        </div>
      </div>
    );
  }

  const book = job.book;

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      {/* Book info card */}
      {book && (
        <section className="card p-6">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center shrink-0">
              <BookOpen size={28} className="text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="text-xl font-bold mb-1">{book.title}</h2>
              <div className="flex flex-wrap gap-3 text-sm text-muted-foreground">
                <span>
                  Topic: <strong className="text-foreground">{book.topic}</strong>
                </span>
                <span>
                  Language:{" "}
                  <strong className="text-foreground">
                    {book.language === "zh" ? "Chinese" : "English"}
                  </strong>
                </span>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Products grid */}
      {job.products.length > 0 && (
        <section>
          <h3 className="font-bold mb-3">Generated Products</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {job.products.map((product, i) => {
              const meta = PRODUCT_META[product.product_type] || {
                icon: Monitor,
                label: product.product_type,
                color: "text-gray-500",
              };
              const Icon = meta.icon;
              const isComplete = product.status === "completed";
              const isFailed = product.status === "failed";
              const isGenerating =
                product.status === "generating" ||
                product.status === "pending";

              return (
                <div
                  key={i}
                  className={`card p-5 flex flex-col items-center text-center gap-3 ${
                    isComplete ? "" : "opacity-75"
                  }`}
                >
                  <div
                    className={`w-12 h-12 rounded-2xl flex items-center justify-center ${
                      isComplete ? "bg-green-50" : isFailed ? "bg-red-50" : "bg-muted"
                    }`}
                  >
                    <Icon
                      size={24}
                      className={
                        isComplete
                          ? meta.color
                          : isFailed
                            ? "text-red-400"
                            : "text-muted-foreground"
                      }
                    />
                  </div>
                  <span className="font-semibold text-sm">{meta.label}</span>

                  {/* Status */}
                  {isComplete && (
                    <div className="flex items-center gap-1 text-xs text-green-600">
                      <CheckCircle2 size={14} />
                      <span>Ready</span>
                    </div>
                  )}
                  {isFailed && (
                    <div className="flex items-center gap-1 text-xs text-red-500">
                      <XCircle size={14} />
                      <span>Failed</span>
                    </div>
                  )}
                  {isGenerating && (
                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                      <Loader2 size={14} className="animate-spin" />
                      <span>Generating...</span>
                    </div>
                  )}

                  {/* Download button */}
                  {isComplete && product.file_path && (
                    <a
                      href={toFileUrl(product.file_path)}
                      download
                      className="mt-1 inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-primary/10 text-primary text-xs font-semibold hover:bg-primary/20 transition"
                    >
                      <Download size={14} />
                      Download
                    </a>
                  )}

                  {/* Error message */}
                  {isFailed && product.error && (
                    <p className="text-xs text-red-400 mt-1 line-clamp-2">
                      {product.error}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Markdown download + preview */}
      {book && (
        <section className="card p-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-bold">Story (Markdown)</h3>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setShowMarkdown((v) => !v)}
                className="inline-flex items-center gap-1 text-sm text-primary font-semibold hover:underline"
              >
                {showMarkdown ? "Hide" : "Preview"}
                <ChevronDown
                  size={16}
                  className={`transition-transform ${showMarkdown ? "rotate-180" : ""}`}
                />
              </button>
              <a
                href={toFileUrl(book.markdown_path)}
                download
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary/10 text-primary text-sm font-semibold hover:bg-primary/20 transition"
              >
                <Download size={14} />
                Download .md
              </a>
            </div>
          </div>

          {showMarkdown && (
            <div className="mt-3 max-h-[500px] overflow-y-auto rounded-xl bg-muted p-5 text-sm leading-relaxed whitespace-pre-wrap font-mono">
              {book.markdown_content}
            </div>
          )}
        </section>
      )}

      {/* Actions */}
      <div className="flex justify-center pt-2">
        <Link
          href="/create"
          className="btn-primary text-base flex items-center gap-2"
        >
          <PlusCircle size={18} />
          Create Another Book
        </Link>
      </div>
    </div>
  );
}

/**
 * Convert an absolute file path from the backend to a /files/ URL.
 * Backend serves output/ as /files/ static mount.
 * e.g. "./output/ocean_20250305.md" -> "/files/ocean_20250305.md"
 */
function toFileUrl(filePath: string): string {
  // Extract filename from path (handle both ./output/x and output/x and /abs/path/output/x)
  const outputIdx = filePath.indexOf("output/");
  if (outputIdx !== -1) {
    const relative = filePath.slice(outputIdx + "output/".length);
    return `/files/${relative}`;
  }
  // Fallback: just use the filename
  const parts = filePath.split("/");
  return `/files/${parts[parts.length - 1]}`;
}

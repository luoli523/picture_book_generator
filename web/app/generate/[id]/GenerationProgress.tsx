"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import {
  Loader2,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  BookOpen,
  ArrowRight,
  RotateCcw,
} from "lucide-react";
import type { SSEEvent } from "@/lib/api";
import { useT } from "@/lib/i18n-provider";

interface Step {
  message: string;
  status: "active" | "done" | "error" | "warning";
}

interface BookPreview {
  title: string;
  summary?: string;
}

export default function GenerationProgress({ jobId }: { jobId: string }) {
  const t = useT();
  const [steps, setSteps] = useState<Step[]>([]);
  const [bookPreview, setBookPreview] = useState<BookPreview | null>(null);
  const [finished, setFinished] = useState(false);
  const [failed, setFailed] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const eventSource = new EventSource(`/api/generate/${jobId}/stream`);

    const addStep = (message: string, status: Step["status"]) => {
      setSteps((prev) => {
        const updated = prev.map((s) =>
          s.status === "active" ? { ...s, status: "done" as const } : s,
        );
        return [...updated, { message, status }];
      });
    };

    eventSource.onmessage = (e) => {
      let event: SSEEvent;
      try {
        event = JSON.parse(e.data);
      } catch {
        return;
      }

      switch (event.type) {
        case "progress":
          addStep(event.message, "active");
          break;

        case "book_title":
          setSteps((prev) => {
            const updated = prev.map((s) =>
              s.status === "active" ? { ...s, status: "done" as const } : s,
            );
            return [
              ...updated,
              { message: event.message, status: "done" as const },
            ];
          });
          if (event.data) {
            setBookPreview({
              title: event.data.title as string,
              summary: event.data.summary as string | undefined,
            });
          }
          break;

        case "book_complete":
          setSteps((prev) =>
            prev.map((s) =>
              s.status === "active" ? { ...s, status: "done" as const } : s,
            ),
          );
          break;

        case "product_start":
          addStep(event.message, "active");
          break;

        case "product_complete":
          setSteps((prev) =>
            prev.map((s) =>
              s.status === "active" ? { ...s, status: "done" as const } : s,
            ),
          );
          break;

        case "product_error":
          setSteps((prev) =>
            prev.map((s) =>
              s.status === "active"
                ? { ...s, status: "warning" as const }
                : s,
            ),
          );
          break;

        case "warning":
          addStep(event.message, "warning");
          break;

        case "error":
          setSteps((prev) =>
            prev.map((s) =>
              s.status === "active" ? { ...s, status: "error" as const } : s,
            ),
          );
          addStep(event.message, "error");
          setFailed(true);
          setErrorMsg(event.message);
          eventSource.close();
          break;

        case "done":
          setSteps((prev) =>
            prev.map((s) =>
              s.status === "active" ? { ...s, status: "done" as const } : s,
            ),
          );
          setFinished(true);
          eventSource.close();
          break;
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
      setFailed(true);
      setErrorMsg(t("progress.connection_lost"));
    };

    return () => {
      eventSource.close();
    };
  }, [jobId, t]);

  // Auto-scroll to bottom on new steps
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [steps]);

  return (
    <div className="max-w-2xl mx-auto">
      {/* Book preview card */}
      {bookPreview && (
        <div className="card p-5 mb-6 border-primary/30">
          <div className="flex items-center gap-2 mb-2">
            <BookOpen size={20} className="text-primary" />
            <h2 className="text-lg font-bold">{bookPreview.title}</h2>
          </div>
          {bookPreview.summary && (
            <p className="text-sm text-muted-foreground line-clamp-3">
              {bookPreview.summary}
            </p>
          )}
        </div>
      )}

      {/* Progress steps */}
      <div className="card p-6">
        <h3 className="font-bold mb-4">{t("progress.title")}</h3>
        <div className="space-y-3">
          {steps.map((step, i) => (
            <div key={i} className="flex items-start gap-3">
              <div className="mt-0.5">{stepIcon(step.status)}</div>
              <span
                className={`text-sm ${
                  step.status === "active"
                    ? "text-foreground font-semibold"
                    : step.status === "error"
                      ? "text-red-600"
                      : step.status === "warning"
                        ? "text-amber-600"
                        : "text-muted-foreground"
                }`}
              >
                {step.message}
              </span>
            </div>
          ))}

          {/* Loading indicator when active */}
          {!finished && !failed && steps.length > 0 && (
            <div className="flex items-center gap-3 pt-2">
              <Loader2 size={16} className="animate-spin text-primary" />
              <span className="text-sm text-muted-foreground">
                {t("progress.working")}
              </span>
            </div>
          )}
        </div>
        <div ref={bottomRef} />
      </div>

      {/* Tip while waiting */}
      {!finished && !failed && (
        <div className="mt-6 text-center text-sm text-muted-foreground">
          <p>{t("progress.tip")}</p>
        </div>
      )}

      {/* Action buttons */}
      {(finished || failed) && (
        <div className="mt-6 flex justify-center gap-4">
          {finished && (
            <Link
              href={`/result/${jobId}`}
              className="btn-primary text-base flex items-center gap-2"
            >
              {t("progress.view_results")}
              <ArrowRight size={18} />
            </Link>
          )}
          {failed && (
            <Link
              href="/create"
              className="btn-primary text-base flex items-center gap-2"
            >
              <RotateCcw size={18} />
              {t("progress.try_again")}
            </Link>
          )}
        </div>
      )}

      {/* Error detail */}
      {failed && errorMsg && (
        <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm text-center">
          {errorMsg}
        </div>
      )}
    </div>
  );
}

function stepIcon(status: Step["status"]) {
  switch (status) {
    case "active":
      return <Loader2 size={16} className="animate-spin text-primary" />;
    case "done":
      return <CheckCircle2 size={16} className="text-green-500" />;
    case "error":
      return <XCircle size={16} className="text-red-500" />;
    case "warning":
      return <AlertTriangle size={16} className="text-amber-500" />;
  }
}

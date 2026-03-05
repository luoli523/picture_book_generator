import Link from "next/link";
import { ArrowLeft, Sparkles } from "lucide-react";
import GenerationProgress from "./GenerationProgress";

export default async function GeneratePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <div className="min-h-screen px-4 py-8 md:px-8">
      <header className="max-w-2xl mx-auto mb-8">
        <Link
          href="/create"
          className="inline-flex items-center gap-1 text-muted-foreground hover:text-foreground transition-colors mb-4"
        >
          <ArrowLeft size={16} />
          <span className="text-sm">Back to Create</span>
        </Link>
        <div className="flex items-center gap-3">
          <Sparkles size={28} className="text-primary" strokeWidth={2.5} />
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
            Creating Your Book...
          </h1>
        </div>
        <p className="mt-2 text-muted-foreground">
          Sit tight! AI is crafting a personalized picture book.
        </p>
      </header>

      <GenerationProgress jobId={id} />
    </div>
  );
}

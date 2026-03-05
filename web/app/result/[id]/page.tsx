import Link from "next/link";
import { ArrowLeft, PartyPopper } from "lucide-react";
import ResultDashboard from "./ResultDashboard";

export default async function ResultPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <div className="min-h-screen px-4 py-8 md:px-8">
      <header className="max-w-4xl mx-auto mb-8">
        <Link
          href="/create"
          className="inline-flex items-center gap-1 text-muted-foreground hover:text-foreground transition-colors mb-4"
        >
          <ArrowLeft size={16} />
          <span className="text-sm">Create Another</span>
        </Link>
        <div className="flex items-center gap-3">
          <PartyPopper size={28} className="text-primary" strokeWidth={2.5} />
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
            Your Picture Book is Ready!
          </h1>
        </div>
      </header>

      <ResultDashboard jobId={id} />
    </div>
  );
}

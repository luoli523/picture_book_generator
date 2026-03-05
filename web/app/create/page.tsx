import Link from "next/link";
import { BookOpen, ArrowLeft } from "lucide-react";
import CreateForm from "./CreateForm";

export default function CreatePage() {
  return (
    <div className="min-h-screen px-4 py-8 md:px-8">
      {/* Header */}
      <header className="max-w-4xl mx-auto mb-8">
        <Link
          href="/"
          className="inline-flex items-center gap-1 text-muted-foreground hover:text-foreground transition-colors mb-4"
        >
          <ArrowLeft size={16} />
          <span className="text-sm">Back</span>
        </Link>
        <div className="flex items-center gap-3">
          <BookOpen size={28} className="text-primary" strokeWidth={2.5} />
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
            Create Your Picture Book
          </h1>
        </div>
        <p className="mt-2 text-muted-foreground">
          Configure your child&apos;s personalized story in a few simple steps.
        </p>
      </header>

      {/* Form */}
      <CreateForm />
    </div>
  );
}

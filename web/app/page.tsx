import Link from "next/link";
import { BookOpen, Sparkles, Film, Headphones, Image } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero */}
      <section className="flex-1 flex flex-col items-center justify-center px-6 py-24 text-center">
        <div className="mb-6 flex items-center gap-2 text-primary">
          <BookOpen size={40} strokeWidth={2.5} />
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight">
            StoryBook Workshop
          </h1>
        </div>

        <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mb-4">
          AI-powered picture book creation for your children.
          <br />
          Personalized stories, beautiful slides, videos, and more.
        </p>
        <p className="text-base text-muted-foreground max-w-xl mb-10">
          Choose a topic, set your child&apos;s age, pick a style — and let AI
          craft a unique educational picture book in minutes.
        </p>

        <Link href="/create" className="btn-primary text-lg">
          Start Creating
        </Link>

        {/* Feature icons */}
        <div className="mt-16 flex flex-wrap justify-center gap-8 text-muted-foreground">
          {[
            { icon: Sparkles, label: "AI Stories" },
            { icon: Film, label: "Video Books" },
            { icon: Headphones, label: "Audio Stories" },
            { icon: Image, label: "Infographics" },
          ].map(({ icon: Icon, label }) => (
            <div key={label} className="flex flex-col items-center gap-2">
              <div className="w-14 h-14 rounded-2xl bg-muted flex items-center justify-center">
                <Icon size={24} />
              </div>
              <span className="text-sm font-semibold">{label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="py-6 text-center text-sm text-muted-foreground">
        StoryBook Workshop &mdash; Making learning magical
      </footer>
    </div>
  );
}

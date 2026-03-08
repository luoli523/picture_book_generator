"use client";

import { use } from "react";
import Link from "next/link";
import { ArrowLeft, Sparkles } from "lucide-react";
import { motion } from "framer-motion";
import GenerationProgress from "./GenerationProgress";
import { useT } from "@/lib/i18n-provider";

export default function GeneratePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const t = useT();

  return (
    <div className="min-h-screen px-4 py-8 md:px-8">
      <motion.header
        className="max-w-2xl mx-auto mb-8"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <Link
          href="/create"
          className="inline-flex items-center gap-1 text-muted-foreground hover:text-foreground transition-colors mb-4"
        >
          <ArrowLeft size={16} />
          <span className="text-sm">{t("generate.page.back")}</span>
        </Link>
        <div className="flex items-center gap-3">
          <Sparkles size={28} className="text-primary" strokeWidth={2.5} />
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
            {t("generate.page.title")}
          </h1>
        </div>
        <p className="mt-2 text-muted-foreground">{t("generate.page.desc")}</p>
      </motion.header>

      <GenerationProgress jobId={id} />
    </div>
  );
}

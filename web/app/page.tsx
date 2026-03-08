"use client";

import Link from "next/link";
import { Sparkles, Film, Headphones, Image } from "lucide-react";
import { motion } from "framer-motion";
import { useT } from "@/lib/i18n-provider";

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.12, duration: 0.5, ease: "easeOut" as const },
  }),
};

export default function Home() {
  const t = useT();

  const features = [
    { icon: Sparkles, labelKey: "home.features.stories" },
    { icon: Film, labelKey: "home.features.video" },
    { icon: Headphones, labelKey: "home.features.audio" },
    { icon: Image, labelKey: "home.features.infographic" },
  ];

  return (
    <div className="min-h-[calc(100vh-3.5rem)] flex flex-col hero-gradient">
      {/* Hero */}
      <section className="flex-1 flex flex-col items-center justify-center px-6 py-24 text-center">
        <motion.h1
          className="text-4xl md:text-6xl font-extrabold tracking-tight text-primary mb-6"
          initial="hidden"
          animate="visible"
          custom={0}
          variants={fadeUp}
        >
          {t("nav.title")}
        </motion.h1>

        <motion.p
          className="text-lg md:text-xl text-muted-foreground max-w-2xl mb-4"
          initial="hidden"
          animate="visible"
          custom={1}
          variants={fadeUp}
        >
          {t("home.hero.subtitle")}
          <br />
          {t("home.hero.desc1")}
        </motion.p>

        <motion.p
          className="text-base text-muted-foreground max-w-xl mb-10"
          initial="hidden"
          animate="visible"
          custom={2}
          variants={fadeUp}
        >
          {t("home.hero.desc2")}
        </motion.p>

        <motion.div
          initial="hidden"
          animate="visible"
          custom={3}
          variants={fadeUp}
        >
          <Link href="/create" className="btn-primary text-lg">
            {t("home.hero.cta")}
          </Link>
        </motion.div>

        {/* Feature icons */}
        <div className="mt-16 flex flex-wrap justify-center gap-8 text-muted-foreground">
          {features.map(({ icon: Icon, labelKey }, i) => (
            <motion.div
              key={labelKey}
              className="flex flex-col items-center gap-2"
              initial="hidden"
              animate="visible"
              custom={4 + i}
              variants={fadeUp}
            >
              <div className="w-14 h-14 rounded-2xl bg-card border border-border flex items-center justify-center shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-200">
                <Icon size={24} />
              </div>
              <span className="text-sm font-semibold">{t(labelKey)}</span>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="py-6 text-center text-sm text-muted-foreground">
        {t("home.footer")}
      </footer>
    </div>
  );
}

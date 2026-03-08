"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  User,
  Palette,
  Package,
  ChevronDown,
  Sparkles,
  Rocket,
  Fish,
  Bug,
  TreePine,
  FlaskConical,
  Crown,
  Globe,
  Monitor,
  Film,
  Headphones,
  Image,
  HelpCircle,
  Layers,
  BrainCircuit,
} from "lucide-react";
import {
  createGeneration,
  DEFAULT_BOOK_REQUEST,
  DEFAULT_PRODUCT_OPTIONS,
  type GenerateRequest,
  type ProductOptions,
  type ProductType,
  type ContentMode,
  type Gender,
  type Language,
  type VideoStyle,
  type AudioFormat,
  type AudioLength,
  type SlidesFormat,
  type SlidesLength,
  type InfographicOrientation,
  type InfographicDetail,
  type QuizDifficulty,
} from "@/lib/api";
import { motion } from "framer-motion";
import { useI18n, useT } from "@/lib/i18n-provider";

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.4, ease: "easeOut" as const },
  }),
};

// === Popular topics ===

const POPULAR_TOPICS = [
  { icon: Rocket, label: "Space", labelZh: "\u592a\u7a7a" },
  { icon: Fish, label: "Ocean", labelZh: "\u6d77\u6d0b" },
  { icon: Bug, label: "Dinosaurs", labelZh: "\u6050\u9f99" },
  { icon: TreePine, label: "Animals", labelZh: "\u52a8\u7269" },
  {
    icon: FlaskConical,
    label: "Science",
    labelZh: "\u79d1\u5b66\u5b9e\u9a8c",
  },
  { icon: Crown, label: "Fairy Tales", labelZh: "\u7ae5\u8bdd\u6545\u4e8b" },
  { icon: Globe, label: "Geography", labelZh: "\u5730\u7406" },
  { icon: Sparkles, label: "Magic", labelZh: "\u9b54\u6cd5\u4e16\u754c" },
];

// === Product definitions ===

const PRODUCT_KEYS: { type: ProductType; icon: typeof Monitor }[] = [
  { type: "slides", icon: Monitor },
  { type: "video", icon: Film },
  { type: "audio", icon: Headphones },
  { type: "infographic", icon: Image },
  { type: "quiz", icon: HelpCircle },
  { type: "flashcards", icon: Layers },
  { type: "mind_map", icon: BrainCircuit },
];

export default function CreateForm() {
  const router = useRouter();
  const { locale, t } = useI18n();
  const [book, setBook] = useState<GenerateRequest>({
    ...DEFAULT_BOOK_REQUEST,
  });
  const [opts, setOpts] = useState<ProductOptions>({
    ...DEFAULT_PRODUCT_OPTIONS,
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [expandedProduct, setExpandedProduct] = useState<string | null>(null);

  const isZh = locale === "zh";

  // Helpers
  const updateBook = (patch: Partial<GenerateRequest>) =>
    setBook((prev) => ({ ...prev, ...patch }));

  const toggleProduct = (pt: ProductType) => {
    setBook((prev) => {
      const has = prev.products.includes(pt);
      return {
        ...prev,
        products: has
          ? prev.products.filter((p) => p !== pt)
          : [...prev.products, pt],
      };
    });
  };

  const handleSubmit = async () => {
    setError("");

    if (book.content_mode === "topic" && !book.topic.trim()) {
      setError(t("error.topic.required"));
      return;
    }
    if (book.content_mode === "story" && !book.story_text.trim()) {
      setError(t("error.story.required"));
      return;
    }

    setSubmitting(true);
    try {
      const res = await createGeneration({
        book,
        product_options: opts,
      });
      router.push(`/generate/${res.job_id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      {/* ====== Card A: About Your Child ====== */}
      <motion.section
        className="card p-6"
        initial="hidden"
        animate="visible"
        custom={0}
        variants={cardVariants}
      >
        <div className="flex items-center gap-2 mb-5">
          <User size={20} className="text-primary" />
          <h2 className="text-lg font-bold">{t("create.child.title")}</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Name */}
          <div>
            <label className="block text-sm font-semibold mb-1.5">
              {t("create.child.name")}{" "}
              <span className="text-muted-foreground font-normal">
                {t("create.child.name.optional")}
              </span>
            </label>
            <input
              type="text"
              className="w-full px-4 py-2.5 rounded-xl border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/30 transition"
              placeholder={t("create.child.name.placeholder")}
              value={book.child_name}
              onChange={(e) => updateBook({ child_name: e.target.value })}
            />
          </div>

          {/* Gender */}
          <div>
            <label className="block text-sm font-semibold mb-1.5">
              {t("create.child.gender")}
            </label>
            <div className="flex gap-2">
              {(
                [
                  ["boy", "create.child.gender.boy"],
                  ["girl", "create.child.gender.girl"],
                  ["unspecified", "create.child.gender.any"],
                ] as const
              ).map(([val, key]) => (
                <button
                  key={val}
                  type="button"
                  onClick={() => updateBook({ child_gender: val as Gender })}
                  className={`flex-1 py-2.5 rounded-xl text-sm font-semibold border transition ${
                    book.child_gender === val
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border hover:border-primary/40"
                  }`}
                >
                  {t(key)}
                </button>
              ))}
            </div>
          </div>

          {/* Age Range */}
          <div>
            <label className="block text-sm font-semibold mb-1.5">
              {t("create.child.age")}: {book.age_min} - {book.age_max}
            </label>
            <div className="flex items-center gap-3">
              <input
                type="range"
                min={3}
                max={12}
                value={book.age_min}
                onChange={(e) => {
                  const v = Number(e.target.value);
                  updateBook({
                    age_min: v,
                    age_max: Math.max(v, book.age_max),
                  });
                }}
                className="flex-1 accent-primary"
              />
              <span className="text-sm text-muted-foreground">
                {t("create.child.age.to")}
              </span>
              <input
                type="range"
                min={3}
                max={12}
                value={book.age_max}
                onChange={(e) => {
                  const v = Number(e.target.value);
                  updateBook({
                    age_max: v,
                    age_min: Math.min(v, book.age_min),
                  });
                }}
                className="flex-1 accent-primary"
              />
            </div>
          </div>

          {/* Language */}
          <div>
            <label className="block text-sm font-semibold mb-1.5">
              {t("create.child.lang")}
            </label>
            <div className="flex gap-2">
              {(
                [
                  ["en", "English"],
                  ["zh", "\u4e2d\u6587"],
                ] as const
              ).map(([val, label]) => (
                <button
                  key={val}
                  type="button"
                  onClick={() => updateBook({ language: val as Language })}
                  className={`flex-1 py-2.5 rounded-xl text-sm font-semibold border transition ${
                    book.language === val
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border hover:border-primary/40"
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </motion.section>

      {/* ====== Card B: Content ====== */}
      <motion.section
        className="card p-6"
        initial="hidden"
        animate="visible"
        custom={1}
        variants={cardVariants}
      >
        <div className="flex items-center gap-2 mb-5">
          <Palette size={20} className="text-secondary" />
          <h2 className="text-lg font-bold">{t("create.content.title")}</h2>
        </div>

        {/* Content mode tabs */}
        <div className="flex gap-1 mb-5 bg-muted p-1 rounded-xl">
          {(
            [
              ["topic", "create.content.topic.tab"],
              ["story", "create.content.story.tab"],
            ] as const
          ).map(([mode, key]) => (
            <button
              key={mode}
              type="button"
              onClick={() => updateBook({ content_mode: mode as ContentMode })}
              className={`flex-1 py-2 rounded-lg text-sm font-semibold transition ${
                book.content_mode === mode
                  ? "bg-card shadow text-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {t(key)}
            </button>
          ))}
        </div>

        {book.content_mode === "topic" ? (
          <>
            {/* Popular topics grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
              {POPULAR_TOPICS.map(({ icon: Icon, label, labelZh }) => {
                const value = label;
                const selected = book.topic === value;
                return (
                  <button
                    key={label}
                    type="button"
                    onClick={() => updateBook({ topic: value })}
                    className={`flex flex-col items-center gap-2 py-4 rounded-2xl border transition ${
                      selected
                        ? "border-primary bg-primary/10 text-primary"
                        : "border-border hover:border-primary/40 hover:bg-muted"
                    }`}
                  >
                    <Icon size={24} />
                    <span className="text-sm font-semibold">
                      {isZh ? labelZh : label}
                    </span>
                  </button>
                );
              })}
            </div>

            {/* Free-form topic input */}
            <div>
              <label className="block text-sm font-semibold mb-1.5">
                {t("create.content.topic.custom")}
              </label>
              <input
                type="text"
                className="w-full px-4 py-2.5 rounded-xl border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/30 transition"
                placeholder={t("create.content.topic.placeholder")}
                value={
                  POPULAR_TOPICS.some((tp) => tp.label === book.topic)
                    ? ""
                    : book.topic
                }
                onChange={(e) => updateBook({ topic: e.target.value })}
              />
            </div>
          </>
        ) : (
          /* Story mode: text area */
          <div>
            <label className="block text-sm font-semibold mb-1.5">
              {t("create.content.story.label")}
            </label>
            <textarea
              className="w-full px-4 py-3 rounded-xl border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/30 transition min-h-[160px] resize-y"
              placeholder={t("create.content.story.placeholder")}
              value={book.story_text}
              onChange={(e) => updateBook({ story_text: e.target.value })}
            />
          </div>
        )}

        {/* Chapters */}
        <div className="mt-5">
          <label className="block text-sm font-semibold mb-1.5">
            {t("create.content.chapters")}: {book.chapters}
          </label>
          <input
            type="range"
            min={3}
            max={10}
            value={book.chapters}
            onChange={(e) => updateBook({ chapters: Number(e.target.value) })}
            className="w-full accent-primary"
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            <span>{t("create.content.chapters.short")}</span>
            <span>{t("create.content.chapters.detailed")}</span>
          </div>
        </div>
      </motion.section>

      {/* ====== Card C: Output Products ====== */}
      <motion.section
        className="card p-6"
        initial="hidden"
        animate="visible"
        custom={2}
        variants={cardVariants}
      >
        <div className="flex items-center gap-2 mb-2">
          <Package size={20} className="text-accent" />
          <h2 className="text-lg font-bold">{t("create.products.title")}</h2>
        </div>
        <p className="text-sm text-muted-foreground mb-5">
          {t("create.products.desc")}
        </p>

        <div className="space-y-3">
          {PRODUCT_KEYS.map(({ type, icon: Icon }) => {
            const selected = book.products.includes(type);
            const expanded = expandedProduct === type;
            return (
              <div
                key={type}
                className={`border rounded-2xl transition ${
                  selected ? "border-primary bg-primary/5" : "border-border"
                }`}
              >
                {/* Product toggle row */}
                <div className="flex items-center gap-3 px-4 py-3">
                  <button
                    type="button"
                    onClick={() => toggleProduct(type)}
                    className={`w-6 h-6 rounded-lg border-2 flex items-center justify-center transition ${
                      selected
                        ? "border-primary bg-primary text-white"
                        : "border-border"
                    }`}
                  >
                    {selected && (
                      <svg width="14" height="14" viewBox="0 0 14 14">
                        <path
                          d="M3 7l3 3 5-5"
                          stroke="currentColor"
                          strokeWidth="2"
                          fill="none"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    )}
                  </button>
                  <Icon size={20} className="text-muted-foreground" />
                  <div className="flex-1">
                    <span className="font-semibold text-sm">
                      {t(`product.${type}`)}
                    </span>
                    <span className="text-muted-foreground text-xs ml-2">
                      {t(`product.${type}.desc`)}
                    </span>
                  </div>
                  {/* Expand options */}
                  {selected &&
                    ["slides", "video", "audio", "infographic", "quiz"].includes(
                      type,
                    ) && (
                      <button
                        type="button"
                        onClick={() =>
                          setExpandedProduct(expanded ? null : type)
                        }
                        className="text-muted-foreground hover:text-foreground transition"
                      >
                        <ChevronDown
                          size={18}
                          className={`transition-transform ${expanded ? "rotate-180" : ""}`}
                        />
                      </button>
                    )}
                </div>

                {/* Expanded options */}
                {selected && expanded && (
                  <div className="px-4 pb-4 pt-1 border-t border-border/50">
                    <ProductOptionsPanel
                      type={type}
                      opts={opts}
                      setOpts={setOpts}
                    />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </motion.section>

      {/* ====== Error ====== */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
          {error}
        </div>
      )}

      {/* ====== Submit ====== */}
      <div className="flex justify-center pt-2">
        <button
          type="button"
          onClick={handleSubmit}
          disabled={submitting}
          className="btn-primary text-lg px-12 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {submitting ? t("create.submitting") : t("create.submit")}
        </button>
      </div>
    </div>
  );
}

// === Product-specific options panels ===

function ProductOptionsPanel({
  type,
  opts,
  setOpts,
}: {
  type: ProductType;
  opts: ProductOptions;
  setOpts: React.Dispatch<React.SetStateAction<ProductOptions>>;
}) {
  const t = useT();
  const selectClass =
    "px-3 py-2 rounded-lg border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30";

  if (type === "slides") {
    return (
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold mb-1">
            {t("option.format")}
          </label>
          <select
            className={selectClass}
            value={opts.slides.slide_format}
            onChange={(e) =>
              setOpts((p) => ({
                ...p,
                slides: {
                  ...p.slides,
                  slide_format: e.target.value as SlidesFormat,
                },
              }))
            }
          >
            <option value="detailed">{t("option.detailed")}</option>
            <option value="presenter">{t("option.presenter")}</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-semibold mb-1">
            {t("option.length")}
          </label>
          <select
            className={selectClass}
            value={opts.slides.slide_length}
            onChange={(e) =>
              setOpts((p) => ({
                ...p,
                slides: {
                  ...p.slides,
                  slide_length: e.target.value as SlidesLength,
                },
              }))
            }
          >
            <option value="default">{t("option.default")}</option>
            <option value="short">{t("option.short")}</option>
          </select>
        </div>
      </div>
    );
  }

  if (type === "video") {
    return (
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold mb-1">
            {t("option.style")}
          </label>
          <select
            className={selectClass}
            value={opts.video.video_style}
            onChange={(e) =>
              setOpts((p) => ({
                ...p,
                video: {
                  ...p.video,
                  video_style: e.target.value as VideoStyle,
                },
              }))
            }
          >
            {(
              [
                "kawaii",
                "watercolor",
                "anime",
                "paper_craft",
                "classic",
                "whiteboard",
                "heritage",
                "retro_print",
                "auto",
              ] as const
            ).map((s) => (
              <option key={s} value={s}>
                {t(`video.${s}`)}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-semibold mb-1">
            {t("option.format")}
          </label>
          <select
            className={selectClass}
            value={opts.video.video_format}
            onChange={(e) =>
              setOpts((p) => ({
                ...p,
                video: {
                  ...p.video,
                  video_format: e.target.value as "explainer" | "brief",
                },
              }))
            }
          >
            <option value="explainer">{t("option.explainer")}</option>
            <option value="brief">{t("option.brief")}</option>
          </select>
        </div>
      </div>
    );
  }

  if (type === "audio") {
    return (
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold mb-1">
            {t("option.format")}
          </label>
          <select
            className={selectClass}
            value={opts.audio.audio_format}
            onChange={(e) =>
              setOpts((p) => ({
                ...p,
                audio: {
                  ...p.audio,
                  audio_format: e.target.value as AudioFormat,
                },
              }))
            }
          >
            <option value="deep_dive">{t("option.deep_dive")}</option>
            <option value="brief">{t("option.brief")}</option>
            <option value="critique">{t("option.critique")}</option>
            <option value="debate">{t("option.debate")}</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-semibold mb-1">
            {t("option.length")}
          </label>
          <select
            className={selectClass}
            value={opts.audio.audio_length}
            onChange={(e) =>
              setOpts((p) => ({
                ...p,
                audio: {
                  ...p.audio,
                  audio_length: e.target.value as AudioLength,
                },
              }))
            }
          >
            <option value="short">{t("audio.short")}</option>
            <option value="default">{t("audio.default")}</option>
            <option value="long">{t("audio.long")}</option>
          </select>
        </div>
      </div>
    );
  }

  if (type === "infographic") {
    return (
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold mb-1">
            {t("option.orientation")}
          </label>
          <select
            className={selectClass}
            value={opts.infographic.orientation}
            onChange={(e) =>
              setOpts((p) => ({
                ...p,
                infographic: {
                  ...p.infographic,
                  orientation: e.target.value as InfographicOrientation,
                },
              }))
            }
          >
            <option value="landscape">{t("option.landscape")}</option>
            <option value="portrait">{t("option.portrait")}</option>
            <option value="square">{t("option.square")}</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-semibold mb-1">
            {t("option.detail")}
          </label>
          <select
            className={selectClass}
            value={opts.infographic.detail_level}
            onChange={(e) =>
              setOpts((p) => ({
                ...p,
                infographic: {
                  ...p.infographic,
                  detail_level: e.target.value as InfographicDetail,
                },
              }))
            }
          >
            <option value="concise">{t("option.concise")}</option>
            <option value="standard">{t("option.standard")}</option>
            <option value="detailed">{t("option.detailed")}</option>
          </select>
        </div>
      </div>
    );
  }

  if (type === "quiz") {
    return (
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold mb-1">
            {t("option.difficulty")}
          </label>
          <select
            className={selectClass}
            value={opts.quiz.difficulty}
            onChange={(e) =>
              setOpts((p) => ({
                ...p,
                quiz: {
                  ...p.quiz,
                  difficulty: e.target.value as QuizDifficulty,
                },
              }))
            }
          >
            <option value="easy">{t("option.easy")}</option>
            <option value="medium">{t("option.medium")}</option>
            <option value="hard">{t("option.hard")}</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-semibold mb-1">
            {t("option.quantity")}
          </label>
          <select
            className={selectClass}
            value={opts.quiz.quantity}
            onChange={(e) =>
              setOpts((p) => ({
                ...p,
                quiz: {
                  ...p.quiz,
                  quantity: e.target.value as "fewer" | "standard",
                },
              }))
            }
          >
            <option value="fewer">{t("option.fewer")}</option>
            <option value="standard">{t("option.standard")}</option>
          </select>
        </div>
      </div>
    );
  }

  return null;
}

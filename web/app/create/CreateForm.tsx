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

// === Popular topics ===

const POPULAR_TOPICS = [
  { icon: Rocket, label: "Space", labelZh: "太空" },
  { icon: Fish, label: "Ocean", labelZh: "海洋" },
  { icon: Bug, label: "Dinosaurs", labelZh: "恐龙" },
  { icon: TreePine, label: "Animals", labelZh: "动物" },
  { icon: FlaskConical, label: "Science", labelZh: "科学实验" },
  { icon: Crown, label: "Fairy Tales", labelZh: "童话故事" },
  { icon: Globe, label: "Geography", labelZh: "地理" },
  { icon: Sparkles, label: "Magic", labelZh: "魔法世界" },
];

// === Product definitions ===

const PRODUCT_DEFS: {
  type: ProductType;
  icon: typeof Monitor;
  label: string;
  desc: string;
}[] = [
  {
    type: "slides",
    icon: Monitor,
    label: "Slides",
    desc: "Presentation deck",
  },
  { type: "video", icon: Film, label: "Video", desc: "Animated video" },
  {
    type: "audio",
    icon: Headphones,
    label: "Audio",
    desc: "Podcast-style story",
  },
  {
    type: "infographic",
    icon: Image,
    label: "Infographic",
    desc: "Visual poster",
  },
  { type: "quiz", icon: HelpCircle, label: "Quiz", desc: "Knowledge check" },
  {
    type: "flashcards",
    icon: Layers,
    label: "Flashcards",
    desc: "Study cards",
  },
  {
    type: "mind_map",
    icon: BrainCircuit,
    label: "Mind Map",
    desc: "Topic overview",
  },
];

// === Video style options ===

const VIDEO_STYLES: { value: VideoStyle; label: string }[] = [
  { value: "kawaii", label: "Kawaii (Cute)" },
  { value: "watercolor", label: "Watercolor" },
  { value: "anime", label: "Anime" },
  { value: "paper_craft", label: "Paper Craft" },
  { value: "classic", label: "Classic" },
  { value: "whiteboard", label: "Whiteboard" },
  { value: "heritage", label: "Heritage" },
  { value: "retro_print", label: "Retro Print" },
  { value: "auto", label: "Auto" },
];

export default function CreateForm() {
  const router = useRouter();
  const [book, setBook] = useState<GenerateRequest>({
    ...DEFAULT_BOOK_REQUEST,
  });
  const [opts, setOpts] = useState<ProductOptions>({
    ...DEFAULT_PRODUCT_OPTIONS,
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [expandedProduct, setExpandedProduct] = useState<string | null>(null);

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

    // Client-side validation
    if (book.content_mode === "topic" && !book.topic.trim()) {
      setError("Please select or enter a topic.");
      return;
    }
    if (book.content_mode === "story" && !book.story_text.trim()) {
      setError("Please enter your story text.");
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

  const isZh = book.language === "zh";

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      {/* ====== Card A: About Your Child ====== */}
      <section className="card p-6">
        <div className="flex items-center gap-2 mb-5">
          <User size={20} className="text-primary" />
          <h2 className="text-lg font-bold">About Your Child</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Name */}
          <div>
            <label className="block text-sm font-semibold mb-1.5">
              Nickname{" "}
              <span className="text-muted-foreground font-normal">
                (optional)
              </span>
            </label>
            <input
              type="text"
              className="w-full px-4 py-2.5 rounded-xl border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/30 transition"
              placeholder="e.g. Luna"
              value={book.child_name}
              onChange={(e) => updateBook({ child_name: e.target.value })}
            />
          </div>

          {/* Gender */}
          <div>
            <label className="block text-sm font-semibold mb-1.5">
              Gender
            </label>
            <div className="flex gap-2">
              {(
                [
                  ["boy", "Boy"],
                  ["girl", "Girl"],
                  ["unspecified", "Any"],
                ] as const
              ).map(([val, label]) => (
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
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Age Range */}
          <div>
            <label className="block text-sm font-semibold mb-1.5">
              Age Range: {book.age_min} - {book.age_max}
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
              <span className="text-sm text-muted-foreground">to</span>
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
              Language
            </label>
            <div className="flex gap-2">
              {(
                [
                  ["en", "English"],
                  ["zh", "中文"],
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
      </section>

      {/* ====== Card B: Content ====== */}
      <section className="card p-6">
        <div className="flex items-center gap-2 mb-5">
          <Palette size={20} className="text-secondary" />
          <h2 className="text-lg font-bold">Content</h2>
        </div>

        {/* Content mode tabs */}
        <div className="flex gap-1 mb-5 bg-muted p-1 rounded-xl">
          {(
            [
              ["topic", "Choose a Topic"],
              ["story", "Tell Your Own Story"],
            ] as const
          ).map(([mode, label]) => (
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
              {label}
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
                Or enter your own topic
              </label>
              <input
                type="text"
                className="w-full px-4 py-2.5 rounded-xl border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/30 transition"
                placeholder={
                  isZh ? "例如：中国历史、恐龙、外太空" : "e.g. Volcanoes, Robots, Pirates"
                }
                value={
                  POPULAR_TOPICS.some((t) => t.label === book.topic)
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
              Your Story
            </label>
            <textarea
              className="w-full px-4 py-3 rounded-xl border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/30 transition min-h-[160px] resize-y"
              placeholder={
                isZh
                  ? "在这里输入或粘贴你的故事，AI 会帮你润色并适配孩子的年龄段..."
                  : "Paste or type your story here. AI will adapt it for your child's age..."
              }
              value={book.story_text}
              onChange={(e) => updateBook({ story_text: e.target.value })}
            />
          </div>
        )}

        {/* Chapters */}
        <div className="mt-5">
          <label className="block text-sm font-semibold mb-1.5">
            Chapters: {book.chapters}
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
            <span>3 (short)</span>
            <span>10 (detailed)</span>
          </div>
        </div>
      </section>

      {/* ====== Card C: Output Products ====== */}
      <section className="card p-6">
        <div className="flex items-center gap-2 mb-2">
          <Package size={20} className="text-accent" />
          <h2 className="text-lg font-bold">Output Products</h2>
        </div>
        <p className="text-sm text-muted-foreground mb-5">
          Select what to generate. Each product is created via NotebookLM.
        </p>

        <div className="space-y-3">
          {PRODUCT_DEFS.map(({ type, icon: Icon, label, desc }) => {
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
                    <span className="font-semibold text-sm">{label}</span>
                    <span className="text-muted-foreground text-xs ml-2">
                      {desc}
                    </span>
                  </div>
                  {/* Expand options (only for types with options) */}
                  {selected &&
                    ["slides", "video", "audio", "infographic", "quiz"].includes(
                      type
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
      </section>

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
          {submitting ? "Creating..." : "Create Picture Book"}
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
  const selectClass =
    "px-3 py-2 rounded-lg border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30";

  if (type === "slides") {
    return (
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold mb-1">Format</label>
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
            <option value="detailed">Detailed</option>
            <option value="presenter">Presenter</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-semibold mb-1">Length</label>
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
            <option value="default">Default</option>
            <option value="short">Short</option>
          </select>
        </div>
      </div>
    );
  }

  if (type === "video") {
    return (
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold mb-1">Style</label>
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
            {VIDEO_STYLES.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-semibold mb-1">Format</label>
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
            <option value="explainer">Explainer</option>
            <option value="brief">Brief</option>
          </select>
        </div>
      </div>
    );
  }

  if (type === "audio") {
    return (
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold mb-1">Format</label>
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
            <option value="deep_dive">Deep Dive</option>
            <option value="brief">Brief</option>
            <option value="critique">Critique</option>
            <option value="debate">Debate</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-semibold mb-1">Length</label>
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
            <option value="short">Short (~5 min)</option>
            <option value="default">Default (~15 min)</option>
            <option value="long">Long (~25 min)</option>
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
            Orientation
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
            <option value="landscape">Landscape</option>
            <option value="portrait">Portrait</option>
            <option value="square">Square</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-semibold mb-1">Detail</label>
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
            <option value="concise">Concise</option>
            <option value="standard">Standard</option>
            <option value="detailed">Detailed</option>
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
            Difficulty
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
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-semibold mb-1">Quantity</label>
          <select
            className={selectClass}
            value={opts.quiz.quantity}
            onChange={(e) =>
              setOpts((p) => ({
                ...p,
                quiz: { ...p.quiz, quantity: e.target.value as "fewer" | "standard" },
              }))
            }
          >
            <option value="fewer">Fewer</option>
            <option value="standard">Standard</option>
          </select>
        </div>
      </div>
    );
  }

  return null;
}

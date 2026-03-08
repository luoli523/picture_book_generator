// API types matching backend schemas + fetch utilities

// === Enums ===

export type Language = "zh" | "en";
export type Gender = "boy" | "girl" | "unspecified";
export type ContentMode = "topic" | "story";
export type LLMProvider = "anthropic" | "openai" | "gemini" | "grok";

export type ProductType =
  | "slides"
  | "video"
  | "audio"
  | "infographic"
  | "quiz"
  | "flashcards"
  | "mind_map";

export type SlidesFormat = "detailed" | "presenter";
export type SlidesLength = "default" | "short";
export type VideoStyle =
  | "auto"
  | "classic"
  | "whiteboard"
  | "kawaii"
  | "anime"
  | "watercolor"
  | "retro_print"
  | "heritage"
  | "paper_craft";
export type VideoFormat = "explainer" | "brief";
export type AudioFormat = "deep_dive" | "brief" | "critique" | "debate";
export type AudioLength = "short" | "default" | "long";
export type InfographicOrientation = "landscape" | "portrait" | "square";
export type InfographicDetail = "concise" | "standard" | "detailed";
export type QuizDifficulty = "easy" | "medium" | "hard";
export type QuizQuantity = "fewer" | "standard";

// === Request types ===

export interface GenerateRequest {
  child_name: string;
  child_gender: Gender;
  age_min: number;
  age_max: number;
  language: Language;
  content_mode: ContentMode;
  topic: string;
  story_text: string;
  chapters: number;
  llm_provider: LLMProvider | null;
  custom_instructions: string;
  products: ProductType[];
}

export interface ProductOptions {
  slides: { slide_format: SlidesFormat; slide_length: SlidesLength };
  video: { video_style: VideoStyle; video_format: VideoFormat };
  audio: { audio_format: AudioFormat; audio_length: AudioLength };
  infographic: {
    orientation: InfographicOrientation;
    detail_level: InfographicDetail;
  };
  quiz: { difficulty: QuizDifficulty; quantity: QuizQuantity };
}

export interface GenerateFullRequest {
  book: GenerateRequest;
  product_options: ProductOptions;
}

// === Response types ===

export interface GenerateResponse {
  job_id: string;
  status: string;
}

export interface SSEEvent {
  type: string;
  message: string;
  data?: Record<string, unknown>;
}

export interface BookResult {
  title: string;
  topic: string;
  language: string;
  markdown_path: string;
  markdown_content: string;
}

export interface ProductResult {
  product_type: ProductType;
  status: string; // "pending" | "generating" | "completed" | "failed"
  file_path: string | null;
  error: string | null;
}

export interface JobStatus {
  job_id: string;
  status: string; // "generating_book" | "generating_products" | "completed" | "failed"
  book: BookResult | null;
  products: ProductResult[];
  error: string | null;
}

// === Defaults ===

export const DEFAULT_BOOK_REQUEST: GenerateRequest = {
  child_name: "",
  child_gender: "unspecified",
  age_min: 7,
  age_max: 10,
  language: "en",
  content_mode: "topic",
  topic: "",
  story_text: "",
  chapters: 5,
  llm_provider: null,
  custom_instructions: "",
  products: ["slides"],
};

export const DEFAULT_PRODUCT_OPTIONS: ProductOptions = {
  slides: { slide_format: "detailed", slide_length: "default" },
  video: { video_style: "kawaii", video_format: "explainer" },
  audio: { audio_format: "deep_dive", audio_length: "default" },
  infographic: { orientation: "landscape", detail_level: "standard" },
  quiz: { difficulty: "easy", quantity: "standard" },
};

// === API functions ===

export async function createGeneration(
  request: GenerateFullRequest
): Promise<GenerateResponse> {
  const res = await fetch("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Failed to create generation");
  }
  return res.json();
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const res = await fetch(`/api/generate/${jobId}/status`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Failed to fetch job status");
  }
  return res.json();
}

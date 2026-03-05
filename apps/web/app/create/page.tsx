"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type ApiTask = {
  task_id: string;
  book_id: string;
  status: "queued" | "running" | "succeeded" | "failed";
  stage: string;
  progress: number;
  message: string;
  error?: string | null;
};

type ApiBook = {
  book_id: string;
  title: string;
  topic: string;
  language: "zh" | "en" | "ja" | "ko";
  age_group: "3-5" | "6-8" | "9-12";
  style_theme: "ocean_pop" | "sunny_story" | "forest_sketch" | "space_quest";
  markdown_path?: string | null;
  slides_pdf_path?: string | null;
  slides_error?: string | null;
};

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export default function CreatePage() {
  const [ageGroup, setAgeGroup] = useState<"3-5" | "6-8" | "9-12">("6-8");
  const [gender, setGender] = useState<"unspecified" | "girl" | "boy">("unspecified");
  const [readingLevel, setReadingLevel] = useState<"beginner" | "basic" | "advanced">("basic");
  const [interests, setInterests] = useState("ocean, plants");
  const [mode, setMode] = useState<"topic" | "parent_story" | "hybrid">("topic");
  const [topic, setTopic] = useState("珊瑚礁探险");
  const [parentStory, setParentStory] = useState("");
  const [themeId, setThemeId] = useState<
    "ocean_pop" | "sunny_story" | "forest_sketch" | "space_quest"
  >("ocean_pop");
  const [tone, setTone] = useState<"exploratory" | "gentle" | "playful" | "informative">(
    "exploratory"
  );
  const [educationGoal, setEducationGoal] = useState<"science" | "habits" | "emotion" | "bedtime">(
    "science"
  );
  const [language, setLanguage] = useState<"zh" | "en" | "ja" | "ko">("zh");
  const [chapters, setChapters] = useState(6);
  const [chapterLength, setChapterLength] = useState<"short" | "medium" | "long">("medium");
  const [includeIllustrations, setIncludeIllustrations] = useState(true);
  const [generateSlides, setGenerateSlides] = useState(true);

  const [submitting, setSubmitting] = useState(false);
  const [task, setTask] = useState<ApiTask | null>(null);
  const [book, setBook] = useState<ApiBook | null>(null);
  const [requestError, setRequestError] = useState("");

  const taskDone = task?.status === "succeeded" || task?.status === "failed";
  const canDownload = task?.status === "succeeded" && !!book;

  const interestsList = useMemo(
    () =>
      interests
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
    [interests]
  );

  useEffect(() => {
    if (!task || taskDone) {
      return;
    }

    const timer = window.setInterval(async () => {
      const res = await fetch(`${API_BASE}/api/v1/tasks/${task.task_id}`);
      if (!res.ok) {
        return;
      }
      const nextTask: ApiTask = await res.json();
      setTask(nextTask);
      if (nextTask.status === "succeeded") {
        const bookRes = await fetch(`${API_BASE}/api/v1/books/${nextTask.book_id}`);
        if (bookRes.ok) {
          const nextBook: ApiBook = await bookRes.json();
          setBook(nextBook);
        }
      }
    }, 1500);

    return () => window.clearInterval(timer);
  }, [task, taskDone]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setRequestError("");
    setBook(null);
    setTask(null);

    try {
      const payload = {
        child_profile: {
          age_group: ageGroup,
          gender,
          reading_level: readingLevel,
          interests: interestsList,
        },
        content_source: {
          mode,
          topic,
          parent_story: parentStory,
        },
        style: {
          theme_id: themeId,
          tone,
          education_goal: educationGoal,
        },
        book_config: {
          language,
          chapters,
          chapter_length: chapterLength,
          include_illustrations: includeIllustrations,
          generate_slides: generateSlides,
        },
      };

      const res = await fetch(`${API_BASE}/api/v1/books`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`请求失败: ${res.status} ${text}`);
      }

      const data: { task_id: string; book_id: string; status: "queued" } = await res.json();
      setTask({
        task_id: data.task_id,
        book_id: data.book_id,
        status: "queued",
        stage: "prepare_context",
        progress: 0,
        message: "任务已提交",
      });
    } catch (err) {
      setRequestError(err instanceof Error ? err.message : "提交失败");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="page-shell">
      <section className="hero">
        <h1>绘本工坊 /create</h1>
        <p>提交后会创建异步任务，右侧状态卡会持续显示生成进度。</p>
      </section>

      <div className="grid-2">
        <form className="card" onSubmit={handleSubmit}>
          <h2 className="section-title">生成参数</h2>

          <div className="grid-3">
            <div>
              <label className="label">年龄段</label>
              <select value={ageGroup} onChange={(e) => setAgeGroup(e.target.value as typeof ageGroup)}>
                <option value="3-5">3-5</option>
                <option value="6-8">6-8</option>
                <option value="9-12">9-12</option>
              </select>
            </div>
            <div>
              <label className="label">性别</label>
              <select value={gender} onChange={(e) => setGender(e.target.value as typeof gender)}>
                <option value="unspecified">不限定</option>
                <option value="girl">女孩</option>
                <option value="boy">男孩</option>
              </select>
            </div>
            <div>
              <label className="label">阅读能力</label>
              <select
                value={readingLevel}
                onChange={(e) => setReadingLevel(e.target.value as typeof readingLevel)}
              >
                <option value="beginner">启蒙</option>
                <option value="basic">基础</option>
                <option value="advanced">进阶</option>
              </select>
            </div>
          </div>

          <div style={{ marginTop: 10 }}>
            <label className="label">兴趣（逗号分隔）</label>
            <input value={interests} onChange={(e) => setInterests(e.target.value)} />
          </div>

          <div className="grid-3" style={{ marginTop: 10 }}>
            <div>
              <label className="label">来源模式</label>
              <select value={mode} onChange={(e) => setMode(e.target.value as typeof mode)}>
                <option value="topic">主题生成</option>
                <option value="parent_story">家长故事改写</option>
                <option value="hybrid">主题 + 家长故事</option>
              </select>
            </div>
            <div>
              <label className="label">风格</label>
              <select value={themeId} onChange={(e) => setThemeId(e.target.value as typeof themeId)}>
                <option value="ocean_pop">Ocean Pop</option>
                <option value="sunny_story">Sunny Story</option>
                <option value="forest_sketch">Forest Sketch</option>
                <option value="space_quest">Space Quest</option>
              </select>
            </div>
            <div>
              <label className="label">教育目标</label>
              <select
                value={educationGoal}
                onChange={(e) => setEducationGoal(e.target.value as typeof educationGoal)}
              >
                <option value="science">科学知识</option>
                <option value="habits">行为习惯</option>
                <option value="emotion">情绪认知</option>
                <option value="bedtime">睡前安抚</option>
              </select>
            </div>
          </div>

          <div style={{ marginTop: 10 }}>
            <label className="label">主题</label>
            <input value={topic} onChange={(e) => setTopic(e.target.value)} />
          </div>

          <div style={{ marginTop: 10 }}>
            <label className="label">家长故事草稿</label>
            <textarea value={parentStory} onChange={(e) => setParentStory(e.target.value)} />
          </div>

          <div className="grid-3" style={{ marginTop: 10 }}>
            <div>
              <label className="label">语言</label>
              <select value={language} onChange={(e) => setLanguage(e.target.value as typeof language)}>
                <option value="zh">zh</option>
                <option value="en">en</option>
                <option value="ja">ja</option>
                <option value="ko">ko</option>
              </select>
            </div>
            <div>
              <label className="label">章节数（3-10）</label>
              <input
                type="number"
                min={3}
                max={10}
                value={chapters}
                onChange={(e) => setChapters(Number(e.target.value))}
              />
            </div>
            <div>
              <label className="label">章节长度</label>
              <select
                value={chapterLength}
                onChange={(e) => setChapterLength(e.target.value as typeof chapterLength)}
              >
                <option value="short">short</option>
                <option value="medium">medium</option>
                <option value="long">long</option>
              </select>
            </div>
          </div>

          <div className="grid-2" style={{ marginTop: 10 }}>
            <label className="muted">
              <input
                type="checkbox"
                checked={includeIllustrations}
                onChange={(e) => setIncludeIllustrations(e.target.checked)}
                style={{ width: "auto", marginRight: 6 }}
              />
              生成插图提示词
            </label>

            <label className="muted">
              <input
                type="checkbox"
                checked={generateSlides}
                onChange={(e) => setGenerateSlides(e.target.checked)}
                style={{ width: "auto", marginRight: 6 }}
              />
              生成 NotebookLM Slides（默认开启）
            </label>
          </div>

          <div style={{ marginTop: 14 }}>
            <button className="btn" disabled={submitting} type="submit">
              {submitting ? "提交中..." : "创建生成任务"}
            </button>
          </div>

          {requestError ? (
            <p className="muted" style={{ color: "#b02020", marginTop: 8 }}>
              {requestError}
            </p>
          ) : null}
        </form>

        <section className="card">
          <h2 className="section-title">任务状态</h2>
          {!task ? <p className="muted">尚未创建任务。</p> : null}

          {task ? (
            <>
              <p className="muted">
                task: <code>{task.task_id}</code>
                <br />
                book: <code>{task.book_id}</code>
              </p>
              <p className="muted">
                状态：{task.status} / 阶段：{task.stage}
              </p>
              <div className="progress">
                <div style={{ width: `${task.progress}%` }} />
              </div>
              <p className="muted" style={{ marginTop: 6 }}>
                {task.progress}% · {task.message}
              </p>
              {task.error ? (
                <p className="muted" style={{ color: "#b02020" }}>
                  {task.error}
                </p>
              ) : null}
            </>
          ) : null}

          {canDownload && book ? (
            <div style={{ marginTop: 14 }}>
              <p className="muted">
                <strong>{book.title}</strong>
                <br />
                主题：{book.topic}
              </p>
              <div className="grid-2">
                <a
                  className="btn"
                  href={`${API_BASE}/api/v1/books/${book.book_id}/download?type=md`}
                  target="_blank"
                  rel="noreferrer"
                >
                  下载 Markdown
                </a>
                <a
                  className="btn"
                  href={`${API_BASE}/api/v1/books/${book.book_id}/download?type=pdf`}
                  target="_blank"
                  rel="noreferrer"
                  style={{ textAlign: "center" }}
                >
                  下载 Slides PDF
                </a>
              </div>
              {book.slides_error ? (
                <p className="muted" style={{ marginTop: 8, color: "#9a5a00" }}>
                  Slides 生成异常：{book.slides_error}
                </p>
              ) : null}
            </div>
          ) : null}
        </section>
      </div>
    </main>
  );
}

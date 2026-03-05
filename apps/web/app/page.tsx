import Link from "next/link";

export default function HomePage() {
  return (
    <main className="page-shell">
      <section className="hero">
        <h1>Picture Book Studio · Ocean Pop</h1>
        <p>
          面向有孩子的家庭，按年龄段、主题和故事风格定制专属绘本。MVP
          版本已支持任务创建、进度追踪和成品下载。
        </p>
      </section>

      <section className="card">
        <h2 className="section-title">开始体验</h2>
        <p className="muted">
          进入绘本工坊，填写孩子画像和故事来源，提交后可实时查看生成进度。
        </p>
        <p>
          <Link href="/create">前往 /create</Link>
        </p>
      </section>
    </main>
  );
}


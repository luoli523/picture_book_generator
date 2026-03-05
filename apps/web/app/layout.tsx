import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Picture Book Studio",
  description: "为孩子生成专属儿童绘本",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}


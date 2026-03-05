import type { Metadata } from "next";
import { Nunito } from "next/font/google";
import "./globals.css";

const nunito = Nunito({
  variable: "--font-nunito",
  subsets: ["latin"],
  weight: ["400", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "StoryBook Workshop - Create Picture Books for Your Kids",
  description:
    "AI-powered picture book generator for children. Create personalized, educational stories tailored to your child's age and interests.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh">
      <body className={`${nunito.variable} antialiased`}>{children}</body>
    </html>
  );
}

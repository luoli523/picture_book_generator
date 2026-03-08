import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Disable compression so SSE streams are not gzip-buffered
  compress: false,
  // Proxy API requests to FastAPI backend during development
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*",
      },
      {
        source: "/files/:path*",
        destination: "http://127.0.0.1:8000/files/:path*",
      },
    ];
  },
};

export default nextConfig;

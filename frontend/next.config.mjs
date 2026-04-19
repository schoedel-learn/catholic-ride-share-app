/** @type {import('next').NextConfig} */
const isGithubPages = process.env.GITHUB_PAGES === "true";

const nextConfig = {
  reactStrictMode: true,
  output: isGithubPages ? "export" : "standalone",
  // Required for GitHub Pages: paths are served under /repo-name/
  ...(isGithubPages && {
    basePath: "/catholic-ride-share-app",
    trailingSlash: true,
  }),
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;

/** @type {import('next').NextConfig} */
const isGithubPages = process.env.GITHUB_PAGES === "true";

const nextConfig = {
  reactStrictMode: true,
  output: isGithubPages ? "export" : "standalone",
  basePath: isGithubPages ? "/catholic-ride-share-app" : "",
  assetPrefix: isGithubPages ? "/catholic-ride-share-app" : "",
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;

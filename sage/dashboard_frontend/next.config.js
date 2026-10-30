/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/v1/:path*',
        destination: `${backendUrl}/api/v1/:path*`,
      },
      {
        source: '/runs/:path*',
        destination: `${backendUrl}/runs/:path*`,
      },
      {
        source: '/runs',
        destination: `${backendUrl}/runs`,
      },
      {
        source: '/audit/:path*',
        destination: `${backendUrl}/audit/:path*`,
      },
      {
        source: '/leaderboard',
        destination: `${backendUrl}/leaderboard`,
      },
      {
        source: '/redteam/:path*',
        destination: `${backendUrl}/redteam/:path*`,
      },
      {
        source: '/telemetry/:path*',
        destination: `${backendUrl}/telemetry/:path*`,
      },
      {
        source: '/backend-health',
        destination: `${backendUrl}/health`,
      },
    ];
  },
};

module.exports = nextConfig;

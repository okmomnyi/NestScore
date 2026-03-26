/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.INTERNAL_API_BASE_URL || 'http://nestscore_backend:8000'}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;

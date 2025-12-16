/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable experimental features if needed
  experimental: {},
  // Ignore TypeScript errors during build (for faster iteration)
  typescript: {
    ignoreBuildErrors: false,
  },
}

module.exports = nextConfig

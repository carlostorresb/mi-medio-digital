/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  experimental: {
    serverComponentsExternalPackages: [],
  },
}

module.exports = nextConfig

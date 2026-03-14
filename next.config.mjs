/** @type {import('next').NextConfig} */
const nextConfig = {
  // React's Strict Mode is a development-only feature that helps find common bugs.
  reactStrictMode: true,

  // Redirects API requests in development to the Flask backend.
  // This avoids CORS issues and simplifies API calls.
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:5001/api/:path*', // Proxy to Backend
      },
    ]
  },

  // Optional: Disable 'x-powered-by' header for security.
  poweredByHeader: false,
};

export default nextConfig;

import type { Metadata } from 'next';
import { Toaster } from 'sonner';
import './globals.css';

export const metadata: Metadata = {
  title: 'Smart Gallery | AI-Powered Photo Organizer',
  description: 'Intelligent photo gallery with face recognition, object detection, and semantic search powered by YOLO, InsightFace, and CLIP.',
  keywords: ['photo gallery', 'AI', 'face recognition', 'object detection', 'CLIP', 'YOLO'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-gallery-bg text-gallery-text antialiased">
        <div className="relative min-h-screen">
          {/* Background effects */}
          <div className="fixed inset-0 grid-pattern pointer-events-none" />
          <div className="fixed inset-0 noise-overlay pointer-events-none" />
          
          {/* Gradient orbs */}
          <div className="fixed top-0 left-1/4 w-[600px] h-[600px] bg-orange-500/5 rounded-full blur-[120px] pointer-events-none" />
          <div className="fixed bottom-0 right-1/4 w-[400px] h-[400px] bg-orange-500/3 rounded-full blur-[100px] pointer-events-none" />
          
          {/* Content */}
          <div className="relative z-10">
            {children}
          </div>
        </div>
        
        <Toaster 
          position="bottom-right"
          toastOptions={{
            style: {
              background: '#1c1c1f',
              border: '1px solid #2a2a2e',
              color: '#fafafa',
            },
          }}
        />
      </body>
    </html>
  );
}

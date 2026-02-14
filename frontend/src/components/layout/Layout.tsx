import { BottomNav } from './BottomNav';
import { ChatWidget } from '../chatbot/ChatWidget';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50 pb-20 sm:pb-24">
      {/* Main content - full width */}
      <main className="w-full min-h-screen">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
          {children}
        </div>
      </main>

      {/* Bottom Navigation */}
      <BottomNav />

      {/* Chatbot Widget */}
      <ChatWidget />
    </div>
  );
}

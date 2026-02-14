import { useState } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { ChatWidget } from '../chatbot/ChatWidget';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-gray-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-gray-900 bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header onMenuClick={() => setSidebarOpen(true)} />

        <main className="flex-1 overflow-y-auto bg-gray-50 p-4 sm:p-6">
          <div className="w-full max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>

      {/* Chatbot widget */}
      <ChatWidget />
    </div>
  );
}

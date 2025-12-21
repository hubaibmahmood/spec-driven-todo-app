"use client";

import { useState, useEffect } from "react";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Header } from "@/components/dashboard/Header";
import ChatPanel from "@/components/chat/ChatPanel";
import ChatToggleButton from "@/components/chat/ChatToggleButton";
import { useSession, signOut } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import { usePanelState } from "@/lib/chat/panel-state";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const { data: session } = useSession();
  const [user, setUser] = useState<{ name: string; email: string; image?: string | null } | null>(null);
  const router = useRouter();

  // Chat panel state with localStorage persistence
  const [panelState, setPanelState] = usePanelState();

  useEffect(() => {
    if (session?.user) {
      setUser({
        name: session.user.name,
        email: session.user.email,
        image: session.user.image
      });
    }
  }, [session]);

  const handleLogout = async () => {
    await signOut();
    router.push("/login");
  };

  // Toggle chat panel with lastOpenedAt tracking
  const toggleChatPanel = () => {
    setPanelState({
      isOpen: !panelState.isOpen,
      lastOpenedAt: !panelState.isOpen ? new Date() : panelState.lastOpenedAt,
    });
  };

  const closeChatPanel = () => {
    setPanelState({
      ...panelState,
      isOpen: false,
    });
  };

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      <Sidebar 
        isOpen={isSidebarOpen} 
        onClose={() => setIsSidebarOpen(false)} 
        onLogout={handleLogout}
        user={user}
      />
      <div className="flex-1 flex flex-col min-w-0">
        <Header onMenuClick={() => setIsSidebarOpen(true)} />
        <main className="flex-1 overflow-y-auto p-4 lg:p-8">
          <div className="max-w-7xl mx-auto space-y-8">
            {children}
          </div>
        </main>
      </div>

      {/* Chat UI Components */}
      <ChatToggleButton onClick={toggleChatPanel} isOpen={panelState.isOpen} />
      <ChatPanel isOpen={panelState.isOpen} onClose={closeChatPanel} />
    </div>
  );
}

import { ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { Dock } from "./Dock";
import { TopBar } from "./TopBar";

export const AppShell = ({ children, title }: { children: ReactNode; title?: string }) => {
  return (
    <div className="min-h-screen w-full relative overflow-x-hidden">
      {/* Decorative orbs */}
      <div className="pointer-events-none absolute -top-40 -left-40 w-[500px] h-[500px] rounded-full bg-primary/20 blur-3xl" />
      <div className="pointer-events-none absolute top-1/3 -right-40 w-[600px] h-[600px] rounded-full bg-accent/20 blur-3xl" />

      <Sidebar />
      <main className="ml-24 mr-6 pt-8 pb-32 max-w-[1500px] mx-auto px-4 lg:pl-28">
        <TopBar title={title} />
        <div className="glass-strong rounded-3xl p-6 lg:p-8 animate-fade-in">{children}</div>
      </main>
      <Dock />
    </div>
  );
};

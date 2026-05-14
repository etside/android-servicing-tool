import { Search, Bell, User } from "lucide-react";

export const TopBar = ({ title = "Welcome Back" }: { title?: string }) => {
  return (
    <header className="flex items-center justify-between mb-6 animate-fade-in">
      <div>
        <p className="text-xs text-muted-foreground tracking-wide uppercase">{title}</p>
        <h1 className="text-3xl font-semibold mt-1">eTool <span className="text-gradient">v2.2</span></h1>
      </div>
      <div className="flex items-center gap-3">
        <div className="glass rounded-full px-4 py-2 flex items-center gap-2 w-72">
          <Search className="w-4 h-4 text-muted-foreground" />
          <input
            placeholder="Search tools, devices…"
            className="bg-transparent outline-none text-sm w-full placeholder:text-muted-foreground"
          />
        </div>
        <button className="glass w-10 h-10 rounded-full flex items-center justify-center hover:bg-white/10 transition">
          <Bell className="w-4 h-4" />
        </button>
        <div className="glass-strong w-10 h-10 rounded-full flex items-center justify-center">
          <User className="w-4 h-4" />
        </div>
      </div>
    </header>
  );
};

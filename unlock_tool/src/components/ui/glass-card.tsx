import { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { ArrowUpRight } from "lucide-react";

export const GlassCard = ({
  children,
  className,
  title,
  action,
  hover = true,
}: {
  children: ReactNode;
  className?: string;
  title?: string;
  action?: ReactNode;
  hover?: boolean;
}) => {
  return (
    <div
      className={cn(
        "glass rounded-2xl p-5 transition-all duration-300",
        hover && "hover:border-white/20 hover:-translate-y-0.5",
        className
      )}
    >
      {(title || action) && (
        <div className="flex items-center justify-between mb-4">
          {title && <h3 className="text-sm font-semibold text-foreground/90">{title}</h3>}
          {action ?? (
            <button className="w-7 h-7 rounded-full bg-white/5 flex items-center justify-center hover:bg-white/10 transition">
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      )}
      {children}
    </div>
  );
};

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { 
  LayoutDashboard, 
  Upload, 
  BrainCircuit, 
  BarChart3, 
  Settings,
  ShieldCheck,
  LogOut
} from "lucide-react";
import { useStore } from "@/store/useStore";
import { useRouter } from "next/navigation";

const routes = [
  {
    label: "Dashboard",
    icon: LayoutDashboard,
    href: "/dashboard",
    color: "text-sky-500",
  },
  {
    label: "Upload Data",
    icon: Upload,
    href: "/upload",
    color: "text-violet-500",
  },
  {
    label: "AI Analysis",
    icon: BrainCircuit,
    href: "/analysis",
    color: "text-pink-500",
  },
  {
    label: "Visualize",
    icon: BarChart3,
    href: "/visualize",
    color: "text-orange-500",
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useStore();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <div className="space-y-4 py-4 flex flex-col h-full bg-secondary/30 border-r">
      <div className="px-3 py-2 flex-1">
        <Link href="/dashboard" className="flex items-center pl-3 mb-14">
          <BrainCircuit className="h-8 w-8 mr-3 text-primary" />
          <h1 className="text-2xl font-bold">VexaAI</h1>
        </Link>
        <div className="space-y-1">
          {routes.map((route) => (
            <Link
              key={route.href}
              href={route.href}
              className={cn(
                "text-sm group flex p-3 w-full justify-start font-medium cursor-pointer hover:bg-primary/10 rounded-lg transition",
                pathname === route.href
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground"
              )}
            >
              <div className="flex items-center flex-1">
                <route.icon className={cn("h-5 w-5 mr-3", route.color)} />
                {route.label}
              </div>
            </Link>
          ))}

          {user?.is_admin && (
            <Link
              href="/admin"
              className={cn(
                "text-sm group flex p-3 w-full justify-start font-medium cursor-pointer hover:bg-primary/10 rounded-lg transition",
                pathname === "/admin"
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground"
              )}
            >
              <div className="flex items-center flex-1">
                <ShieldCheck className="h-5 w-5 mr-3 text-red-500" />
                Admin Panel
              </div>
            </Link>
          )}
        </div>
      </div>

      <div className="px-3 pb-4">
        <div className="p-3 bg-primary/5 rounded-lg mb-3">
          <p className="text-sm font-medium">{user?.full_name}</p>
          <p className="text-xs text-muted-foreground">{user?.email}</p>
          {user?.is_admin && (
            <span className="inline-block mt-2 px-2 py-1 bg-red-500 text-white text-xs rounded">
              Admin
            </span>
          )}
        </div>
        <Button
          onClick={handleLogout}
          variant="outline"
          className="w-full justify-start"
        >
          <LogOut className="h-4 w-4 mr-2" />
          Logout
        </Button>
      </div>
    </div>
  );
}
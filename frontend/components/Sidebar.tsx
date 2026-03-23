"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Brain,
  MessageSquare,
  FileText,
  Home,
  Settings,
  HelpCircle,
} from "lucide-react";

const navItems = [
  { name: "Home", href: "/", icon: Home },
  { name: "Chat", href: "/chat", icon: MessageSquare },
  { name: "Documents", href: "/documents", icon: FileText },
];

const bottomItems = [
  { name: "Help", href: "#", icon: HelpCircle },
  { name: "Settings", href: "#", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-full w-64 flex-col border-r border-gray-800 bg-surface-900/50">
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 border-b border-gray-800 px-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-violet-500">
          <Brain className="h-5 w-5 text-white" />
        </div>
        <div>
          <p className="text-sm font-bold text-white">NexusAI</p>
          <p className="text-[10px] text-gray-500">Document Intelligence</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-3">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all ${
                isActive
                  ? "bg-brand-500/10 text-brand-400"
                  : "text-gray-400 hover:bg-surface-800 hover:text-gray-200"
              }`}
            >
              <item.icon
                className={`h-5 w-5 ${isActive ? "text-brand-400" : "text-gray-600"}`}
              />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Bottom items */}
      <div className="space-y-1 border-t border-gray-800 p-3">
        {bottomItems.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-gray-500 transition-all hover:bg-surface-800 hover:text-gray-300"
          >
            <item.icon className="h-5 w-5 text-gray-600" />
            {item.name}
          </Link>
        ))}
      </div>
    </aside>
  );
}

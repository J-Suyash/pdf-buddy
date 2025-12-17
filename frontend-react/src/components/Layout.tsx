import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Library, Upload, Search, BookOpen, Sun, Moon } from 'lucide-react';
import { cn } from '../utils';
import { useState, useEffect } from 'react';

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    // Check system preference or localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setIsDark(savedTheme === 'dark');
    } else {
      const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setIsDark(systemPrefersDark);
    }
  }, []);

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [isDark]);

  const toggleTheme = () => setIsDark(!isDark);

  const links = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/search', icon: Search, label: 'Search' },
    { to: '/library', icon: BookOpen, label: 'Library' },
    { to: '/upload', icon: Upload, label: 'Upload' },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground font-sans selection:bg-primary/10 overflow-x-hidden transition-colors duration-300">
      <div className="fixed inset-y-0 left-0 w-64 bg-card border-r border-border z-30 flex flex-col">
        {/* Header */}
        <div className="p-6">
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary text-primary-foreground flex items-center justify-center">
              <BookOpen className="w-5 h-5" />
            </div>
            PDF Buddy
          </h1>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {links.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.to;

            return (
              <Link
                key={link.to}
                to={link.to}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-md transition-colors text-sm font-medium",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                )}
              >
                <Icon className="w-4 h-4" />
                <span>{link.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Footer / User / Theme Toggle */}
        <div className="p-4 border-t border-border space-y-4">
            <button 
                onClick={toggleTheme}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-md border border-border hover:bg-muted transition-colors text-sm font-medium text-muted-foreground hover:text-foreground"
            >
                {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                {isDark ? 'Light Mode' : 'Dark Mode'}
            </button>
            
          <div className="flex items-center gap-3 px-2">
             <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center border border-border">
                <span className="text-xs font-medium">SA</span>
             </div>
             <div className="flex-1 min-w-0">
               <p className="text-sm font-medium truncate">Scholar Agent</p>
               <p className="text-xs text-muted-foreground truncate">Online</p>
             </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="pl-64 min-h-screen w-full bg-background transition-colors duration-300">
        <div className="p-8 max-w-7xl mx-auto animate-fade-in">
          {children}
        </div>
      </main>
    </div>
  );
}

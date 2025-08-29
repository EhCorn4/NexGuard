import { useState, useEffect } from "react";
import { Link, useLocation } from "wouter";
import { Menu, X } from "lucide-react";
import { AnimatedShield } from "@/components/ui/animated-shield";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { BotStatusIndicator } from "@/components/ui/bot-status";
import { HoverScale } from "@/components/ui/hover-scale";
import { useAuth } from "@/hooks/useAuth";
import { motion } from "framer-motion";
import nexguardIcon from "@assets/file_00000000ee7c61f7a421642c4ce3b538_1751938060068.png";

export function Navbar() {
  const [location] = useLocation();
  const [isScrolled, setIsScrolled] = useState(false);
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const publicNavItems = [
    { href: "/", label: "Home" },
    { href: "/features", label: "Features" },
    { href: "/dashboard", label: "Dashboard" },
    { href: "/invite", label: "Invite Bot" },
    { href: "/developers", label: "Developers" },
    { href: "/community", label: "Community" },
    { href: "/testimonials", label: "Testimonials" },
    { href: "/feedback", label: "Feedback" },
    { href: "/docs", label: "Docs" },
    { href: "/analytics", label: "Analytics" },
    { href: "/donate", label: "Donate" },
  ];

  const authNavItems = [
    { href: "/", label: "Home" },
    { href: "/dashboard", label: "Security Dashboard" },
    { href: "/features", label: "Features" },
    { href: "/analytics", label: "Analytics" },
    { href: "/invite", label: "Invite Bot" },
    { href: "/developers", label: "Developers" },
    { href: "/community", label: "Community" },
    { href: "/testimonials", label: "Testimonials" },
    { href: "/feedback", label: "Feedback" },
    { href: "/docs", label: "Docs" },
    { href: "/donate", label: "Donate" },
  ];

  const navItems = isAuthenticated ? authNavItems : publicNavItems;

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 backdrop-blur-md border-b border-[hsl(var(--nexguard-cyan))]/20 transition-all duration-300 ${
      isScrolled ? "bg-[hsl(var(--nexguard-dark))]/95" : "bg-[hsl(var(--nexguard-dark))]/90"
    }`}>
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <HoverScale scale={1.05}>
            <Link href="/" className="flex items-center space-x-3">
              <motion.img 
                src={nexguardIcon} 
                alt="NexGuard" 
                className="w-10 h-10 rounded-lg"
                whileHover={{ rotate: 5 }}
                transition={{ duration: 0.2 }}
              />
              <div>
                <h1 className="text-xl font-bold text-white">NEXGUARD</h1>
                <p className="text-xs text-[hsl(var(--nexguard-cyan))]">PROTECT. MANAGE. ENHANCE.</p>
              </div>
            </Link>
          </HoverScale>
          
          <div className="hidden md:flex items-center space-x-8">
            {navItems.map((item, index) => (
              <motion.div
                key={item.href}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1, duration: 0.3 }}
                whileHover={{ y: -2 }}
              >
                <Link
                  href={item.href}
                  className={`relative nav-link text-white hover:text-[hsl(var(--nexguard-cyan))] transition-colors duration-200 ${
                    location === item.href ? "text-[hsl(var(--nexguard-cyan))]" : ""
                  }`}
                >
                  {item.label}
                  {location === item.href && (
                    <motion.div
                      className="absolute -bottom-1 left-0 right-0 h-0.5 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-full"
                      layoutId="activeNavItem"
                      transition={{ duration: 0.3, ease: "easeInOut" }}
                    />
                  )}
                </Link>
              </motion.div>
            ))}
            <BotStatusIndicator compact />
            <ThemeToggle />
            {/* Dashboard functionality removed */}
          </div>
          
          <div className="md:hidden flex items-center space-x-2">
            <BotStatusIndicator compact />
            <ThemeToggle />
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="text-white hover:text-[hsl(var(--nexguard-cyan))]">
                  <Menu size={24} />
                </Button>
              </SheetTrigger>
              <SheetContent side="right" className="bg-[hsl(var(--nexguard-darker))]/95 backdrop-blur-md border-[hsl(var(--nexguard-cyan))]/20">
                <div className="flex flex-col space-y-4 mt-8">
                  {navItems.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={`nav-link text-white hover:text-[hsl(var(--nexguard-cyan))] text-lg ${
                        location === item.href ? "text-[hsl(var(--nexguard-cyan))]" : ""
                      }`}
                    >
                      {item.label}
                    </Link>
                  ))}
                  <div className="pt-4">
                    <BotStatusIndicator />
                  </div>
                  {/* Dashboard functionality removed */}
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>
    </nav>
  );
}

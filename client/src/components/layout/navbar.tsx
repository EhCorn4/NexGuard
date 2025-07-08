import { useState, useEffect } from "react";
import { Link, useLocation } from "wouter";
import { Menu, X } from "lucide-react";
import { AnimatedShield } from "@/components/ui/animated-shield";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import nexguardIcon from "@assets/file_00000000ee7c61f7a421642c4ce3b538_1751938060068.png";

export function Navbar() {
  const [location] = useLocation();
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navItems = [
    { href: "/", label: "Home" },
    { href: "/features", label: "Features" },
    { href: "/invite", label: "Invite Bot" },
    { href: "/developers", label: "Developers" },
    { href: "/community", label: "Community" },
  ];

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 backdrop-blur-md border-b border-[hsl(var(--nexguard-cyan))]/20 transition-all duration-300 ${
      isScrolled ? "bg-[hsl(var(--nexguard-dark))]/95" : "bg-[hsl(var(--nexguard-dark))]/90"
    }`}>
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-3">
            <img 
              src={nexguardIcon} 
              alt="NexGuard" 
              className="w-10 h-10 rounded-lg"
            />
            <div>
              <h1 className="text-xl font-bold text-white">NEXGUARD</h1>
              <p className="text-xs text-[hsl(var(--nexguard-cyan))]">PROTECT. MANAGE. ENHANCE.</p>
            </div>
          </Link>
          
          <div className="hidden md:flex space-x-8">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`nav-link text-white hover:text-[hsl(var(--nexguard-cyan))] ${
                  location === item.href ? "text-[hsl(var(--nexguard-cyan))]" : ""
                }`}
              >
                {item.label}
              </Link>
            ))}
          </div>
          
          <div className="md:hidden">
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
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>
    </nav>
  );
}

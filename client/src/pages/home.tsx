import { Link } from "wouter";
import { GradientText } from "@/components/ui/gradient-text";
import { AnimatedShield } from "@/components/ui/animated-shield";
import { Button } from "@/components/ui/button";
import { SiDiscord } from "react-icons/si";
import nexguardLogo from "@assets/Nexguard_1751937048860.png";
import nexguardBanner from "@assets/file_00000000ee7c61f7a421642c4ce3b538_1751936999714.png";
import nexguardIcon from "@assets/file_0000000003fc61f58b4fd114190f81c9_1751936993313.png";

export default function Home() {
  return (
    <div className="min-h-screen hero-gradient circuit-pattern flex items-center justify-center relative overflow-hidden">
      <div 
        className="absolute inset-0 bg-cover bg-center opacity-20" 
        style={{ backgroundImage: `url(${nexguardIcon})` }}
      ></div>
      <div className="absolute inset-0 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/5 to-[hsl(var(--nexguard-purple))]/5 animate-pulse-slow"></div>
      
      <div className="container mx-auto px-4 text-center relative z-10">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8 flex justify-center">
            <img 
              src={nexguardBanner} 
              alt="NexGuard Banner" 
              className="w-64 md:w-80 h-auto max-w-full animate-float"
            />
          </div>
          

          
          <p className="text-xl md:text-2xl text-[hsl(var(--nexguard-cyan))] mb-6 font-medium">
            PROTECT. MANAGE. ENHANCE.
          </p>
          
          <p className="text-lg md:text-xl text-gray-300 mb-12 max-w-2xl mx-auto leading-relaxed">
            The ultimate Discord moderation and quality-of-life bot designed to keep your server safe, organized, and thriving. Advanced automation meets intuitive management.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link href="/invite">
              <Button size="lg" className="bg-[hsl(var(--discord-blurple))] hover:bg-[hsl(var(--discord-light))] text-white font-semibold text-lg px-8 py-4 transform hover:scale-105 transition-all duration-300">
                <SiDiscord className="mr-2" size={20} />
                Invite to Server
              </Button>
            </Link>
            
            <Link href="/features">
              <Button 
                variant="outline" 
                size="lg" 
                className="border-2 border-[hsl(var(--nexguard-cyan))] text-[hsl(var(--nexguard-cyan))] hover:bg-[hsl(var(--nexguard-cyan))] hover:text-[hsl(var(--nexguard-dark))] font-semibold text-lg px-8 py-4 transform hover:scale-105 transition-all duration-300"
              >
                Explore Features
              </Button>
            </Link>
          </div>
          
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8 max-w-2xl mx-auto">
            <div className="text-center">
              <div className="text-3xl font-bold text-[hsl(var(--nexguard-cyan))]">2,847</div>
              <div className="text-sm text-gray-400">Servers Protected</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-[hsl(var(--nexguard-cyan))]">156K</div>
              <div className="text-sm text-gray-400">Users Secured</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-[hsl(var(--nexguard-cyan))]">98.7%</div>
              <div className="text-sm text-gray-400">Uptime</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-[hsl(var(--nexguard-cyan))]">24/7</div>
              <div className="text-sm text-gray-400">Support</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

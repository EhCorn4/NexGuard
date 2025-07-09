import { Link } from "wouter";
import { AnimatedShield } from "@/components/ui/animated-shield";
import { SiDiscord } from "react-icons/si";
import nexguardIcon from "@assets/file_00000000ee7c61f7a421642c4ce3b538_1751938060068.png";

export function Footer() {
  return (
    <footer className="bg-[hsl(var(--nexguard-darker))] border-t border-[hsl(var(--nexguard-cyan))]/20 py-12">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <img 
                src={nexguardIcon} 
                alt="NexGuard" 
                className="w-8 h-8 rounded-lg"
              />
              <div>
                <h3 className="text-lg font-bold text-white">NEXGUARD</h3>
                <p className="text-xs text-[hsl(var(--nexguard-cyan))]">PROTECT. MANAGE. ENHANCE.</p>
              </div>
            </div>
            <p className="text-gray-400 text-sm">
              The ultimate Discord moderation and quality-of-life bot for your server.
            </p>
          </div>
          
          <div>
            <h4 className="text-white font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="/features" className="text-gray-400 hover:text-[hsl(var(--nexguard-cyan))] transition-colors">Features</Link></li>
              <li><Link href="/invite" className="text-gray-400 hover:text-[hsl(var(--nexguard-cyan))] transition-colors">Invite Bot</Link></li>
              <li><Link href="/developers" className="text-gray-400 hover:text-[hsl(var(--nexguard-cyan))] transition-colors">Developers</Link></li>
              <li><Link href="/community" className="text-gray-400 hover:text-[hsl(var(--nexguard-cyan))] transition-colors">Community</Link></li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-white font-semibold mb-4">Support</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="https://discord.gg/wpjZMPXaR" className="text-gray-400 hover:text-[hsl(var(--nexguard-cyan))] transition-colors">Discord Server</a></li>
              <li><a href="#" className="text-gray-400 hover:text-[hsl(var(--nexguard-cyan))] transition-colors">Documentation</a></li>
              <li><a href="#" className="text-gray-400 hover:text-[hsl(var(--nexguard-cyan))] transition-colors">FAQ</a></li>
              <li><a href="#" className="text-gray-400 hover:text-[hsl(var(--nexguard-cyan))] transition-colors">Contact</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-white font-semibold mb-4">Legal</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="/privacy-policy" className="text-gray-400 hover:text-[hsl(var(--nexguard-cyan))] transition-colors">Privacy Policy</Link></li>
              <li><Link href="/terms-of-service" className="text-gray-400 hover:text-[hsl(var(--nexguard-cyan))] transition-colors">Terms of Service</Link></li>
              <li><a href="#" className="text-gray-400 hover:text-[hsl(var(--nexguard-cyan))] transition-colors">Cookie Policy</a></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-[hsl(var(--nexguard-cyan))]/20 mt-8 pt-8 text-center">
          <p className="text-gray-400 text-sm">
            © 2024 NexGuard. All rights reserved. Made with <span className="text-red-400">❤️</span> for the Discord community.
          </p>
        </div>
      </div>
    </footer>
  );
}

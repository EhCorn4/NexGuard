import { Link } from "wouter";
import { GradientText } from "@/components/ui/gradient-text";
import { AnimatedShield } from "@/components/ui/animated-shield";
import { Button } from "@/components/ui/button";
import { SiDiscord } from "react-icons/si";
import { Shield, Users, MessageSquare, Bot, Settings, Zap, Eye } from "lucide-react";
import nexguardLogo from "@assets/Nexguard_1751937048860.png";
import nexguardBanner from "@assets/file_00000000ee7c61f7a421642c4ce3b538_1751936999714.png";
import nexguardIcon from "@assets/file_0000000003fc61f58b4fd114190f81c9_1751936993313.png";
import { memo } from "react";

const Home = memo(function Home() {
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
              <div className="text-3xl font-bold text-[hsl(var(--nexguard-cyan))]">127</div>
              <div className="text-sm text-gray-400">Servers Protected</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-[hsl(var(--nexguard-cyan))]">8.2K</div>
              <div className="text-sm text-gray-400">Users Secured</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-[hsl(var(--nexguard-cyan))]">96.3%</div>
              <div className="text-sm text-gray-400">Uptime</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-[hsl(var(--nexguard-cyan))]">24/7</div>
              <div className="text-sm text-gray-400">Support</div>
            </div>
          </div>
        </div>
      </div>

      {/* Why Choose NexGuard Section */}
      <div className="py-20 px-4 bg-gradient-to-b from-[hsl(var(--nexguard-darker))] to-[hsl(var(--nexguard-dark))]">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">
              <GradientText>Why Choose NexGuard?</GradientText>
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Built by Discord enthusiasts for Discord communities, NexGuard combines powerful automation with intuitive design.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 mb-16">
            <div className="text-center p-6 rounded-lg bg-background/10 backdrop-blur-sm border border-[hsl(var(--nexguard-cyan))]/20">
              <div className="w-16 h-16 mx-auto mb-4 bg-[hsl(var(--nexguard-cyan))]/20 rounded-full flex items-center justify-center">
                <Shield className="w-8 h-8 text-[hsl(var(--nexguard-cyan))]" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-[hsl(var(--nexguard-cyan))]">Advanced Protection</h3>
              <p className="text-gray-300">
                AI-powered moderation that learns and adapts to your server's unique needs and culture.
              </p>
            </div>
            
            <div className="text-center p-6 rounded-lg bg-background/10 backdrop-blur-sm border border-[hsl(var(--nexguard-purple))]/20">
              <div className="w-16 h-16 mx-auto mb-4 bg-[hsl(var(--nexguard-purple))]/20 rounded-full flex items-center justify-center">
                <Zap className="w-8 h-8 text-[hsl(var(--nexguard-purple))]" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-[hsl(var(--nexguard-purple))]">Lightning Fast</h3>
              <p className="text-gray-300">
                Optimized performance with sub-second response times and 99%+ uptime guarantee.
              </p>
            </div>
            
            <div className="text-center p-6 rounded-lg bg-background/10 backdrop-blur-sm border border-[hsl(var(--nexguard-cyan))]/20">
              <div className="w-16 h-16 mx-auto mb-4 bg-[hsl(var(--nexguard-cyan))]/20 rounded-full flex items-center justify-center">
                <Settings className="w-8 h-8 text-[hsl(var(--nexguard-cyan))]" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-[hsl(var(--nexguard-cyan))]">Easy Setup</h3>
              <p className="text-gray-300">
                Get started in minutes with our intuitive dashboard and step-by-step configuration guide.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Featured Capabilities Section */}
      <div className="py-20 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">
              <GradientText>Core Capabilities</GradientText>
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Everything you need to create a safe, engaging, and well-managed Discord community.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-6 rounded-lg bg-background/5 border border-[hsl(var(--nexguard-cyan))]/10 hover:border-[hsl(var(--nexguard-cyan))]/30 transition-colors">
              <MessageSquare className="w-8 h-8 text-[hsl(var(--nexguard-cyan))] mb-4" />
              <h3 className="text-lg font-semibold mb-2">Smart Moderation</h3>
              <p className="text-sm text-gray-400">Automated content filtering and behavior analysis</p>
            </div>
            
            <div className="p-6 rounded-lg bg-background/5 border border-[hsl(var(--nexguard-purple))]/10 hover:border-[hsl(var(--nexguard-purple))]/30 transition-colors">
              <Users className="w-8 h-8 text-[hsl(var(--nexguard-purple))] mb-4" />
              <h3 className="text-lg font-semibold mb-2">Member Management</h3>
              <p className="text-sm text-gray-400">Role automation and user engagement tracking</p>
            </div>
            
            <div className="p-6 rounded-lg bg-background/5 border border-[hsl(var(--nexguard-cyan))]/10 hover:border-[hsl(var(--nexguard-cyan))]/30 transition-colors">
              <Eye className="w-8 h-8 text-[hsl(var(--nexguard-cyan))] mb-4" />
              <h3 className="text-lg font-semibold mb-2">Real-time Monitoring</h3>
              <p className="text-sm text-gray-400">Live activity feeds and instant alerts</p>
            </div>
            
            <div className="p-6 rounded-lg bg-background/5 border border-[hsl(var(--nexguard-purple))]/10 hover:border-[hsl(var(--nexguard-purple))]/30 transition-colors">
              <Bot className="w-8 h-8 text-[hsl(var(--nexguard-purple))] mb-4" />
              <h3 className="text-lg font-semibold mb-2">Custom Commands</h3>
              <p className="text-sm text-gray-400">Personalized bot interactions and responses</p>
            </div>
          </div>
        </div>
      </div>

      {/* Call to Action Section */}
      <div className="py-20 px-4 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/10 to-[hsl(var(--nexguard-purple))]/10">
        <div className="container mx-auto text-center">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-4xl font-bold mb-6">
              <GradientText>Ready to Protect Your Server?</GradientText>
            </h2>
            <p className="text-xl text-gray-300 mb-8">
              Join hundreds of Discord communities that trust NexGuard to keep their servers safe and engaged.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/invite">
                <Button size="lg" className="bg-[hsl(var(--nexguard-cyan))] hover:bg-[hsl(var(--nexguard-cyan))]/80 text-white px-8 py-4 text-lg font-semibold">
                  Add to Server
                </Button>
              </Link>
              <Link href="/features">
                <Button size="lg" variant="outline" className="border-[hsl(var(--nexguard-purple))] text-[hsl(var(--nexguard-purple))] hover:bg-[hsl(var(--nexguard-purple))]/10 px-8 py-4 text-lg font-semibold">
                  View Features
                </Button>
              </Link>
            </div>
            <p className="text-sm text-gray-400 mt-6">
              Free setup • No credit card required • 24/7 support included
            </p>
          </div>
        </div>
      </div>
    </div>
  );
});

export default Home;

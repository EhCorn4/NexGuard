import { GradientText } from "@/components/ui/gradient-text";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Heart, Coffee, Github, CreditCard, Zap, Shield, Users, Star } from "lucide-react";
import { SiPaypal, SiKofi, SiGithubsponsors } from "react-icons/si";
import { memo } from "react";

const Donate = memo(function Donate() {
  const donationOptions = [
    {
      name: "PayPal",
      icon: <SiPaypal size={32} />,
      description: "One-time or recurring donations via PayPal",
      url: "https://paypal.me/nexguard",
      color: "bg-[#0070ba] hover:bg-[#005ea6]",
      popular: false
    },
    {
      name: "Ko-fi",
      icon: <SiKofi size={32} />,
      description: "Buy us a coffee to fuel development",
      url: "https://ko-fi.com/nexguard",
      color: "bg-[#ff5722] hover:bg-[#e64a19]",
      popular: true
    },
    {
      name: "GitHub Sponsors",
      icon: <SiGithubsponsors size={32} />,
      description: "Support through GitHub's sponsorship program",
      url: "https://github.com/sponsors/nexguard",
      color: "bg-[#ea4aaa] hover:bg-[#d73a94]",
      popular: false
    }
  ];

  const impactStats = [
    {
      icon: <Shield className="text-[hsl(var(--nexguard-cyan))]" size={32} />,
      title: "Server Protection",
      description: "Keep NexGuard running 24/7 to protect Discord communities",
      stat: "9+ Servers"
    },
    {
      icon: <Zap className="text-[hsl(var(--nexguard-cyan))]" size={32} />,
      title: "Feature Development",
      description: "Fund new commands and advanced moderation features",
      stat: "45+ Commands"
    },
    {
      icon: <Users className="text-[hsl(var(--nexguard-cyan))]" size={32} />,
      title: "Community Support",
      description: "Maintain hosting costs and provide user support",
      stat: "168+ Users"
    }
  ];

  const supportTiers = [
    {
      name: "Supporter",
      amount: "$3",
      period: "month",
      description: "Help cover basic hosting costs",
      benefits: [
        "Supporter role in Discord",
        "Early feature previews",
        "Priority support"
      ],
      color: "border-gray-600"
    },
    {
      name: "Patron",
      amount: "$10",
      period: "month", 
      description: "Significantly impact development",
      benefits: [
        "All Supporter benefits",
        "Feature request priority",
        "Beta testing access",
        "Monthly progress updates"
      ],
      color: "border-[hsl(var(--nexguard-cyan))]",
      popular: true
    },
    {
      name: "Champion",
      amount: "$25",
      period: "month",
      description: "Become a development champion",
      benefits: [
        "All Patron benefits",
        "Direct developer contact",
        "Custom feature discussions",
        "Recognition on website"
      ],
      color: "border-[hsl(var(--nexguard-purple))]"
    }
  ];

  return (
    <div className="min-h-screen hero-gradient circuit-pattern pt-24 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/5 to-[hsl(var(--nexguard-purple))]/5 animate-pulse-slow"></div>
      <div className="container mx-auto px-4 py-20 relative z-10">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <PageHeader 
              title={
                <span>
                  Support <GradientText>NexGuard</GradientText> Development
                </span>
              }
              description="Your donations help us maintain and improve NexGuard, keeping Discord communities safe and well-moderated. Every contribution makes a difference!"
            />
            
            <div className="flex items-center justify-center gap-2 mt-6">
              <Heart className="text-red-500" size={20} />
              <span className="text-gray-300">Made with love for the Discord community</span>
              <Heart className="text-red-500" size={20} />
            </div>
          </div>

          {/* Impact Statistics */}
          <div className="grid md:grid-cols-3 gap-6 mb-16">
            {impactStats.map((stat, index) => (
              <Card key={index} className="bg-[hsl(var(--nexguard-darker))]/80 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20 text-center">
                <CardContent className="p-6">
                  <div className="flex justify-center mb-4">
                    {stat.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">{stat.title}</h3>
                  <p className="text-gray-400 text-sm mb-3">{stat.description}</p>
                  <div className="text-2xl font-bold text-[hsl(var(--nexguard-cyan))]">{stat.stat}</div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Donation Options */}
          <Card className="bg-[hsl(var(--nexguard-darker))]/80 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20 mb-16">
            <CardHeader>
              <CardTitle className="text-2xl text-center text-white">Choose Your Donation Method</CardTitle>
              <p className="text-gray-400 text-center">Select your preferred platform to support NexGuard development</p>
            </CardHeader>
            <CardContent className="p-8">
              <div className="grid md:grid-cols-3 gap-6">
                {donationOptions.map((option, index) => (
                  <div key={index} className="relative">
                    {option.popular && (
                      <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 z-10">
                        <span className="bg-gradient-to-r from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))] text-white text-xs font-semibold px-3 py-1 rounded-full flex items-center gap-1">
                          <Star size={12} />
                          Most Popular
                        </span>
                      </div>
                    )}
                    <Card className={`bg-[hsl(var(--nexguard-dark))]/60 backdrop-blur-sm border-gray-600 hover:border-[hsl(var(--nexguard-cyan))]/50 transition-all duration-300 transform hover:scale-105 ${option.popular ? 'border-[hsl(var(--nexguard-cyan))]/30' : ''}`}>
                      <CardContent className="p-6 text-center">
                        <div className="flex justify-center mb-4 text-white">
                          {option.icon}
                        </div>
                        <h3 className="text-lg font-semibold text-white mb-2">{option.name}</h3>
                        <p className="text-gray-400 text-sm mb-4">{option.description}</p>
                        <a 
                          href={option.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block"
                        >
                          <Button 
                            className={`w-full ${option.color} text-white font-semibold`}
                          >
                            Donate via {option.name}
                          </Button>
                        </a>
                      </CardContent>
                    </Card>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Support Tiers */}
          <Card className="bg-[hsl(var(--nexguard-darker))]/80 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20 mb-16">
            <CardHeader>
              <CardTitle className="text-2xl text-center text-white">Monthly Support Tiers</CardTitle>
              <p className="text-gray-400 text-center">Join our community of supporters and get exclusive benefits</p>
            </CardHeader>
            <CardContent className="p-8">
              <div className="grid md:grid-cols-3 gap-6">
                {supportTiers.map((tier, index) => (
                  <div key={index} className="relative">
                    {tier.popular && (
                      <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 z-10">
                        <span className="bg-gradient-to-r from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))] text-white text-xs font-semibold px-3 py-1 rounded-full flex items-center gap-1">
                          <Star size={12} />
                          Recommended
                        </span>
                      </div>
                    )}
                    <Card className={`bg-[hsl(var(--nexguard-dark))]/60 backdrop-blur-sm border-2 ${tier.color} hover:border-[hsl(var(--nexguard-cyan))]/50 transition-all duration-300 transform hover:scale-105 h-full`}>
                      <CardContent className="p-6">
                        <div className="text-center mb-4">
                          <h3 className="text-lg font-semibold text-white mb-2">{tier.name}</h3>
                          <div className="text-3xl font-bold text-[hsl(var(--nexguard-cyan))] mb-1">
                            {tier.amount}
                            <span className="text-sm text-gray-400">/{tier.period}</span>
                          </div>
                          <p className="text-gray-400 text-sm">{tier.description}</p>
                        </div>
                        <ul className="space-y-2 mb-6">
                          {tier.benefits.map((benefit, i) => (
                            <li key={i} className="flex items-center text-gray-300 text-sm">
                              <div className="w-2 h-2 bg-[hsl(var(--nexguard-cyan))] rounded-full mr-3 flex-shrink-0"></div>
                              {benefit}
                            </li>
                          ))}
                        </ul>
                        <Button 
                          className="w-full bg-gradient-to-r from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))] hover:from-[hsl(var(--nexguard-cyan))]/80 hover:to-[hsl(var(--nexguard-purple))]/80 text-white font-semibold"
                          onClick={() => window.open('https://ko-fi.com/nexguard', '_blank')}
                        >
                          Support at {tier.amount}
                        </Button>
                      </CardContent>
                    </Card>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* FAQ Section */}
          <Card className="bg-[hsl(var(--nexguard-darker))]/80 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20 mb-16">
            <CardHeader>
              <CardTitle className="text-2xl text-center text-white">Donation FAQ</CardTitle>
            </CardHeader>
            <CardContent className="p-8">
              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-lg font-semibold text-white mb-3">💝 How are donations used?</h4>
                  <p className="text-gray-400 text-sm mb-6">
                    Donations directly support server hosting costs, development time, and new feature implementation. 
                    We're committed to keeping NexGuard free while improving its capabilities.
                  </p>
                  
                  <h4 className="text-lg font-semibold text-white mb-3">🔒 Is my payment secure?</h4>
                  <p className="text-gray-400 text-sm mb-6">
                    All payments are processed through secure, trusted platforms (PayPal, Ko-fi, GitHub). 
                    We never store your payment information.
                  </p>
                </div>
                <div>
                  <h4 className="text-lg font-semibold text-white mb-3">🎁 What do I get for donating?</h4>
                  <p className="text-gray-400 text-sm mb-6">
                    Depending on your support tier, you'll receive Discord roles, early access to features, 
                    priority support, and our eternal gratitude!
                  </p>
                  
                  <h4 className="text-lg font-semibold text-white mb-3">❓ Can I cancel anytime?</h4>
                  <p className="text-gray-400 text-sm">
                    Absolutely! Monthly subscriptions can be cancelled anytime through your chosen platform. 
                    There are no long-term commitments.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Thank You Message */}
          <Card className="bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/10 to-[hsl(var(--nexguard-purple))]/10 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/30">
            <CardContent className="p-8 text-center">
              <Heart className="text-red-500 mx-auto mb-4" size={48} />
              <h3 className="text-2xl font-bold text-white mb-4">Thank You for Your Support!</h3>
              <p className="text-gray-300 max-w-2xl mx-auto">
                Every donation, no matter the size, helps us continue developing and maintaining NexGuard. 
                Your support enables us to keep Discord communities safe and well-moderated. 
                Together, we're building a better Discord experience for everyone.
              </p>
              <div className="mt-6">
                <Button 
                  variant="outline" 
                  className="border-[hsl(var(--nexguard-cyan))] text-[hsl(var(--nexguard-cyan))] hover:bg-[hsl(var(--nexguard-cyan))] hover:text-white"
                  onClick={() => window.open('https://discord.gg/wpjZMPXaRT', '_blank')}
                >
                  <Users className="mr-2" size={18} />
                  Join Our Community
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
});

export default Donate;
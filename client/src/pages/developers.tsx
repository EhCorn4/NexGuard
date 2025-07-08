import { useQuery } from "@tanstack/react-query";
import { GradientText } from "@/components/ui/gradient-text";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, User, Mail } from "lucide-react";
import { SiDiscord, SiGithub, SiX, SiLinkedin } from "react-icons/si";
import type { Developer } from "@shared/schema";

export default function Developers() {
  const { data: developers, isLoading, error } = useQuery<Developer[]>({
    queryKey: ["/api/developers"],
  });

  if (error) {
    return (
      <div className="min-h-screen bg-[hsl(var(--nexguard-darker))] pt-24 px-4">
        <div className="container mx-auto">
          <Alert className="max-w-2xl mx-auto">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Failed to load developer information. Please try again later.
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[hsl(var(--nexguard-darker))] pt-24">
      <div className="container mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <GradientText>Meet the Developers</GradientText>
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            The talented team behind NexGuard, dedicated to creating the best Discord moderation experience.
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {isLoading ? (
            Array.from({ length: 3 }).map((_, i) => (
              <Card key={i} className="bg-[hsl(var(--nexguard-dark))]/50 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20">
                <CardContent className="p-6 text-center">
                  <Skeleton className="w-24 h-24 rounded-full mx-auto mb-4" />
                  <Skeleton className="h-6 w-3/4 mx-auto mb-2" />
                  <Skeleton className="h-4 w-1/2 mx-auto mb-3" />
                  <Skeleton className="h-4 w-full mb-2" />
                  <Skeleton className="h-4 w-full mb-2" />
                  <Skeleton className="h-4 w-2/3 mx-auto mb-4" />
                  <div className="flex justify-center space-x-4">
                    <Skeleton className="w-6 h-6 rounded" />
                    <Skeleton className="w-6 h-6 rounded" />
                    <Skeleton className="w-6 h-6 rounded" />
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            developers?.map((developer) => (
              <Card 
                key={developer.id} 
                className="bg-[hsl(var(--nexguard-dark))]/50 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20 hover:border-[hsl(var(--nexguard-cyan))]/50 transition-all duration-300"
              >
                <CardContent className="p-6 text-center">
                  <div className="w-24 h-24 bg-gradient-to-br from-[hsl(var(--nexguard-cyan))] to-[hsl(var(--nexguard-purple))] rounded-full flex items-center justify-center mx-auto mb-4">
                    <User className="text-white" size={32} />
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-2">{developer.name}</h3>
                  <p className="text-[hsl(var(--nexguard-cyan))] mb-3">{developer.role}</p>
                  <p className="text-gray-300 text-sm mb-4">{developer.bio}</p>
                  <div className="flex justify-center space-x-4">
                    {developer.githubUrl && (
                      <a 
                        href={developer.githubUrl} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-gray-400 hover:text-[hsl(var(--nexguard-cyan))] transition-colors"
                      >
                        <SiGithub size={20} />
                      </a>
                    )}
                    {developer.twitterUrl && (
                      <a 
                        href={developer.twitterUrl} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-gray-400 hover:text-[hsl(var(--nexguard-cyan))] transition-colors"
                      >
                        <SiX size={20} />
                      </a>
                    )}
                    {developer.linkedinUrl && (
                      <a 
                        href={developer.linkedinUrl} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-gray-400 hover:text-[hsl(var(--nexguard-cyan))] transition-colors"
                      >
                        <SiLinkedin size={20} />
                      </a>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
        
        <div className="mt-16 text-center">
          <Card className="bg-[hsl(var(--nexguard-dark))]/50 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20 max-w-2xl mx-auto">
            <CardContent className="p-8">
              <h3 className="text-2xl font-semibold text-white mb-4">Get in Touch</h3>
              <p className="text-gray-300 mb-6">
                Have questions, suggestions, or want to collaborate? We'd love to hear from you!
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <a 
                  href="mailto:nexguards@gmail.com"
                  className="inline-block"
                >
                  <Button 
                    className="bg-[hsl(var(--nexguard-cyan))] hover:bg-[hsl(var(--nexguard-cyan))]/80 text-[hsl(var(--nexguard-dark))] font-semibold px-6 py-3 transition-all duration-300"
                  >
                    <Mail className="mr-2" size={20} />
                    Email Us
                  </Button>
                </a>
                <a 
                  href="https://discord.gg/wpjZMPXaR"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block"
                >
                  <Button 
                    variant="outline"
                    className="border-2 border-[hsl(var(--nexguard-cyan))] text-[hsl(var(--nexguard-cyan))] hover:bg-[hsl(var(--nexguard-cyan))] hover:text-[hsl(var(--nexguard-dark))] font-semibold px-6 py-3 transition-all duration-300"
                  >
                    <SiDiscord className="mr-2" size={20} />
                    Join Our Discord
                  </Button>
                </a>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

import { memo } from "react";
import { useQuery } from "@tanstack/react-query";
import { GradientText } from "@/components/ui/gradient-text";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { AlertCircle, User, Mail, MapPin, Calendar, Award, Code, Briefcase, GraduationCap, Globe, MessageSquare } from "lucide-react";
import { SiDiscord, SiGithub, SiX, SiLinkedin, SiJavascript, SiReact, SiNodedotjs, SiPostgresql, SiDocker, SiTypescript } from "react-icons/si";
import type { Developer } from "@shared/schema";
import devAvatar from "@assets/Devavatar_1752722055445.png";
import nexguardIcon from "@assets/file_0000000003fc61f58b4fd114190f81c9_1751936993313.png";

const Developers = memo(function Developers() {
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
    <div className="min-h-screen hero-gradient circuit-pattern pt-24 relative overflow-hidden">
      <div 
        className="absolute inset-0 bg-cover bg-center opacity-20" 
        style={{ backgroundImage: `url(${nexguardIcon})` }}
      ></div>
      <div className="absolute inset-0 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/5 to-[hsl(var(--nexguard-purple))]/5 animate-pulse-slow"></div>
      <div className="container mx-auto px-4 py-20 relative z-10">
        <PageHeader 
          title="Meet the Developers"
          description="The talented team behind NexGuard, dedicated to creating the best Discord moderation experience."
        />
        
        <div className="max-w-6xl mx-auto">
          {isLoading ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <Card className="bg-[hsl(var(--nexguard-dark))]/50 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20">
                <CardContent className="p-6">
                  <Skeleton className="w-32 h-32 rounded-full mx-auto mb-4" />
                  <Skeleton className="h-6 w-2/3 mx-auto mb-4" />
                  <Skeleton className="h-4 w-full mb-6" />
                  <div className="space-y-4">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-4 w-5/6" />
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-[hsl(var(--nexguard-dark))]/50 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20">
                <CardContent className="p-6">
                  <Skeleton className="h-6 w-1/2 mb-4" />
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-4/5" />
                    <Skeleton className="h-4 w-3/4" />
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            developers?.map((developer) => (
              <div key={developer.id} className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Main Profile Card */}
                <Card className="bg-[hsl(var(--nexguard-dark))]/50 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20 hover:border-[hsl(var(--nexguard-cyan))]/50 transition-all duration-300">
                  <CardContent className="p-8">
                    <div className="text-center mb-6">
                      <div className="w-32 h-32 rounded-full overflow-hidden mx-auto mb-4 border-3 border-[hsl(var(--nexguard-cyan))]">
                        <img 
                          src={devAvatar} 
                          alt={`${developer.name} Avatar`} 
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <h3 className="text-2xl font-bold text-white mb-2">{developer.name}</h3>
                      <p className="text-[hsl(var(--nexguard-cyan))] text-lg font-semibold mb-2">{developer.role}</p>
                      {developer.location && (
                        <div className="flex items-center justify-center text-gray-300 mb-2">
                          <MapPin className="w-4 h-4 mr-2" />
                          <span>{developer.location}</span>
                        </div>
                      )}
                      {developer.yearsOfExperience && (
                        <div className="flex items-center justify-center text-gray-300 mb-4">
                          <Calendar className="w-4 h-4 mr-2" />
                          <span>{developer.yearsOfExperience}+ years of experience</span>
                        </div>
                      )}
                    </div>
                    
                    <p className="text-gray-300 text-center mb-6">{developer.bio}</p>
                    
                    <div className="flex justify-center space-x-4 mb-6">
                      {developer.githubUrl && (
                        <a 
                          href={developer.githubUrl} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-gray-400 hover:text-[hsl(var(--nexguard-cyan))] transition-colors"
                        >
                          <SiGithub size={24} />
                        </a>
                      )}
                      {developer.twitterUrl && (
                        <a 
                          href={developer.twitterUrl} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-gray-400 hover:text-[hsl(var(--nexguard-cyan))] transition-colors"
                        >
                          <SiX size={24} />
                        </a>
                      )}
                      {developer.linkedinUrl && (
                        <a 
                          href={developer.linkedinUrl} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-gray-400 hover:text-[hsl(var(--nexguard-cyan))] transition-colors"
                        >
                          <SiLinkedin size={24} />
                        </a>
                      )}
                      {developer.discord && (
                        <div className="flex items-center text-gray-400">
                          <SiDiscord size={24} className="mr-2" />
                          <span className="text-sm">{developer.discord}</span>
                        </div>
                      )}
                    </div>
                    
                    <div className="space-y-4">
                      {developer.email && (
                        <div className="flex items-center text-gray-300">
                          <Mail className="w-4 h-4 mr-3 text-[hsl(var(--nexguard-cyan))]" />
                          <a href={`mailto:${developer.email}`} className="hover:text-[hsl(var(--nexguard-cyan))] transition-colors">
                            {developer.email}
                          </a>
                        </div>
                      )}
                      {developer.website && (
                        <div className="flex items-center text-gray-300">
                          <Globe className="w-4 h-4 mr-3 text-[hsl(var(--nexguard-cyan))]" />
                          <a href={developer.website} target="_blank" rel="noopener noreferrer" className="hover:text-[hsl(var(--nexguard-cyan))] transition-colors">
                            {developer.website}
                          </a>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>

                {/* Skills and Experience Card */}
                <div className="space-y-6">
                  {/* Skills */}
                  <Card className="bg-[hsl(var(--nexguard-dark))]/50 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20">
                    <CardHeader>
                      <CardTitle className="text-[hsl(var(--nexguard-cyan))] flex items-center">
                        <Code className="w-5 h-5 mr-2" />
                        Technical Skills
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-2">
                        {developer.skills?.map((skill, index) => (
                          <Badge key={index} variant="secondary" className="bg-[hsl(var(--nexguard-cyan))]/20 text-[hsl(var(--nexguard-cyan))] border-[hsl(var(--nexguard-cyan))]/30">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Specialties */}
                  <Card className="bg-[hsl(var(--nexguard-dark))]/50 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20">
                    <CardHeader>
                      <CardTitle className="text-[hsl(var(--nexguard-cyan))] flex items-center">
                        <Award className="w-5 h-5 mr-2" />
                        Specialties
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-2">
                        {developer.specialties?.map((specialty, index) => (
                          <Badge key={index} variant="outline" className="border-[hsl(var(--nexguard-cyan))]/50 text-gray-300 hover:bg-[hsl(var(--nexguard-cyan))]/10">
                            {specialty}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Experience */}
                  <Card className="bg-[hsl(var(--nexguard-dark))]/50 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20">
                    <CardHeader>
                      <CardTitle className="text-[hsl(var(--nexguard-cyan))] flex items-center">
                        <Briefcase className="w-5 h-5 mr-2" />
                        Experience
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-300 text-sm leading-relaxed">{developer.experience}</p>
                    </CardContent>
                  </Card>
                </div>

                {/* Achievements */}
                <Card className="bg-[hsl(var(--nexguard-dark))]/50 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20">
                  <CardHeader>
                    <CardTitle className="text-[hsl(var(--nexguard-cyan))] flex items-center">
                      <Award className="w-5 h-5 mr-2" />
                      Key Achievements
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {developer.achievements?.map((achievement, index) => (
                        <li key={index} className="text-gray-300 text-sm flex items-start">
                          <span className="w-2 h-2 bg-[hsl(var(--nexguard-cyan))] rounded-full mt-2 mr-3 flex-shrink-0"></span>
                          {achievement}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>

                {/* Projects */}
                <Card className="bg-[hsl(var(--nexguard-dark))]/50 backdrop-blur-sm border-[hsl(var(--nexguard-cyan))]/20">
                  <CardHeader>
                    <CardTitle className="text-[hsl(var(--nexguard-cyan))] flex items-center">
                      <Code className="w-5 h-5 mr-2" />
                      Notable Projects
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {developer.projects?.map((project, index) => (
                        <li key={index} className="text-gray-300 text-sm flex items-start">
                          <span className="w-2 h-2 bg-[hsl(var(--nexguard-cyan))] rounded-full mt-2 mr-3 flex-shrink-0"></span>
                          {project}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              </div>
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
                  href="https://discord.gg/wpjZMPXaRT"
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
});

export default Developers;

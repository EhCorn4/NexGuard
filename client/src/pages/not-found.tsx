import { Card, CardContent } from "@/components/ui/card";
import { AlertCircle } from "lucide-react";
import nexguardIcon from "@assets/file_0000000003fc61f58b4fd114190f81c9_1751936993313.png";

export default function NotFound() {
  return (
    <div className="min-h-screen hero-gradient circuit-pattern flex items-center justify-center relative overflow-hidden">
      <div 
        className="absolute inset-0 bg-center opacity-20" 
        style={{ 
          backgroundImage: `url(${nexguardIcon})`,
          backgroundSize: '400px 400px',
          backgroundRepeat: 'no-repeat'
        }}
      ></div>
      <div className="absolute inset-0 bg-gradient-to-r from-[hsl(var(--nexguard-cyan))]/5 to-[hsl(var(--nexguard-purple))]/5 animate-pulse-slow"></div>
      <div className="relative z-10">
      <Card className="w-full max-w-md mx-4">
        <CardContent className="pt-6">
          <div className="flex mb-4 gap-2">
            <AlertCircle className="h-8 w-8 text-red-500" />
            <h1 className="text-2xl font-bold text-gray-900">404 Page Not Found</h1>
          </div>

          <p className="mt-4 text-sm text-gray-600">
            Did you forget to add the page to the router?
          </p>
        </CardContent>
      </Card>
      </div>
    </div>
  );
}

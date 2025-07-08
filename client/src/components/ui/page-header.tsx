import { GradientText } from "@/components/ui/gradient-text";
import nexguardLogo from "@assets/file_00000000ee7c61f7a421642c4ce3b538_1751941112899.png";

interface PageHeaderProps {
  title: string;
  description?: string;
  showLogo?: boolean;
}

export function PageHeader({ title, description, showLogo = true }: PageHeaderProps) {
  return (
    <div className="text-center mb-16 pt-8">
      {showLogo && (
        <div className="mb-8 flex justify-center">
          <img 
            src={nexguardLogo} 
            alt="NexGuard Logo" 
            className="w-24 h-24 md:w-32 md:h-32 object-contain animate-float"
          />
        </div>
      )}
      <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
        <GradientText>{title}</GradientText>
      </h1>
      {description && (
        <p className="text-xl text-gray-300 max-w-3xl mx-auto">
          {description}
        </p>
      )}
    </div>
  );
}
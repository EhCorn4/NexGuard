import { useQuery } from "@tanstack/react-query";
import type { Feature } from "@shared/schema";

function Features() {
  const { data: features, isLoading, error } = useQuery<Feature[]>({
    queryKey: ["/api/features"],
    retry: 3,
  });

  console.log('=== FEATURES DEBUG ===', { 
    isLoading, 
    error: error?.toString(), 
    featuresCount: features?.length,
    firstFeature: features?.[0]?.title
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 pt-24 px-4">
        <div className="container mx-auto">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-white mb-8">Loading Features...</h1>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    console.error('Features query error:', error);
    return (
      <div className="min-h-screen bg-slate-900 pt-24 px-4">
        <div className="container mx-auto">
          <div className="bg-red-600 text-white p-6 rounded-lg max-w-2xl mx-auto">
            <h1 className="text-2xl font-bold mb-4">Error Loading Features</h1>
            <p>Failed to load features: {error.toString()}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!features || features.length === 0) {
    return (
      <div className="min-h-screen bg-slate-900 pt-24 px-4">
        <div className="container mx-auto">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-white mb-8">No Features Found</h1>
            <p className="text-gray-400">No features are currently available.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 pt-24">
      <div className="container mx-auto px-4 py-12">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent mb-6">
            Bot Features
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            NexGuard offers comprehensive Discord bot functionality with 66+ slash commands, 
            enterprise security systems, professional ticket system, and real-time analytics.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div 
              key={feature.id} 
              className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6 hover:bg-slate-800/70 transition-all duration-300 hover:transform hover:scale-105"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="mb-4">
                <div className="w-12 h-12 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg flex items-center justify-center mb-4">
                  <span className="text-white font-bold text-lg">
                    {feature.icon?.charAt(0)?.toUpperCase() || '🔧'}
                  </span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-gray-300 leading-relaxed">{feature.description}</p>
              </div>

              {feature.benefits && feature.benefits.length > 0 && (
                <div className="mt-4 space-y-2">
                  <h4 className="text-sm font-medium text-cyan-400 mb-2">Key Benefits:</h4>
                  <div className="flex flex-wrap gap-1">
                    {feature.benefits.map((benefit, idx) => (
                      <span 
                        key={idx}
                        className="inline-block bg-slate-700/50 text-xs px-2 py-1 rounded text-gray-300"
                      >
                        {benefit}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Stats Section */}
        <div className="mt-16 text-center">
          <div className="inline-flex items-center gap-4 bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-lg px-6 py-3">
            <div className="w-2 h-2 rounded-full animate-pulse bg-green-400"></div>
            <span className="text-sm text-gray-300">Bot Online & Ready</span>
            <div className="w-px h-4 bg-slate-600"></div>
            <span className="text-sm text-cyan-400">66+ Commands</span>
            <div className="w-px h-4 bg-slate-600"></div>
            <span className="text-sm text-cyan-400">20+ Servers</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Features;

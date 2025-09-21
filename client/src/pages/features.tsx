import { useQuery } from "@tanstack/react-query";

function Features() {
  console.log('FEATURES COMPONENT LOADED!!!');
  
  const { data: features, isLoading, error } = useQuery({
    queryKey: ["/api/features"],
    retry: false,
  });

  console.log('FEATURES DATA:', { isLoading, error, features: features?.length });

  if (error) {
    console.error('ERROR:', error);
    return (
      <div className="min-h-screen bg-red-900 text-white p-8">
        <h1>ERROR DETECTED</h1>
        <p>{String(error)}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-green-500 text-white p-8">
      <h1 className="text-6xl mb-8">FEATURES PAGE WORKING!</h1>
      <div className="bg-white text-black p-4 rounded mb-4">
        <p>Loading: {isLoading ? 'YES' : 'NO'}</p>
        <p>Error: {error ? 'YES' : 'NO'}</p>
        <p>Features count: {features?.length || 0}</p>
      </div>
      
      {features && features.map((feature) => (
        <div key={feature.id} className="bg-white text-black p-4 mb-2 rounded">
          <h3>{feature.title}</h3>
          <p>{feature.description}</p>
        </div>
      ))}
    </div>
  );
}

export default Features;

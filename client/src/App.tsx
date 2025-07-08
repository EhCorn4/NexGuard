import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import Home from "@/pages/home";
import Features from "@/pages/features";
import Invite from "@/pages/invite";
import Developers from "@/pages/developers";
import Community from "@/pages/community";
import NotFound from "@/pages/not-found";

function Router() {
  return (
    <div className="min-h-screen bg-[hsl(var(--nexguard-dark))] text-white">
      <Navbar />
      <main>
        <Switch>
          <Route path="/" component={Home} />
          <Route path="/features" component={Features} />
          <Route path="/invite" component={Invite} />
          <Route path="/developers" component={Developers} />
          <Route path="/community" component={Community} />
          <Route component={NotFound} />
        </Switch>
      </main>
      <Footer />
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Router />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;

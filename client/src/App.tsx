import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ThemeProvider } from "@/components/theme-provider";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import Home from "@/pages/home";
import Features from "@/pages/features";
import Invite from "@/pages/invite";
import Developers from "@/pages/developers";
import Community from "@/pages/community";
import Testimonials from "@/pages/testimonials";
import Feedback from "@/pages/feedback";
import Docs from "@/pages/docs";
import NotFound from "@/pages/not-found";

function Router() {
  return (
    <div className="min-h-screen bg-[hsl(var(--nexguard-dark))] text-foreground transition-colors duration-300">
      <Navbar />
      <main>
        <Switch>
          <Route path="/" component={Home} />
          <Route path="/features" component={Features} />
          <Route path="/invite" component={Invite} />
          <Route path="/developers" component={Developers} />
          <Route path="/community" component={Community} />
          <Route path="/testimonials" component={Testimonials} />
          <Route path="/feedback" component={Feedback} />
          <Route path="/docs" component={Docs} />
          <Route component={NotFound} />
        </Switch>
      </main>
      <Footer />
    </div>
  );
}

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="nexguard-ui-theme">
      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <Router />
          <Toaster />
        </TooltipProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;

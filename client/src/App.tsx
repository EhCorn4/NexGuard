import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ThemeProvider } from "@/components/theme-provider";
import { Navbar } from "@/components/layout/navbar";
import { useScrollToTop } from "@/hooks/use-scroll-to-top";
import { Footer } from "@/components/layout/footer";
import { ErrorBoundary } from "@/components/ui/error-boundary";
import { PerformanceWrapper } from "@/components/optimized/performance-wrapper";
import { Suspense, lazy } from "react";

// Lazy load pages for better performance
const Home = lazy(() => import("@/pages/home"));
const Features = lazy(() => import("@/pages/features"));
const Invite = lazy(() => import("@/pages/invite"));
const Developers = lazy(() => import("@/pages/developers"));
const Community = lazy(() => import("@/pages/community"));
const Testimonials = lazy(() => import("@/pages/testimonials"));
const Feedback = lazy(() => import("@/pages/feedback"));
const Docs = lazy(() => import("@/pages/docs"));
const NotFound = lazy(() => import("@/pages/not-found"));

function Router() {
  // Enable smooth scrolling to top on page navigation
  useScrollToTop();
  
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-[hsl(var(--nexguard-dark))] text-foreground transition-colors duration-300">
        <Navbar />
        <main role="main">
          <Switch>
            <Route path="/" component={() => (
              <PerformanceWrapper skeletonType="grid" skeletonCount={1}>
                <Home />
              </PerformanceWrapper>
            )} />
            <Route path="/features" component={() => (
              <PerformanceWrapper skeletonType="grid" skeletonCount={6}>
                <Features />
              </PerformanceWrapper>
            )} />
            <Route path="/invite" component={() => (
              <PerformanceWrapper skeletonType="card" skeletonCount={3}>
                <Invite />
              </PerformanceWrapper>
            )} />
            <Route path="/developers" component={() => (
              <PerformanceWrapper skeletonType="card" skeletonCount={1}>
                <Developers />
              </PerformanceWrapper>
            )} />
            <Route path="/community" component={() => (
              <PerformanceWrapper skeletonType="grid" skeletonCount={6}>
                <Community />
              </PerformanceWrapper>
            )} />
            <Route path="/testimonials" component={() => (
              <PerformanceWrapper skeletonType="grid" skeletonCount={4}>
                <Testimonials />
              </PerformanceWrapper>
            )} />
            <Route path="/feedback" component={() => (
              <PerformanceWrapper skeletonType="card" skeletonCount={2}>
                <Feedback />
              </PerformanceWrapper>
            )} />
            <Route path="/docs" component={() => (
              <PerformanceWrapper skeletonType="list" skeletonCount={5}>
                <Docs />
              </PerformanceWrapper>
            )} />
            <Route component={() => (
              <PerformanceWrapper skeletonType="card" skeletonCount={1}>
                <NotFound />
              </PerformanceWrapper>
            )} />
          </Switch>
        </main>
        <Footer />
      </div>
    </ErrorBoundary>
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

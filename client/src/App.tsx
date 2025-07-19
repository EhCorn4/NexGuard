import { Switch, Route, useLocation } from "wouter";
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
import { PageTransition } from "@/components/ui/page-transition";
import { Suspense, lazy } from "react";
import { AnimatePresence } from "framer-motion";

// Lazy load pages for better performance
const Home = lazy(() => import("@/pages/home"));
const Features = lazy(() => import("@/pages/features"));
const Invite = lazy(() => import("@/pages/invite"));
const Developers = lazy(() => import("@/pages/developers"));
const Community = lazy(() => import("@/pages/community"));
const Testimonials = lazy(() => import("@/pages/testimonials"));
const Feedback = lazy(() => import("@/pages/feedback"));
const FAQ = lazy(() => import("@/pages/faq"));
const Docs = lazy(() => import("@/pages/docs"));
const Analytics = lazy(() => import("@/pages/analytics"));
const Donate = lazy(() => import("@/pages/donate"));
// Dashboard functionality removed
const TermsOfService = lazy(() => import("@/pages/terms-of-service"));
const PrivacyPolicy = lazy(() => import("@/pages/privacy-policy"));
const CookiesPolicy = lazy(() => import("@/pages/cookies-policy"));
const Contact = lazy(() => import("@/pages/contact"));
const NotFound = lazy(() => import("@/pages/not-found"));

function Router() {
  // Enable smooth scrolling to top on page navigation
  useScrollToTop();
  const [location] = useLocation();
  
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-background text-foreground transition-colors duration-300">
        <Navbar />
        <main role="main">
          <AnimatePresence mode="wait" initial={false}>
            <Switch key={location}>
              <Route path="/" component={() => (
                <PageTransition key="home">
                  <PerformanceWrapper skeletonType="grid" skeletonCount={1}>
                    <Home />
                  </PerformanceWrapper>
                </PageTransition>
              )} />
              <Route path="/features" component={() => (
                <PageTransition key="features">
                  <PerformanceWrapper skeletonType="grid" skeletonCount={6}>
                    <Features />
                  </PerformanceWrapper>
                </PageTransition>
              )} />
              <Route path="/invite" component={() => (
                <PageTransition key="invite">
                  <PerformanceWrapper skeletonType="card" skeletonCount={3}>
                    <Invite />
                  </PerformanceWrapper>
                </PageTransition>
              )} />
              <Route path="/developers" component={() => (
                <PageTransition key="developers">
                  <PerformanceWrapper skeletonType="card" skeletonCount={1}>
                    <Developers />
                  </PerformanceWrapper>
                </PageTransition>
              )} />
              <Route path="/community" component={() => (
                <PageTransition key="community">
                  <PerformanceWrapper skeletonType="grid" skeletonCount={6}>
                    <Community />
                  </PerformanceWrapper>
                </PageTransition>
              )} />
              <Route path="/testimonials" component={() => (
                <PageTransition key="testimonials">
                  <PerformanceWrapper skeletonType="grid" skeletonCount={4}>
                    <Testimonials />
                  </PerformanceWrapper>
                </PageTransition>
              )} />
              <Route path="/feedback" component={() => (
                <PageTransition key="feedback">
                  <PerformanceWrapper skeletonType="card" skeletonCount={2}>
                    <Feedback />
                  </PerformanceWrapper>
                </PageTransition>
              )} />
              <Route path="/faq" component={() => (
                <PageTransition key="faq">
                  <PerformanceWrapper skeletonType="grid" skeletonCount={5}>
                    <FAQ />
                  </PerformanceWrapper>
                </PageTransition>
              )} />
              <Route path="/docs" component={() => (
                <PageTransition key="docs">
                  <PerformanceWrapper skeletonType="list" skeletonCount={5}>
                    <Docs />
                  </PerformanceWrapper>
                </PageTransition>
              )} />
              <Route path="/analytics" component={() => (
                <PageTransition key="analytics">
                  <PerformanceWrapper skeletonType="grid" skeletonCount={8}>
                    <Analytics />
                  </PerformanceWrapper>
                </PageTransition>
              )} />
              <Route path="/donate" component={() => (
                <PageTransition key="donate">
                  <PerformanceWrapper skeletonType="grid" skeletonCount={6}>
                    <Donate />
                  </PerformanceWrapper>
                </PageTransition>
              )} />
              {/* Dashboard functionality removed */}
              <Route path="/terms-of-service" component={() => (
                <PageTransition key="terms-of-service">
                  <PerformanceWrapper skeletonType="card" skeletonCount={1}>
                    <TermsOfService />
                  </PerformanceWrapper>
                </PageTransition>
              )} />
              <Route path="/privacy-policy" component={() => (
                <PageTransition key="privacy-policy">
                  <PerformanceWrapper skeletonType="card" skeletonCount={1}>
                    <PrivacyPolicy />
                  </PerformanceWrapper>
                </PageTransition>
              )} />
              <Route path="/cookies-policy" component={() => (
                <PageTransition key="cookies-policy">
                  <PerformanceWrapper skeletonType="card" skeletonCount={1}>
                    <CookiesPolicy />
                  </PerformanceWrapper>
                </PageTransition>
              )} />
              <Route path="/contact" component={() => (
                <PageTransition key="contact">
                  <PerformanceWrapper skeletonType="card" skeletonCount={1}>
                    <Contact />
                  </PerformanceWrapper>
                </PageTransition>
              )} />
              <Route component={() => (
                <PageTransition key="notfound">
                  <PerformanceWrapper skeletonType="card" skeletonCount={1}>
                    <NotFound />
                  </PerformanceWrapper>
                </PageTransition>
              )} />
            </Switch>
          </AnimatePresence>
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

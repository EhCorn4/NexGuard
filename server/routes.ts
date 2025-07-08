import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";

export async function registerRoutes(app: Express): Promise<Server> {
  // API routes for NexGuard website
  app.get("/api/news", async (req, res) => {
    try {
      const news = await storage.getNewsUpdates();
      res.json(news);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch news updates" });
    }
  });

  app.get("/api/developers", async (req, res) => {
    try {
      const developers = await storage.getDevelopers();
      res.json(developers);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch developers" });
    }
  });

  app.get("/api/features", async (req, res) => {
    try {
      const features = await storage.getFeatures();
      res.json(features);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch features" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}

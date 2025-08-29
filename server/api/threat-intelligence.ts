import { db } from '../db';
import { threatIntelligence, attackPatterns, behavioralProfiles, threatAlerts, crossServerIntelligence } from '@shared/schema';
import { eq, desc, and, gte } from 'drizzle-orm';

export interface ThreatIntelligenceAPI {
  // Get threat analysis for specific user
  getUserThreatScore(userId: string, guildId: string): Promise<{
    threatScore: number;
    riskLevel: string;
    riskFactors: string[];
    lastAssessment: Date;
  }>;
  
  // Get active threats for guild
  getActiveThreatsByGuild(guildId: string): Promise<Array<{
    id: number;
    threatType: string;
    threatScore: number;
    affectedUsers: string[];
    detectedAt: Date;
    actionTaken: string | null;
  }>>;
  
  // Get attack patterns
  getAttackPatterns(): Promise<Array<{
    id: number;
    patternName: string;
    patternType: string;
    description: string;
    severity: number;
    occurrenceCount: number;
    lastSeen: Date;
  }>>;
  
  // Get cross-server intelligence
  getCrossServerIntelligence(userId?: string): Promise<Array<{
    id: number;
    userId: string;
    threatSignature: string;
    guildsAffected: string[];
    threatLevel: number;
    sharedAt: Date;
  }>>;
  
  // Get threat alerts
  getThreatAlerts(guildId: string, severity?: string): Promise<Array<{
    id: number;
    alertType: string;
    severity: string;
    threatDescription: string;
    affectedUsers: string[];
    alertedAt: Date;
    resolvedAt: Date | null;
  }>>;
  
  // Analytics endpoints
  getThreatTrends(guildId: string, days: number): Promise<{
    totalThreats: number;
    threatsByType: Record<string, number>;
    threatsByDay: Array<{
      date: string;
      count: number;
    }>;
    severityDistribution: Record<string, number>;
  }>;
}

export class ThreatIntelligenceService implements ThreatIntelligenceAPI {
  
  async getUserThreatScore(userId: string, guildId: string) {
    try {
      const [latestThreat] = await db.select()
        .from(threatIntelligence)
        .where(and(
          eq(threatIntelligence.userId, userId),
          eq(threatIntelligence.guildId, guildId),
          eq(threatIntelligence.isActive, true)
        ))
        .orderBy(desc(threatIntelligence.detectedAt))
        .limit(1);

      if (!latestThreat) {
        return {
          threatScore: 0,
          riskLevel: 'low',
          riskFactors: [],
          lastAssessment: new Date()
        };
      }

      const riskLevel = latestThreat.threatScore > 70 ? 'high' : 
                       latestThreat.threatScore > 40 ? 'medium' : 'low';

      return {
        threatScore: latestThreat.threatScore,
        riskLevel,
        riskFactors: latestThreat.riskFactors || [],
        lastAssessment: latestThreat.detectedAt
      };
    } catch (error) {
      console.error('Error getting user threat score:', error);
      throw error;
    }
  }

  async getActiveThreatsByGuild(guildId: string) {
    try {
      const threats = await db.select()
        .from(threatIntelligence)
        .where(and(
          eq(threatIntelligence.guildId, guildId),
          eq(threatIntelligence.isActive, true)
        ))
        .orderBy(desc(threatIntelligence.detectedAt));

      return threats.map(threat => ({
        id: threat.id,
        threatType: threat.threatType,
        threatScore: threat.threatScore,
        affectedUsers: [threat.userId],
        detectedAt: threat.detectedAt,
        actionTaken: threat.actionTaken
      }));
    } catch (error) {
      console.error('Error getting active threats:', error);
      throw error;
    }
  }

  async getAttackPatterns() {
    try {
      const patterns = await db.select()
        .from(attackPatterns)
        .orderBy(desc(attackPatterns.lastSeen));

      return patterns.map(pattern => ({
        id: pattern.id,
        patternName: pattern.patternName,
        patternType: pattern.patternType,
        description: pattern.description,
        severity: pattern.severity,
        occurrenceCount: pattern.occurrenceCount,
        lastSeen: pattern.lastSeen
      }));
    } catch (error) {
      console.error('Error getting attack patterns:', error);
      throw error;
    }
  }

  async getCrossServerIntelligence(userId?: string) {
    try {
      let query = db.select().from(crossServerIntelligence);
      
      if (userId) {
        query = query.where(eq(crossServerIntelligence.userId, userId));
      }

      const intelligence = await query.orderBy(desc(crossServerIntelligence.sharedAt));

      return intelligence.map(intel => ({
        id: intel.id,
        userId: intel.userId,
        threatSignature: intel.threatSignature,
        guildsAffected: intel.guildsAffected || [],
        threatLevel: intel.threatLevel,
        sharedAt: intel.sharedAt
      }));
    } catch (error) {
      console.error('Error getting cross-server intelligence:', error);
      throw error;
    }
  }

  async getThreatAlerts(guildId: string, severity?: string) {
    try {
      let query = db.select()
        .from(threatAlerts)
        .where(eq(threatAlerts.guildId, guildId));
      
      if (severity) {
        query = query.where(and(
          eq(threatAlerts.guildId, guildId),
          eq(threatAlerts.severity, severity)
        ));
      }

      const alerts = await query.orderBy(desc(threatAlerts.alertedAt));

      return alerts.map(alert => ({
        id: alert.id,
        alertType: alert.alertType,
        severity: alert.severity,
        threatDescription: alert.threatDescription,
        affectedUsers: alert.affectedUsers || [],
        alertedAt: alert.alertedAt,
        resolvedAt: alert.resolvedAt
      }));
    } catch (error) {
      console.error('Error getting threat alerts:', error);
      throw error;
    }
  }

  async getThreatTrends(guildId: string, days: number = 30) {
    try {
      const since = new Date();
      since.setDate(since.getDate() - days);

      const threats = await db.select()
        .from(threatIntelligence)
        .where(and(
          eq(threatIntelligence.guildId, guildId),
          gte(threatIntelligence.detectedAt, since)
        ))
        .orderBy(desc(threatIntelligence.detectedAt));

      const alerts = await db.select()
        .from(threatAlerts)
        .where(and(
          eq(threatAlerts.guildId, guildId),
          gte(threatAlerts.alertedAt, since)
        ));

      // Calculate trends
      const totalThreats = threats.length;
      
      // Threats by type
      const threatsByType: Record<string, number> = {};
      threats.forEach(threat => {
        threatsByType[threat.threatType] = (threatsByType[threat.threatType] || 0) + 1;
      });

      // Threats by day
      const threatsByDay: Array<{ date: string; count: number }> = [];
      const dayMap: Record<string, number> = {};
      
      threats.forEach(threat => {
        const date = threat.detectedAt.toISOString().split('T')[0];
        dayMap[date] = (dayMap[date] || 0) + 1;
      });

      Object.entries(dayMap).forEach(([date, count]) => {
        threatsByDay.push({ date, count });
      });

      // Severity distribution from alerts
      const severityDistribution: Record<string, number> = {};
      alerts.forEach(alert => {
        severityDistribution[alert.severity] = (severityDistribution[alert.severity] || 0) + 1;
      });

      return {
        totalThreats,
        threatsByType,
        threatsByDay: threatsByDay.sort((a, b) => a.date.localeCompare(b.date)),
        severityDistribution
      };
    } catch (error) {
      console.error('Error getting threat trends:', error);
      throw error;
    }
  }
}

export const threatIntelligenceService = new ThreatIntelligenceService();
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Send, Plus, Calendar, Tag, FileText, ExternalLink } from "lucide-react";
import { apiRequest } from '@/lib/queryClient';

interface Changelog {
  id: number;
  version: string;
  title: string;
  description: string;
  changes: string[];
  type: 'major' | 'minor' | 'patch' | 'hotfix';
  releaseDate: string;
  isPublished: boolean;
}

export default function ChangelogManager() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [showNewForm, setShowNewForm] = useState(false);
  const [newChangelog, setNewChangelog] = useState({
    version: '',
    title: '',
    description: '',
    changes: [''],
    type: 'minor' as const
  });

  // Fetch changelogs
  const { data: changelogs = [], isLoading } = useQuery<Changelog[]>({
    queryKey: ['/api/changelogs'],
  });

  // Publish latest changelog
  const publishLatestMutation = useMutation({
    mutationFn: () => 
      fetch('/api/changelog/publish/latest', { method: 'POST' })
        .then(res => res.json()),
    onSuccess: () => {
      toast({
        title: "Success!",
        description: "Latest changelog published to Discord successfully",
      });
      queryClient.invalidateQueries({ queryKey: ['/api/changelogs'] });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to publish changelog",
        variant: "destructive",
      });
    },
  });

  // Publish specific version
  const publishVersionMutation = useMutation({
    mutationFn: (version: string) => 
      fetch(`/api/changelog/publish/${version}`, { method: 'POST' })
        .then(res => res.json()),
    onSuccess: (_, version) => {
      toast({
        title: "Success!",
        description: `Changelog v${version} published to Discord successfully`,
      });
      queryClient.invalidateQueries({ queryKey: ['/api/changelogs'] });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to publish changelog",
        variant: "destructive",
      });
    },
  });

  // Create and publish custom changelog
  const createChangelogMutation = useMutation({
    mutationFn: (data: typeof newChangelog) => 
      fetch('/api/changelog/publish/custom', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...data,
          changes: data.changes.filter(c => c.trim() !== '')
        })
      }).then(res => res.json()),
    onSuccess: () => {
      toast({
        title: "Success!",
        description: "Changelog created and published to Discord successfully",
      });
      setShowNewForm(false);
      setNewChangelog({
        version: '',
        title: '',
        description: '',
        changes: [''],
        type: 'minor'
      });
      queryClient.invalidateQueries({ queryKey: ['/api/changelogs'] });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to create changelog",
        variant: "destructive",
      });
    },
  });

  const handleAddChange = () => {
    setNewChangelog(prev => ({
      ...prev,
      changes: [...prev.changes, '']
    }));
  };

  const handleRemoveChange = (index: number) => {
    setNewChangelog(prev => ({
      ...prev,
      changes: prev.changes.filter((_, i) => i !== index)
    }));
  };

  const handleChangeUpdate = (index: number, value: string) => {
    setNewChangelog(prev => ({
      ...prev,
      changes: prev.changes.map((change, i) => i === index ? value : change)
    }));
  };

  const getTypeColor = (type: string) => {
    const colors = {
      major: 'bg-red-500',
      minor: 'bg-blue-500',
      patch: 'bg-green-500',
      hotfix: 'bg-orange-500'
    };
    return colors[type as keyof typeof colors] || 'bg-gray-500';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Changelog Manager</h1>
        <p className="text-muted-foreground">
          Create and publish changelogs to Discord channel automatically
        </p>
      </div>

      {/* Action Buttons */}
      <div className="mb-6 space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Publish changelogs to Discord channel: 1389986013404991498
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            <Button
              onClick={() => publishLatestMutation.mutate()}
              disabled={publishLatestMutation.isPending}
              className="gap-2"
            >
              {publishLatestMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              <Send className="h-4 w-4" />
              Publish Latest
            </Button>
            <Button
              variant="outline"
              onClick={() => setShowNewForm(!showNewForm)}
              className="gap-2"
            >
              <Plus className="h-4 w-4" />
              Create New
            </Button>
          </CardContent>
        </Card>

        {/* New Changelog Form */}
        {showNewForm && (
          <Card>
            <CardHeader>
              <CardTitle>Create New Changelog</CardTitle>
              <CardDescription>
                Create and immediately publish a new changelog to Discord
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Version</label>
                  <Input
                    placeholder="e.g., 2.3.3"
                    value={newChangelog.version}
                    onChange={(e) => setNewChangelog(prev => ({ ...prev, version: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Type</label>
                  <Select 
                    value={newChangelog.type} 
                    onValueChange={(value) => setNewChangelog(prev => ({ ...prev, type: value as any }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="major">Major</SelectItem>
                      <SelectItem value="minor">Minor</SelectItem>
                      <SelectItem value="patch">Patch</SelectItem>
                      <SelectItem value="hotfix">Hotfix</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div>
                <label className="text-sm font-medium mb-2 block">Title</label>
                <Input
                  placeholder="e.g., Enhanced Ticket System"
                  value={newChangelog.title}
                  onChange={(e) => setNewChangelog(prev => ({ ...prev, title: e.target.value }))}
                />
              </div>
              
              <div>
                <label className="text-sm font-medium mb-2 block">Description</label>
                <Textarea
                  placeholder="Brief description of what this update includes..."
                  value={newChangelog.description}
                  onChange={(e) => setNewChangelog(prev => ({ ...prev, description: e.target.value }))}
                  rows={3}
                />
              </div>
              
              <div>
                <label className="text-sm font-medium mb-2 block">Changes</label>
                {newChangelog.changes.map((change, index) => (
                  <div key={index} className="flex gap-2 mb-2">
                    <Input
                      placeholder="Describe a change..."
                      value={change}
                      onChange={(e) => handleChangeUpdate(index, e.target.value)}
                    />
                    {newChangelog.changes.length > 1 && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleRemoveChange(index)}
                      >
                        Remove
                      </Button>
                    )}
                  </div>
                ))}
                <Button variant="outline" size="sm" onClick={handleAddChange}>
                  Add Change
                </Button>
              </div>
              
              <div className="flex gap-2">
                <Button
                  onClick={() => createChangelogMutation.mutate(newChangelog)}
                  disabled={createChangelogMutation.isPending || !newChangelog.version || !newChangelog.title}
                  className="gap-2"
                >
                  {createChangelogMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                  <Send className="h-4 w-4" />
                  Create & Publish
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setShowNewForm(false)}
                >
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Existing Changelogs */}
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold">Existing Changelogs</h2>
        
        {changelogs.length === 0 ? (
          <Card>
            <CardContent className="text-center py-8">
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">No changelogs found</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {changelogs.map((changelog) => (
              <Card key={changelog.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <CardTitle className="text-xl">v{changelog.version} - {changelog.title}</CardTitle>
                      <Badge className={getTypeColor(changelog.type)}>
                        {changelog.type.toUpperCase()}
                      </Badge>
                      {changelog.isPublished && (
                        <Badge variant="secondary">
                          <ExternalLink className="h-3 w-3 mr-1" />
                          Published
                        </Badge>
                      )}
                    </div>
                    {!changelog.isPublished && (
                      <Button
                        size="sm"
                        onClick={() => publishVersionMutation.mutate(changelog.version)}
                        disabled={publishVersionMutation.isPending}
                        className="gap-2"
                      >
                        {publishVersionMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                        <Send className="h-4 w-4" />
                        Publish
                      </Button>
                    )}
                  </div>
                  <CardDescription className="flex items-center gap-4">
                    <span className="flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      {new Date(changelog.releaseDate).toLocaleDateString()}
                    </span>
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-4">{changelog.description}</p>
                  <div>
                    <h4 className="font-medium mb-2">Changes:</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm">
                      {changelog.changes.map((change, index) => (
                        <li key={index}>{change}</li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
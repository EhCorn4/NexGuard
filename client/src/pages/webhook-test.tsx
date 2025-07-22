import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";

export default function WebhookTest() {
  const [channelId, setChannelId] = useState('1332207898545229978');
  const [message, setMessage] = useState('Hello from my webhook!');
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const sendWebhookMessage = async () => {
    if (!channelId.trim() || !message.trim()) {
      toast({
        title: "Error",
        description: "Please fill in both channel ID and message",
        variant: "destructive"
      });
      return;
    }

    setIsLoading(true);
    try {
      const response = await apiRequest('POST', '/webhook/send', {
        api_key: 'nexguard-fun-webhook',
        channel_id: channelId.trim(),
        content: message
      });

      if (response.ok) {
        const result = await response.json();
        toast({
          title: "Success! 🎉",
          description: result.message || "Message sent successfully!",
        });
        
        // Clear message after successful send
        setMessage('Hello from my webhook!');
      } else {
        const error = await response.json();
        toast({
          title: "Failed to send",
          description: error.message || "Something went wrong",
          variant: "destructive"
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to send webhook message",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
            NexGuard Webhook Tester
          </CardTitle>
          <CardDescription>
            Send messages to your Discord channel easily. No coding required.
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6">
          <div>
            <Label htmlFor="channelId">Discord Channel ID</Label>
            <Input
              id="channelId"
              value={channelId}
              onChange={(e) => setChannelId(e.target.value)}
              placeholder="1332207898545229978"
              className="mt-1"
            />
            <p className="text-sm text-muted-foreground mt-1">
              Right-click a Discord channel → Copy Channel ID
            </p>
          </div>

          <div>
            <Label htmlFor="message">Your Message</Label>
            <Textarea
              id="message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Hello from my webhook!"
              rows={4}
              className="mt-1"
            />
          </div>

          <Button 
            onClick={sendWebhookMessage}
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700"
          >
            {isLoading ? "Sending..." : "Send Message"}
          </Button>

          <div className="bg-muted p-4 rounded-lg">
            <h3 className="font-semibold mb-2">Quick Tips:</h3>
            <ul className="text-sm space-y-1">
              <li>• Make sure NexGuard has permission to send messages in the channel</li>
              <li>• Your channel ID is already filled in from what you provided</li>
              <li>• Messages will be sent directly to your Discord channel</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
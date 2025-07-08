import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { insertFeedbackSchema } from "@shared/schema";
import { MessageSquare, Bug, Lightbulb, HelpCircle, Send } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { z } from "zod";

const feedbackFormSchema = insertFeedbackSchema;

export default function Feedback() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();

  const form = useForm<z.infer<typeof feedbackFormSchema>>({
    resolver: zodResolver(feedbackFormSchema),
    defaultValues: {
      username: "",
      email: "",
      subject: "",
      message: "",
      type: "general"
    }
  });

  const createFeedbackMutation = useMutation({
    mutationFn: async (data: z.infer<typeof feedbackFormSchema>) => {
      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (!response.ok) throw new Error('Failed to submit feedback');
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Success!",
        description: "Your feedback has been submitted. We'll get back to you soon!",
      });
      form.reset();
      setIsSubmitting(false);
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to submit feedback. Please try again.",
        variant: "destructive"
      });
      setIsSubmitting(false);
    }
  });

  const onSubmit = (data: z.infer<typeof feedbackFormSchema>) => {
    setIsSubmitting(true);
    createFeedbackMutation.mutate(data);
  };

  const feedbackTypes = [
    { value: "bug", label: "Bug Report", icon: Bug, description: "Report a bug or issue" },
    { value: "feature", label: "Feature Request", icon: Lightbulb, description: "Suggest a new feature" },
    { value: "general", label: "General Feedback", icon: MessageSquare, description: "General comments or questions" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 pt-20">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent mb-4">
              Feedback & Support
            </h1>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Help us improve NexGuard by sharing your feedback, reporting bugs, or suggesting new features
            </p>
          </div>

          <div className="grid gap-8 lg:grid-cols-2">
            {/* Feedback Types */}
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold text-white mb-4">How can we help?</h2>
              {feedbackTypes.map((type) => (
                <Card key={type.value} className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-colors">
                  <CardHeader className="pb-3">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-lg">
                        <type.icon className="w-6 h-6 text-cyan-400" />
                      </div>
                      <div>
                        <CardTitle className="text-lg font-semibold text-white">
                          {type.label}
                        </CardTitle>
                        <p className="text-sm text-gray-400">{type.description}</p>
                      </div>
                    </div>
                  </CardHeader>
                </Card>
              ))}

              <Card className="bg-slate-800/50 border-slate-700 mt-6">
                <CardHeader>
                  <CardTitle className="text-white flex items-center space-x-2">
                    <HelpCircle className="w-5 h-5 text-cyan-400" />
                    <span>Need Immediate Help?</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-gray-300">
                    For urgent issues or quick questions, you can also reach out to us directly:
                  </p>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center space-x-2">
                      <MessageSquare className="w-4 h-4 text-purple-400" />
                      <span className="text-gray-300">Discord: Join our support server</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <MessageSquare className="w-4 h-4 text-purple-400" />
                      <span className="text-gray-300">Email: nexguards@gmail.com</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Feedback Form */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Submit Feedback</CardTitle>
              </CardHeader>
              <CardContent>
                <Form {...form}>
                  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                    <FormField
                      control={form.control}
                      name="username"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-gray-300">Username</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              placeholder="Your Discord username"
                              className="bg-slate-700 border-slate-600 text-white placeholder:text-gray-400"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="email"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-gray-300">Email</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              type="email"
                              placeholder="your.email@example.com"
                              className="bg-slate-700 border-slate-600 text-white placeholder:text-gray-400"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="type"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-gray-300">Feedback Type</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                                <SelectValue placeholder="Select feedback type" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent className="bg-slate-700 border-slate-600">
                              <SelectItem value="bug">🐛 Bug Report</SelectItem>
                              <SelectItem value="feature">💡 Feature Request</SelectItem>
                              <SelectItem value="general">💬 General Feedback</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="subject"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-gray-300">Subject</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              placeholder="Brief description of your feedback"
                              className="bg-slate-700 border-slate-600 text-white placeholder:text-gray-400"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="message"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-gray-300">Message</FormLabel>
                          <FormControl>
                            <Textarea
                              {...field}
                              placeholder="Please provide detailed information about your feedback..."
                              className="bg-slate-700 border-slate-600 text-white placeholder:text-gray-400 min-h-[120px]"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <Button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white border-0"
                    >
                      {isSubmitting ? (
                        'Submitting...'
                      ) : (
                        <>
                          <Send className="w-4 h-4 mr-2" />
                          Send Feedback
                        </>
                      )}
                    </Button>
                  </form>
                </Form>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
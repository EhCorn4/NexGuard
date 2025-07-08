import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { queryClient } from "@/lib/queryClient";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { insertTestimonialSchema, type Testimonial } from "@shared/schema";
import { Star, Quote, MessageCircle, Plus } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { z } from "zod";

const testimonialFormSchema = insertTestimonialSchema.extend({
  rating: z.number().min(1).max(5)
});

export default function Testimonials() {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const { toast } = useToast();

  const { data: testimonials, isLoading } = useQuery<Testimonial[]>({
    queryKey: ['/api/testimonials'],
  });

  const form = useForm<z.infer<typeof testimonialFormSchema>>({
    resolver: zodResolver(testimonialFormSchema),
    defaultValues: {
      username: "",
      serverName: "",
      content: "",
      rating: 5
    }
  });

  const createTestimonialMutation = useMutation({
    mutationFn: async (data: z.infer<typeof testimonialFormSchema>) => {
      const response = await fetch('/api/testimonials', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (!response.ok) throw new Error('Failed to submit testimonial');
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Success!",
        description: "Your testimonial has been submitted and is pending approval.",
      });
      form.reset();
      setIsDialogOpen(false);
      queryClient.invalidateQueries({ queryKey: ['/api/testimonials'] });
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to submit testimonial. Please try again.",
        variant: "destructive"
      });
    }
  });

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${i < rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`}
      />
    ));
  };

  const onSubmit = (data: z.infer<typeof testimonialFormSchema>) => {
    createTestimonialMutation.mutate(data);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 pt-20">
        <div className="container mx-auto px-4 py-12">
          <div className="text-center text-white">Loading testimonials...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 pt-20">
      <div className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent mb-4">
            Community Testimonials
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto mb-8">
            See what server owners and moderators are saying about NexGuard
          </p>
          
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white border-0">
                <Plus className="w-4 h-4 mr-2" />
                Share Your Experience
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px] bg-slate-800 border-slate-700">
              <DialogHeader>
                <DialogTitle className="text-white">Share Your Testimonial</DialogTitle>
              </DialogHeader>
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
                    name="serverName"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-gray-300">Server Name</FormLabel>
                        <FormControl>
                          <Input
                            {...field}
                            placeholder="Your Discord server name"
                            className="bg-slate-700 border-slate-600 text-white placeholder:text-gray-400"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="rating"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-gray-300">Rating</FormLabel>
                        <Select onValueChange={(value) => field.onChange(parseInt(value))} defaultValue={field.value?.toString()}>
                          <FormControl>
                            <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                              <SelectValue placeholder="Select a rating" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent className="bg-slate-700 border-slate-600">
                            <SelectItem value="5">⭐⭐⭐⭐⭐ (5 stars)</SelectItem>
                            <SelectItem value="4">⭐⭐⭐⭐ (4 stars)</SelectItem>
                            <SelectItem value="3">⭐⭐⭐ (3 stars)</SelectItem>
                            <SelectItem value="2">⭐⭐ (2 stars)</SelectItem>
                            <SelectItem value="1">⭐ (1 star)</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="content"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-gray-300">Your Experience</FormLabel>
                        <FormControl>
                          <Textarea
                            {...field}
                            placeholder="Tell us about your experience with NexGuard..."
                            className="bg-slate-700 border-slate-600 text-white placeholder:text-gray-400 min-h-[100px]"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <div className="flex justify-end space-x-3">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setIsDialogOpen(false)}
                      className="border-slate-600 text-gray-300 hover:bg-slate-700"
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      disabled={createTestimonialMutation.isPending}
                      className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white border-0"
                    >
                      {createTestimonialMutation.isPending ? 'Submitting...' : 'Submit Testimonial'}
                    </Button>
                  </div>
                </form>
              </Form>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {testimonials?.map((testimonial) => (
            <Card key={testimonial.id} className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-colors">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Quote className="w-5 h-5 text-cyan-400" />
                    <div className="flex">
                      {renderStars(testimonial.rating)}
                    </div>
                  </div>
                  <Badge variant="secondary" className="bg-purple-600/20 text-purple-300 border-purple-600/30">
                    {testimonial.serverName}
                  </Badge>
                </div>
                <CardTitle className="text-lg font-semibold text-white">
                  {testimonial.username}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300 leading-relaxed mb-4">
                  {testimonial.content}
                </p>
                <div className="flex items-center justify-between text-sm text-gray-400">
                  <span>
                    {new Date(testimonial.createdAt).toLocaleDateString()}
                  </span>
                  <div className="flex items-center space-x-1">
                    <MessageCircle className="w-4 h-4" />
                    <span>Verified User</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {testimonials?.length === 0 && (
          <div className="text-center py-12">
            <Quote className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 text-lg">
              No testimonials yet. Be the first to share your experience!
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
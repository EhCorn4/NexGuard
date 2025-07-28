import { useEffect } from "react";

interface SEOHeadProps {
  title: string;
  description: string;
  keywords?: string;
  image?: string;
  url?: string;
  type?: "website" | "article";
}

export function SEOHead({ 
  title, 
  description, 
  keywords, 
  image = "/nexguard-logo.png",
  url,
  type = "website" 
}: SEOHeadProps) {
  useEffect(() => {
    // Update document title
    document.title = `${title} | NexGuard - Professional Discord Bot`;
    
    // Update meta tags
    const updateMeta = (name: string, content: string) => {
      const existingTag = document.querySelector(`meta[name="${name}"], meta[property="${name}"]`);
      if (existingTag) {
        existingTag.setAttribute("content", content);
      } else {
        const meta = document.createElement("meta");
        if (name.startsWith("og:") || name.startsWith("twitter:")) {
          meta.setAttribute("property", name);
        } else {
          meta.setAttribute("name", name);
        }
        meta.setAttribute("content", content);
        document.head.appendChild(meta);
      }
    };

    // Basic SEO tags
    updateMeta("description", description);
    if (keywords) updateMeta("keywords", keywords);
    
    // Open Graph tags
    updateMeta("og:title", `${title} | NexGuard`);
    updateMeta("og:description", description);
    updateMeta("og:type", type);
    updateMeta("og:image", image);
    if (url) updateMeta("og:url", url);
    updateMeta("og:site_name", "NexGuard");
    
    // Twitter Card tags
    updateMeta("twitter:card", "summary_large_image");
    updateMeta("twitter:title", `${title} | NexGuard`);
    updateMeta("twitter:description", description);
    updateMeta("twitter:image", image);
    
    // Additional meta tags
    updateMeta("theme-color", "#6366f1");
    updateMeta("robots", "index, follow");
    updateMeta("author", "NexGuard Team");
    
  }, [title, description, keywords, image, url, type]);

  return null;
}
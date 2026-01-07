import markdownIt from "markdown-it";
import pluginSyntaxHighlight from "@11ty/eleventy-plugin-syntaxhighlight";

export default function (eleventyConfig) {

  // ---- site metadata ----
  eleventyConfig.addGlobalData("site", {
    name: "Minimal Eleventy Blog",
    description: "A barebones Eleventy 3 blog with no extras",
    url: "https://bijumon.github.io",
    author: "bijumon"
  });
  // Set the current date
  eleventyConfig.addGlobalData("now", () => new Date());

  eleventyConfig.addPlugin(pluginSyntaxHighlight, {
    preAttributes: { tabindex: 0 }
  });

  // ---- static assets ----
  eleventyConfig.addPassthroughCopy({
    "assets/css": "css",
    "assets/js": "js",
    "assets/img": "img",
    "assets/fonts": "fonts",
    "images": "images",
  });

  eleventyConfig.addWatchTarget("assets/css/*.css");


  eleventyConfig.addShortcode("currentBuildDate", () => {
    return (new Date()).toISOString();
  });

  // ---- date filter (Eleventy 3) ----
  eleventyConfig.addFilter("date", (dateObj, format = "yyyy-MM-dd") => {
    if (!(dateObj instanceof Date)) {
      dateObj = new Date(dateObj);
    }

    if (format === "yyyy") {
      return dateObj.getFullYear();
    }

    return dateObj.toISOString().slice(0, 10);
  });

  // 1. Create the markdown instance
  const md = markdownIt({
    html: true,
    linkify: true,
    typographer: true
  });

  // 2. Tell Eleventy to use this instance for .md files
  eleventyConfig.setLibrary("md", md);

  // 3. Add your filter using that same instance
  eleventyConfig.addFilter("markdown", (content = "") => {
    return md.render(content);
  });

  return {
    dir: {
      input: ".",
      includes: "_includes",
      output: "_site"
    },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk"
  };
}

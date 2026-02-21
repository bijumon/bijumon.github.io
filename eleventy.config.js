import "dotenv/config";
import { feedPlugin } from "@11ty/eleventy-plugin-rss";
import markdownIt from "markdown-it";
import pluginSyntaxHighlight from "@11ty/eleventy-plugin-syntaxhighlight";
import * as lightningcss from "lightningcss";

export default function (eleventyConfig) {

  // Define a CSS bundle with a lightningcss post-processor
  eleventyConfig.addBundle("css", {
    toFileDirectory: "css",
    transforms: [
      async function(content) {
        if (this.type === "css") {
          let { code, map } = lightningcss.transform({
            filename: this.page.inputPath,
            code: Buffer.from(content),
            minify: true,
            sourceMap: true
          });
          
          if (map) {
            let mapBase64 = Buffer.from(JSON.stringify(map)).toString("base64");
            return code.toString() + `\n/*# sourceMappingURL=data:application/json;base64,${mapBase64} */`;
          }
          return code.toString();
        }
        return content;
      }
    ]
  });

  // ---- site metadata ----
  const metadata = {
    title: "Notes",
    description: "tech notes from bijumon @github",
    url: "https://bijumon.github.io",
    author: "bijumon",
    language: "en",
    googleAnalyticsId: process.env.GA_ID
  };
  eleventyConfig.addGlobalData("metadata", metadata);
  
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

  eleventyConfig.addCollection("posts", collection =>
    collection.getAll().filter(item => item.data.layout === "post")
  );

  const feedMetadata = {
    language: metadata.language,
    title: metadata.title,
    subtitle: metadata.description,
    base: metadata.url,
    author: {
      name: metadata.author
    }
  };

  eleventyConfig.addPlugin(feedPlugin, {
    type: "atom",
    outputPath: "/atom.xml",
    //stylesheet: "pretty-atom-feed.xsl",

    templateData: {
      eleventyNavigation: {
        key: "Atom Feed",
        order: 4
      }
    },

    collection: {
      name: "posts",
      limit: 10
    },

    metadata: feedMetadata
  });

  eleventyConfig.addPlugin(feedPlugin, {
    type: "rss",
    outputPath: "/rss.xml",

    templateData: {
      eleventyNavigation: {
        key: "RSS Feed",
        order: 5
      }
    },

    collection: {
      name: "posts",
      limit: 10
    },

    metadata: feedMetadata
  });




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

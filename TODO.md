# Project TODOs & Improvements

## Nunjucks Templates
- [ ] **Extract Hardcoded Index Content**: Move the "recently read" links from `index.njk` into a separate Markdown file or a global data file for better maintenance.
- [ ] **Accessibility (A11y) Improvements**:
    - [ ] Add `aria-hidden="true"` to the decorative "N" logo span.
    - [ ] Wrap "bookmarks" and "recent" links in structured lists (`<ul>`) or use `aria-label` for better screen reader navigation.
- [ ] **RSS/Atom Feed Content**: Ensure the feed plugins are configured to include full post content rather than just metadata.

## CSS & Styling
- [ ] **Contrast Ratio Audit**: Verify that all "rainbow" link colors meet WCAG 2.1 Level AA (4.5:1) standards against both light and dark backgrounds.
- [ ] **Refine Fluid Typography**: Replace multiple media queries in `layout.css` with a single `clamp()` function for smoother, more modern text scaling.
- [ ] **Layout Review**: Evaluate the narrow `max-width` on high-resolution displays; consider a slightly wider container or multi-column layout for the links section.

## Configuration & Performance
- [ ] **Robust Date Filtering**: Update the `date` filter in `eleventy.config.js` to use `Luxon` (already in `node_modules`) for better locale and timezone support.
- [ ] **Image Optimization**: Integrate the `eleventy-img` plugin to automatically generate responsive, next-gen (WebP/AVIF) versions of images in `assets/img` and `images/`.

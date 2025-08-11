## user
i have scss files in the folder _sass with styles.scss being the main file. i want to output to styles.css
## assistant

To compile your SCSS files into a single `styles.css`, you can use the Sass command-line tool. If you haven't installed Sass yet, you can do so with:

```bash
npm install -g sass
```

Once installed, navigate to your project folder where `_sass` and `styles.scss` are located. Then, run this command to compile `styles.scss` to `styles.css`:

```bash
sass _sass/styles.scss styles.css
```

This command will take `styles.scss` as the main file, compile it, and output the result as `styles.css` in the same directory.

### Additional Options

If you want Sass to automatically watch for changes in your SCSS files and recompile `styles.css` each time a file is modified, add the `--watch` flag:

```bash
sass --watch _sass/styles.scss:styles.css
```

This setup will keep your CSS up-to-date while you work.
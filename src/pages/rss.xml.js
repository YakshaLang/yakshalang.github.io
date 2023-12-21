import rss, { pagesGlobToRssItems }  from '@astrojs/rss';

export async function GET(context) {
  return rss({
    title: 'Yaksha Blog',
    description: 'Yaksha Programming Languge Blog',
    site: context.site,
    stylesheet: '/rss/styles.xsl',
    items: await pagesGlobToRssItems(
        import.meta.glob('./blog/*.{md,mdx}'),
      ),
  });
}
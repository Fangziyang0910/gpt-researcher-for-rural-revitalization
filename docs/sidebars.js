/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

 module.exports = {
  docsSidebar: [
    'welcome',
    {
      type: 'category',
      label: 'Getting Started',
      collapsible: true,
      collapsed: false,
      items: [
        'gpt-researcher/getting-started/introduction',
        'gpt-researcher/getting-started/how-to-choose',
        'gpt-researcher/getting-started/getting-started',
        'gpt-researcher/getting-started/cli',
        'gpt-researcher/getting-started/getting-started-with-docker',
        'gpt-researcher/getting-started/linux-deployment',
      ]
    },
    {
      type: 'category',
      label: 'GPT Researcher',
      collapsible: true,
      collapsed: true,
      items: [
        'gpt-researcher/gptr/pip-package',
        'gpt-researcher/gptr/example',
        'gpt-researcher/gptr/config',
        'gpt-researcher/gptr/scraping',
        'gpt-researcher/gptr/handling-logs-as-they-stream',
        'gpt-researcher/gptr/querying-the-backend',
        'gpt-researcher/gptr/automated-tests',
        'gpt-researcher/gptr/troubleshooting',
        'gpt-researcher/gptr/logs'
      ],
    },
    {
      type: 'category',
      label: 'Frontend',
      collapsible: true,
      collapsed: true,
      items: [
        'gpt-researcher/frontend/introduction',
        'gpt-researcher/frontend/nextjs-frontend',
        'gpt-researcher/frontend/vanilla-js-frontend',
        'gpt-researcher/frontend/discord-bot',
        'gpt-researcher/frontend/debugging-websockets'
      ],
    },
    {
      type: 'category',
      label: 'Custom Context',
      collapsible: true,
      collapsed: true,
      items: [
        'gpt-researcher/context/tailored-research',
        'gpt-researcher/context/local-docs',
        'gpt-researcher/context/filtering-by-domain',
        'gpt-researcher/context/vector-stores',
        'gpt-researcher/context/data-ingestion'
        ]
    },
    {
      type: 'category',
      label: 'Handling Logs',
      collapsible: true,
      collapsed: true,
      items: [
        'gpt-researcher/handling-logs/all-about-logs',
        'gpt-researcher/handling-logs/simple-logs-example',
        'gpt-researcher/handling-logs/langsmith-logs'
        ]
    },
    {
      type: 'category',
      label: 'LLM Providers',
      collapsible: true,
      collapsed: true,
      items: [
        'gpt-researcher/llms/llms',
        'gpt-researcher/llms/running-with-ollama',
        'gpt-researcher/llms/testing-your-llm'
      ]
    },
    {
      type: 'category',
      label: 'Search Engines',
      collapsible: true,
      collapsed: true,
      items: [
        'gpt-researcher/search-engines/retrievers',
        'gpt-researcher/search-engines/test-your-retriever'
        ]
    },
    {
      type: 'category',
      label: 'Multi-Agent Frameworks',
      collapsible: true,
      collapsed: true,
      items: [
        'gpt-researcher/multi_agents/langgraph',
        ]
    },
    {'Examples': [{type: 'autogenerated', dirName: 'examples'}]},
    'contribute',
    'roadmap',
    'faq',
  ],
  // pydoc-markdown auto-generated markdowns from docstrings
  referenceSideBar: [require("./docs/reference/sidebar.json")]
};

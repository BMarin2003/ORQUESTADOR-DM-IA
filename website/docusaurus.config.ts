import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'DM-IA',
  tagline: 'Coherencia narrativa: sistema multiagente vs. monolítico',
  favicon: 'img/favicon.ico',
  future: {v4: true},

  url: 'https://bmarin2003.github.io',
  baseUrl: '/ORQUESTADOR-DM-IA/',
  organizationName: 'BMarin2003',
  projectName: 'ORQUESTADOR-DM-IA',

  onBrokenLinks: 'throw',
  markdown: {
    format: 'detect',
    mermaid: true,
    hooks: {onBrokenMarkdownLinks: 'warn'},
  },
  themes: ['@docusaurus/theme-mermaid'],

  i18n: {defaultLocale: 'es', locales: ['es']},

  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/',
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/BMarin2003/ORQUESTADOR-DM-IA/tree/main/website/',
        },
        blog: false,
        theme: {customCss: './src/css/custom.css'},
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'DM-IA',
      items: [
        {type: 'docSidebar', sidebarId: 'docs', position: 'left', label: 'Documentación'},
        {href: 'https://github.com/BMarin2003/ORQUESTADOR-DM-IA', label: 'GitHub', position: 'right'},
      ],
    },
    footer: {
      style: 'dark',
      copyright: 'Tesis de Ingeniería de Sistemas e IA, UPAO 2026 · Marin Yupanqui y Mostacero Cieza',
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'sql', 'powershell', 'bash'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;

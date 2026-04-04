import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import { IBM_Plex_Mono, IBM_Plex_Sans } from 'next/font/google';
import Script from 'next/script';
import './globals.css';

const ibmSans = IBM_Plex_Sans({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-sans'
});

const ibmMono = IBM_Plex_Mono({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  variable: '--font-mono'
});

export const metadata: Metadata = {
  title: 'HirePath Product Dashboard',
  description: 'Single-page product dashboard for ATS, resume optimization, skill gaps, GitHub quality, and job matching.'
};

export default function RootLayout({
  children
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${ibmSans.variable} ${ibmMono.variable}`}>
        <Script id="matchmedia-polyfill" strategy="beforeInteractive">
          {`(function () {
  if (typeof window === 'undefined') return;
  if (!window.matchMedia) {
    window.matchMedia = function (query) {
      return {
        matches: false,
        media: query,
        onchange: null,
        addListener: function () {},
        removeListener: function () {},
        addEventListener: function () {},
        removeEventListener: function () {},
        dispatchEvent: function () { return false; }
      };
    };
    return;
  }
  try {
    var mql = window.matchMedia('(min-width: 1px)');
    if (mql && typeof mql.addListener !== 'function') {
      mql.addListener = function () {};
      mql.removeListener = function () {};
    }
  } catch (e) {}
})();`}
        </Script>
        {children}
      </body>
    </html>
  );
}

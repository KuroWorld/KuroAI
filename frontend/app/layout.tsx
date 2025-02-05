import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Header from '@/components/Header'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: "Kuro's Adventure",
  description: 'An AI-powered cat adventure game',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-slate-900 text-slate-100`}>
        <div className="flex flex-col min-h-screen">
          <Header />
          <div className="flex-grow flex">
            <main className="flex-grow p-4">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  )
}


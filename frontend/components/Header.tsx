import Link from 'next/link'
import { Cat, Map, User } from 'lucide-react'

export default function Header() {
  return (
    <header className="bg-slate-800 p-4 shadow-md">
      <nav className="flex justify-between items-center">
        <Link href="/" className="text-2xl font-bold text-yellow-400 flex items-center gap-2">
          <Cat className="w-8 h-8" />
          Kuro's Adventure
        </Link>
        <ul className="flex space-x-4">
          <li>
            <Link href="/world" className="text-slate-200 hover:text-yellow-400 flex items-center gap-1">
              <Map className="w-5 h-5" />
              World
            </Link>
          </li>
          <li>
            <Link href="/agent" className="text-slate-200 hover:text-yellow-400 flex items-center gap-1">
              <User className="w-5 h-5" />
              Agent
            </Link>
          </li>
        </ul>
      </nav>
    </header>
  )
}


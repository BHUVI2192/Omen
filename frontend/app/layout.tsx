import './globals.css';
import type { Metadata } from 'next';
export const metadata: Metadata = { title:'OMEN — Career intelligence', description:'Discover, measure, improve, match, apply.' };
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}

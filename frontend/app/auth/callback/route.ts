import {NextResponse} from 'next/server';
import {createServerClient} from '@supabase/ssr';
import {cookies} from 'next/headers';
export async function GET(request:Request){const url=new URL(request.url);const code=url.searchParams.get('code');const cookieStore=await cookies();const response=NextResponse.redirect(new URL('/onboarding',url.origin));if(code){const supabase=createServerClient(process.env.NEXT_PUBLIC_SUPABASE_URL!,process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,{cookies:{getAll(){return cookieStore.getAll()},setAll(cookiesToSet){cookiesToSet.forEach(({name,value,options})=>response.cookies.set(name,value,options))}}});await supabase.auth.exchangeCodeForSession(code)}return response}

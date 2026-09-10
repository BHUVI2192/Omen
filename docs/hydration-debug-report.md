# OMEN hydration debug report

## Scope

The affected route is `/student/dashboard`, which renders the client component `frontend/components/StudentWorkspace.tsx` beneath the root App Router layout.

## Files and architecture inspected

The inspection covered `frontend/package.json`, the installed Next.js/React dependency tree, `frontend/app/layout.tsx`, all files under `frontend/app`, `frontend/components/StudentWorkspace.tsx`, `frontend/lib/supabase-browser.ts`, the OAuth callback route, and `frontend/next.config.mjs`. There are no student-specific layouts, `head.tsx` files, theme providers, global authentication providers, `generateMetadata` functions, viewport exports, loading boundaries, error boundaries, not-found boundaries, Suspense boundaries, or dynamic imports in the affected tree.

The root layout exports only static metadata and renders one `html` and one `body`. The dashboard is a Client Component. Its first render is a deterministic loading shell because `loading` is initialized to `true`; Supabase session lookup and all API requests occur inside `useEffect` after hydration. No user-specific markup is rendered until the browser session and API response have resolved.

The dependency tree contains one deduplicated React installation: Next.js 15.5.25, React 19.3.0, and React DOM 19.3.0. `npm ls react react-dom next --depth=1` showed no duplicate React copies.

## Hydration-risk search

The repository was searched for browser-only APIs, dates, locale formatting, randomness, generated IDs, metadata, viewport, Suspense, dynamic imports, and hydration suppression. The only date formatting found in the affected source tree is inside the separate `/demo` route and is not imported by `/student/dashboard`. The dashboard tree has no `window`, `document`, `localStorage`, `sessionStorage`, `navigator`, `Math.random`, `Date.now`, `new Date`, `Intl`, `useSearchParams`, `cookies`, or `headers` calls during render.

The existing root layout previously contained `suppressHydrationWarning` on both `html` and `body`. This was a blanket suppression and has been removed. There is now no `suppressHydrationWarning` in the root layout.

## Initial diagnosis

The displayed React difference was:

```text
+ <div hidden={true}>
- <div hidden={null}>
```

The stack pointed at `Next.Metadata`, `MetadataWrapper`, and the internal metadata Suspense boundary. That stack was treated as the detection point rather than assumed to be the source.

The mismatch was reproduced in development. The development server emitted:

```text
Could not find the module
.../next-devtools/userspace/app/segment-explorer-node.js#SegmentViewNode
in the React Client Manifest
```

This was followed by `__webpack_modules__[moduleId] is not a function`, a blank dashboard, and a development HTTP 500. The error came from Next.js 15.5 development tooling while loading the Segment Explorer module. It was not caused by OMEN’s metadata object or the student dashboard component.

The dashboard itself rendered correctly after the devtools path was disabled, including the expected logged-out authentication gate. The browser console then contained only the standard React DevTools informational message and no recoverable hydration mismatch.

## Fix

`frontend/next.config.mjs` sets `devIndicators: false`. This disables the broken Next.js development indicator/Segment Explorer path while leaving ordinary compile and runtime errors available. No SSR-wide disablement or dynamic `ssr: false` workaround was added.

The root layout now uses standard App Router metadata and ordinary `html`/`body` elements without `suppressHydrationWarning`.

Only generated `.next` output is removed before final development verification. Source files, environment files, database data, and migrations are preserved.

## Commands and verification

The following checks are required for the final pass:

- `npm run build`
- `npx tsc --noEmit`
- backend `pytest -q`
- backend `python -m compileall -q app`
- `git diff --check`
- development browser hard refresh of `/student/dashboard`
- client-side navigation to and from `/student/dashboard`
- logged-out dashboard verification
- production server verification of `/student/dashboard`
- browser console inspection for hydration errors

## Results

The production build and backend suite were already green before this focused debugging pass. Final results will be recorded below after the no-suppression build and browser checks complete.

## Remaining limitations

A real logged-in browser account was not available in the sandbox, so the authenticated dashboard was validated through the existing Supabase-aware application flow and logged-out route behavior. Supabase OAuth/email configuration remains an environment/integration setup requirement rather than a code change.


## Final validation outcomes

- `npx tsc --noEmit`: passed.
- `npm run build`: passed with Next.js 15.5.25.
- Backend `pytest -q`: 31 passed, one unrelated Starlette deprecation warning.
- Backend `python -m compileall -q app`: passed.
- `git diff --check`: passed.
- Search for `suppressHydrationWarning` under `frontend`: no matches.
- Production hard navigation to `/student/dashboard`: rendered the logged-out authentication gate successfully.
- Production client-side navigation from `/student/dashboard` to `/login`: succeeded without a console error.
- Production browser console: no output, including no hydration warning.
- Clean development navigation to `/student/dashboard`: rendered the logged-out authentication gate successfully.
- Clean development browser console: only the standard React DevTools informational message; no recoverable hydration mismatch.
- `npm run lint`: the repository’s legacy `next lint` script opened Next.js’s interactive ESLint migration prompt and was stopped without changing configuration. The production build’s built-in lint/type validation passed.

## Final conclusion

The confirmed failure was a Next.js 15.5 development Segment Explorer/React Client Manifest defect exposed at the internal metadata Suspense boundary. OMEN did not have a server/client data mismatch in the affected dashboard tree. The fix is targeted: disable the broken development indicator path, remove the blanket hydration suppression, retain standard static metadata, clear only `.next`, and verify both development and production behavior.

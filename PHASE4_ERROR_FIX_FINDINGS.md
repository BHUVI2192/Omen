# Phase 4 error and upload findings

The reported development failure was reproduced from the server log. It was not an application hydration mismatch. Next.js 15.5 development tooling crashed while loading its Segment Explorer module:

`Could not find the module ... next-devtools/userspace/app/segment-explorer-node.js#SegmentViewNode in the React Client Manifest`

This caused the blank page, `globalError`, and HTTP 500 in development. The fix disables Next.js development indicators through `frontend/next.config.mjs` with `devIndicators: false`. The application itself remains unchanged in production. After restarting development mode, `/student/dashboard` rendered the expected unauthenticated sign-in gate and browser console output contained only the standard React DevTools informational message.

The onboarding resume upload path now visibly shows `Uploading securely…`, the selected filename, an animated progress bar, `Resume uploaded successfully`, private storage confirmation, and server errors. The response path is corrected to accept either `storage_path` or demo `path`.

Backend validation confirmed 15 local demo courses, authenticated dashboard rejection with HTTP 401, invalid resume MIME rejection with HTTP 415, valid PDF acceptance, and 31 passing backend tests after the course and upload additions.

# Vercel Deployment

Scoutkat deploys the frontend to Vercel to keep MVP hosting costs low while preserving a simple Next.js workflow.

## Service

- `frontend/`: Next.js application deployed as a Vercel project

## Environment Variable

Set this in the Vercel project:

- `NEXT_PUBLIC_API_BASE_URL`

Value example:

```text
https://scoutkat-backend.onrender.com
```

## Setup Steps

1. Import the GitHub repo into Vercel.
2. Set the project root directory to `frontend`.
3. Add `NEXT_PUBLIC_API_BASE_URL` and point it to the Render backend URL.
4. Deploy.

## Notes

- Vercel Hobby is sufficient for the current MVP frontend.
- The frontend does not need any server secrets; only `NEXT_PUBLIC_API_BASE_URL` is required.

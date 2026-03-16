"use server";

import { revalidatePath } from "next/cache";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export async function addToWatchlist(formData: FormData) {
  const tokenId = String(formData.get("token_id") || "");
  const symbol = String(formData.get("symbol") || "");
  if (!tokenId) {
    return;
  }

  await fetch(`${API_BASE_URL}/watchlist`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ token_id: tokenId }),
    cache: "no-store",
  });

  revalidatePath("/watchlist");
  if (symbol) {
    revalidatePath(`/tokens/${symbol}`);
  }
}

export async function removeFromWatchlist(formData: FormData) {
  const tokenId = String(formData.get("token_id") || "");
  const symbol = String(formData.get("symbol") || "");
  if (!tokenId) {
    return;
  }

  await fetch(`${API_BASE_URL}/watchlist/${tokenId}`, {
    method: "DELETE",
    cache: "no-store",
  });

  revalidatePath("/watchlist");
  if (symbol) {
    revalidatePath(`/tokens/${symbol}`);
  }
}

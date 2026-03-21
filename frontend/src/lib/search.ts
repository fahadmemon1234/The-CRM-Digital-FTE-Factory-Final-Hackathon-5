/**
 * Global Search API Client
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface SearchResult {
  type: 'ticket' | 'customer' | 'conversation' | 'message';
  id: string;
  title: string;
  subtitle: string;
  icon: 'ticket' | 'user' | 'message' | 'conversation';
  url: string;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total: number;
}

export interface GlobalSearchResponse {
  query: string;
  total: number;
  tickets: any[];
  customers: any[];
  conversations: any[];
  messages: any[];
}

/**
 * Quick search for navbar autocomplete
 */
export async function quickSearch(query: string, limit: number = 5): Promise<SearchResponse> {
  if (!query || query.length < 2) {
    return { query: '', results: [], total: 0 };
  }

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/search/quick?q=${encodeURIComponent(query)}&limit=${limit}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Quick search error:', error);
    return { query, results: [], total: 0 };
  }
}

/**
 * Global search across all categories
 */
export async function globalSearch(
  query: string,
  limit: number = 20,
  types?: string[]
): Promise<GlobalSearchResponse> {
  if (!query || query.length < 2) {
    return { query: '', total: 0, tickets: [], customers: [], conversations: [], messages: [] };
  }

  try {
    let url = `${API_BASE_URL}/api/search/global?q=${encodeURIComponent(query)}&limit=${limit}`;
    
    if (types && types.length > 0) {
      url += `&types=${types.join(',')}`;
    }

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Global search error:', error);
    return { query: '', total: 0, tickets: [], customers: [], conversations: [], messages: [] };
  }
}

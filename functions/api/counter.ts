// Cloudflare Pages Function
// Maps to /api/counter

export async function onRequest(context) {
  const kv = context.env.akun_kv;
  
  if (!kv) {
    return new Response(JSON.stringify({ count: 0, error: 'KV not bound' }), { 
      headers: { 'Content-Type': 'application/json' } 
    });
  }

  const key = 'generate_count';

  if (context.request.method === 'POST') {
    let currentCountStr = await kv.get(key);
    let count = currentCountStr ? parseInt(currentCountStr, 10) : 0;
    count += 1;
    await kv.put(key, count.toString());
    
    return new Response(JSON.stringify({ count }), { 
      headers: { 'Content-Type': 'application/json' } 
    });
  } else if (context.request.method === 'GET') {
    let currentCountStr = await kv.get(key);
    let count = currentCountStr ? parseInt(currentCountStr, 10) : 0;
    
    return new Response(JSON.stringify({ count }), { 
      headers: { 'Content-Type': 'application/json' } 
    });
  }

  return new Response("Method not allowed", { status: 405 });
}

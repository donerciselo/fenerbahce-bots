// Cloudflare Worker — Discord Verify Relay
// 1. Go to https://workers.cloudflare.com
// 2. Create a new Worker, paste this code
// 3. Go to Settings → Variables → Add BOT_TOKEN (your bot token)
// 4. Deploy, copy the URL → paste in index.php as WORKER_URL

export default {
  async fetch(request, env) {
    if (request.method !== 'POST') return new Response('Method not allowed', { status: 405 })

    const { user_id, guild_id } = await request.json()
    if (!user_id || !guild_id) return new Response('Missing fields', { status: 400 })

    const headers = { Authorization: `Bot ${env.BOT_TOKEN}`, 'Content-Type': 'application/json' }

    const rolesRes = await fetch(`https://discord.com/api/v9/guilds/${guild_id}/roles`, { headers })
    if (!rolesRes.ok) return new Response('Failed to fetch roles', { status: 500 })
    const roles = await rolesRes.json()

    for (const r of roles) {
      if (r.name === 'Doğrulanmamış') {
        await fetch(`https://discord.com/api/v9/guilds/${guild_id}/members/${user_id}/roles/${r.id}`, { method: 'DELETE', headers })
      }
      if (r.name === 'Doğrulanmış') {
        await fetch(`https://discord.com/api/v9/guilds/${guild_id}/members/${user_id}/roles/${r.id}`, { method: 'PUT', headers })
      }
    }

    return new Response('ok')
  }
}

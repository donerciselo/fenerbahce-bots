#!/bin/bash
set -e

echo "=== Fenerbahce Bot - Fly.io Deploy ==="

if ! command -v flyctl &> /dev/null; then
    echo "flyctl bulunamadı. Yükleniyor..."
    curl -L https://fly.io/install.sh | sh
    export FLYCTL_INSTALL="/home/$USER/.fly"
    export PATH="$FLYCTL_INSTALL/bin:$PATH"
fi

echo ""
echo "1. Fly.io'ya giriş yapılıyor..."
fly auth login

echo ""
echo "2. Uygulama oluşturuluyor (veya mevcut kullanılıyor)..."
fly launch --no-deploy --copy-config --yes 2>/dev/null || true

echo ""
echo "3. Secret'lar ayarlanıyor..."
echo "Lütfen aşağıdaki değerleri girin:"
read -p "DISCORD_TOKEN: " DISCORD_TOKEN
read -p "YOUTUBE_API_KEY (yoksa boş bırakın): " YOUTUBE_API_KEY
read -p "FB_CHANNEL_ID (yoksa boş bırakın): " FB_CHANNEL_ID

fly secrets set DISCORD_TOKEN="$DISCORD_TOKEN"
[ -n "$YOUTUBE_API_KEY" ] && fly secrets set YOUTUBE_API_KEY="$YOUTUBE_API_KEY"
[ -n "$FB_CHANNEL_ID" ] && fly secrets set FB_CHANNEL_ID="$FB_CHANNEL_ID"

echo ""
echo "4. Deploy ediliyor..."
fly deploy

echo ""
echo "=== Deploy tamamlandı! ==="
echo "Durum kontrolü: fly status"
echo "Loglar: fly logs"

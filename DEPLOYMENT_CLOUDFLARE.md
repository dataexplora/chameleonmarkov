## Deploy CHAMELEON to Cloudflare (Tunnel + DNS)

This app is a Python Flask server (port 8885). We'll containerize it and expose it via Cloudflare Tunnel without opening inbound ports.

### 1) Build and run locally (Docker)

```bash
docker build -t chameleon:latest .
docker run --rm -p 8885:8885 chameleon:latest
# or
docker compose up --build -d
```

Open http://localhost:8885 to verify.

### 2) Create a Cloudflare Tunnel

Prerequisites: a domain on Cloudflare and `cloudflared` installed.

```bash
# Login
cloudflared tunnel login

# Create a named tunnel
cloudflared tunnel create chameleon-tunnel

# Note the tunnel ID that is printed
```

### 3) Configure the Tunnel to route to the container

Create `~/.cloudflared/config.yml` (or a project-local config) with:

```yaml
tunnel: <YOUR_TUNNEL_ID>
credentials-file: ~/.cloudflared/<YOUR_TUNNEL_ID>.json

ingress:
  - hostname: chameleon.yourdomain.com
    service: http://localhost:8885
  - service: http_status:404
```

Start the tunnel:

```bash
cloudflared tunnel run chameleon-tunnel
```

### 4) Create DNS CNAME in Cloudflare

In Cloudflare dashboard → DNS → Add record:
- Type: CNAME
- Name: `chameleon`
- Target: `<YOUR_TUNNEL_ID>.cfargotunnel.com`
- Proxy status: Proxied (Orange cloud)

After DNS propagates, visit `https://chameleon.yourdomain.com`.

### 5) Production tips

- Use `gunicorn` (already configured in Dockerfile).
- Enable health checks on the container and consider adding a `/health` route.
- For static files, Cloudflare will cache assets under `/static/` automatically. Add Cache Rules as desired.
- If running on a VM or K8s, point the tunnel `service` to the internal IP of the instance instead of `localhost`.

### 6) Environment variables

If you need to tweak host/port:

```bash
gunicorn --bind 0.0.0.0:8885 chameleon_server:app
```

### 7) Troubleshooting

- 502 from tunnel: ensure the container is listening on 0.0.0.0:8885 and the tunnel `service` matches.
- CSS not loading: verify `/static/...` paths resolve under your Cloudflare domain.
- Increase Gunicorn `--timeout` if melody processing takes longer.



Nginx & Next.js Troubleshooting Guide
This guide documents common issues and their solutions when setting up Nginx as a reverse proxy for a Next.js application, including the steps we followed to resolve the "Apache default page" issue.

Issue 1: Port Conflict (Apache running alongside Nginx)
Symptom: You can access your website, but it shows a different web server's default page (e.g., Apache's).

Diagnosis: Multiple services are trying to listen on the same port (80 or 443).

Solution:

Check for conflicting processes:
```
sudo ss -tulpn | grep -E ':80|:443'
```

Look for any services other than nginx listening on those ports. If you see apache2 or httpd, you need to stop and disable it.

Stop and disable Apache:
```
sudo systemctl stop apache2
sudo systemctl disable apache2
```

Issue 2: Nginx Configuration File Conflict
Symptom: Nginx is running and listening on the correct ports, but your website still isn't loading correctly.

Diagnosis: Nginx is loading multiple configuration files that are conflicting with each other. A "catch-all" server block is taking precedence over your domain-specific configuration.

Solution:

List all active Nginx configuration files:
```
ls -l /etc/nginx/sites-enabled/
```
You should only see a symbolic link for your domain, e.g., www.worldwideamerican.net.

Remove any conflicting links:
If you see a link named default, nextjs, or anything other than your domain name, remove it.
```
sudo unlink /etc/nginx/sites-enabled/nextjs
sudo unlink /etc/nginx/sites-enabled/default
```

Issue 3: Nginx is Serving Local Files Instead of Proxying to Next.js
Symptom: You can access your site via HTTPS (with a padlock), but you still see an incorrect page (e.g., Apache's default page).

Diagnosis: Your Nginx HTTPS server block is misconfigured to serve static files from a root directory instead of acting as a reverse proxy.

Solution:

Edit your domain's Nginx configuration file:
```
sudo nano /etc/nginx/sites-available/www.worldwideamerican.net
```
Modify the HTTPS server block:
Remove the root and try_files directives from the server block for port 443.
Add a proxy_pass directive to forward traffic to your Next.js application (usually running on port 3000).

Corrected Server Block Example:
```
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name www.worldwideamerican.net;

    ssl_certificate /etc/letsencrypt/live/www.worldwideamerican.net-0001/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/www.worldwideamerican.net-0001/privkey.pem; # managed by Certbot

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```
Final Steps: Test and Restart Nginx
After making any changes to your configuration files, always run these commands to verify the syntax and apply the changes:
```
sudo nginx -t
sudo systemctl restart nginx
```

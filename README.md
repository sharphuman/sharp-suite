# Sharp Suite - Standalone Apps
# SH
Each app is completely self-contained. No shared imports.

## Passwords
- GOD: G0DHum@n101!!!
- DEMO: D3M0Human101!!!

## Deploy to Railway

1. Upload this folder to GitHub
2. For each service, set Root Directory to the app folder:
   - Portal: /apps/sharp_portal
   - JD: /apps/sharp_jd
   - Screen: /apps/sharp_screen
   - Interview: /apps/sharp_interview
   - Source: /apps/sharp_source
   - Content: /apps/sharp_content
   - Sales: /apps/sharp_sales
   - Reach: /apps/sharp_reach
   - Assistant: /apps/sharp_assistant
   - Admin: /apps/sharp_admin

3. Start command for ALL: streamlit run app.py --server.port $PORT --server.address 0.0.0.0

4. Environment variable: ANTHROPIC_API_KEY

## Subdomains
- suite.sharphuman.com → Portal
- jd.sharphuman.com → JD
- screen.sharphuman.com → Screen
- hire.sharphuman.com → Interview
- outreach.sharphuman.com → Source
- content.sharphuman.com → Content
- sales.sharphuman.com → Sales
- reach.sharphuman.com → Reach
- assistant.sharphuman.com → Assistant
- admin.sharphuman.com → Admin

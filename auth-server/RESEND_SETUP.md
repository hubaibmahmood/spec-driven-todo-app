# Resend Email Setup Guide

## Quick Setup

### 1. Get Your Resend API Key

1. Go to [resend.com](https://resend.com)
2. Sign up or log in
3. Navigate to **API Keys** in the dashboard
4. Click **Create API Key**
5. Copy the API key (starts with `re_`)

### 2. Verify Your Sender Email

**IMPORTANT**: You must verify the email address you want to send from.

#### Option A: Use Resend's Test Domain (Recommended for Development)
- Use: `onboarding@resend.dev`
- No verification needed
- Works immediately
- Limited to 100 emails/day

#### Option B: Use Your Own Domain (Recommended for Production)
1. Go to **Domains** in Resend dashboard
2. Click **Add Domain**
3. Enter your domain (e.g., `yourdomain.com`)
4. Add the DNS records to your domain provider
5. Wait for verification (usually 5-15 minutes)
6. Once verified, you can use any email from that domain (e.g., `noreply@yourdomain.com`)

### 3. Configure Environment Variables

#### Local Development (.env file)
```bash
RESEND_API_KEY="re_your_actual_api_key_here"
EMAIL_FROM="onboarding@resend.dev"  # or your verified email
```

#### Vercel (Production)
1. Go to your Vercel project → Settings → Environment Variables
2. Add:
   - `RESEND_API_KEY`: Your Resend API key
   - `EMAIL_FROM`: Your verified sender email

### 4. Test Email Sending

#### In Development
When you sign up a user, you'll see the verification link in the console:
```
=================================
📧 EMAIL VERIFICATION LINK
=================================
To: user@example.com
Link: http://localhost:3000/verify-email?token=...
=================================
```

You can either:
- Click the link in the console (if it's clickable)
- Copy and paste it into your browser
- Check your email inbox if Resend is configured correctly

#### Check Resend Dashboard
1. Go to [resend.com/emails](https://resend.com/emails)
2. You should see the emails being sent
3. Check the status (Delivered, Bounced, etc.)

## Troubleshooting

### No Emails Received

1. **Check Spam Folder**: Verification emails might go to spam

2. **Verify Sender Email**:
   - If using custom domain, make sure DNS is configured
   - Check Resend dashboard → Domains for verification status

3. **Check API Key**:
   - Make sure it starts with `re_`
   - Verify it's set in environment variables
   - Try creating a new API key

4. **Check Server Logs**:
   - Look for `[Email]` log messages
   - Check for errors like "API key invalid" or "Domain not verified"

5. **Test with Resend's Test Domain**:
   ```bash
   EMAIL_FROM="onboarding@resend.dev"
   ```

### Common Errors

#### "Domain not verified"
- **Solution**: Use `onboarding@resend.dev` or verify your domain in Resend dashboard

#### "API key is invalid"
- **Solution**: Generate a new API key from Resend dashboard

#### "Rate limit exceeded"
- **Solution**: Free tier: 100 emails/day. Upgrade or wait 24 hours

#### Emails going to spam
- **Solution**:
  - Use a verified custom domain (not resend.dev)
  - Configure SPF, DKIM, and DMARC records
  - Avoid spam trigger words in email content

## Free Tier Limits

- **100 emails/day** with test domain (onboarding@resend.dev)
- **3,000 emails/month** with verified custom domain
- Need more? Upgrade to paid plan

## Production Checklist

- [ ] Verified custom domain in Resend
- [ ] DNS records (SPF, DKIM, DMARC) configured
- [ ] `RESEND_API_KEY` set in Vercel environment variables
- [ ] `EMAIL_FROM` uses your verified domain email
- [ ] `NODE_ENV=production` set in Vercel
- [ ] Tested email delivery end-to-end
- [ ] Checked spam folder and email deliverability

## Resources

- [Resend Documentation](https://resend.com/docs)
- [Domain Verification Guide](https://resend.com/docs/dashboard/domains/introduction)
- [API Reference](https://resend.com/docs/api-reference/emails/send-email)

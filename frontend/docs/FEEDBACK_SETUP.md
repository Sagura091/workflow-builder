# Setting Up the Feedback System

This document explains how to set up the feedback system for the Workflow Builder demo so that you receive all user feedback directly to your email.

## Overview

The Workflow Builder demo includes a feedback system that allows users to:

1. Rate their experience (1-5 stars)
2. Provide detailed feedback
3. Optionally include their email for follow-up

This feedback is sent directly to your email using Formspree, a free service that handles form submissions from static websites.

## Step 1: Create a Formspree Account

1. Go to [Formspree.io](https://formspree.io/) and sign up for a free account
2. Verify your email address when prompted

## Step 2: Create a New Form

1. Log in to your Formspree account
2. Click "New Form"
3. Give your form a name (e.g., "Workflow Builder Feedback")
4. Enter the email address where you want to receive feedback
5. Click "Create Form"

## Step 3: Get Your Form Endpoint

1. After creating the form, you'll see a form endpoint URL that looks like:
   ```
   https://formspree.io/f/xbjnkdvj
   ```
2. Copy this URL - you'll need it in the next step

## Step 4: Update the Demo Files

You need to update two files with your Formspree endpoint:

### 1. React Component (DemoFeedbackButton.tsx)

1. Open `frontend/src/components/DemoMode/DemoFeedbackButton.tsx`
2. Find this line:
   ```typescript
   const FORMSPREE_ENDPOINT = 'https://formspree.io/f/YOUR_FORM_ID';
   ```
3. Replace `YOUR_FORM_ID` with your actual form ID (the last part of the URL, e.g., `xbjnkdvj`)

### 2. Standalone HTML Demo

1. Open `docs/examples/standalone-demo.html`
2. Find this line (around line 433):
   ```javascript
   const response = await fetch('https://formspree.io/f/YOUR_FORM_ID', {
   ```
3. Replace `YOUR_FORM_ID` with your actual form ID

## Step 5: Test the Feedback System

1. Run the demo locally or deploy it
2. Click the "Send Feedback" button
3. Fill out the form and submit it
4. Check your email to confirm you received the feedback

## How Feedback is Categorized

The feedback system automatically categorizes feedback based on content:

- **Bug Report**: Contains words like "bug", "error", "issue", "doesn't work"
- **Feature Request**: Contains words like "feature", "add", "would be nice", "should have"
- **Usability Issue**: Contains words like "confusing", "hard to", "difficult", "unclear"
- **Positive Feedback**: Contains words like "like", "love", "great", "good"
- **General Feedback**: Any other feedback

This categorization helps you prioritize and organize feedback.

## Additional Information Collected

Along with the user's feedback, the system collects:

- **Rating**: 1-5 star rating
- **Email**: If provided by the user
- **Source**: Which demo version was used (React or Standalone HTML)
- **Timestamp**: When the feedback was submitted
- **Browser**: The user's browser
- **Device**: Whether the user is on mobile or desktop
- **Screen Size**: The user's screen dimensions
- **Referrer**: Where the user came from
- **URL**: The exact page URL

This information helps you understand the context of the feedback and reproduce any issues.

## Formspree Limitations

The free plan of Formspree has some limitations:

- 50 submissions per month
- Basic spam filtering
- Email notifications only

If you expect more feedback, consider upgrading to a paid plan or implementing a different solution.

## Alternative Solutions

If you prefer not to use Formspree, here are some alternatives:

1. **Google Forms**: Create a Google Form and embed it in the demo
2. **Netlify Forms**: If you're hosting on Netlify, use their built-in form handling
3. **Custom Backend**: Implement a simple backend service to receive and store feedback

## Troubleshooting

If you're not receiving feedback:

1. Check your spam folder
2. Verify that you've entered the correct form ID
3. Test the form submission manually
4. Check the browser console for any errors
5. Verify that your Formspree account is active

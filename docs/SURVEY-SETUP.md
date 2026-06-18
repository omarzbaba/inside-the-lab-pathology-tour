# Adding the student feedback survey (Google Form)

The site has a "Tell us what you think" section ready for a survey. Wiring it up takes ~2 min.

## 1. Create the Google Form

Go to <https://forms.new> and create a form. Suggested questions (copy/paste):

1. **How much did you enjoy the tour?** — *Linear scale 1–5* (1 = not much, 5 = loved it)
2. **Which station was the most interesting?** — *Multiple choice* (list the 12 stations)
3. **How clear was the explanation for a high‑school student?** — *Linear scale 1–5*
4. **What is one thing you learned today?** — *Short answer*
5. **What questions do you still have about working in a pathology lab?** — *Paragraph*
6. **Would you consider a career in science, medicine, or laboratory work after this?**
   — *Multiple choice* (Yes / Maybe / Not sure / No)
7. **Any other feedback for the team?** — *Paragraph*

(Optional) Turn on **Settings → Responses → Collect email addresses** only if you want to
reply to students directly.

## 2. Get the embed link

In the form: **Send → `< >` (Embed HTML)** → copy the URL inside `src="..."`.
It looks like `https://docs.google.com/forms/d/e/XXXXXXXX/viewform?embedded=true`.

## 3. Paste it into the site

Open [`data/stations.json`](../data/stations.json) and set the `survey.embedUrl` field:

```json
"survey": {
  "heading": "Tell us what you think",
  "body": "We'd love your feedback! ...",
  "embedUrl": "https://docs.google.com/forms/d/e/XXXXXXXX/viewform?embedded=true",
  "fallbackUrl": "https://forms.gle/your-short-link"
}
```

- `embedUrl` shows the form **inside** the page.
- `fallbackUrl` (optional) is a plain "Open the feedback form →" button — handy as a backup.

Commit and push; the form appears automatically. Responses collect in the form's
**Responses** tab (and a linked Google Sheet if you create one).

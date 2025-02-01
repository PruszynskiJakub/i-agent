import os

import resend

resend.api_key = os.getenv("RESEND_API_KEY")

r = resend.Emails.send({
  "from": "onboarding@resend.dev",
  "to": "jakub.mikolaj.pruszynski@gmail.com",
  "subject": "Hello World",
  "html": "<p>Congrats on sending your <strong>first email</strong>!</p>"
})
# User Story: Login with email and OTP

**As a** registered customer of a lending app
**I want to** log in using my email and a one-time password (OTP)
**So that** I can access my loan account without remembering a password

## Acceptance Criteria

1. The user enters a registered email address and taps "Send OTP".
2. A 6-digit OTP is sent to the email and is valid for 5 minutes.
3. Entering the correct OTP logs the user in and opens the dashboard.
4. After 3 wrong OTP attempts, the account is locked for 15 minutes.
5. The user can request a new OTP after 30 seconds; requesting one invalidates the previous OTP.
6. Unregistered emails show the message "We couldn't find an account with that email".

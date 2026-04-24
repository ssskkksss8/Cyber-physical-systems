# Inference report

- Service URL: `http://127.0.0.1:8000/classify`
- Total messages: **10**
- Predicted spam: **3**
- Predicted non-spam: **7**

| ID | SMS message | Verdict | Reasoning |
|---:|---|---:|---|
| 1 | WINNER! You have won a free vacation. Reply YES to claim now. | 1 | The message contains a clear and direct offer of a free vacation, which is typically not associated with spam messages. |
| 2 | Hi Alex, are we still meeting at 18:30 near the station? | 0 | The message is asking about a specific time and location, which is not typical for an SMS spam classification. |
| 3 | URGENT: Your bank account is blocked. Follow the link immediately. | 1 | The message contains a direct and urgent request for action, which is typical of spam messages. |
| 4 | Please review the draft and send comments before tomorrow morning. | 0 | The message is asking for a draft of an email, which is typically used to discuss content with others. It does not contain any spammy language or requests for sensitive information. |
| 5 | Congratulations! You were selected for a cash prize. Call now. | 1 | The message is clearly asking the recipient to call, which is a common practice in SMS spam. |
| 6 | Mom, I bought bread and milk. I will be home in 20 minutes. | 0 | The message is about a planned trip to the store, which is not typical for an SMS spam message. |
| 7 | Limited offer only today: get a cheap loan with no documents required. | 0 | The message contains a direct and clear offer to apply for a loan without any personal details, which is typically not associated with spam messages. |
| 8 | The lesson has been moved from Friday to Saturday at 10:00. | 0 | This message is a direct request for information about the move of the lesson, which is not typical spam. |
| 9 | Claim your bonus points before they expire. Click the link. | 0 | The message is asking for a link to claim bonus points, which is typically found in an email with a link attached. |
| 10 | I left the charger on your desk. Take it when you arrive. | 0 | The message is a polite reminder to take the charger when arriving at the location. |

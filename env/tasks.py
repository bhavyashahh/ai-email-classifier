TASKS = {
    "task_1_easy": {
        "instructions": "Classify each email as 'spam' or 'not_spam'.",
        "required_fields": ["spam_status"],
        "emails": [
            {
                "content": "CONGRATULATIONS!!! You've WON $1,000,000! Click HERE NOW to claim your prize before it expires! Act FAST!",
                "ground_truth": {"spam_status": "spam"},
            },
            {
                "content": "Hi John, can we reschedule our 3pm meeting to 4pm tomorrow? I have a conflict. Thanks, Sarah",
                "ground_truth": {"spam_status": "not_spam"},
            },
            {
                "content": "BUY NOW!!! 90% OFF all products! LIMITED TIME! Free shipping! No questions asked! Click below!",
                "ground_truth": {"spam_status": "spam"},
            },
            {
                "content": "Please find attached the Q3 financial report for your review. Let me know if you have questions. - David, Finance Team",
                "ground_truth": {"spam_status": "not_spam"},
            },
            {
                "content": "You have been SELECTED for a SPECIAL prize! Send your bank details and SSN to claim your $50,000 reward immediately!",
                "ground_truth": {"spam_status": "spam"},
            },
        ],
    },
    "task_2_medium": {
        "instructions": "Classify each email as 'spam' or 'not_spam', and assign a category: 'work', 'personal', 'promotions', 'updates', or 'finance'.",
        "required_fields": ["spam_status", "category"],
        "emails": [
            {
                "content": "Team, the product launch deadline has been moved to Friday. Please update your tasks in Jira and confirm by EOD. - PM Lead",
                "ground_truth": {"spam_status": "not_spam", "category": "work"},
            },
            {
                "content": "Your monthly bank statement for March 2025 is ready. Log in to your account to view transaction details and balance summary.",
                "ground_truth": {"spam_status": "not_spam", "category": "finance"},
            },
            {
                "content": "Hey! Are we still on for dinner Saturday? I was thinking that new Italian place on 5th. Let me know! - Mike",
                "ground_truth": {"spam_status": "not_spam", "category": "personal"},
            },
            {
                "content": "Your package #TRK-9281 has shipped and is estimated to arrive on April 10. Track your delivery at the link below.",
                "ground_truth": {"spam_status": "not_spam", "category": "updates"},
            },
            {
                "content": "Spring Sale! 40% off everything at StyleMart this weekend only. Use code SPRING40 at checkout. Shop now!",
                "ground_truth": {"spam_status": "not_spam", "category": "promotions"},
            },
        ],
    },
    "task_3_hard": {
        "instructions": "Classify each email as 'spam' or 'not_spam', assign a category ('work', 'personal', 'promotions', 'updates', 'finance'), and set priority ('high', 'medium', 'low'). These emails are deliberately ambiguous.",
        "required_fields": ["spam_status", "category", "priority"],
        "emails": [
            {
                "content": "URGENT: Your company account password expires in 2 hours. Click here to reset immediately or you will be locked out. IT Security Team.",
                "ground_truth": {"spam_status": "spam", "category": "work", "priority": "high"},
            },
            {
                "content": "Hi, I noticed an unauthorized charge of $847.50 on my credit card ending in 4521. This was not me. Please investigate and reverse this charge immediately. I'm very concerned about fraud on my account.",
                "ground_truth": {"spam_status": "not_spam", "category": "finance", "priority": "high"},
            },
            {
                "content": "Hey team, someone left a bag of chips in the break room fridge with a note saying 'free for all'. Just a heads up in case anyone wants some. - Janet",
                "ground_truth": {"spam_status": "not_spam", "category": "work", "priority": "low"},
            },
            {
                "content": "Your subscription to CloudSync Pro will auto-renew at $299/year on April 15. If you wish to cancel or change your plan, visit account settings before the renewal date.",
                "ground_truth": {"spam_status": "not_spam", "category": "finance", "priority": "medium"},
            },
            {
                "content": "We are excited to invite you to an exclusive VIP networking event with top industry leaders. Limited spots available! RSVP now to confirm your attendance. Early bird registration closes soon.",
                "ground_truth": {"spam_status": "not_spam", "category": "promotions", "priority": "low"},
            },
        ],
    },
}

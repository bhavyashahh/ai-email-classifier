from agent.geminiai_agent import get_email_analysis

def run_interactive():
    print("Welcome to the AI Email Classifier!\n")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        user_email = input("Enter the email content: ")

        if user_email.lower() in ['exit' , 'quit']:
            print("Goodbye!")
            break

        print("Thinking...")
        action = get_email_analysis(user_email)

        print(f"AI Classification: {action}")

if __name__ == "__main__":
    run_interactive()
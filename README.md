
AUTOMATED MULTI-PLATFORM POSTING SYSTEM

1. PROJECT OVERVIEW

   1.1 Description

       The Automated Multi-Platform Posting System is a Python-based application that allows users to publish a single message across five different platforms through one API request.

       The application uses FastAPI to receive messages and integrates with Telegram, Discord, Bluesky, Slack, and Google Chat to publish them concurrently.

   1.2 Project Objective

       To simplify multi-platform content publishing by providing a centralized API that handles message validation, concurrent publishing, and individual platform responses.

2. KEY FEATURES

   2.1 Multi-Platform Publishing

       - Publish a single message across five platforms.
       - Support concurrent publishing.
       - Integrate with five third-party platforms.

   2.2 Message Validation

       - Reject empty messages.
       - Restrict messages to a maximum of 200 characters.
       - Require exactly one valid HTTP or HTTPS URL.

   2.3 Error Handling and Reporting

       - Handle platform failures independently.
       - Return individual publishing results.
       - Provide status, post URL when available, public accessibility, date, time, and error details.

3. TECHNOLOGIES USED

   3.1 Programming Language

       - Python 3

   3.2 Frameworks and Libraries

       - FastAPI – API development.
       - Uvicorn – ASGI server.
       - Pydantic – Request validation and response models.
       - HTTPX – Asynchronous HTTP requests.
       - Python-dotenv – Environment variable management.
       - Pytest – Automated testing.

4. SUPPORTED PLATFORMS

   4.1 Telegram

   4.2 Discord

   4.3 Bluesky

   4.4 Slack

   4.5 Google Chat

5. PROJECT STRUCTURE

   5.1 Application Package

       app/
           platforms/
               telegram.py
               discord.py
               bluesky.py
               slack.py
               google_chat.py

           services/
               posting_service.py

           main.py
           schemas.py
           config.py

   5.2 Testing

       tests/
           __init__.py
           conftest.py
           test_posting.py
           test_platforms.py

   5.3 Configuration and Documentation

       .env
       .env.example
       .gitignore
       requirements.txt
       README.md

6. INSTALLATION AND SETUP

   6.1 Clone the Repository

       Clone the project repository from GitHub and open the project directory.

       git clone https://github.com/vinuthnareddy0/automated-multi-platform-posting.git

       cd automated-multi-platform-posting

   6.2 Create a Virtual Environment

       Create and activate a Python virtual environment to manage project dependencies.

       python -m venv .venv

       .venv\Scripts\Activate.ps1

   6.3 Install Dependencies

       Install the packages listed in requirements.txt.

       pip install -r requirements.txt

   6.4 Configure Environment Variables

       Create a .env file in the project root and provide the required platform credentials.

7. ENVIRONMENT CONFIGURATION

   7.1 Required Environment Variables

       - TELEGRAM_BOT_TOKEN
       - TELEGRAM_CHAT_ID
       - DISCORD_WEBHOOK_URL
       - BLUESKY_HANDLE
       - BLUESKY_APP_PASSWORD
       - SLACK_WEBHOOK_URL
       - GOOGLE_CHAT_WEBHOOK_URL

   7.2 Credential Security

       All actual credentials must be stored in the local .env file.

       The .env file must not be committed to the public GitHub repository. The .env.example file should contain placeholder values only.

8. RUNNING THE APPLICATION

   8.1 Start the Server

       Run the FastAPI application using Uvicorn on port 4000.

       uvicorn app.main:app --host 127.0.0.1 --port 4000 --reload

   8.2 Application URL

       http://127.0.0.1:4000

   8.3 Interactive API Documentation

       http://127.0.0.1:4000/docs

9. API SPECIFICATION

   9.1 Endpoint

       Method: POST

       Endpoint: /posting

   9.2 Description

       Accepts a message and publishes it across all five configured platforms.

   9.3 Request Validation

       - Message must not be empty.
       - Message must not exceed 200 characters.
       - Message must contain exactly one valid HTTP or HTTPS URL.

   9.4 Example Request

       {
           "message": "Check out our latest update at https://example.com"
       }

10. RESPONSE DETAILS

   10.1 Response Structure

       The API returns an overall success indicator and individual publishing results for each platform.

   10.2 Response Fields

       - Platform name
       - Publishing status
       - Published post URL, when available
       - Public accessibility status
       - Publishing date
       - Publishing time
       - Error details, if publishing fails

   10.3 Success Indicator

       The overall success field is true when at least one platform publishes successfully.

       A null post URL does not necessarily indicate a publishing failure. Some webhook integrations do not return a message permalink.

11. ERROR HANDLING

   11.1 Independent Platform Execution

       The system handles platform failures independently. A failure on one platform does not prevent the application from attempting to publish to the remaining platforms.

   11.2 Error Reporting

       Individual results identify successful and failed publishing attempts and provide error details where available.

12. TESTING

   12.1 Testing Framework

       Pytest is used to execute automated test cases.

   12.2 Test Cases

       1. Home endpoint response.
       2. Rejection of messages without a URL.
       3. Rejection of messages containing multiple URLs.
       4. Rejection of messages exceeding 200 characters.
       5. Acceptance of valid messages.
       6. Acceptance of valid messages containing www links.
       7. Independent platform failure handling.
       8. Overall failure when all platforms fail.
       9. Handling of invalid platform responses.
       10. Telegram publishing success and API failure.
       11. Discord publishing success and API failure.
       12. Bluesky publishing success and API failure.
       13. Slack publishing success and API failure.
       14. Google Chat publishing success and API failure.

   12.3 Test Results

       Total test cases: 20

       Passed: 20

       Failed: 0

       All platform integration tests use mocked HTTP responses to test success and failure handling without creating real posts.

13. SECURITY

   13.1 Credential Management

       Platform credentials are loaded through environment variables.

   13.2 Repository Security

       - The actual .env file must remain private.
       - The .env.example file must contain placeholder values.
       - Access tokens, app passwords, and webhook URLs must not be exposed publicly.
       - The .env file is excluded through .gitignore.

14. PROJECT OUTCOME

   14.1 Implementation

       The system integrates five platforms through a single API endpoint and provides platform-wise publishing results.

   14.2 Skills Demonstrated

       - REST API development
       - Third-party API integration
       - Asynchronous programming
       - Input validation
       - Environment-based configuration
       - Error handling
       - Automated testing
       - Python backend development

   14.3 Conclusion

       The Automated Multi-Platform Posting System provides a centralized approach to publishing messages across multiple platforms. It demonstrates how Python, FastAPI, asynchronous execution, and third-party integrations can be combined to simplify content distribution.

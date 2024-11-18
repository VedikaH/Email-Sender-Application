# Email Sender Application  

An efficient and user-friendly web application to manage email communication with advanced features like dynamic email generation, scheduling, bulk email dispatch, and analytics.  

This application integrates:  
- **Amazon SES** for email delivery  
- **Llama 3.2 API** (via OpenRouter) for content generation using LLM
- **MongoDB** for database management  

---

## Features  

- **Single & Bulk Email Sending**: Send emails to individual recipients or groups effortlessly.  
- **Dynamic Content Generation**: Generate customized email content using the Llama 3.2 API.  
- **Scheduling**: Schedule emails to be sent at a specific date and time.  
- **Analytics Dashboard**: Track delivery, open rates, click-through rates, and other key metrics.  

---

## Setup and Configuration  

### Prerequisites  

- **Backend**: Python 3.8 or above  
- **Frontend**: Node.js 
- **Database**: MongoDB  
- **Email Service Provider**: Amazon SES account with API credentials  
- **LLM Integration**: Llama 3.2 API key from OpenRouter  

---

### Configuring Amazon SES  

1. Sign in to the [Amazon SES Console](https://console.aws.amazon.com/ses/).  
2. Verify your sender email addresses or domains.  
3. Obtain your **Access Key** and **Secret Key** from the **IAM Console**.  
4. Update `.env` with the credentials:  
   ```bash
   AWS_ACCESS_KEY_ID = "your-aws-ses-access-key"
   AWS_SECRET_ACCESS_KEY = "your-aws-ses-secret-key"
   AWS_REGION="your-aws-region"
   SENDER_EMAIL="verified-aws-ses-email"
   ```

---
### Configuring Llama 3.2 API Integration  

1. Sign up at [OpenRouter](https://openrouter.ai/) and obtain your API key.  
2. Include the API key in `.env`:  
   ```bash
   OPENROUTER_API_KEY = "your-openrouter-api-key"
   ```

---

### Backend Setup  

1. **Clone the repository**:  
   ```bash  
   git clone https://github.com/your-username/email-sender.git  
   cd email-sender/backend  
   ```  

2. **Create a virtual environment and install dependencies**:  
   ```bash  
   pip install -r requirements.txt  
   ```  

3. **Set up environment variables**:  
  1. Create a `.env` file in the `backend` directory.  
  2. Add the following environment variables to the `.env` file:  
     ```env
     MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/dbname
     MONGODB_DB_NAME=your-mongo-database-name
     AWS_ACCESS_KEY_ID=your-aws-ses-access-key
     AWS_SECRET_ACCESS_KEY=your-aws-ses-secret-key
     AWS_REGION=your-aws-region
     OPENROUTER_API_KEY=your-openrouter-api-key
     SENDER_EMAIL=verified-aws-ses-email
     ```  

4. **Run the FastAPI server**:  
   ```bash  
   uvicorn main:app --reload  
   ```  

---

### Frontend Setup  

1. **Navigate to the frontend directory**:  
   ```bash  
   cd ../frontend  
   ```  

2. **Install dependencies**:  
   ```bash  
   npm install  
   ```  

3. **Start the development server**:  
   ```bash  
   npm start  
   ```  


---

### Email Scheduling 

- Use the frontend form to specify the date and time for sending emails.  
- The backend handles queuing and dispatch using a scheduler.  

---

## Usage Instructions  

#### Access the Application  

1. Open your browser and visit:  
   ```
   http://localhost:3000
   ```

#### Explore Features  

- Navigate via the menu bar to access features like:  
  - Sending emails  
  - Generating content  
  - Scheduling  
  - Viewing analytics  

#### Monitor Campaigns  

- Use the analytics dashboard to track:  
  - Open rates  
  - Delivery statistics  
  - User engagement  

---


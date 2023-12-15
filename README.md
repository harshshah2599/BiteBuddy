
## BiteBuddy: Make informed dining choices with AI 

**Tired of menu anxiety?** BiteBuddy uses crowdsourced data from multiple sources including Google reviews to **Recommend** the best dishes at any restaurant.

**BiteBuddy** is a crowdsourced dining companion that helps you ditch menu paralysis and discover the best dishes based on real customer experiences. No more relying on upselling waiters or blindly picking dishes. BiteBuddy empowers you to make informed dining choices with confidence.

### Features:

* **Personalized recommendations:** Discover hidden gems and avoid menu duds.
* **Data-driven:** Make informed choices based on real user experiences.
* **Simple and free:** Easy to use and no cost to access.

**Use BiteBuddy and eat like a local!**


### Work Docs:

<ul>

<li>💻 <a href="https://docs.google.com/presentation/d/17kCFljf3qQ_N1jVAuPRQN1Kkjuj9VNN2pcAsQIeOGnE/edit#slide=id.g28262b8e96a_2_268">Proposal</a> </li>
<li>⏰ <a href="https://docs.google.com/document/d/1YcQwmBuYPS7HSb4ALRMpa9Gh8zakGQQZ15gFDOKEQ34/edit">Progress Documentation</a> </li>
<li>📖 <a href="https://wepik.com/share/9ad95fa2-c2ae-4cf0-8395-1b6dd5acddd8#rs=link">Presentation Slides </a> </li>
<li>📋 <a href="https://github.com/LLM-App-DataEng-Group2/BiteBuddy/tree/14e06cbd283a127ab057e47673c5808f3e3b17ce/report">Project Report</a></li>

</ul>


#### Part 1
1. Clone the repository:

   ```bash
   git clone https://github.com/LLM-App-DataEng-Group2/BiteBuddy.git

#### Part 2

1. Install the requirements.txt
   ```bash
   pip install requirements.txt

2. Add a .env file with following credentials:
   ```bash
   SNOWFLAKE_USER=
   SNOWFLAKE_PASSWORD=
   SNOWFLAKE_ACCOUNT=
   SERPAPI_KEY = 
   ID = ""
   IDTS = ""
   IDCC = ""

3. Change the path of the .env to your path:
   - app.py
   - snowflake_data.py
   - snowflake_conn.py

4. Navigate to streamlit folder :
   ```bash
   cd streamlit

5. Run the following command :
   ```bash
   streamlit run app.py

### Test Use credentials:
- Email: test
- Password: test

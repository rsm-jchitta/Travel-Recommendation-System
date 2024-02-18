**Travel Recommendation System**

**Project Overview**

The Travel Recommendation System is designed to provide personalized travel destination recommendations based on user preferences. This innovative system simplifies the travel planning process by considering various factors such as the destination city, origin city, budget, duration of stay, number of travelers (adults and children), and preferred number of stopovers. Using a user-friendly Streamlit dashboard, the system delivers a customized travel plan that fits within the user's budget.

**Features**

Personalized Recommendations: Offers travel suggestions tailored to the user's specific preferences and requirements.
Comprehensive Planning: Considers flights, accommodations, and local attractions in the destination city.
Budget-Friendly: Optimizes recommendations to fit within the user's specified budget.
User-Friendly Interface: Easy-to-navigate Streamlit dashboard for inputting travel preferences and viewing recommendations.
How It Works
User Input: Through the Streamlit dashboard, users input their travel preferences, including origin and destination cities, budget, travel duration, number of adults and children, and preferred stopovers.
API Integration: The system utilizes the Google Maps API and Google Places API to gather information on travel routes, local accommodations, and attractions. The Ticketmaster API is used to recommend events and activities.
Webscraping: For additional hotel details in certain cities, the system employs webscraping techniques using BeautifulSoup.
Output: Based on the collected data and user preferences, the system calculates and presents the best travel plan, including flight options, accommodations, and activities, all tailored to fit the user's budget.
Technologies and APIs Used
Streamlit: For creating the user interface and dashboard.
Google Maps API: To calculate travel routes and distances.
Google Places API: To find hotels and attractions near the destination.
Ticketmaster API: To recommend local events and activities.
BeautifulSoup: For web scraping hotel details from various websites.

**Usage**

Open the Streamlit dashboard.
Input your travel preferences in the provided fields.
Click the "Recommend" button to view your personalized travel plan.
Explore the recommended flights, accommodations, and activities within your budget.

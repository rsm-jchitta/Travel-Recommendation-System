import streamlit as st
from datetime import date
import requests
import pandas as pd
import googlemaps
from amadeus import Client, ResponseError
import json
from serpapi import GoogleSearch


def get_events_by_city_and_date(city, date_range):
    base_url = 'https://app.ticketmaster.com/discovery/v2/events.json'
    params = {
        'apikey': 'JG4GuLDIGDPhGwFfL46GKKJqjidVAANm',
        'city': city,
        'size': 50,  # Adjust size as needed
        'startDateTime': date_range.split(',')[0] + 'T00:00:00Z',  # Start date
        'endDateTime': date_range.split(',')[1] + 'T23:59:59Z',    # End date
    }

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        return pd.DataFrame()  # Return an empty DataFrame if the request fails

    data = response.json()

    if '_embedded' not in data or 'events' not in data['_embedded']:
        return pd.DataFrame()  # Return an empty DataFrame if no events are found

    events = data['_embedded']['events']
    event_list = []
    for event in events:
        venue = event['_embedded']['venues'][0] if '_embedded' in event and 'venues' in event['_embedded'] else {}
        min_price = event['priceRanges'][0]['min'] if 'priceRanges' in event else float('inf')
        event_details = {
            'Event Name': event['name'],
            'Event URL': event['url'],
            'Event Start Date': event['dates']['start']['localDate'],
            'Min Price': min_price,
            'Max Price': event['priceRanges'][0]['max'] if 'priceRanges' in event else 'Not available',
            'Currency': event['priceRanges'][0]['currency'] if 'priceRanges' in event else 'Not available'
        }
        event_list.append(event_details)

    events_df = pd.DataFrame(event_list)
    events_df['Min Price'] = pd.to_numeric(events_df['Min Price'], errors='coerce')
    sorted_events_df = events_df.sort_values(by='Min Price')

    # Remove duplicate events based on 'Event Name'
    unique_events_df = sorted_events_df.drop_duplicates(subset='Event Name')

    return unique_events_df

def cheapest_hotel(city, hotel_budget):
    hotels = pd.read_csv('hotels.csv')
    hotels['price'] = hotels['price'].str.replace('US\$', '', regex=True)
    hotels['price'] = pd.to_numeric(hotels['price'], errors='coerce')

    hotel_destinations = hotels[hotels['address'].str.contains(city, case=False, na=False)]

    if not hotel_destinations.empty:
        min_price_index = hotel_destinations['price'].idxmin()
        hotel_with_min_price = hotel_destinations.loc[min_price_index]

        cheapest_hotel_name = hotel_with_min_price['name']
        cheapest_hotel_price = hotel_with_min_price['price']

        if cheapest_hotel_price <= hotel_budget:
            return cheapest_hotel_name, cheapest_hotel_price
    return "We haven't found a hotel within the budget"

def cheapest_flight(departure_airport_code, arrival_airport_code, departure_date,
                              number_of_adults, number_of_children, num_stops):
    details={}
    api_key = '6561253ef354679a7c8aaed9'  # Replace with your actual API key
    url = f'https://api.flightapi.io/onewaytrip/{api_key}/{departure_airport_code}/{arrival_airport_code}/{departure_date}/{number_of_adults}/{number_of_children}/0/Economy/USD'
    
    resp = requests.get(url)
    data = resp.json()

    # Debugging: Print API response
    print("API Response:", data)

    flights_data = []

    # Create a map of trip IDs to fares
    fares_map = {fare['tripId']: fare['price']['totalAmountUsd'] for fare in data.get('fares', [])}

    # Create a map of leg IDs to trip IDs
    trips_map = {}
    for trip in data.get('trips', []):
        for leg_id in trip['legIds']:
            trips_map[leg_id] = trip['id']

    # Check if data contains 'legs'
    if 'legs' in data:
        for leg in data['legs']:
            leg_id = leg.get('id')
            trip_id = trips_map.get(leg_id)
            price = fares_map.get(trip_id, 'Unknown')

            flight_info = {
                "Departure Code": leg.get('departureAirportCode', 'Unknown'),
                "Arrival Code": leg.get('arrivalAirportCode', 'Unknown'),
                "Airline Code":leg.get('airlineCodes','Unknown'),
                "StopOver Code":leg.get('stopoverAirportCodes','Unknown'),
                "Duration": leg.get('duration', 'Unknown'),
                "Start Time": leg.get('departureTime', 'Unknown'),
                "End Time": leg.get('arrivalTime', 'Unknown'),
                "Price": price
            }

            flights_data.append(flight_info)

    flights_df = pd.DataFrame(flights_data)
    flight_df = flights_df[flights_df['StopOver Code'].apply(lambda x: len(x) == num_stops)]
    flight_sorted_df=flight_df.sort_values(by='Price')
    best_flight = flight_sorted_df.iloc[[0]]
    details['Airlines'] = best_flight['Airline Code'].values[0][0]
    details['Stop'] = best_flight['StopOver Code'].values[0]
    details['Duration'] = best_flight['Duration'].values[0]
    details['Departure_time'] = best_flight['Start Time'].values[0]
    details['Arrival_time'] = best_flight['End Time'].values[0]
    details['Price'] = best_flight['Price'].values[0]
    return details['Airlines'], details['Stop'], details['Duration'], details['Departure_time'], details['Arrival_time'], details['Price']

def airport_code(city):
    amadeus = Client(
        client_id='2s74LcHZrvSGJsHLTsZ5eag8Lqew5ens',
        client_secret='gNg0XxiniAK4ReKn'
    )

    try:
        # Make the API call
        response = amadeus.reference_data.locations.get(
            keyword=f'{city}',
            subType='CITY,AIRPORT'
        )

        # Check if there is at least one result
        if response.data:
            first_location = response.data[0]
            # Access the 'iataCode' field
            iata_code = first_location.get('iataCode')
        else:
            print("No results found")

    except ResponseError as error:
        print(error)
    return iata_code

def top_sights(city):
    params = {
        "engine": "google",
        "q": f"Things to do in {city}",
        "api_key": "08042b572002104b0e5902f184cb96defb13dbdf051080c7bc54d956d905612a"
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    top_sights = results["top_sights"]
    df = pd.DataFrame(top_sights['sights'])
    df_sorted = df.sort_values(by=['extracted_price', 'reviews'], ascending=[True, False])
    return df_sorted

# Streamlit app interface
st.title('Welcome to the Smart Travel Recommendation System')
st.write('Below, we will ask you to let us know your travel details. We will then propose the cheapest hotel proposed by ebooking.com, the cheapest flight travel, and some events while you are visiting the city you selected.')
st.write('This interface is part of an academic project aiming to collect data and analyze them. This travel Recommender System has many limitations and requires additional work for a real use. As such, the hotel prices shown are the cheapest prices seen the internet with no consideration of the dates or the number of people traveling. Improved version requires non-free API')
st.write('Flights and events shows the price for the dates provided by you. Please note that the flight prices shown might not be fully accurate due to the free API used for this academic work.')
st.write('A business version would require subscribing to paid API for accurate and more detailed prices')
st.write('For this prototype, you can only choose between San Francisco or Miami as a destination')
# Inputs for departure and destination cities
departure_city = st.text_input('Enter your departure city', '')
destination_city = st.text_input('Enter your destination city', '')

# Inputs for the number of adults and children
number_of_adults = st.number_input('Number of adults', min_value=1, max_value=10, value=2)
number_of_children = st.number_input('Number of children', min_value=0, max_value=10, value=0)

# Input for budget
budget = st.slider('Select your maximum budget', 0, 10000, 2500)

# Input for travel and return dates
today = date.today()
tomorrow = today.replace(day=today.day + 1)
start_date = st.date_input('Travel Date', today)
end_date = st.date_input('Return Date', tomorrow)

date_range = f'{start_date},{end_date}'

# Input for the number of stops for flights
num_stops = st.selectbox('Preferred number of stops for flights', (0, 1))

if st.button('Find Cheapest Trip'):
    if departure_city and destination_city and start_date < end_date:
        # Get airport codes
        departure_airport_code = airport_code(departure_city)
        arrival_airport_code = airport_code(destination_city)

        if departure_airport_code and arrival_airport_code:
            # Get the cheapest flights
            airline, stop, duration, departure_time, arrival, price = cheapest_flight(departure_airport_code, arrival_airport_code, start_date.strftime('%Y-%m-%d'),
                                                   number_of_adults, number_of_children, num_stops)
            if airline:
                st.write(f'Cheapest Flight to go:, Airline: {airline}, stopover: {stop}, duration: {duration}, departure: {departure_time}, arrival: {arrival}, price: {price}')
                updated_budget = budget - price
            else:
                st.error("No flights found for the given criteria.")
            #Return flights   
            airline, stop, duration, departure_time, arrival, price = cheapest_flight(departure_airport_code, arrival_airport_code, start_date.strftime('%Y-%m-%d'),
                                                   number_of_adults, number_of_children, num_stops)
            if airline:
                st.write(f'Cheapest Flight to return:, Airline: {airline}, stopover: {stop}, duration: {duration}, departure: {departure_time}, arrival: {arrival}, price: {price}')
                updated_budget = updated_budget - price
            else:
                st.error("No flights found for the given criteria.")
            # Get the cheapest hotel
            st.write(f'After selecting these flights, your budget now stands at: {updated_budget}')
            hotel_name, hotel_price = cheapest_hotel(destination_city, updated_budget)
            if hotel_name and hotel_price:
                st.success(f"Cheapest Hotel: {hotel_name}, Price: {hotel_price}")
                updated_budget = updated_budget - price
            else:
                st.error("No hotels found within the given budget.")
    
            st.write(f'After selecting this hotel, your budget now stands at : {updated_budget}')
            st.write("Below, we provide you a list of events happening in the destination during your stay. You are free to make a selection depending on your remaining budget and interests")
            events_list = get_events_by_city_and_date(destination_city, date_range)
            st.write(events_list)
            sights = top_sights(destination_city)
            st.write("Below, we provide you a list of touristic attraction in the destination. You are free to make a selection depending on your remaining budget and interests")
            st.write(sights)
        else:
            st.error("Could not retrieve airport codes.")
    else:
        st.error("Please enter valid cities and ensure the travel dates are correct.")

# Add here additional logic for processing the inputs, 
# like fetching flight prices, event details, etc.

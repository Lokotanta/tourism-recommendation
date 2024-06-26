import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import urllib.request
import io
import googlemaps
import datetime

# Google Maps API setup
google_maps_api_key = "AIzaSyAkkI9g3oQwduXlSOQDvcgq3OUimSfhhh4"
gmaps = googlemaps.Client(key=google_maps_api_key)

def get_lat_lng(destination):
    geocode_result = gmaps.geocode(destination)
    if geocode_result and geocode_result[0]:
        return geocode_result[0]['geometry']['location']
    else:
        return None

def get_top_places(destination):
    lat_lng = get_lat_lng(destination)
    if lat_lng:
        places_result = gmaps.places_nearby(location=lat_lng,
                                             radius=10000,
                                             type='tourist_attraction',
                                             rank_by='prominence')
        top_places = []
        if places_result['status'] == 'OK':
            for place in places_result['results'][:5]:
                place_name = place['name']
                place_rating = place.get('rating', 'N/A')
                place_photo = place.get('photos', [])
                photo_url = None
                if place_photo:
                    photo_reference = place_photo[0]['photo_reference']
                    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={google_maps_api_key}"
                top_places.append((place_name, place_rating, photo_url))
        return top_places
    else:
        return None

def provide_destination_info(destination):
    if destination:
        message = f"Sure! {destination} is a popular tourist destination. Let me find some top-rated and nearest places for you."
        top_places = get_top_places(destination)

        if top_places:
            for place_name, place_rating, photo_url in top_places:
                message += f"\n{place_name} (Rating: {place_rating}):"
                if photo_url:
                    message += "\n"
                    image = Image.open(io.BytesIO(urllib.request.urlopen(photo_url).read()))
                    photo = ImageTk.PhotoImage(image)
                    root = tk.Toplevel()
                    label = tk.Label(root, image=photo)
                    label.image = photo
                    label.pack()
                else:
                    message += "\nNo photo available."
                places_result = gmaps.places(query=place_name)
                if places_result['status'] == 'OK' and places_result['results']:
                    place_id = places_result['results'][0]['place_id']
                    place_details = gmaps.place(place_id)
                    if place_details['status'] == 'OK':
                        place_info = place_details['result']
                        place_address = place_info.get('formatted_address', 'Address not available')
                        place_hours = place_info.get('opening_hours', {}).get('weekday_text', [])
                        message += f"\n  Address: {place_address}"
                        message += f"\n  Opening Hours:"
                        for hour in place_hours:
                            message += f"\n    {hour}"
                        message += f"\n  Description: {place_name} is a popular tourist destination known for its {place_name.lower()}. It is located at {place_address}."
                else:
                    message += f"\nNo additional information found for {place_name}."
        else:
            message += "\nNo top places found for this destination."
    else:
        message = "Please provide a valid destination."
    return message

def provide_reviews(destination):
    message = f"Reviews for {destination}:"
    top_places = get_top_places(destination)
    if top_places:
        for place_name, _, _ in top_places:
            places_result = gmaps.places(query=place_name)
            if places_result['status'] == 'OK' and places_result['results']:
                place_id = places_result['results'][0]['place_id']
                place_details = gmaps.place(place_id)
                if place_details['status'] == 'OK':
                    place_reviews = place_details['result'].get('reviews', [])
                    if place_reviews:
                        message += f"\n{place_name}:"
                        for review in place_reviews:
                            message += f"\n - {review['text']}"
                    else:
                        message += f"\nNo reviews found for {place_name}."
                else:
                    message += f"\nFailed to fetch details for {place_name}."
            else:
                message += f"\nFailed to find {place_name}."
    else:
        message += "\nNo top places found for this destination."
    return message

def generate_itinerary(destination):
    message = "Generating itinerary..."
    top_places = get_top_places(destination)
    if top_places:
        message += "\nYour itinerary:"
        total_time = datetime.timedelta(hours=0)
        for i, (place_name, _, _) in enumerate(top_places, 1):
            message += f"\n{i}. {place_name}"
            travel_time = datetime.timedelta(minutes=30)
            total_time += travel_time
            message += f"\n   Travel time: {travel_time}"
            message += f"\n   Time spent: 1-2 hours"
            total_time += datetime.timedelta(hours=1)
        message += f"\nTotal time for the trip: {total_time}"
        message += "\nEnjoy your trip!"
    else:
        message += "\nNo top places found for this destination."
    return message

def ask_destination():
    destination = simpledialog.askstring("Destination", "Where do you want to go?")
    return destination

def main():
    root = tk.Tk()
    root.withdraw()

    destination = ask_destination()
    info_message = provide_destination_info(destination)
    messagebox.showinfo("Destination Information", info_message)

    reviews_message = provide_reviews(destination)
    messagebox.showinfo("Reviews", reviews_message)

    itinerary_message = generate_itinerary(destination)
    messagebox.showinfo("Itinerary", itinerary_message)

    messagebox.showinfo("Thanks", "Thank you for using our service!")

if __name__ == "__main__":
    main()
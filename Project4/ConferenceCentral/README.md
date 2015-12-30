App Engine application for the Udacity training course.

## Products
- [App Engine][1]

## Language
- [Python][2]

## APIs
- [Google Cloud Endpoints][3]

## Setup Instructions
1. Update the value of `application` in `app.yaml` to the app ID you
   have registered in the App Engine admin console and would like to use to host
   your instance of this sample.
2. Update the values at the top of `settings.py` to
   reflect the respective client IDs you have registered in the
   [Developer Console][4].
3. Update the value of CLIENT_ID in `static/js/app.js` to the Web client ID
4. (Optional) Mark the configuration files as unchanged as follows:
   `$ git update-index --assume-unchanged app.yaml settings.py static/js/app.js`
5. Run the app with the devserver using `dev_appserver.py DIR`, and ensure it's running by visiting your local server's address (by default [localhost:8080][5].)
6. (Optional) Generate your client library(ies) with [the endpoints tool][6].
7. Deploy your application.


[1]: https://developers.google.com/appengine
[2]: http://python.org
[3]: https://developers.google.com/appengine/docs/python/endpoints/
[4]: https://console.developers.google.com/
[5]: https://localhost:8080/
[6]: https://developers.google.com/appengine/docs/python/endpoints/endpoints_tool

## Course Tasks
1a. Define the Session class and SessionForm
    
    A Session class and SessionForm model were created so that the user can create sesssions for conferences.
    
1b. Define the following Endpoints methods
    
    Created endpoints getConferenceSessions(webSafeConferenceKey), getConferenceSessionsByType(webSafeConferenceKey, typeOfSession), getSessionsBySpeaker(speaker),
    and createSession(SessionForm, webSafeConferenceKey) so that users can interact with sessions now.
    
1c. Explain your design choices

        I designed the Session and SessionForm models with the Conference and ConferenceForm models in mind. The Session model has all the required properties
    for this application's current needs. Things to note regarding Session: all properties are treated as strings except for duration, date, and startTime, which
    are respectively Float, Date, and Time properties.
        The SessionForm model is slightly different because of the need for a webSafeConferenceKey to do a lookup for the associated conference. There is another slight
    difference - the Date and Time properties are received as strings in the SessionForm model. This creates validation problems but allows the user to submit the fields
    in whatever format the programmer desires.
    
2a. Add Sessions to User Wishlist

    Added the endpoints addSessionToWishlist(SessionKey), getSessionsInWishlist(), and deleteSessionInWishlist(SessionKey) so that users can add sessions to a wishlist
    to possibly register for later.
    


    


from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
import logging
import webapp2
import json
import random
import os
import urllib
import string


CLIENT_ID = "998515741323-lsrfvgktllh131t70k5vabndqll5dkrs.apps.googleusercontent.com"

CLIENT_SECRET = "pzJmjEjAO5hiMj1p4JBm2sV2"
AUTH_REDIRECT_URI = "https://cs496-oauth-assign.appspot.com/oauth" 
STATE_GLOBAL = ""


class OauthHandler(webapp2.RequestHandler):
	def get(self):
		#logging.debug('The contents of the GET request are:' + repr(self.reqeust.GET))
		global STATE_GLOBAL	

		oauth = self.request.GET['code']
		state = self.request.GET['state']

		#validFlag = False	
		#if state == STATE_GLOBAL:
			#validFlag = True	

		#form post request
		post_req = {"code": oauth, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
			'redirect_uri': AUTH_REDIRECT_URI, "grant_type": "authorization_code"}	

		#send redirect to google's endpoint in order to get token back
		#https://piazza.com/class/jirt8wnwnke6bt?cid=54 (use urlencode)	
		payload = urllib.urlencode(post_req)
		header = {"Content-Type": "application/x-www-form-urlencoded"}
		
		#or use https://accounts.google.com/o/oauth2/token??????
        #lectures slide/notes indicate to use https://www.googleapis.com/oauth2/v4/token
		result = urlfetch.fetch(url="https://www.googleapis.com/oauth2/v4/token", payload=payload, 
			method=urlfetch.POST, headers=header)


		#"server resopnse with access token"	
		res_data = json.loads(result.content)

		bigError = True
		for i in res_data:
			if i == "access_token":
				bigError = False

		snapshot = str(res_data) 

		#more info here/source: https://developers.google.com/+/web/api/rest/latest/people/get
		header = {'Authorization': 'Bearer ' + res_data['access_token']}
		result = urlfetch.fetch(url="https://www.googleapis.com/plus/v1/people/me",
			method=urlfetch.GET, headers=header)	

		#get the user's first and last name and the URL to access their Google Plus account	
		res_data = json.loads(result.content)

		nameFieldPresent = False
		gURLPresent = False	
	
	
		#check if the necessary fields are present
		for i in res_data:
			if i == "name":
				if i[0]:
					nameFieldPresent = True		
			if i == "url":
				if i[0]:
					gURLPresent = True		


			
		#https://developers.google.com/+/web/api/rest/latest/people#resource		
		if nameFieldPresent == True and gURLPresent	== True: #and validFlag == True:		
			firstName = res_data["name"]["givenName"]
			lastName = res_data["name"]["familyName"]
			gplusURL = res_data["url"]
			form_output = {"fname": firstName, "lname": lastName, "gplus_url": gplusURL, "state": state}

		elif bigError == True:
			form_output	= {"error": "BIG ERROR FLAG TRIPPED, WE DIDNT' EVEN GET THE TOKEN BACK!"}

		else:
			form_output = {"error": "Ooops something bad happened!", "state": state, "gplus_url": "google.com",
			"fname": "SUM TING", "lname": "WONG", "edata": str(res_data), "first_req": snapshot}		


		#display result
		path = os.path.join(os.path.dirname(__file__), 'views/results.html')
		self.response.out.write(template.render(path, form_output))





class MainPage(webapp2.RequestHandler):
	def get(self):
		global STATE_GLOBAL

		#generate random string for state
		#source: https://stackoverflow.com/questions/2257441/random-string-generation
		#-with-upper-case-letters-and-digits-in-python 
		randStr = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(32)])

		url_linktext = "Go to provide google account"	


		complete_URL = "https://accounts.google.com/o/oauth2/v2/auth?"	
		
		#example URL:
		#https://accounts.google.com/o/oauth2/v2/auth?response_type=code
		#&client_id=107461084371-0vr1hjlgafvltftq307ceq0pcjrk2ad4.apps.googleusercontent.com
		#&redirect_uri=https://osu-cs496-demo.appspot.com/oauth
		#&scope=email
		#&state=SuperSecret9000

		response_type = "response_type=code"
		access_type = "&access_type=offline"
		client_id = "&client_id=" + CLIENT_ID
		redirect_uri = "&redirect_uri=" + AUTH_REDIRECT_URI
		scope = "&scope=email"
		state = "&state=" + randStr
		STATE_GLOBAL = STATE_GLOBAL	+ randStr	

		#form the URL
		complete_URL = complete_URL	+ response_type
		complete_URL = complete_URL	+ access_type
		complete_URL = complete_URL	+ client_id
		complete_URL = complete_URL	+ redirect_uri
		complete_URL = complete_URL	+ scope
		complete_URL = complete_URL	+ state
		complete_URL = complete_URL	+ "&include_granted_scopes=true" #why this doesn't work without this i have no clue


		#source: https://stackoverflow.com/questions/26724083/how-to-load-html-page-with-python-on-app-engine		
		form_input = {'input_URL' : complete_URL}
		path = os.path.join(os.path.dirname(__file__), 'views/home.html')
		self.response.out.write(template.render(path, form_input))		

app = webapp2.WSGIApplication([
	('/', MainPage),
	('/oauth', OauthHandler)
], debug=True)
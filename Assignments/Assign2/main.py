# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from google.appengine.ext import ndb

import webapp2
import json


#class definitions, source: lecture video/google cloud tutorials

#boat class definition
class Boat(ndb.Model):
	id = ndb.StringProperty()
	name = ndb.StringProperty(required=True)
	type = ndb.StringProperty(required=True)
	length = ndb.IntegerProperty(required=True)
	at_sea = ndb.BooleanProperty()


#slip class definition
class Slip(ndb.Model):
	id = ndb.StringProperty()
	number = ndb.IntegerProperty(required=True)
	current_boat = ndb.StringProperty()
	arrival_date = ndb.StringProperty()
	departure_history = ndb.JsonProperty(repeated=True)




#route definitions

#boat route
class BoatHandler(webapp2.RequestHandler):


	#add boat (POST)
	def post(self):
		#obtain the data from request body
		boat_data = json.loads(self.request.body)

		namePresent = False
		typePresent = False
		lengthPresent = False	


		#validate input format - check that the manditory fields are present and not empty/valid
		for i in boat_data:
			if i == "name" and boat_data['name'] != "":
				namePresent = True
			elif i == "type" and boat_data['type'] != "":
				typePresent = True
			elif i == "length" and boat_data['length'] != "":
				lengthPresent = True		


		#validate length input
		#source: https://stackoverflow.com/questions/19440952/how-do-i-check-if-raw-input-is-integer-in-python-2-7
		try:
			int(boat_data['length'])
			if boat_data['length'] > 0:
				lengthPresent = True

		except ValueError:
			lengthPresent = False


		#if input was valid create the boat					
		if namePresent and typePresent and lengthPresent and lengthPresent:	
			new_boat = Boat(name=boat_data['name'], type=boat_data['type'], length=boat_data['length'])
			
			#default neewly created boat at sea
			new_boat.at_sea = True
			new_boat.put()

			#assign urlsafe id
			new_boat.id = str(new_boat.key.urlsafe())
			new_boat.put()


			#get the urlsafe key
			boat_dict = new_boat.to_dict()
			boat_dict['self'] = '/boats/' + new_boat.key.urlsafe()
			self.response.status = 200
			self.response.write(json.dumps(boat_dict)) #output the url so that we can quickly call a GET on it while testing


		else:
			self.response.status = 400
			self.response.write("Bad Request ERROR: Input format error. ")		


	#delete a boat
	def delete(self, id=None):
		if id:
			#check if boat id to be deleted exists
			present = False 
			for boat in Boat.query():
				if boat.id == id:
					present = True
			if present != False:

				boat_removed_fromSlip = False

				#if we found the boat that is to be deleted, remove associated slip data (if applicable)
				for s in Slip.query(Slip.current_boat == id):
					if s.current_boat:
						s.current_boat = ""
						s.arrival_date = ""
						s.departure_history = ""
						slip.put()
						boat_removed_fromSlip = True
						break	

				if boat_removed_fromSlip == True:
					ndb.Key(urlsafe=id).delete()
					self.response.status = 200
					self.response.write("Boat was successfully deleted and associated slip cleared.");
				else:
					ndb.Key(urlsafe=id).delete()
					self.response.status = 200
					self.response.write("Boat was successfully deleted. (No associated slip.)")


			else:
				self.response.status = 404
				self.response.write("ERROR: Cannot delete boat - boat id provided could not be found.")
		else:
			self.response.status = 400
			self.response.write("ERROR: Bad request.")

			
	#view a boat (GET) or many boats
	def get(self, id=None):
		
		#first case: only one boat to be displayed
		if id:
			present = False
			for boat in Boat.query():
				if boat.id == id:
					present = True

			if present != False:   #apply lecture example replacing boat for fish related names
				self.response.status = 200
				b = ndb.Key(urlsafe=id).get()
				boat_dict = b.to_dict()
				boat_dict['self'] = "/boats/" + id
				self.response.write(json.dumps(boat_dict))

			else:
				self.response.status = 404
				self.response.write("ERROR: Cannot find provided boat id.")


		#second case, display all boats
		else:
			self.response.status = 200
			
			output = []

			for b in Boat.query():
				#b = ndb.Key(urlsafe=id).get()
				boat_dict = b.to_dict()
				output.append(boat_dict)
			
			self.response.write(json.dumps(output))	
	

	#modify a boat (PATCH) - note this patch method does not allow for ship/dock assignment
	def patch(self, id=None):
		
		if id:
			present = False
			for boat in Boat.query():
				if boat.id == id:
					boat_data = json.loads(self.request.body)
					present = True
					

					namePresent = False
					typePresent = False
					lengthPresent = False

					#validate input format - check that the manditory fields are present and not empty/valid
					for i in boat_data:
						if i == "name" and boat_data['name'] != "":
							namePresent = True
						elif i == "type" and boat_data['type'] != "":
							typePresent = True
						elif i == "length" and boat_data['length'] != "":
							lengthPresent = True

					#validate length input
					#source: https://stackoverflow.com/questions/19440952/
						#how-do-i-check-if-raw-input-is-integer-in-python-2-7
					lengthVald = False
					try:
						int(boat_data['length'])
						if boat_data['length'] > 0:
							lengthValid = True

					except ValueError:
						lengthValid = False

					b = ndb.Key(urlsafe=id).get()
					#if input was valid update appropriate fields


					if (namePresent == False and typePresent == False and lengthPresent == False) or lengthValid == False:
						self.response = 400
						self.response.write("ERROR: update request fields were empty or incorrect.")
					else:
						if namePresent  == True:
							b.name = boat_data['name']
							b.put()
							self.response.write("Name updated.\n")
						if typePresent == True:
							b.type = boat_data['type']
							b.put()
							self.response.write("Type updated.\n")
						if lengthPresent == True:
							b.type = boat_data['length']
							b.put()
							self.response.write("Length updated.\n")
						break

			if present == False:
				self.response.status = 404
				self.response.write("ERROR: Cannot find provided boat id for editing.")		
				
		else:
			self.response.status = 400
			self.response.write("ERROR: Valid id must be provided to edit boat entry.")






class SlipHandler(webapp2.RequestHandler):

	#add slip (POST)
	def post(self):
		#just as with BoatHandler, obtain data from request body
		slip_data = json.loads(self.request.body)
		
		numberPresent = False
		for i in slip_data:
			if i == "number" and slip_data['number'] != "" and slip_data['number'] != None:
				numberPresent = True
			else:
				numberPresent = False

		#validate length input
		#source: https://stackoverflow.com/questions/19440952/how-do-i-check-if-raw-input-is-integer-in-python-2-7
		numberValid = False
		if numberPresent == True:
			try:
				int(slip_data['number'])
				if slip_data['number'] > 0:
					numberValid = True

			except ValueError:
				numberValid = False


		slip_AlreadyExists = False
		if numberPresent == True and numberValid == True:			
			#check to see if slip number already exists
			for slip in Slip.query():
				if slip.number == slip_data['number']:
					slip_AlreadyExists = True
					self.response.status = 400
					self.response.write("ERROR: Slip number " + (str)(slip.number) + " already taken.")
					break

		#if error validation did not trigger, update values
		if slip_AlreadyExists == False and numberValid == True and numberPresent == True:
			new_slip = Slip(number=slip_data['number'])

			#populate default values
			new_slip.current_boat = ""
			new_slip.put()

			new_slip.arrival_date = ""
			new_slip.put()

			new_slip.departure_history = []
			new_slip.put()

			new_slip.id = str(new_slip.key.urlsafe())
			new_slip.put()	

			#urlsafe key to url
			slip_dict = new_slip.to_dict()
			slip_dict['self'] = '/slips/' + new_slip.key.urlsafe()
			self.response.status = 200
			self.response.write(json.dumps(slip_dict))

		else:
			self.response.status = 400
			self.response.write("ERROR: Null or invalid slip number given.")			

	def get(self, id=None):

		#first case: only one slip to be displayed
		if id:
			present = False
			for s in Slip.query():
				if s.id == id:
					present = True

			if present != False:
				self.response.status = 200
				s = ndb.Key(urlsafe=id).get()
				slip_dict = s.to_dict()
				slip_dict['self'] = "/slips/" + id
				self.response.write(json.dumps(slip_dict))

			else:
				self.response.status = 404
				self.response.write("ERROR: Cannot find proivded slip id.")

		#second case, display all slips
		else:
			self.response.status = 200

			output = []

			for s in Slip.query():
				slip_dict = s.to_dict()
				output.append(slip_dict)
			self.response.write(json.dumps(output))

	def delete(self, id=None):
		if id:
			present = False
			for s in Slip.query():
				if s.id == id:
					present = True
			if present != False:
				
				slip_to_del = ndb.Key(urlsafe=id).get()
				boat_set_to_sea = False

				#check to see if we need to set a boat to be at sea
				if slip_to_del.current_boat != "":
					boat_in_pier = ndb.Key(urlsafe=slip_to_del.current_boat).get()
					boat_in_pier.at_sea = True
					boat_in_pier.put()
					boat_set_to_sea = True

				if boat_set_to_sea == True:
					ndb.Key(urlsafe=id).delete()
					self.response.status = 200
					self.response.write("Slip was successfully deleted and associated ship set to sea.")
				else:
					ndb.Key(urlsafe=id).delete()
					self.response.status = 200
					self.response.write("Slip was successfully deleted. (No associated boat).")

			else:
				self.response.status = 404
				self.response.write("ERROR: Cannot delete slip - slip id provided could not be found.")
		else:
			self.response.status = 400
			self.response.write("ERROR: Bad request.")

	#in this case the only values that should be editable via patch request is the id.
	#all other values are handled in separate handler or not editable (i.e. id)		
	def patch(self, id=None):
		if id:
			present = False
			slip_data = json.loads(self.request.body)

			numberPresent = False
			slip_AlreadyExists = False

			for i in slip_data:
				if i == "number" and slip_data['number'] != "" and slip_data['number'] != None:
					numberPresent = True
				else:
					numberPresent = False

			#validate length input
			#source: https://stackoverflow.com/questions/19440952/how-do-i-check-if-raw-input-is-integer-in-python-2-7
			numberValid = False
			if numberPresent == True:
				try:
					int(slip_data['number'])
					if slip_data['number'] > 0:
						numberValid = True

				except ValueError:
					numberValid = False	

			if numberPresent == True and numberValid == True:
				#check to see if slip number already exists
				for s in Slip.query():
					if s.number == slip_data['number']:
						slip_AlreadyExists = True
						self.response.status = 400
						self.response.write("ERROR: Slip number " + (str)(slip.number) + "already taken.")
						break

			#update if no errors encountered
			if slip_AlreadyExists == False and numberValid == True and numberPresent == True:
				s = ndb.Key(urlsafe=id).get()

				s.number = slip_data['number']
				s.put()

				slip_dict = s.to_dict()
				slip_dict['self'] = '/slips/' + s.key.urlsafe()
				self.response.status = 200
				self.response.write(json.dumps(slip_dict))

			else:
				self.response.status = 400
				self.response.write("ERROR: Null or invalid slip number for update given.")	



		else:
			self.response.status = 400
			self.response.write("ERROR: Valid id must be provided to edit slip entry.")





#https://stackoverflow.com/questions/46723212/gae-python-webapp2-url-resource-id-resource
#arrival handler is what it is: only to be used for adding ships to dock plus a single get
#ships or slips cannot be deleted or edited here
#the id passed in the URL is that of the boat
#slip number, arrival date passed in body of post request
class Arrival_DepartureHandler(webapp2.RequestHandler):

	#arrival of boat at dock portion
	def post(self, id=None):

		if id:
			boat_present = False
			slip_present = False
			boat_at_sea = False
			slip_empty = False

			arrival_data = json.loads(self.request.body)

			#check that Boat exists
			for boat in Boat.query():
				if boat.id == id:
					boat_present = True
					break


			#check that boat is actually at sea
			if boat_present == True:
				b = ndb.Key(urlsafe=id).get()
				if b.at_sea == True:
					boat_at_sea = True



			#check that slip exists		
			for slip in Slip.query():
				if slip.number == arrival_data['number']:
					raw_slip_id = slip.id
					slip_present = True

			#now check that slip is not occupied
			if slip_present == True:
				#check that slip is empty
				s = ndb.Key(urlsafe=raw_slip_id).get()
				if s.current_boat == "":
					slip_empty = True

			#if checks passed, add boat to slip
			if boat_present and slip_present and boat_at_sea and slip_empty:
				
				#Update Boat
				b.at_sea = False
				b.put()

				#Update Slip
				s.current_boat = b.id
				s.put()

				s.arrival_date = arrival_data['arrival_date']
				s.put()

				self.response.status = 200
				self.response.write("Successfully added boat to slip.")



			else:
				
				if boat_present == False:
					self.response.status = 400 
					self.response.write("ERROR: Boat does not exist/not found.\n")
				if slip_present == False:
					self.response.status = 400
					self.response.write("ERROR: Slip number does not exist/not found.\n")
				if boat_at_sea == False:
					self.response.status = 400
					self.response.write("ERROR: Boat is not at sea and already docked.\n")
				if slip_empty == False:
					self.response.status = 403
					self.response.write("ERROR: Slip is not empty and cannot be assigned a new boat.\n")
					
			

		else:
			self.response.status = 400
			self.response.write("ERROR: bad request, id of arriving boat must be provided.")



	#departure of boat from dock
	#input: {"departure_date":"xx/xx/xxxx"} and departing boat id in the header
	def put(self, id=None):
		invalidData = True

		#this should be the only data check necessary since an incomplete JSON object will trigger a 500
		#"internal server error"
		departure_data = json.loads(self.request.body)
		if departure_data["departure_date"] != "":
			invalidData = False

		if id and invalidData == False:
			boat_present = False
			boat_docked = False

			#check that boat exists
			for boat in Boat.query():
				if boat.id == id:
					boat_present = True
					break

			#check that boat is docked
			if boat_present == True:
				b = ndb.Key(urlsafe=id).get()
				if b.at_sea == False:
					boat_docked = True

			#if checks passed, add departure data to slip and send boat to sea

			if boat_present and boat_docked:
				for dock in Slip.query():
					if dock.current_boat == id:
						raw_slip_id = dock.id
						break

						
				s = ndb.Key(urlsafe=raw_slip_id).get()

				#update slip data
				#update departure_history
				s.departure_history.append({"departure_date" : departure_data["departure_date"], 
					"departed_boat" : id})
				s.put()

				#update current_boat
				s.current_boat = ""
				s.put()

				#clear arrival_date
				s.arrival_date = ""
				s.put()

				b.at_sea = True
				b.put()


				self.response.status = 200
				self.response.write("Boat successfully departed from slip.")

			else:
				self.response.status = 400
				if boat_present == False:
					self.response.write("ERROR: Boat does not exist/not found.\n")



		elif invalidData == False:
			self.response.status = 400
			self.response.write("ERROR: bad request, id of departing boat must be provided.\n")

		else:
			self.response.status = 400
			self.response.write("ERROR: bad request.\n")


	#combined get call for ease of testing - list boats and docks or just one boat
	def get(self, id=None):
		if id:
			present = False
			for b in Boat.query():
				if b.id == id:
					present = True

			if present != False:
				self.response.status = 200
				b = ndb.Key(urlsafe=id).get()
				boat_dict = b.to_dict()
				boat_dict['self'] = "/boats/" + id
				self.response.write(json.dumps(slip_dict))


		else:
			self.response.status = 200

			output = []

			#display boats
			for b in Boat.query():
				boats_dict = b.to_dict()
				output.append(boats_dict)
				

			#display slips": 
			for s in Slip.query():
				slip_dict = s.to_dict()
				output.append(slip_dict)
			self.response.write(json.dumps(output))








class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!\n')
        



#as per lecture video, the PATCH method needs to be added since it is not supported by default
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/boats', BoatHandler),
    ('/slips', SlipHandler),
    ('/boats/(.*)', BoatHandler),
    ('/slips/(.*)', SlipHandler),
    ('/boat/(.*)/arrival', Arrival_DepartureHandler),
    ('/boat/(.*)/departure', Arrival_DepartureHandler),
    ('/marina', Arrival_DepartureHandler)          
], debug=True)

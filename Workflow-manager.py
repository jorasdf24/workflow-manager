import os
import sys
import time
import sqlite3
import urllib.request as req
import urllib.parse as p

def is_valid_url(url):
	"""Return True if the URL is valid, and false if not"""
	try:
		request = req.Request(url)
		try:
			response = req.urlopen(request)
			response = True
		except:
			response = False
	except:
		response = False

	return response
	
def is_valid_path(path):
	"""Return True if the path is valid and False if not"""
	return os.path.exists(path)
	
def get_paths_based_workflow(cursor,workflow_name):
	"""Take the cursor and the workflow name, and return a list of paths that are found in this workflow"""
	path_list = []
	
	for name in cursor.execute("SELECT path FROM workflows WHERE workflow_name=?;",(workflow_name,)):
		path_list.append(name[0])
	return path_list

def get_workflow_list(cursor):
	"""Return a list that contains all the name of the workflows exists in the DB"""
	workflow_list = []
		
	for name in cursor.execute("SELECT workflow_name FROM workflows;"):

		#Clean the name
		name = str(name).replace("(","")
		name = str(name).replace(")","")
		name = str(name).replace(",","")
		name = str(name).replace("'","")
		workflow_list.append(name)

	return workflow_list

def open_paths_from_workflow(cursor,workflow_name):
	"""Launch all paths from the workflow called workflow_name"""
	# iterate through each path 
	for path in cursor.execute("SELECT path FROM workflows WHERE workflow_name = " + "'" + workflow_name + "';"):
		try:
		
			# Start the path
			os.startfile(path[0])
			time.sleep(0.1)
			
		except Exception:
			print ("Error opening file: " + str(path[0]))
			
		# There is at least one path				
		is_workflow_exist = True
		
	if not is_workflow_exist:
		print ("This workflow does not exist...")
	else:
		print ("Enjoy")
		
			
			

def print_menu():
	"""Print the Main Menu"""
	print ("\n1 - Start workflow")
	print ("2 - Create new workflow")
	print ("3 - Edit workflow")
	print ("4 - Delete workflow")
	print ("5 - Print workflows")
	print ("6 - Exit")

def print_menu2():
	"""Print the Sub Menu to the third option of the Main Menu"""
	print ("\n\t1 - Change workflow name")
	print ("\t2 - Add path")
	print ("\t3 - Delete Path")
	print ("\t4 - Exit edit")

def workflow_exists(data_base, workflow_name):
	"""Check if a certain workflow exists in the DB"""
	result = False
	
	# Need at least one iteration
	for path in data_base.execute("SELECT path FROM workflows WHERE workflow_name = ?;", (workflow_name,)):
		result = True
	
	return result
	
def path_exists(data_base, workflow_name, path):
	"""Return True if a certain path exist in the DB in a specific workflow, and False if not"""
	result = False
	
	# Need at least one iteration
	for workflow_name, path in data_base.execute("SELECT workflow_name, path FROM workflows WHERE workflow_name = " + "'" + workflow_name + "'" + " and path = " + "'" + path + "';"):
		result = True
		
	return result

def main():

	# Connect to the DB, create new one if doesn't exist
	connection = sqlite3.connect('workflows.db')
	
	# The cursor used for execute SQL command through the code
	data_base = connection.cursor()
	
	# Declare the architecture if the DB is just created 
	try:
		data_base.execute("CREATE TABLE workflows(workflow_name text, path text);")
	except Exception:
		pass
	
	run = True
	
	
	while run:

		workflow_list_name = get_workflow_list(data_base)
		print_menu()
				
		menu_choose = str(input("Enter your choice: "))
		
		if menu_choose in workflow_list_name:
			open_paths_from_workflow(data_base,menu_choose)
			run = False

		# Start workflow
		if menu_choose is "1":
			workflow_name = str(input("Which workflow do you want to start? "))
			is_workflow_exist = False
			
			# iterate through each path 
			for path in data_base.execute("SELECT path FROM workflows WHERE workflow_name = " + "'" + workflow_name + "';"):
				try:
				
					# Start the path
					os.startfile(path[0])
					time.sleep(0.1)
					
				except Exception:
					print ("Error opening file: " + str(path[0]))
					
				# There is at least one path				
				is_workflow_exist = True
				
			if not is_workflow_exist:
				print ("This workflow does not exist...")
			else:
				print ("Enjoy")
				run = False
				
		# New workflow
		elif menu_choose is "2":
			valid_path = []
			workflow_name = str(input("Enter a name for this workflow: "))
			
			# Check if the requested new workflow name is not in use
			if workflow_exists(data_base, workflow_name):
				print ("There's already a workflow with this name!")
				
			# Make sure the name is not empty
			elif workflow_name == '':
				print ("Empty name?")
			else:
				print ("Enter the paths of your desired things to be open. Enter -1 to close and save this workflow")
				print ('')
				
				path = ""
				counter = 1
				
				while path != "-1":
					path = str(input("Enter path number " + str(counter) + ": "))
					
					# Check valid path\URL and that they not exist in the DB
					if (is_valid_path(path) or is_valid_url(path)) is False or path_exists(data_base, workflow_name, path):
						if path != "-1":
							print ("Path either already exists or is invalid!")
							
						valid_path.append(False)
					else:
						values = (workflow_name, path)
						
						# Insert the values for the new workflow
						data_base.execute("INSERT INTO workflows VALUES (?,?);", values)
						print ("Path saved")
						valid_path.append(True)
					counter += 1
				
				# Save changes
				connection.commit()
				
				if True in valid_path:
					print (workflow_name + " workflow saved successfully!")
				else:
					print ("Workflow wasn't saved")
		
		# Edit workflow
		elif menu_choose is "3":
			run2 = True
			workflow_name = str(input("Which workflow do you want to edit? "))
			
			if workflow_exists(data_base, workflow_name):
			
				while run2:
					print_menu2()
					edit_choose = str(input("\tEnter your choice: "))
					
					# Change workflow name
					if edit_choose is "1":
					
						new_workflow_name = str(input("\tEnter new workflow name: "))
						
						data_base.execute("UPDATE workflows SET workflow_name = " + "'" + new_workflow_name + "'" + " WHERE workflow_name = " + "'" + workflow_name + "';")
						
						# Save changes						
						connection.commit()
						
						workflow_name = new_workflow_name
						print ("\tName changed!")
					
					# Add path to the workflow
					elif edit_choose is "2":
						path = str(input("\tEnter the path of your desired thing to be open: "))
						
						if (is_valid_path(path) or is_valid_url(path)) is True and not path_exists(data_base, workflow_name, path):
						
							values = (workflow_name, path)
							data_base.execute("INSERT INTO workflows VALUES (?,?);", values)
							connection.commit()
							
							print ("\tPath added!")
							
						else:
							print ("\tPath either already exists or is invalid!")
					
					# Delete path in the workflow
					elif edit_choose is "3":
							
						print("\tEnter path to delete: ")
						
						# Get the lost of paths in the workflows
						path_list = get_paths_based_workflow(data_base,workflow_name)
						
						path_number_dict = {}
						
						# Make number based choosing system
						for i in range(len(path_list)):
							print("\t" + str(i + 1) + " - " + str(path_list[i]))
							path_number_dict[str(i + 1)] = path_list[i]
						
						number_input = str(input("\t"))
						
						try:	
							path = path_number_dict[number_input]
						except:
							path = ""
						
						if path_exists(data_base, workflow_name, path):
							
							# Delete...
							data_base.execute("DELETE FROM workflows WHERE workflow_name = " + "'" + workflow_name + "'" + " and path = " + "'" + path + "';")
							connection.commit()
							
							print ("\tPath/URL deleted!")
						else:
							print ("\tPath doesn't exist!")
					
					# Exit to Main Menu
					elif edit_choose is "4":
						print ("\tChanges saved!")
						run2 = False
			else:
				print ("This workflow does not exist...")
		elif menu_choose is "4":
		
			print ("Which workflow do you want to delete?")
			workflow_name = str(input())
			
			# Check if the workflow exists
			if workflow_exists(data_base, workflow_name):
				data_base.execute("DELETE FROM workflows WHERE workflow_name = ?;", (workflow_name,))

				# Save changes to prevent loss
				connection.commit()
				print ("Workflow deleted successfully!")
			else:
				print ("This workflow does not exist...")
		
		# Print workflows
		elif menu_choose is "5":
			workflows_dict = {}
			
			# Save the data to a dict
			for name in data_base.execute("SELECT workflow_name, path FROM workflows;"):
				workflows_dict[name[0]] = []
			
			for name in data_base.execute("SELECT workflow_name, path FROM workflows;"):
				workflows_dict[name[0]].append(name[1])
			
			if bool(workflows_dict):
				print ("We found these workflows:")
				print ('')
			else:
				print ("No workflows were created!")
			
			# Print the data
			for key, value in workflows_dict.items():
				print ("Name: " + key)
				
				for i in range(len(value)):
					if i == 0:
						print ("Paths: " + value[i])
					else:
						print ("	   " + value[i])
				print ('')
		
		# Exit the program
		elif menu_choose is "6":
			print ("See you later!")
			run = False
			
	# Save (commit) the changes
	connection.commit()
	
	# Close the connection with the DB
	connection.close()

if __name__ == "__main__": 
	main()